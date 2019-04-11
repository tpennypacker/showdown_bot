import asyncio
import websockets
import requests
import json
import os
from string import printable

import ai
import bot_settings
from helper_functions import funcs
from battle import Battle

battles = []

async def parse_response(ws, msg):
	msg_arr = msg.split('|')

	# triggers when a battle ends
	if ("|win|" in msg):
		battletag = msg_arr[0][1:].split('\n')[0]
		win_str = "|win|" + bot_settings.username.lower()
		if (win_str in msg.lower()): # see who won, and give appropriate response
			await funcs.on_battle_end(ws, battletag, 1)
		else:
			await funcs.on_battle_end(ws, battletag, 0)

	elif (len(msg_arr) < 3):
		pass

	# triggers at team preview
	elif (msg_arr[1] == "request" and msg_arr[2][0:14] == '{"teamPreview"'):
		battletag = msg_arr[0][1:].split('\n')[0]
		await ai.choose_leads(ws, msg_arr[2], battletag)

	# triggers when forced to switch
	elif (msg_arr[1] == "request" and msg_arr[2][0:14] == '{"forceSwitch"'):
		battletag = msg_arr[0][1:].split('\n')[0]
		battle = funcs.get_battle(battles, battletag)
		funcs.update_active_pokemon(msg_arr, battles)
		battle.team_data = json.loads(msg_arr[2])
		await ai.choose_switch(ws, battle, battletag)

	# triggers when get move request or wait request
	elif (msg_arr[1] == "request" and len(msg_arr[2]) > 0):
		battletag = msg_arr[0][1:].split('\n')[0]
		battle = funcs.get_battle(battles, battletag)
		battle.team_data = json.loads(msg_arr[2])

	# triggers when receieve battle information, can be at end of or during turn
	elif (msg_arr[0][0:7] == ">battle" and msg_arr[1] == "\n"):
		funcs.update_active_pokemon(msg_arr, battles)
		battletag = msg_arr[0][1:].split('\n')[0]
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

	# triggers when a battle starts
	elif ('>battle' in msg_arr[0] and msg_arr[1] == 'player' and msg_arr[3].lower() == bot_settings.username.lower()):
		battletag = msg_arr[0][1:].split('\n')[0]
		battles.append(Battle(battletag, msg_arr[2])) # instantiate battle object
		await funcs.on_battle_start(ws, battletag)


async def connect_to_ps():
	async with websockets.connect("ws://sim.smogon.com:8000/showdown/websocket") as ws:
		#with open("C:\\Users\\Stephen\\Desktop\\Programming\\Python\\codees\\bot with fespy5\\showdown_bot\\Bot\\bot_log.txt", "w") as logfile:
		while(True):
			msg = await ws.recv()
			#print(msg)
			#print("_____________________\n")
			#msg = msg.replace("\u2606", "*plyr*")
			#print(msg, file=logfile)
			#print("_____________________________\n", file=logfile)
			await parse_response(ws, msg)

#os.system('cls') # windows
#os.system('clear') # mac
asyncio.get_event_loop().run_until_complete(connect_to_ps())
