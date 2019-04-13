import json
import random
from operator import itemgetter
from settings import ai_settings
import numpy as np


def random_move():
	return random.randint(1, 4)

def random_foe():
	return random.randint(1, 2)

# called at start of each turn, checks if can mega
def get_can_mega(team_data):

	mega_dic = {True: ' mega', False: ''}
	can_mega1 = 'canMegaEvo' in team_data['active'][0].keys()
	can_mega2 = 'canMegaEvo' in team_data['active'][1].keys()
	mega_str1 = mega_dic[can_mega1]
	mega_str2 = mega_dic[can_mega2]
	return mega_str1, mega_str2


# attack_type is a string, ie "Fire"
# target_types is an array, ie ["Fire"] or ["Fire, Flying"]
def get_type_effectiveness(attack_type, target_types):
	mult = 1.0
	with open('data/typechart.json') as typechart_file:
		typechart = json.load(typechart_file)
		for target_type in target_types:
			x = typechart[target_type]["damageTaken"][attack_type]
			if (x == 1): mult *= 2 # super effective
			elif (x == 2): mult *= 0.5 # not very effective
			elif (x == 3): mult *= 0 # doesn't affect

	return mult


# return index position of target pokemon in list of pokemon (e.g. target foe in active mons)
def index_of_pokemon(target, pokemon_list):
	target = get_formatted_name(target)
	pokemon_list = [get_formatted_name(pokemon) for pokemon in pokemon_list]
	return pokemon_list.index(target)


# e.g. convert "hiddenpowerice60" to "hiddenpowerice"
def remove_hp_power(move_name):
	if ("hiddenpower" in move_name):
		return move_name[:-2]
	else:
		return move_name


# format active moves, and denote disabled moves as ""
def format_active_move(move):
	if (move["disabled"] == True):
		return ""
	else:
		return move["move"].lower().replace(" ", "").replace("'", "").replace("-", "").replace(",", "")


def get_formatted_team_names(battle):
	pokemons = battle.team_data['side']['pokemon']
	pokemons = [get_formatted_name(pokemon['details']) for pokemon in pokemons]
	return pokemons


# find best move for a given mon against the active foes
# returns (move_name, foe_index, effective base power)
def find_best_move_active_foes(battle, user):
	possible_moves = []
	foes = battle.foes
	for i, foe in enumerate(foes, 1):
		if (foe == ""): # ignore dead foe
			continue
		moves_damage = find_best_move_against_foe(battle, user, foe)
		possible_moves.append(moves_damage)

	# deal with spread moves which only hit opponents (e.g. Muddy Water)
	if (len(possible_moves) > 1):
		for i in range (len(possible_moves[0])):
			move = possible_moves[0][i]
			if (is_spread_move(move[0])):
				possible_moves[0][i][2] += possible_moves[1][i][2] # add base power against second target
				possible_moves[0][i][2] *= 0.75 # apply spread reduction factor
				possible_moves[0][i][1] = 3 # indicate that target is both foes
				possible_moves[1].pop(i) # pop the second instance of the spread move

	# combine lists of moves against each foe into single list of possible moves
	possible_moves = [move for sublist in possible_moves for move in sublist]

	# sort based on power
	possible_moves = sorted(possible_moves, key=itemgetter(2), reverse=True)
	# return (move name, target index, effective bp) of strongest move/target combination
	return possible_moves[0]



