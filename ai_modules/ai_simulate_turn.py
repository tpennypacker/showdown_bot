"""
Simulate Turn AI (WIP)
Bot will choose first two Pokemon on team for leads
Bot switch to Pokemon with best ratio of calculated damage dealt/received against opposing active Pokemon
Bot will simulate each possible combination of attacks (without considering foe) and choose by heuristic prioritising KOs, then total damage
Bot will never use Mega Evolution, Z-moves, or Dynamax
Bot does not 'see' Dynamax


process:
- get legal moves (don't include switches)
- for each possible combination of moves:
	- calculate move order ()
	- calc and deal damage for attacks (don't consider status; or moves that hit partner properly)
	- if KO foe, then mark as fainted and remove from move queue
	- after all moves completed, evaluate new battle state with heuristic (100 per alive mon, and 1 per % hp, + your team - foe's team)
	- use move combination leading to highest state evalution
"""



from helper_functions import calc
from helper_functions import funcs
from helper_functions import get_info
from helper_functions import simulation
from helper_functions import senders
from helper_functions import formatting
from battle import Battle
from settings import ai_settings
import copy
import sys
import json
import random
from operator import itemgetter


mega_dic = {True: ' mega', False: ''}
dyna_dic = {True: ' dynamax', False: ''}


# evaluates battle and returns a single number representing how 'good' it is
def state_heuristic(battle):
	score = 0
	for pokemon in battle.my_team:
		if ( not pokemon.fainted ):
			score += 100 + pokemon.health_percentage
	for pokemon in battle.foe_team:
		if ( not pokemon.fainted ):
			score -= 100 + pokemon.health_percentage
	return score

# gets called at the start of each turn
async def choose_moves(ws, battle):

	# get active pokemon
	allies = battle.active_pokemon("bot")
	foes = battle.active_pokemon("foe")

	bot_choices = []

	# get list of legal moves for each Pokemon
	for pokemon in allies:
		if pokemon.fainted: # for dead pokemon pass
			bot_choices.append(['pass'])
		else:
			moves = simulation.get_possible_moves(pokemon, battle, 0)
			bot_choices.append(moves)


	# for foes
	foe_choices = []
	for pokemon in foes:
		if pokemon.fainted: # for dead pokemon pass
			foe_choices.append(['pass'])
		else:
			moves = simulation.get_possible_moves(pokemon, battle, 0)
			foe_choices.append(moves)

	best_choice = ""
	best_state = None

	player_dict = {"bot": "foe", "foe": "bot"}
	with open('data/moves.json') as moves_file:
		moves_dex = json.load(moves_file)

	#pos = len(bot_choices[0]) * len(bot_choices[1]) #* len(foe_choices[0]) * len(foe_choices[1])
	#ind = 0

	# simulate each possible user move combination against foe's first option
	for move_1 in bot_choices[0]:
		for move_2 in bot_choices[1]:
			#for foe_move_1 in foe_choices[0]:
				#for foe_move_2 in foe_choices[1]:
			foe_move_1 = foe_choices[0][0]
			foe_move_2 = foe_choices[1][0]
			#ind += 1
			#print("Simulation {}/{}".format(ind,pos))
			#foe_move_1, foe_move_2 = foe_choices[0][0], foe_choices[1][0]
			move_order = [move_1, move_2, foe_move_1, foe_move_2]
			#print(move_order)
			move_order = [move for move in move_order if move != "pass"] # remove moves from dead pokemon
			move_order = sorted(move_order, key=lambda x: (x[-2], x[-1])) # sort by priority then by speed
			battle_copy = copy.deepcopy(battle)
			# while moves left
			while ( len(move_order) > 0 ):
				# sort order after each move due to new speed mechanics (need to recalculate speeds first!)
				#moves = sorted(unsorted, key=lambda x: (x[1], x[2]))
				# get move and remove from list
				move = move_order.pop(0)
				# currently only consider attacks by bot
				if (moves_dex[move[2]]['category'] == 'Status' or move[0] == "foe"):
					continue
				# get user and targets to deal with attack
				user = next((mon for mon in battle_copy.active_pokemon(move[0]) if mon.id == move[1]))
				foes = battle_copy.active_pokemon(player_dict[move[0]])
				simulation.simulate_attack(move, user, foes, battle_copy, move_order)
			# moves done, would do end of turn effects here
			# evaluate new state with heuristic function based on hp/alive pokemon
			score = state_heuristic(battle_copy)
			# if better than current best choice, then update
			if (best_state == None or score > best_state):
				best_state = score
				best_choice = formatting.format_move_choice(move_1, move_2)

	command_str = battle.battletag + "|/choose " + best_choice
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
