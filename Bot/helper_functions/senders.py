import websockets
from settings import bot_settings



async def ionext(ws):
	await ws.send("|/ionext")
	print("Your next match will be invite-only. \n")

async def change_avatar(ws):
	await ws.send("|/avatar " + bot_settings.avatar)
	print("Your avatar has been changed to " + bot_settings.avatar + ".\n")

async def join_room(ws):
	await ws.send("|/join " + bot_settings.auto_join_room)
	print("Joining the " + bot_settings.auto_join_room + " room\n")

async def timer(ws, battletag):
	await ws.send(battletag + "|/timer on")
	print("Timer started for match: " + battletag + "\n")

async def hello(ws, battletag, phrase):
	await ws.send(battletag + "|" + phrase)
	print("Saying " + phrase + "\n")

async def goodbye(ws, battletag, phrase):
	await ws.send(battletag + "|" + phrase)
	print("Saying " + phrase + "\n")

async def leave_battle(ws, battletag):
	await ws.send(battletag + "|/leave")

async def search_again(ws, battletag):
	mode = battletag.split('-')[1]
	await ws.send("|/search " + mode)
	print("Searching for a new match. \n")

async def blockpms(ws):
	if (bot_settings.block_pms):
		await ws.send("|/blockpms")
		print("Blocked PMs")
	else:
		await ws.send("|/unblockpms")
		print("Unblocked PMs")

async def blockchallenges(ws):
	if (bot_settings.block_challenges):
		await ws.send("|/blockchallenges")
		print("Blocked challenges")
	else:
		await ws.send("|/unblockchallenges")
		print("Unblocked challenges")

async def accept_challenge(ws, challenger, bot_team):
	await ws.send("|/utm " + bot_team)
	await ws.send("|/accept " + challenger)
	print("Accepting challenge from " + challenger + " in " + bot_settings.play_tier + "\n")

async def send_login_msg(ws, msg):
	await ws.send(msg)
	print("Logging in")

async def send_pm(ws, msg, user):
	await ws.send("|/pm {}, {}".format(user,msg))
	#print("Sending following message to user {}: {}".format(user, msg))


async def send_lead_decision(ws, leads, battletag):
	command_str = battletag + "|/choose team " + "".join(leads)
	print("Sending lead decision: " + command_str)
	await ws.send(command_str)

async def send_turn_decision(ws, command_str):
	print("Sending turn decision: " + command_str)
	await ws.send(command_str)

async def send_forced_switch_decision(ws, command_str):
	print("Sending forced switch: " + command_str)
	await ws.send(command_str)