# user is Pokemon's name, foe is Pokemon's name
# returns list of (move_name, foe_index, effective base power) for each usable move
def find_best_move_against_foe(battle, user, foe):
	with open('data/moves.json') as moves_file:
		moves = json.load(moves_file)
		user_index = index_of_pokemon(user, get_formatted_team_names(battle))
		my_types = get_pokemons_types([user])[0]
		my_ability = battle.team_data["side"]["pokemon"][user_index]["ability"]
		foe_types = get_pokemons_types([foe])[0]
		possible_moves = [] # list of possible moves in format [move, target, effective bp]

		if (user_index <= 1): # active pokemon
			user_active = True
			my_moves = battle.team_data["active"][user_index]["moves"]
			my_moves = [format_active_move(move) for move in my_moves]
			if (my_moves[0] == "struggle"): # if only have struggle, then send set response
				return (1, None, 50)
		else: # pokemon in back
			user_active = False
			my_moves = battle.team_data["side"]["pokemon"][user_index]["moves"]
			my_moves = [remove_hp_power(move) for move in my_moves]

		if (foe in battle.foes): # if target foe active then get position for sending move
			foe_index = index_of_pokemon(foe, battle.foes) + 1
		else:
			foe_index = None

		# for each move
		for move in my_moves:
			if (move == ""): # don't consider disabled moves
				continue
			move_category = moves[move]["category"]
			move_type = moves[move]["type"]
			base_power = moves[move]["basePower"]
			effective_bp = base_power * get_stab_effectiveness(move_type, my_types, my_ability) * get_type_effectiveness(move_type, foe_types) * get_ability_effectiveness(my_ability, move_type, battle.foes, foe) * get_field_modifier(battle, my_types, my_ability, move_type, move_category, foe, foe_types)
			possible_moves.append([move, foe_index, effective_bp])

	# return (move name, target index, effective bp) of each move
	return possible_moves


# example return: [["Fire"], ["Fire", "Flying"]]
def get_pokemons_types(pokemon_list):
	types = []
	with open('data/pokedex.json') as pokedex_file:
		pokedex = json.load(pokedex_file)
		for pokemon in pokemon_list:
			if (pokemon != ""):
				formatted_pokemon = get_formatted_name(pokemon)
				types.append(pokedex[formatted_pokemon]["types"])
			else: # return empty list [] if fainted pokemon
				types.append([])

	return types


mons_with_useless_forms = ['gastrodon', 'shellos', 'florges', 'genesect',
							'deerling', 'sawsbuck', 'burmy', 'furfrou',
							'magearna', 'minior']

def get_formatted_name(pokemon):
	formatted = pokemon.split(",")[0].lower().replace(' ', '').replace('-', '').replace("'", "").replace(":", "").strip("\n")

	for mon in mons_with_useless_forms:
		if mon in formatted:
			return mon

	return formatted


# calculate STAB bonus
def get_stab_effectiveness(move_type, my_types, my_ability):
	if (move_type in my_types):
		if (my_ability == "adaptability"):
			return 2
		else:
			return 1.5
	else:
		return 1


absorbable_types = {"Fire":["Flash Fire"], "Water":["Dry Skin", "Water Absorb", "Storm Drain"], "Grass":["Sap Sipper"], "Electric":["Volt Absorb", "Lightning Rod", "Motor Drive"], "Ground":["Levitate"]}
redirectable_types = {"Water":"Storm Drain", "Electric":"Lightning Rod"}
# consider absorbing abilities
def get_ability_effectiveness(my_ability, move_type, foes, target):
	with open('data/pokedex.json') as pokedex_file:
		pokedex = json.load(pokedex_file)
		# if don't have ability ignoring ability, and absorbable move type, then check for abilities
		if (my_ability != "terravolt" and my_ability != "turboblaze" and my_ability != "moldbreaker"):
			if (move_type in redirectable_types.keys()):
				# get both foes abilities need to consider, list of all possiblities in one big list
				alive_foes = [get_formatted_name(foe) for foe in foes if foe != ""]
				foes_abilities = [pokedex[foe]["abilities"].values() for foe in alive_foes]
				foes_abilities = [item for sublist in foes_abilities for item in sublist]
				# if foes have ability then return 0
				if redirectable_types[move_type] in foes_abilities:
					return 0

			if (move_type in absorbable_types.keys()):
				# get possible abilities for targeted foe
				target_foe = get_formatted_name(target)
				target_abilities = pokedex[target_foe]["abilities"].values()
				# if foe has ability then return 0
				for foe_ability in target_abilities:
					if foe_ability in absorbable_types[move_type]:
						return 0
	# if opponent can't have any absorbing abilities, then return 1
	return 1


# get relevant team_data about a given pokemon
def get_pokemon_from_team(battle, target_mon):
	return next((pokemon for pokemon in battle.team_data["side"]["pokemon"] if target_mon in pokemon["details"]), None)


