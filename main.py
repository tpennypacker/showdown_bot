import asyncio
import websockets
import requests
import json
import os
import sys
import platform
from string import printable

import ai
from settings import bot_settings
from helper_functions import funcs
from helper_functions import team_reader
from helper_functions import battlelog_parser
from helper_functions import pm_commands
from battle import Battle
from pokemon import Pokemon


battles = []

async def parse_response(ws, msg):
	msg_arr = msg.split('|')

	# if get message from whitelisted username starting with $ then take command
	if (msg_arr[1] == "pm" and msg_arr[4][0] == "$"):
		sender = msg_arr[2].strip().lower().replace(" ", "")
		whitelist = [username.lower().strip() for username in bot_settings.bot_owners.split(",")]
		if (sender in whitelist):
			await pm_commands.parse_command(ws, msg_arr[4], sender)

	# triggers when a battle ends, checks if bot won and sends appropriate message
	if (msg_arr[0][0:7] == ">battle" and "win" in msg_arr):
		battletag = funcs.get_battletag(msg_arr)
		win_id = msg_arr.index("win") + 1
		bot_won = (msg_arr[win_id].strip("\n").lower() == bot_settings.username.lower())
		await funcs.on_battle_end(ws, battles, battletag, bot_won)
		# remove finished battle
		battle = funcs.get_battle(battles, battletag)
		remove_id = battles.index(battle)
		battles.pop(remove_id)

	# checks if challenges to be accepted
	elif (msg_arr[1] == "updatechallenges" and bot_settings.accept_challenges == True):
		await funcs.handle_challenges(ws, msg_arr)

	# triggers on any request message, adds team_data from it to battle
	elif (msg_arr[1] == "request"):
		battletag = funcs.get_battletag(msg_arr)
		battle = funcs.get_battle(battles, battletag)
		battle.next_team_data = msg_arr[2]

	# triggers when receive information about a battle
	elif (msg_arr[0][0:7] == ">battle" and msg_arr[1] == "\n"):
		battletag = funcs.get_battletag(msg_arr)
		battle = funcs.get_battle(battles, battletag)
		# read in information from message
		battlelog_parser.battlelog_parsing(battle, msg)
		# read data from previous request message, and prompt any needed switch/move
		await battle.load_team_data(ws)

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

	# triggers when get information at start of battle about either player
	elif ('>battle' in msg_arr[0] and msg_arr[1] == 'player'):
		battletag = funcs.get_battletag(msg_arr)
		battle = funcs.get_battle(battles, battletag)
		# note player's side
		if (msg_arr[3].lower() == bot_settings.username.lower()):
			battle.my_side = msg_arr[2]
		else: # note foe's name, side, and send greeting message
			battle.opponent_name = msg_arr[3]
			battle.foe_side = msg_arr[2]
			await funcs.on_battle_start(ws, battles, battletag)
		# if message contains team preview, read in teams and prompt leads
		if ("teampreview\n" in msg_arr):
			battle.initialise_teams(msg_arr)
			await battle.load_team_data(ws)


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


# clear screen
if (platform.system() == "Windows"):
	os.system('cls') # windows
else:
	os.system('clear') # mac

asyncio.get_event_loop().run_until_complete(connect_to_ps())
