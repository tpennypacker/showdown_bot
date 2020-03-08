import requests
import json
import os
import random
import time

from settings import bot_settings
from helper_functions import get_info
from helper_functions import senders
from helper_functions import team_reader


def attack(move, foe, mega, dynamax):
    if foe != None and foe != 3: # make sure there is a foe, and that the move is not a spread move
        return ("move " + str(move) + mega + dynamax + " " + str(foe))
    else:
        return ("move " + str(move) + mega + dynamax)


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
async def startup_ops(ws, msg_arr):
    print("You have successfully logged in as " + bot_settings.username + "\n")

    bot_settings.all_bot_teams = team_reader.read_all_teams(os.listdir("teams"))
    bot_settings.active_bot_team = bot_settings.all_bot_teams[bot_settings.team_file]

    if (bot_settings.accept_challenges):
        print("Using team {} for accepting challenges in tier {}".format(bot_settings.team_file, bot_settings.play_tier))

    login_data = json.loads(msg_arr[-1])

    await senders.blockpms(ws, login_data['blockPMs'])
    await senders.blockchallenges(ws, login_data['blockChallenges'])

    if (len(bot_settings.avatar) > 0):
        await senders.change_avatar(ws)

    if (bot_settings.ionext):
        await senders.ionext(ws)

    if (len(bot_settings.auto_join_room) > 0):
        await senders.join_room(ws)

    if (bot_settings.autosearch):
        await senders.search_for_battle(ws)


# gets called once at the start of the battle
async def on_battle_start(ws, battles, battletag):
    battle = get_battle(battles, battletag)
    if (bot_settings.ionext):
        await senders.ionext(ws)
    await senders.hello(ws, battletag, random.choice(bot_settings.hello).replace("<opponent_name>", battle.opponent_name).replace("<username>", bot_settings.username))
    if (bot_settings.timer):
        await senders.timer(ws, battletag)


# gets called once at the end of the battle
async def on_battle_end(ws, battles, battletag, winner):
    battle = get_battle(battles, battletag)
    # send win/lose text
    if (winner == True):
        phrase = random.choice(bot_settings.win_txt).replace("<opponent_name>", battle.opponent_name).replace("<username>", bot_settings.username)
    else:
        phrase = random.choice(bot_settings.lose_txt).replace("<opponent_name>", battle.opponent_name).replace("<username>", bot_settings.username)
    await senders.goodbye(ws, battletag, phrase, winner)
    # save replay
    await senders.save_replay(ws, battletag)
    with open("replays.txt", 'a') as outfile:
        battle = get_battle(battles, battletag)
        win_dict = {True: "Win", False: "Loss"}
        opp_team = [mon.id for mon in battle.foe_team]
        opp_name = ''.join( [ ch for ch in battle.opponent_name if ch.isalnum() ])
        out_text = "https://replay.pokemonshowdown.com/" + battletag.split("battle-")[-1] + " | " + win_dict[winner] + " | " + opp_name + " | " + ", ".join(opp_team) + "\n"
        outfile.write(out_text)
    # leave battle and look for next
    time.sleep(3)  # wait 1 second so replay saved before leaving
    await senders.leave_battle(ws, battletag)
    if(bot_settings.autosearch):
        await senders.search_for_battle(ws)


# accept challenges if in correct tier
async def handle_challenges(ws, msg_arr):
    challenges = json.loads(msg_arr[2])
    challengers = challenges["challengesFrom"].keys()
    for challenger in challengers:
        if (challenges["challengesFrom"][challenger] == bot_settings.play_tier):
            await senders.accept_challenge(ws, challenger, bot_settings.active_bot_team)
