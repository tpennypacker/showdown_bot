import json
import random
from operator import itemgetter

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


# user is 0 or 1
# returns move_index, foe_index
def find_best_move(battle, user):
	with open('data/moves.json') as moves_file:
		moves = json.load(moves_file)
		my_pokemon = get_pokemon_from_team(battle, battle.allies[user])
		my_moves = battle.team_data["active"][user]["moves"]
		my_types = get_pokemons_types(battle.allies)[user]
		my_ability = my_pokemon["baseAbility"]
		foes = battle.foes
		foes_types = get_pokemons_types(foes)
		possible_moves = [] # list of possible moves in format [move, target, effective bp]

		if (my_moves[0]["id"] == "struggle"): # if only have struggle, then send set response
			return (1, None)


		# for each move
		for i, move in enumerate(my_moves, 1):
			id = move["id"]
			type = moves[id]["type"]
			base_power = moves[id]["basePower"]

			if (move["disabled"] == True): # don't consider disabled moves
				continue


			# for each foe
			if (foes[0] != "" and foes[1] != ""): # both alive
				for j, foe in enumerate(foes_types, 1):
					effective_bp = base_power * get_stab_effectiveness(type, my_types, my_ability) * get_type_effectiveness(type, foe) * get_ability_effectiveness(my_ability, type, foes, j-1)
					possible_moves.append([i, j, effective_bp])
			else:
				if (foes[0] != ""): # only 1st alive
					effective_bp = base_power * get_stab_effectiveness(type, my_types, my_ability) * get_type_effectiveness(type, foes_types[0]) * get_ability_effectiveness(my_ability, type, foes, 0)
					possible_moves.append([i, 1, effective_bp])
				else: # only 2nd alive
					effective_bp = base_power * get_stab_effectiveness(type, my_types, my_ability) * get_type_effectiveness(type, foes_types[1]) * get_ability_effectiveness(my_ability, type, foes, 1)
					possible_moves.append([i, 2, effective_bp])

		# sort possible moves by effective base power in descending order
		possible_moves = sorted(possible_moves, key=itemgetter(2), reverse=True)
	# return move/target of strongest move
	return possible_moves[0][0:2]


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
	formatted = pokemon.lower().replace(' ', '').replace('-', '').replace("'", "")

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
		if (my_ability != "terravolt" or my_ability != "turboblaze" or my_ability != "moldbreaker"):
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
				target_foe = get_formatted_name(foes[target])
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