# get modifier from weather/terrain
def get_field_modifier(battle, my_types, my_ability, move_type, move_category, foe, foe_types):
	with open('data/pokedex.json') as pokedex_file:
		pokedex = json.load(pokedex_file)
		formatted_foe = get_formatted_name(foe)
		# each True or False
		user_flying = ("Flying" in my_types or my_ability == "levitate")
		target_flying = ("Flying" in foe_types or "Levitate" in pokedex[formatted_foe]["abilities"].values())
		mult = 1
		# rock sp def boost in sand
		if (battle.weather == "Sandstorm" and "Rock" in foe_types and  move_category == "Special"):
			mult *= 2/3
		# sun/rain effects
		elif (move_type == "Fire"):
			if (battle.weather == "SunnyDay"):
				mult *= 1.5
			elif (battle.weather == "RainDance"):
				mult *= 0.5
		elif (move_type == "Water"):
			if (battle.weather == "SunnyDay"):
				mult *= 0.5
			elif (battle.weather == "RainDance"):
				mult *= 1.5
		# terrain
		if (move_type == "Dragon"):
			if (battle.terrain == "Misty Terrain" and target_flying == False):
				mult *= 0.5
		elif (user_flying == False):
			if (move_type == "Electric" and battle.terrain == "Electric Terrain"):
				mult *= 1.5
			if (move_type == "Psychic" and battle.terrain == "Psychic Terrain"):
				mult *= 1.5
			if (move_type == "Grass" and battle.terrain == "Grassy Terrain"):
				mult *= 1.5
	return mult


# calculate scores used for switching, uses strongest move for each available pokemon
def calculate_score_ratio_switches(battle):
	with open('data/pokedex.json') as pokedex_file:
		pokedex = json.load(pokedex_file)
		scores = []

		pokemons = battle.team_data['side']['pokemon']

		for pokemon in pokemons:
			# skip if the pokemon is already out, or if fainted
			if (pokemon['active'] or pokemon['condition'] == '0 fnt'):
				continue

			name = get_formatted_name(pokemon['details'])

			ratio = calculate_score_ratio_single(battle, name)

			scores.append({'name':name, 'ratio':ratio})

		if (len(scores) > 0):
			scores = sorted(scores, key = lambda i: i['ratio'], reverse=True)
		return(scores)


# calculate score ratio for a single pokemon with formatted name "name"
def calculate_score_ratio_single(battle, name):
	with open('data/pokedex.json') as pokedex_file:
		pokedex = json.load(pokedex_file)

		# get pokemon's "score" against the opponent
		move, target, power = find_best_move_active_foes(battle, name)

		# get the sum of the opponent's scores against us
		foes_score = []
		for foe in battle.foes:
			foe_score = []
			foe_types = pokedex[get_formatted_name(foe)]['types']
			for foe_type in foe_types:
				# NEED TO TAKE INTO ACCOUNT WEATHER / TERRAIN / ABILITIES
				damage = ai_settings.ai_bp * 1.5 * get_type_effectiveness(foe_type, pokedex[name]['types'])
				foe_score.append(damage)

			index, value = max(enumerate(foe_score), key=itemgetter(1))
			foes_score.append(value)
		foes_total_score = np.sum(foes_score)

		ratio = power / foes_total_score
	return ratio


def format_switch_name(pokemon_name):
	pokemon_name = pokemon_name.split(',')[0]
	if (pokemon_name[-4:] == "mega"):
		return pokemon_name[:-4]
	elif (pokemon_name[-5:] == "megax" or pokemon_name[-5:] == "megay"):
		return pokemon_name[:-5]
	else:
		return pokemon_name


def get_can_switch(team_data):
	active_info = team_data["active"]
	can_switch = []
	for i in range(2):
		keys = active_info[i].keys()
		if ("trapped" in keys or "maybeTrapped" in keys):
			can_switch.append(False)
		else:
			can_switch.append(True)
	return can_switch


def is_spread_move(formatted_move):
	with open('data/moves.json') as moves_file:
		moves = json.load(moves_file)
		move_data = moves[formatted_move]
		return (move_data['target'] == 'allAdjacentFoes')
