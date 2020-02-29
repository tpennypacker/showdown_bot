import json
from battle import Battle
from helper_functions import formatting



def get_move_bp(move, all_moves):
	move_data = all_moves[move]
	power = move_data["basePower"]
	return power


def get_spread_mult(move, all_moves, target, battle):
	move_data = all_moves[move]
	attack_type = move_data["target"]

	alive_foes = [mon for mon in battle.active_pokemon('foe') if not mon.fainted]
	alive_friends = [mon for mon in battle.active_pokemon('bot') if not mon.fainted]
	#alive_all = [mon for mon in battle.active_pokemon('both') if not mon.fainted]
	alive_all = alive_foes + alive_friends

	# moves that hit all pokemon on field
	if (attack_type == "allAdjacent" and len(alive_all) > 2):
		return 0.75

	# if there's only 1 target, spread mult is automatically 1
	if ((target.side == 'foe' and len(alive_foes) == 1) or (target.side == 'bot' and len(alive_friends) == 1)):
		return 1

	# if spread move
	if (attack_type == "allAdjacentFoes"):
		return 0.75

	return 1


# calculate STAB bonus
def get_stab_effectiveness(move_type, my_types, abilities):
	if (move_type in my_types):
		if ("adaptability" in abilities):
			return 2
		else:
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


absorbable_types = {"Fire":["flashfire"], "Water":["dryskin", "waterabsorb", "stormdrain"], "Grass":["sapsipper"], "Electric":["voltabsorb", "lightningrod", "motordrive"], "Ground":["levitate"]}
redirectable_types = {"Water":"stormdrain", "Electric":"lightningrod"}

# consider absorbing / redirecting abilities
def get_ability_effectiveness(user_abilities, move_type, foes, target, type_eff):

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
		# wonder guard
		if (type_eff <= 1 and "wonderguard" in target.abilities):
			return 0

	# if opponent can't have any absorbing abilities, then return 1
	return 1

# get modifier from weather/terrain
def get_field_modifier(battle, my_types, my_abilities, move_type, move_category, foe):

	# each True or False
	user_flying = ("Flying" in my_types or "levitate" in my_abilities)
	target_flying = ("Flying" in foe.types or "levitate" in foe.abilities)
	mult = 1
	# rock sp def boost in sand
	if (battle.weather == "sandstorm" and "Rock" in foe.types and  move_category == "Special"):
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
	# could combine below terrains and weather above
	elif (user_flying == False):
		if (move_type == "Electric" and battle.terrain == "electricterrain"):
			if (battle.gen >= 8):
				mult *= 1.5
			else:
				mult *= 1.3
		elif (move_type == "Psychic" and battle.terrain == "psychicterrain"):
			if (battle.gen >= 8):
				mult *= 1.5
			else:
				mult *= 1.3
		elif (move_type == "Grass" and battle.terrain == "grassyterrain"):
			if (battle.gen >= 8):
				mult *= 1.5
			else:
				mult *= 1.3
	return mult


# Currently based on base stats. Should be based on actual stats in the future.
# Still need to take into account moves like psyshock, secret sword
def get_stat_ratio(category, user, target):
	stat_ratio = 1
	if (category == "Physical"):
		attack = user.stats["atk"] * user.buff["atk"][1]
		defense = target.stats["def"] * target.buff["def"][1]
		stat_ratio = attack / defense
	elif (category == "Special"):
		spatk = user.stats["spa"] * user.buff["spa"][1]
		spdef = target.stats["spd"] * target.buff["spd"][1]
		stat_ratio = spatk / spdef
	return stat_ratio


def get_burn_modifier(move_name, move_category, status, abilities):
	facade_status = ["brn", "psn", "tox", "par"]
	mult = 1
	# double facade bp
	if (move_name == "facade" and status in facade_status):
		mult *= 2
	# burn halves physical damage, unless have guts or using facade
	if (status == "brn" and move_category == "Physical"):
		if ("guts" in abilities):
			mult *= 1.5
		elif (move_name == "facade"):
			mult *= 1
		else:
			mult *= 0.5
	return mult


def get_item_modifier(has_item, item, move_type, move_category):
	mult = 1
	# double facade bp
	if (not has_item):
		pass
	elif (move_category == "Physical" and 'choiceband' in item):
		mult *= 1.5
	elif (move_category == "Special" and 'choicespecs' in item):
		mult *= 1.5
	elif ('lifeorb' in item):
		mult *= 1.3
	return mult


# move is the move ID (string)
# user and target are pokemon objects
# battle is a battle object
def calc_damage (move, user, target, battle):
	with open('data/moves.json') as moves_file:
		all_moves = json.load(moves_file)
	with open('data/pokedex.json') as pokedex_file:
		pokedex = json.load(pokedex_file)

	power = get_move_bp(move, all_moves)
	if (power == 0):
		return 0

	move_type = all_moves[move]["type"]
	move_category = all_moves[move]["category"]

	#spread = get_spread_mult(move, all_moves, target, battle)
	spread = 1
	stab = get_stab_effectiveness(move_type, user.types, user.abilities)
	type_eff = get_type_effectiveness(move_type, target.types)
	ability_eff = get_ability_effectiveness(user.abilities, move_type, battle.active_pokemon('foe'), target, type_eff)
	field_mult = get_field_modifier(battle, user.types, user.abilities, move_type, move_category, target)
	crit = 1
	random = 1 # actually between 0.85 and 1
	burn = get_burn_modifier(move, move_category, user.status, user.abilities)
	item_mod = get_item_modifier(user.has_item, user.item, move_type, move_category)

	modifier = spread * field_mult * crit * random * stab * type_eff * burn * ability_eff * item_mod

	level = user.level
	stat_ratio = get_stat_ratio(all_moves[move]["category"], user, target)

	damage = int( ((2 * level / 5 + 2) * power * stat_ratio / 50 + 2) * modifier )
	#print(target.stats)
	# convert to percentage (can still be >100) and round to 1 decimal place e.g. 50.7
	damage_percent = round (damage / target.stats["hp"] * 100, 1)

	return damage_percent
