import websockets
import bot_settings
import requests
import json
import random
from helper_functions import get_info

async def ionext(ws):
	await ws.send("|/ionext")

async def change_avatar(ws):
	await ws.send("|/avatar " + bot_settings.avatar)

async def timer(ws, battletag):
	await ws.send(battletag + "|/timer on")

async def hello(ws, battletag):
	await ws.send(battletag + "|" + bot_settings.hello)

async def goodbye(ws, battletag):
	await ws.send(battletag + "|" + bot_settings.goodbye)

async def leave_battle(ws, battletag):
	await ws.send(battletag + "|/leave")

async def search_again(ws, battletag):
	mode = battletag.split('-')[1]
	await ws.send("|/search " + mode)

async def blockpms(ws):
	if (bot_settings.block_pms):
		await ws.send("|/blockpms")
	else:
		await ws.send("|/unblockpms")

async def blockchallenges(ws):
	if (bot_settings.block_challenges):
		await ws.send("|/blockchallenges")
	else:
		await ws.send("|/unblockchallenges")

def attack(move, foe, mega):
	return ("move " + str(move) + mega + " " + str(foe))

def get_battle(battles, battletag):
	return next((battle for battle in battles if battle.battletag == battletag), None)


async def log_in(ws, msg_arr):
	ID = msg_arr[2]
	challstr = msg_arr[3]
	response = requests.post("https://play.pokemonshowdown.com/action.php?",
		data={
			'act': 'login',
			'name': bot_settings.username,
			'pass': bot_settings.password,
			'challstr': ID + "%7C" + challstr
		})
	jdata = json.loads(response.text[1:])
	login_msg = "|/trn " + bot_settings.username + ",0," + jdata['assertion']
	await ws.send(login_msg)


# this gets called once when the user logs in
async def startup_ops(ws):
	print("You have successfully logged in as " + bot_settings.username + "\n")

	await blockpms(ws)
	if (bot_settings.block_pms):
		print("Blocked PMs.")
	else:
		print("Unblocked PMs.")

	await blockchallenges(ws)
	if (bot_settings.block_challenges):
		print("Blocked challenges.")
	else:
		print("Unblocked challenges.")

	if (len(bot_settings.avatar) > 0):
		await change_avatar(ws)
		print("Your avatar has been changed to " + bot_settings.avatar + ".\n")

	if (bot_settings.ionext):
		await ionext(ws)
		print("Your next match will be invite-only. \n")


# gets called once at the start of the battle
async def on_battle_start(ws, battletag):
	if (bot_settings.ionext):
		await ionext(ws)
		print("Your next match will be invite-only. \n")
	await hello(ws, battletag)
	print("Saying " + bot_settings.hello + "\n")
	if (bot_settings.timer):
		await timer(ws, battletag)
		print("Timer started for match: " + battletag + "\n")

# gets called once at the end of the battle
async def on_battle_end(ws, battletag):
	await goodbye(ws, battletag)
	print("Saying " + bot_settings.goodbye + "\n")
	await leave_battle(ws, battletag)
	if(bot_settings.autosearch):
		await search_again(ws, battletag)
		print("Searching for a new match. \n")


# gets called at the start of each turn
async def choose_moves(ws, battles, battletag):
	battle = get_battle(battles, battletag)

	mega1, mega2 = get_info.get_can_mega(battle.team_data)
	move1, target1 = get_info.find_supereffective_move(battle, 0)
	move2, target2 = get_info.find_supereffective_move(battle, 1)
	decision1 = attack(move1, target1, mega1)
	decision2 = attack(move2, target2, mega2)
	command_str = battletag + "|/choose " + decision1 + ", " + decision2
	print("Sending command: " + command_str)
	await ws.send(command_str)


# gets called at team preview
async def choose_leads(ws, battletag):

	leads = random.sample(range(1, 7), 2)  # 2 unique numbers from 1-6
	leads = [str(i) for i in leads]
	command_str = battletag + "|/choose team " + "".join(leads)
	print("Sending command: " + command_str)
	await ws.send(command_str)


# gets called when forced to switch
async def choose_switch(ws, battledata, battletag):

	battle_json = json.loads(battledata)
	switch1, switch2 = battle_json['forceSwitch']  # each True or False
	if (switch1 == switch2):
		switch_str = "switch, switch"
	else:
		switch_str = "switch"
	command_str = battletag + "|/choose " + switch_str
	print("Sending command: " + command_str)
	await ws.send(command_str)


# updates foes in the associated battle object
def update_active_foes(msg_arr, battles):
	battletag = msg_arr[0][1:].split("\n")[0]
	battle = get_battle(battles, battletag)
	
	# parse through the update looking for switches made by the opponent
	for i in range (3, len(msg_arr)):
		if (msg_arr[i-2] == "switch" and msg_arr[i-1][0:2] != battle.my_side):
			# store the new pokemon in the correct slot in the battle object
			if (msg_arr[i-1][2] == 'a'):
				battle.foes[0] = msg_arr[i].split(',')[0]
			elif (msg_arr[i-1][2] == 'b'):
				battle.foes[1] = msg_arr[i].split(',')[0]












