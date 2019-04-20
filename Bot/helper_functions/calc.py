import json


def get_move_bp(move, all_moves):
	move_data = all_moves[move]
	power = move_data["basePower"]

	spread = 1
	target = move_data["target"]
	if (target == "allAdjacent" or target == "allAdjacentFoes"):
		spread = 0.75

	return power, spread


# calculate STAB bonus
def get_stab_effectiveness(move_type, my_types):
	if (move_type in my_types):
		return 1.5
	else:
		return 1

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


absorbable_types = {"Fire":["Flash Fire"], "Water":["Dry Skin", "Water Absorb", "Storm Drain"], "Grass":["Sap Sipper"], "Electric":["Volt Absorb", "Lightning Rod", "Motor Drive"], "Ground":["Levitate"]}
redirectable_types = {"Water":"Storm Drain", "Electric":"Lightning Rod"}

# consider absorbing / redirecting abilities
def get_ability_effectiveness(user_abilities, move_type, foes, target):

	# if don't have ability ignoring ability, and absorbable move type, then check for abilities
	if (not ("teravolt" in user_abilities) and not ("turboblaze" in user_abilities) and not ("moldbreaker" in user_abilities)):
		if (move_type in redirectable_types.keys()):
			# get both foes abilities need to consider, list of all possiblities in one big list
			alive_foes = [foe for foe in foes if not foe.fainted]  # only consider alive foes
			foes_abilities = [foe.abilities for foe in alive_foes]  # get possible abilities
			foes_abilities = [item for sublist in foes_abilities for item in sublist]  # combine to single list
			# if foes have ability then return 0
			if redirectable_types[move_type] in foes_abilities:
				return 0

		if (move_type in absorbable_types.keys()):
			# get possible abilities for targeted foe
			target_abilities = target.abilities
			# if foe has ability then return 0
			for foe_ability in target_abilities:
				if foe_ability in absorbable_types[move_type]:
					return 0
	# if opponent can't have any absorbing abilities, then return 1
	return 1

# get modifier from weather/terrain
def get_field_modifier(battle, my_types, my_abilities, move_type, move_category, foe):

	# each True or False
	user_flying = ("flying" in my_types or "levitate" in my_abilities)
	target_flying = ("flying" in foe.types or "levitate" in foe.abilities)
	mult = 1
	# rock sp def boost in sand
	if (battle.weather == "sandstorm" and "rock" in foe.types and  move_category == "Special"):
		mult *= 2/3
	# sun/rain effects
	elif (move_type == "Fire"):
		if (battle.weather == "sunnyday"):
			mult *= 1.5
		elif (battle.weather == "raindance"):
			mult *= 0.5
	elif (move_type == "Water"):
		if (battle.weather == "sunnyday"):
			mult *= 0.5
		elif (battle.weather == "raindance"):
			mult *= 1.5
	# terrain
	if (move_type == "Dragon"):
		if (battle.terrain == "mistyterrain" and target_flying == False):
			mult *= 0.5
	elif (user_flying == False):
		if (move_type == "Electric" and battle.terrain == "electricterrain"):
			mult *= 1.5
		if (move_type == "Psychic" and battle.terrain == "psychicterrain"):
			mult *= 1.5
		if (move_type == "Grass" and battle.terrain == "grassyterrain"):
			mult *= 1.5
	return mult


# Currently based on base stats. Should be based on actual stats in the future.
# Still need to take into account moves like psyshock
def get_stat_ratio(category, user, target):
	stat_ratio = 1
	if (category == "Physical"):
		attack = user.base_stats["atk"] * user.buff["atk"][1]
		defense = target.base_stats["def"] * user.buff["def"][1]
		stat_ratio = attack / defense
	elif (category == "Special"):
		spatk = user.base_stats["spa"] * user.buff["spa"][1]
		spdef = target.base_stats["spd"] * user.buff["spd"][1]
		stat_ratio = spatk / spdef
	return stat_ratio


# move is the move ID (string)
# user and target are pokemon objects
# battle is a battle object
def calc_damage (move, user, target, battle):
	with open('data/moves.json') as moves_file:
		with open('data/pokedex.json') as pokedex_file:
			all_moves = json.load(moves_file)
			pokedex = json.load(pokedex_file)

			power, spread = get_move_bp(move, all_moves) #includes spread damage mult
			if (power == 0): 
				return 0
			stab = get_stab_effectiveness(all_moves[move]["type"], user.types)
			type_eff = get_type_effectiveness(all_moves[move]["type"], target.types)
			ability_eff = get_ability_effectiveness(user.abilities, all_moves[move]["type"], battle.foe_team, target)
			field_mult = get_field_modifier(battle, user.types, user.abilities, all_moves[move]["type"], all_moves[move]["category"], target)
			crit = 1
			random = 1 # actually between 0.85 and 1
			burn = 1

			modifier = spread * field_mult * crit * random * stab * type_eff * burn * ability_eff

			level = 100
			stat_ratio = get_stat_ratio(all_moves[move]["category"], user, target)

			damage = ((2 * level / 5) * power * stat_ratio / 50 + 2) * modifier

			#print("Damage of " + user.id + "'s " + move + " against " + target.id + ": " + str(damage))

			return damage


