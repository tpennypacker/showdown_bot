import json
import random
from operator import itemgetter
from settings import ai_settings
from helper_functions import formatting
import numpy as np


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


# find best move for a given pokemon against the active foes
# returns (move_name, foe_index, effective base power)
def find_best_move_active_foes(battle, user):
	possible_moves = []
	foes = battle.active_pokemon("foe")
	for i, foe in enumerate(foes, 1):
		if (foe.fainted): # ignore dead foe
			continue
		moves_damage = find_best_move_against_foe(battle, user, foe)
		possible_moves.append(moves_damage)

	# deal with spread moves which only hit opponents (e.g. Muddy Water)
	for i in range (len(possible_moves[0])):
		move = possible_moves[0][i]
		if (is_spread_move(move[0])):
			possible_moves[0][i][1] = 3  # indicate that target is both foes
			if (len(possible_moves) > 1):  # apply spread calculations if both foes alive
				possible_moves[0][i][2] += possible_moves[1][i][2]  # add base power against second target
				possible_moves[0][i][2] *= 0.75  # apply spread reduction factor
				possible_moves[1][i][2] = 0  # set second instance of spread move to 0 damage

	# combine lists of moves against each foe into single list of possible moves
	possible_moves = [move for sublist in possible_moves for move in sublist]

	# sort based on power
	possible_moves = sorted(possible_moves, key=itemgetter(2), reverse=True)
	# return (move name, target index, effective bp) of strongest move/target combination
	return possible_moves[0]


# user is a pokemon object, foe is a pokemon object
# returns list of (move_name, foe_index, effective base power) for each usable move
def find_best_move_against_foe(battle, user, foe):
	with open('data/moves.json') as moves_file:
		moves = json.load(moves_file)
		user_index = user.active
		my_types = user.types
		my_ability = user.active_ability
		foe_types = foe.types
		possible_moves = [] # list of possible moves in format [move, target, effective bp]

		if (user_index > 0): # active pokemon
			user_active = True
			my_moves = user.active_info["moves"]
			my_moves = [formatting.format_active_move(move) for move in my_moves]
			if (my_moves[0] == "struggle"): # if only have struggle, then send set response
				return (1, None, 50)
		else: # pokemon in back
			user_active = False
			my_moves = [formatting.remove_hp_power(move) for move in user.moves]

		if (foe.active > 0): # if target foe active then give position
			foe_index = foe.active
		else:  # otherwise return None
			foe_index = None

		# for each move
		for move in my_moves:
			if (move == ""): # don't consider disabled moves
				continue
			move_category = moves[move]["category"]
			move_type = moves[move]["type"]
			base_power = moves[move]["basePower"]
			effective_bp = base_power * get_stab_effectiveness(move_type, my_types, my_ability) * get_type_effectiveness(move_type, foe_types) * get_ability_effectiveness(my_ability, move_type, battle.active_pokemon("foe"), foe) * get_field_modifier(battle, my_types, my_ability, move_type, move_category, foe, foe_types)
			possible_moves.append([move, foe_index, effective_bp])

	# return (move name, target index, effective bp) of each move
	return possible_moves


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
				alive_foes = [foe for foe in foes if not foe.fainted]  # only consider alive foes
				foes_abilities = [foe.possible_abilities for foe in alive_foes]  # get possible abilities
				foes_abilities = [item for sublist in foes_abilities for item in sublist]  # combine to single list
				# if foes have ability then return 0
				if redirectable_types[move_type] in foes_abilities:
					return 0

			if (move_type in absorbable_types.keys()):
				# get possible abilities for targeted foe
				target_abilities = target.possible_abilities
				# if foe has ability then return 0
				for foe_ability in target_abilities:
					if foe_ability in absorbable_types[move_type]:
						return 0
	# if opponent can't have any absorbing abilities, then return 1
	return 1


# get modifier from weather/terrain
def get_field_modifier(battle, my_types, my_ability, move_type, move_category, foe, foe_types):
	# each True or False
	user_flying = ("Flying" in my_types or my_ability == "levitate")
	target_flying = ("Flying" in foe_types or "Levitate" in foe.possible_abilities)
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
	scores = []
	pokemons = battle.my_team
	# for each pokemon on team
	for pokemon in pokemons:
		# skip if the pokemon is already out, or if fainted
		if (pokemon.active > 0 or pokemon.fainted):
			continue
		# otherwise calculate score ratio and append to list with name
		name = formatting.get_formatted_name(pokemon.id)
		ratio = calculate_score_ratio_single(battle, pokemon)
		scores.append({'name':name, 'ratio':ratio})
	# sort if required from highest to lowest ratio
	if (len(scores) > 0):
		scores = sorted(scores, key = lambda i: i['ratio'], reverse=True)
	return(scores)


# calculate score ratio for a single pokemon object
def calculate_score_ratio_single(battle, pokemon):
	# get pokemon's "score" against the opponent
	move, target, power = find_best_move_active_foes(battle, pokemon)
	# get the sum of the opponent's scores against us
	foes_score = []
	foes = battle.active_pokemon("foe")
	for foe in foes:
		if (foe.fainted): # ignore dead foes
			continue

		foe_score = []
		foe_types = foe.types
		for foe_type in foe_types:
			# NEED TO TAKE INTO ACCOUNT WEATHER / TERRAIN / ABILITIES
			damage = ai_settings.ai_bp * 1.5 * get_type_effectiveness(foe_type, pokemon.types)
			foe_score.append(damage)

		index, value = max(enumerate(foe_score), key=itemgetter(1))
		foes_score.append(value)
	foes_total_score = np.sum(foes_score)

	ratio = power / foes_total_score
	return ratio


def is_spread_move(formatted_move):
	with open('data/moves.json') as moves_file:
		moves = json.load(moves_file)
		move_data = moves[formatted_move]
		return (move_data['target'] == 'allAdjacentFoes')
