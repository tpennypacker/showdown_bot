"""
Damage Calc AI
Bot will choose first two Pokemon on team for leads
Bot switch to Pokemon with best ratio of calculated damage dealt/received against opposing active Pokemon
Bot will attack with move dealing most damage to either/both foes, or manually switch if damage output is relatively low
Bot will always Mega Evolve if possible, but will not use Z-moves or Dynamax*
*: Will always immediately dynamax Braviary if possible
Will also always double Rock Slide vs Indeedee-F + common TR setter
Bot does not 'see' Dynamax

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


mega_dic = {True: ' mega', False: ''}
dyna_dic = {True: ' dynamax', False: ''}


# gets called at the start of each turn
async def choose_moves(ws, battle):

	# get active pokemon
	allies = battle.active_pokemon("bot")
	foes = battle.active_pokemon("foe")

	# if have sand vs indeedee TR, use double rock slide
	if (allies[0].id == "Tyranitar" and allies[1].id == "Excadrill"):
		foe_ids = [mon.id for mon in foes]
		if ("Indeedee-F" in foe_ids):
			if ("Hatterene" in foe_ids or "Dusclops" in foe_ids or "Runerigus" in foe_ids or "Oranguru" in foe_ids or "Chandelure" in foe_ids or "Gothitelle" in foe_ids or "Bronzong" in foe_ids or "Reuniclus" in foe_ids or "Mr Rime" in foe_ids or "Mimikyu" in foe_ids):
				print("Sand vs TR: Rock Slide time")
				command_str = battle.battletag + "|/choose move rockslide, move rockslide"
				await senders.send_turn_decision(ws, command_str, battle)
				return
		if ("Runerigus" in foe_ids and "Greedent" in foe_ids):

			print("Sand vs Squirrel guy")
			iddd = foe_ids.index("Runerigus") + 1
			command_str = battle.battletag + "|/choose move crunch {}, move highhorsepower {}".format(iddd, iddd)
			await senders.send_turn_decision(ws, command_str, battle)
			return

	# get score ratios for switching
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
			can_dynamax = ("canDynamax" in keys and pokemon.id == "Braviary")

			# switch under certain conditions
			if (len(sorted_ratios) > 0 and can_switch and bp <= ai_settings.damage_floor and sorted_ratios[0]['ratio'] > (ai_settings.switch_mult * my_ratio)):
				decisions.append('switch ' +  formatting.format_switch_name(sorted_ratios[0]['name']))
				sorted_ratios.pop(0) # make sure you don't switch to the same pokemon twice

			# attack, otherwise
			else:
				decisions.append(funcs.attack(move, target, mega_dic[can_mega], dyna_dic[can_dynamax]))

			print("{}'s strongest move is {} against target {} for {}% damage".format(pokemon.id, move, target, bp))

	# combine moves
	if (len(decisions) > 1):
		command_str = battle.battletag + "|/choose " + decisions[0] + ", " + decisions[1]
	else:
		command_str = battle.battletag + "|/choose " + decisions[0]
	# send turn decision
	await senders.send_turn_decision(ws, command_str, battle)



# gets called when forced to switch
async def choose_switch(ws, battle, switches):

	# get score ratios used for determining best switch
	sorted_scores = get_info.calculate_score_ratio_switches(battle)
	switch1, switch2 = switches  # each True or False

	# if only one mon left
	if (len(sorted_scores) < 2):
		if (switch1 == switch2): # 2 switches required
			switch_str = "switch, switch"
		elif (switch1): # switch in 1st slot
			switch_str = "switch, pass"
		else: # switch in 2nd slot
			switch_str = "pass, switch"

	# switch both, multiple mons left
	elif (switch1 == switch2):
		switch_str = "switch " + formatting.format_switch_name(sorted_scores[0]['name']) + ", switch " +  formatting.format_switch_name(sorted_scores[1]['name'])

	# switch one, multiple mons left
	elif (switch1):
		switch_str = "switch " +  formatting.format_switch_name(sorted_scores[0]['name']) + ", pass"
	else:
		switch_str = "pass, switch " +  formatting.format_switch_name(sorted_scores[0]['name'])
	# send switch decision
	command_str = battle.battletag + "|/choose " + switch_str
	await senders.send_forced_switch_decision(ws, command_str, battle)



# gets called at team preview
async def choose_leads(ws, battle):
	# pick 2 random pokemon on team
	#num_pokemon = len(battle.my_team)
	#leads = random.sample(range(1, num_pokemon+1), 2)  # e.g. 2 unique numbers from 1-6
	#leads = [str(i) for i in leads]
	leads = ["1", "2"] # choose first two pokemon
	# send leads decision
	await senders.send_lead_decision(ws, leads, battle)
