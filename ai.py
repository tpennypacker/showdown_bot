from helper_functions import funcs
from helper_functions import get_info
from helper_functions import senders
from helper_functions import formatting
from battle import Battle
from settings import ai_settings
import json
import random
from operator import itemgetter


mega_dic = {True: ' mega', False: ''}


# gets called at the start of each turn
async def choose_moves(ws, battle):

	# get active pokemon and scores for possible switches
	allies = battle.active_pokemon("bot")
	sorted_ratios = get_info.calculate_score_ratio_switches(battle)

	decisions = []
	# for each active pokemon
	for i, pokemon in enumerate(allies):
		if (not pokemon.fainted): # only need move for alive pokemon
			# get best (strongest) move and ratio score
			move, target, bp = get_info.find_best_move_active_foes(battle, pokemon)
			my_ratio = get_info.calculate_score_ratio_single(battle, pokemon)
			# check if can switch or mega
			keys = pokemon.active_info.keys()
			can_mega = ("canMegaEvo" in keys)
			can_switch = ("trapped" not in keys and "maybeTrapped" not in keys)

			# switch under certain conditions
			if (len(sorted_ratios) > 0 and can_switch and bp <= ai_settings.damage_floor and sorted_ratios[0]['ratio'] > (ai_settings.switch_mult * my_ratio)):
				decisions.append('switch ' +  formatting.format_switch_name(sorted_ratios[0]['name']))
				sorted_ratios.pop(0) # make sure you don't switch to the same pokemon twice

			# attack, otherwise
			else:
				decisions.append(funcs.attack(move, target, mega_dic[can_mega]))

			print("{}'s strongest move is {} against target {} for {}% damage".format(pokemon.id, move, target, bp))

	# combine moves
	if (len(decisions) > 1):
		command_str = battle.battletag + "|/choose " + decisions[0] + ", " + decisions[1]
	else:
		command_str = battle.battletag + "|/choose " + decisions[0]
	# send turn decision
	await senders.send_turn_decision(ws, command_str)



# gets called when forced to switch
async def choose_switch(ws, battle, switches):

	# get score ratios used for determining best switch
	sorted_scores = get_info.calculate_score_ratio_switches(battle)
	switch1, switch2 = switches  # each True or False

	# if only one mon left
	if (len(sorted_scores) < 2):
		if (switch1 == switch2): # 2 switches required
			switch_str = "switch, switch"
		else: # 1 switch required
			switch_str = "switch"

	# switch both, multiple mons left
	elif (switch1 == switch2):
		switch_str = "switch " + formatting.format_switch_name(sorted_scores[0]['name']) + ", switch " +  formatting.format_switch_name(sorted_scores[1]['name'])

	# switch one, multiple mons left
	else:
		switch_str = "switch " +  formatting.format_switch_name(sorted_scores[0]['name'])
	# send switch decision
	command_str = battle.battletag + "|/choose " + switch_str
	await senders.send_forced_switch_decision(ws, command_str)



# gets called at team preview
async def choose_leads(ws, battle):
	# pick 2 random pokemon on team
	num_pokemon = len(battle.my_team)
	leads = random.sample(range(1, num_pokemon+1), 2)  # e.g. 2 unique numbers from 1-6
	leads = [str(i) for i in leads]
	# send leads decision
	await senders.send_lead_decision(ws, leads, battle.battletag)
