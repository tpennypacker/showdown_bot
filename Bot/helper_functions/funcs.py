from settings import bot_settings
import requests
import json
from helper_functions import get_info
from helper_functions import senders


def attack(move, foe, mega):
	if foe != None and foe != 3: # make sure there is a foe, and that the move is not a spread move
		return ("move " + str(move) + mega + " " + str(foe))
	else:
		return ("move " + str(move) + mega)


def get_battle(battles, battletag):
	return next((battle for battle in battles if battle.battletag == battletag), None)


def get_battletag(msg_arr):
	return msg_arr[0][1:].split('\n')[0]


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
	await senders.send_login_msg(ws, login_msg)


# this gets called once when the user logs in
async def startup_ops(ws):
	print("You have successfully logged in as " + bot_settings.username + "\n")

	await senders.blockpms(ws)
	await senders.blockchallenges(ws)

	if (len(bot_settings.avatar) > 0):
		await senders.change_avatar(ws)

	if (bot_settings.ionext):
		await senders.ionext(ws)

	if (len(bot_settings.auto_join_room) > 0):
		await senders.join_room(ws)


# gets called once at the start of the battle
async def on_battle_start(ws, battles, battletag):
	battle = get_battle(battles, battletag)
	if (bot_settings.ionext):
		await senders.ionext(ws)
	await senders.hello(ws, battletag, bot_settings.hello.replace("<opponent_name>", battle.opponent_name))
	if (bot_settings.timer):
		await senders.timer(ws, battletag)


# gets called once at the end of the battle
async def on_battle_end(ws, battles, battletag, winner):
	battle = get_battle(battles, battletag)
	if (winner == True):
		phrase = bot_settings.win_txt.replace("<opponent_name>", battle.opponent_name)
	else:
		phrase = bot_settings.lose_txt.replace("<opponent_name>", battle.opponent_name)
	await senders.goodbye(ws, battletag, phrase)
	await senders.leave_battle(ws, battletag)
	if(bot_settings.autosearch):
		await senders.search_again(ws, battletag)


# accept challenges if in correct tier
async def handle_challenges(ws, msg_arr, bot_team):
	challenges = json.loads(msg_arr[2])
	challengers = challenges["challengesFrom"].keys()
	for challenger in challengers:
		if (challenges["challengesFrom"][challenger] == bot_settings.play_tier):
			await senders.accept_challenge(ws, challenger, bot_team)
