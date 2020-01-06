"""
Random Move AI
Bot will randomly choose leads and switches from available Pokemon
Bot will randomly choose legal moves, excluding single target moves on teammate
Bot will not use Mega evolution / Z-moves / Dynamax

"""

from helper_functions import funcs
from helper_functions import get_info
from helper_functions import senders
from helper_functions import formatting
from battle import Battle
from settings import ai_settings
import json
import random
from operator import itemgetter

# variable determining if move decisions are formatted for printing or shown as sent to PS
format_output = True

# gets called at the start of each turn
async def choose_moves(ws, battle):

	# get active pokemon
	allies = battle.active_pokemon("bot")
	#sorted_ratios = get_info.calculate_score_ratio_switches(battle)

	decisions = []
	# for each active pokemon
	for i, pokemon in enumerate(allies):
		if pokemon.fainted: # for dead pokemon pass
			decisions.append(['pass'])
		else:
			#print(pokemon.active_info)

			moves_id = []
			#moves_name = []

			# get each legal move
			for j, move in enumerate(pokemon.active_info['moves']):
				j = str(j+1)
				# ignore disabled moves
				if ( 'disabled' in move.keys() and move['disabled'] ):
					continue
				# moves with no target required
				if ('target' not in move.keys() or move['target'] not in ['normal', 'any', 'adjacentFoe', 'adjacentAlly']):
					moves_id.append("move " + j)
					#moves_name.append("move " + move['id'])
				elif (move['target'] == 'adjacentAlly'): # move targetting teammate (e.g. Helping Hand)
					moves_id.append("move " + j + " -1")
				else: # moves with an individual target (ignore targetting teammate)
					moves_id.append("move " + j + " 1")
					moves_id.append("move " + j + " 2")
					#moves_name.append("move " + move['id'] + " 1")
					#moves_name.append("move " + move['id'] + " 2")

			#print(moves_name)

			decisions.append(moves_id)

			# check if can switch or mega
			#keys = pokemon.active_info.keys()
			#can_mega = ("canDynamax" in keys) also have ["maxMoves"]["maxMoves"][{"move":"maxrockfall","target":"adjacentFoe"},{"move":"maxdarkness","target":"adjacentFoe"}]
			#can_switch = ("trapped" not in keys and "maybeTrapped" not in keys)

			# switch under certain conditions
			#decisions.append('switch ' +  formatting.format_switch_name(sorted_ratios[0]['name']))

			# attack, otherwise
			#decisions.append(funcs.attack(move, target, mega_dic[can_mega]))

			#print("{}'s strongest move is {} against target {} for {}% damage".format(pokemon.id, move, target, bp))

	# choose random moves for each alive pokemon
	command_str = battle.battletag + "|/choose " + random.choice(decisions[0]) + ", " + random.choice(decisions[1])

	# send turn decision
	await senders.send_turn_decision(ws, command_str, battle, format_output)


# gets called when forced to switch
async def choose_switch(ws, battle, switches):

	#switches_id = []
	switches_names = []
	# for each pokemon on team
	for i, pokemon in enumerate(battle.my_team):
		# skip if the pokemon is already out, or if fainted
		if (pokemon.active > 0 or pokemon.fainted):
			continue
		# otherwise append to list
		name = formatting.get_formatted_name(pokemon.id)
		#switches_id.append(i+1)
		switches_names.append(name)

	# figure out number of switches, and randomly pick appropriate number
	if (switches[0] == switches[1] and len(switches_names) > 1): # 2 switches required
		switch1, switch2 = random.sample(switches_names, 2)
		switch_str = "switch " + switch1 + ", switch " + switch2
	elif (switches[0] == switches[1]): # 2 switches required but only 1 mon left
		switch_str = "switch " + switches_names[0] + ", pass"
	else: # 1 switch required
		switch_str = "switch " + random.choice(switches_names)

	# send switch decision
	command_str = battle.battletag + "|/choose " + switch_str
	await senders.send_forced_switch_decision(ws, command_str, battle, format_output)

"""
# gets called when forced to switch
async def choose_switch(ws, battle, switches):

	switches_id = []
	switches_name = []
	# for each pokemon on team
	for i, pokemon in enumerate(battle.my_team):
		# skip if the pokemon is already out, or if fainted
		if (pokemon.active > 0 or pokemon.fainted):
			continue
		# otherwise append to list
		name = formatting.get_formatted_name(pokemon.id)
		switches_id.append(i+1)
		switches_name.append(name)

	# figure out number of switches, and randomly pick appropriate number
	if (switches[0] == switches[1] and len(switches_names) > 1): # 2 switches required
		switch1, switch2 = random.sample(switches_names, 2)
		switch_str = "switch " + switch1 + ", switch " + switch2
	elif (switches[0] == switches[1]): # 2 switches required but only 1 mon left
		switch_str = "switch " + switches_names[0] + ", pass"
	else: # 1 switch required
		switch_str = "switch " + random.choice(switches_names)

	# send switch decision
	command_str = battle.battletag + "|/choose " + switch_str
	print(command_str)
	await senders.send_forced_switch_decision(ws, command_str, battle, format_output)
"""


# gets called at team preview
async def choose_leads(ws, battle):

	# pick 2 random pokemon on team
	num_pokemon = len(battle.my_team)
	leads = random.sample(range(1, num_pokemon+1), 2)  # e.g. 2 unique numbers from 1-6
	leads = [str(i) for i in leads]
	# send leads decision
	await senders.send_lead_decision(ws, leads, battle, format_output)
