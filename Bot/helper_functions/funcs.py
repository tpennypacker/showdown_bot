from settings import bot_settings
import requests
import json
from helper_functions import get_info
from helper_functions import senders


def attack(move, foe, mega):
	if foe != None:
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


# gets called once at the start of the battle
async def on_battle_start(ws, battletag):
	if (bot_settings.ionext):
		await senders.ionext(ws)
	await senders.hello(ws, battletag)
	if (bot_settings.timer):
		await senders.timer(ws, battletag)

# gets called once at the end of the battle
async def on_battle_end(ws, battletag, winner):
	if (winner == 1):
		phrase = bot_settings.win_txt
	else:
		phrase = bot_settings.lose_txt
	await senders.goodbye(ws, battletag, phrase)
	await senders.leave_battle(ws, battletag)
	if(bot_settings.autosearch):
		await senders.search_again(ws, battletag)


# updates foes/allies in the associated battle object
def update_active_pokemon(msg_arr, battles):
	battletag = msg_arr[0][1:].split("\n")[0]
	battle = get_battle(battles, battletag)

	# parse through the update looking for relevant information
	for i in range (3, len(msg_arr)):
		# store new pokemon from switches or megas in correct slot of the battle object
		if (msg_arr[i-2] == "switch" or msg_arr[i-2] == "detailschange"):
			if (msg_arr[i-1][0:2] != battle.my_side):
				if (msg_arr[i-1][2] == 'a'):
					battle.foes[0] = msg_arr[i].split(',')[0]
				elif (msg_arr[i-1][2] == 'b'):
					battle.foes[1] = msg_arr[i].split(',')[0]
			else:
				if (msg_arr[i-1][2] == 'a'):
					battle.allies[0] = msg_arr[i].split(',')[0]
				elif (msg_arr[i-1][2] == 'b'):
					battle.allies[1] = msg_arr[i].split(',')[0]
		# replace fainted pokemon with empty string
		elif (msg_arr[i-2] == "faint"):
			if (msg_arr[i-1][0:2] != battle.my_side):
				if (msg_arr[i-1][2] == 'a'):
					battle.foes[0] = ""
				elif (msg_arr[i-1][2] == 'b'):
					battle.foes[1] = ""
			else:
				if (msg_arr[i-1][2] == 'a'):
					battle.allies[0] = ""
				elif (msg_arr[i-1][2] == 'b'):
					battle.allies[1] = ""
		# look for terrain being set
		elif (msg_arr[i-1] == "-fieldstart"):
			battle.terrain = msg_arr[i][6:]
		# look for terrain ending
		elif (msg_arr[i-1] == "-fieldend"):
			battle.terrain = None
		# look for weather
		elif (msg_arr[i-1] == "-weather"):
			if (msg_arr[i][0:4] == "none"):
				battle.weather = None
			else:
				battle.weather = msg_arr[i]




