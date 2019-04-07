import asyncio
import websockets
import requests
import json
import os
from string import printable

import bot_settings
import funcs


async def parse_response(ws, msg):
	msg_arr = msg.split('|')

	if (len(msg_arr) < 3):
		pass

	# triggers at team preview
	elif (msg_arr[1] == "request" and msg_arr[2][0:14] == '{"teamPreview"'):
		battletag = msg_arr[0][1:].split('\n')[0]
		await funcs.choose_leads(ws, battletag)

	# triggers when forced to switch
	elif (msg_arr[1] == "request" and msg_arr[2][0:14] == '{"forceSwitch"'):
		battletag = msg_arr[0][1:].split('\n')[0]
		await funcs.choose_switch(ws, msg_arr[2], battletag)

	# check if wait message
	elif (msg_arr[1] == "request" and msg_arr[2][0:7] == '{"wait"'):
		pass

	# triggers at the start of each turn
	elif (msg_arr[1] == "request" and len(msg_arr[2]) > 0):
		battletag = msg_arr[0][1:].split('\n')[0]
		await funcs.choose_moves(ws, msg_arr[2], battletag)

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
		await funcs.on_battle_start(ws, battletag)

	# triggers when a battle ends
	elif ('>battle' in msg_arr[0] and msg_arr[2] == 'win'):
		battletag = msg_arr[0][1:].split('\n')[0]
		await funcs.on_battle_end(ws, battletag)


async def connect_to_ps():
	async with websockets.connect("ws://sim.smogon.com:8000/showdown/websocket") as ws:
		with open("C:\\Users\\Stephen\\Desktop\\Programming\\Python\\codees\\bot with fespy3\\showdown_bot\\Bot\\bot_log.txt", "w") as logfile:
			while(True):
				#print("_____________________________")
				msg = await ws.recv()
				msg = msg.replace("\u2606", "*plyr*")
				print(msg, file=logfile)
				print("_____________________________\n", file=logfile)
				#print(msg)
				#print("_____________________________\n")
				await parse_response(ws, msg)

#os.system('cls') # windows
#os.system('clear') # mac
asyncio.get_event_loop().run_until_complete(connect_to_ps())
