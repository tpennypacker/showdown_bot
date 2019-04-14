import asyncio
import websockets
import requests
import json
import os
from string import printable

import ai
from settings import bot_settings
from helper_functions import funcs
from helper_functions import team_reader
from battle import Battle
from pokemon import Pokemon

battles = []
bot_team = team_reader.read_team()

async def parse_response(ws, msg):
	msg_arr = msg.split('|')

	# triggers when a battle ends, checks if bot won and sends appropriate message
	if ("|win|" in msg):
		battletag = funcs.get_battletag(msg_arr)
		win_str = "|win|" + bot_settings.username.lower()
		bot_won = (win_str in msg.lower())
		await funcs.on_battle_end(ws, battles, battletag, 1)

	# checks if challenges to be accepted
	elif (msg_arr[1] == "updatechallenges" and bot_settings.accept_challenges == True):
		await funcs.handle_challenges(ws, msg_arr, bot_team)

	elif (len(msg_arr) < 3):
		pass

	# triggers at team preview
	elif (msg_arr[1] == "request" and msg_arr[2][0:14] == '{"teamPreview"'):
		battletag = funcs.get_battletag(msg_arr)
		await ai.choose_leads(ws, msg_arr[2], battletag)

	# triggers when forced to switch
	elif (msg_arr[1] == "request" and msg_arr[2][0:14] == '{"forceSwitch"'):
		battletag = funcs.get_battletag(msg_arr)
		battle = funcs.get_battle(battles, battletag)
		funcs.update_active_pokemon(msg_arr, battles)
		battle.team_data = json.loads(msg_arr[2])
		await ai.choose_switch(ws, battle, battletag)

	# triggers when get move request or wait request
	elif (msg_arr[1] == "request" and len(msg_arr[2]) > 0):
		battletag = funcs.get_battletag(msg_arr)
		battle = funcs.get_battle(battles, battletag)
		battle.team_data = json.loads(msg_arr[2])

	# triggers when receieve battle information, can be at end of or during turn
	elif (msg_arr[0][0:7] == ">battle" and msg_arr[1] == "\n"):
		funcs.update_active_pokemon(msg_arr, battles)
		battletag = funcs.get_battletag(msg_arr)
		battle = funcs.get_battle(battles, battletag)
		if ("|turn|" in msg):
			await ai.choose_moves(ws, battles, battletag)

	# check for short messages
	elif (len(msg_arr) < 4):
		pass

	# login action
	elif (msg_arr[1] == "challstr"):
		await funcs.log_in(ws, msg_arr)

	# triggers when user first logs in
	elif (msg_arr[1] == 'updateuser' and msg_arr[2].lower() == bot_settings.username.lower()):
		await funcs.startup_ops(ws)

	# triggers when battle initialises
	elif ('>battle' in msg_arr[0] and msg_arr[1] == 'init'):
		battletag = funcs.get_battletag(msg_arr)
		battles.append(Battle(battletag)) # instantiate battle object

	# triggers when can identify foe
	elif ('>battle' in msg_arr[0] and msg_arr[1] == 'player' and msg_arr[3].lower() != bot_settings.username.lower()):
		battletag = funcs.get_battletag(msg_arr)
		battle = funcs.get_battle(battles, battletag)
		battle.opponent_name = msg_arr[3]
		await funcs.on_battle_start(ws, battles, battletag)
		if ("clearpoke\n" in msg_arr):
			print(msg_arr)
			battle.initialise_teams(msg_arr)
			print(battle.my_team)
			print(battle.foe_team)

	# triggers when can identify bot's side
	elif ('>battle' in msg_arr[0] and msg_arr[1] == 'player' and msg_arr[3].lower() == bot_settings.username.lower()):
		battletag = funcs.get_battletag(msg_arr)
		battle = funcs.get_battle(battles, battletag)
		battle.my_side = msg_arr[2]
		if ("clearpoke\n" in msg_arr):
			battle.initialise_teams(msg_arr)
			battle.print_teams()

async def connect_to_ps():
	async with websockets.connect("ws://sim.smogon.com:8000/showdown/websocket") as ws:
		#with open("text_files/bot_log.txt", "w") as logfile:
		while(True):
			msg = await ws.recv()
			#print(msg)
			#print("_____________________\n")
			#msg = msg.replace("\u2606", "*plyr*")
			#print(msg, file=logfile)
			#print("_____________________________\n", file=logfile)
			await parse_response(ws, msg)

#os.system('cls') # windows
os.system('clear') # mac
asyncio.get_event_loop().run_until_complete(connect_to_ps())
