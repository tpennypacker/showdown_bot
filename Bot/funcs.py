import websockets
import bot_settings
import requests
import json
import random

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

def random_move():
	return random.randint(1, 4)

def random_foe():
	return random.randint(1, 2)


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
	await hello(ws, battletag)
	print("Saying " + bot_settings.hello + "\n")
	if (bot_settings.timer):
		await timer(ws, battletag)
		print("Timer started for match: " + battletag + "\n")
		#await choose_leads(ws, battletag)

# gets called once at the end of the battle
async def on_battle_end(ws, battletag):
	await goodbye(ws, battletag)
	print("Saying " + bot_settings.goodbye + "\n")
	await leave_battle(ws, battletag)
	if (bot_settings.ionext):
		await ionext(ws)
		print("Your next match will be invite-only. \n")
	if(bot_settings.autosearch):
		await search_again(ws, battletag)
		print("Searching for a new match. \n")


# gets called at the start of each turn
async def choose_moves(ws, battledata, battletag):

	mega1, mega2 = get_can_mega(ws, battledata, battletag)
	decision1 = attack(random_move(), random_foe(), mega1)
	decision2 = attack(random_move(), random_foe(), mega2)
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


# called at start of each turn, checks if can mega
def get_can_mega(ws, battledata, battletag):

	battle_json = json.loads(battledata)
	mega_dic = {True: ' mega', False: ''}
	can_mega1 = 'canMegaEvo' in battle_json['active'][0].keys()
	can_mega2 = 'canMegaEvo' in battle_json['active'][1].keys()
	mega_str1 = mega_dic[can_mega1]
	mega_str2 = mega_dic[can_mega2]
	return mega_str1, mega_str2
