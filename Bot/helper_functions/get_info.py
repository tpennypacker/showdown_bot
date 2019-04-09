import json
import random


def random_move():
	return random.randint(1, 4)

def random_foe():
	return random.randint(1, 2)

# called at start of each turn, checks if can mega
def get_can_mega(battledata):

	mega_dic = {True: ' mega', False: ''}
	can_mega1 = 'canMegaEvo' in battledata['active'][0].keys()
	can_mega2 = 'canMegaEvo' in battledata['active'][1].keys()
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
def find_supereffective_move(battle, user):
	with open('data/moves.json') as moves_file:
		moves = json.load(moves_file)
		my_moves = battle.team_data["active"][user]["moves"]

		# for each move
		for i in range(len(my_moves)):
			id = my_moves[i]["move"].lower().replace(" ", "").replace("-", "")

			type = moves[id]["type"]
			foes_types = get_foes_types(battle)

			# for each foe
			for j in range (len(foes_types)):
				if (get_type_effectiveness(type, foes_types[j]) > 1):
					return (i+1, j+1)

	return (random_move(), random_foe())



# example return: [["Fire"], ["Fire", "Flying"]]
def get_foes_types(battle):
	types = []
	with open('data/pokedex.json') as pokedex_file:
		pokedex = json.load(pokedex_file)
		for foe in battle.foes:
			formatted_foe = get_formatted_name(foe)
			types.append(pokedex[formatted_foe]["types"])

	return types



mons_with_useless_forms = ['gastrodon', 'shellos', 'florges', 'genesect',
							'deerling', 'sawsbuck', 'burmy', 'furfrou',
							'magearna', 'minior']
def get_formatted_name(foe):
	formatted = foe.lower().replace(' ', '').replace('-', '').replace("'", "")

	for mon in mons_with_useless_forms:
		if mon in formatted:
			return mon

	return formatted



