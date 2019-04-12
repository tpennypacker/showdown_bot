from helper_functions import funcs
from helper_functions import get_info
from helper_functions import senders
from battle import Battle
from settings import ai_settings
import json
import random
from operator import itemgetter





# gets called at the start of each turn
async def choose_moves(ws, battles, battletag):

	battle = funcs.get_battle(battles, battletag)
	allies = battle.allies
	mega = get_info.get_can_mega(battle.team_data)

	scores = get_info.calculate_scores(battle)
	sorted_scores = sorted(scores, key = lambda i: i['power'], reverse=True)


	decisions = []
	for i in range (2):
		if (allies[i] != ""):
			move, target, bp = get_info.find_best_move_active_foes(battle, allies[i])

			# consider switching
			if (bp >= ai_settings.damage_floor and sorted_scores[0]['power'] > (ai_settings.switch_mult * bp)):
				decisions.append('switch ' + sorted_scores[0]['name'])
				sorted_scores.pop(0) # make sure you don't switch to the same pokemon twice

			# attack
			else:
				decisions.append(funcs.attack(move, target, mega[i]))

		# if the slot is fainted, don't send a command for it
		else:
			decisions.append("")


	# combine moves
	if (allies[0] != "" and allies[1] != ""):
		#command_str = battletag + "|/choose " + decision1 + ", " + decision2
		command_str = battletag + "|/choose " + decisions[0] + ", " + decisions[1]
	else:
		#command_str = battletag + "|/choose " + decision1 + decision2
		command_str = battletag + "|/choose " + decisions[0] + decisions[1]

	await senders.send_turn_decision(ws, command_str)



# gets called when forced to switch
async def choose_switch(ws, battle, battletag):

	scores = get_info.calculate_scores(battle)
	sorted_scores = sorted(scores, key = lambda i: i['power'], reverse=True)

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
