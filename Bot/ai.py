from helper_functions import funcs
from helper_functions import get_info
from helper_functions import senders
from battle import Battle
import json
import random
from operator import itemgetter





# gets called at the start of each turn
async def choose_moves(ws, battles, battletag):
	battle = funcs.get_battle(battles, battletag)
	allies = battle.allies
	mega1, mega2 = get_info.get_can_mega(battle.team_data)
	if (allies[0] != ""): # decide 1st move if alive
		move1, target1, bp1 = get_info.find_best_move_active_foes(battle, allies[0])
		decision1 = funcs.attack(move1, target1, mega1)
	else:
		decision1 = ""
	if (allies[1] != ""): # decide 2nd move if alive
		move2, target2, bp2 = get_info.find_best_move_active_foes(battle, allies[1])
		decision2 = funcs.attack(move2, target2, mega2)
	else:
		decision2 = ""
	if (allies[0] != "" and allies[1] != ""): # combine moves
		command_str = battletag + "|/choose " + decision1 + ", " + decision2
	else:
		command_str = battletag + "|/choose " + decision1 + decision2
	await senders.send_turn_decision(ws, command_str)



# gets called when forced to switch
async def choose_switch(ws, battle, battletag):

	scores = get_info.calculate_scores(battle)
	sorted_scores = sorted(scores, key = lambda i: i['power'], reverse=True)

	print("_________________\n")

	switch1, switch2 = battle.team_data['forceSwitch']  # each True or False

	# if only one mon left
	if (len(sorted_scores) < 2):
		if (switch1 == switch2):
			switch_str = "switch, switch"
		else:
			switch_str = "switch"

	# switch both, multiple mons left
	elif (switch1 == switch2):
		switch_str = "switch " + sorted_scores[0]['name'].split(',')[0] + ", switch " + sorted_scores[1]['name'].split(',')[0]

	# switch one
	else:
		switch_str = "switch " + sorted_scores[0]['name'].split(',')[0]

	command_str = battletag + "|/choose " + switch_str
	await senders.send_forced_switch_decision(ws, command_str)



# gets called at team preview
async def choose_leads(ws, battledata, battletag):
	battle_json = json.loads(battledata)
	num_pokemon = len(battle_json["side"]["pokemon"])
	leads = random.sample(range(1, num_pokemon+1), 2)  # e.g. 2 unique numbers from 1-6
	leads = [str(i) for i in leads]
	await senders.send_lead_decision(ws, leads, battletag)
