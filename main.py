import asyncio
import copy
import websockets
import requests
import json
import os
import sys
import platform
from string import printable

from ai_modules import ai_simulate_turn as ai # need to change in battle.py as well
from settings import bot_settings
from helper_functions import funcs
from helper_functions import team_reader
from helper_functions import battlelog_parser
from helper_functions import pm_commands
#from helper_functions import logging
from battle import Battle
from pokemon import Pokemon


battles = []

async def parse_response(ws, msg):

    msg_arr = msg.split('|')

    # ignore short messages
    if ( len(msg_arr) == 1 ):
        print("length 1 message: " + msg)

    # display error messages
    elif (msg_arr[1] == "error" or msg_arr[1] == "popup"):
        print(msg)

    #  display PMs received, handle command messages from whitelisted users
    elif (msg_arr[1] == "pm"):
        print(msg)
        sender = msg_arr[2].strip().lower().replace(" ", "").replace("≧◡≦","")
        whitelist = [username.lower().strip() for username in bot_settings.bot_owners.split(",")]
        if (msg_arr[4][0] == "$" and sender in whitelist):
            await pm_commands.parse_command(ws, msg_arr[4], sender)

    # triggers when a battle ends, checks if bot won and sends appropriate message
    elif (msg_arr[0][0:7] == ">battle" and "win" in msg_arr):
        battletag = funcs.get_battletag(msg_arr)
        win_id = msg_arr.index("win") + 1
        bot_won = (msg_arr[win_id].strip("\n").lower() == bot_settings.username.lower())
        await funcs.on_battle_end(ws, battles, battletag, bot_won)
        # remove finished battle
        battle = funcs.get_battle(battles, battletag)
        battle.did_bot_win = bot_won
        #logging.record_battle(battle)
        remove_id = battles.index(battle)
        battles.pop(remove_id)

    # checks if challenges to be accepted
    elif (msg_arr[1] == "updatechallenges" and bot_settings.accept_challenges == True):
        #print(msg)
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
    elif (msg_arr[1] == 'updateuser' and msg_arr[2].lower().strip() == bot_settings.username.lower()):
        #print(msg)
        await funcs.startup_ops(ws, msg_arr)

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
            #battle.opponent_elo, battle.opponent_gxe = logging.get_rank(battle.opponent_name)
            #battle.my_elo, battle.my_gxe = logging.get_rank(bot_settings.username)
            battle.foe_side = msg_arr[2]
            await funcs.on_battle_start(ws, battles, battletag)
        # if message contains team preview, read in teams and prompt leads
        if ("teampreview\n" in msg_arr):
            battle.initialise_teams(msg_arr)
            await battle.load_team_data(ws)

async def connect_to_ps():
    async with websockets.connect("ws://sim.smogon.com:8000/showdown/websocket", ping_interval=None) as ws:
        while(True):
            msg = await ws.recv()
            await parse_response(ws, msg)


# clear screen
if (platform.system() == "Windows"):
    os.system('cls') # windows
else:
    os.system('clear') # mac


asyncio.get_event_loop().run_until_complete(connect_to_ps())
#asyncio.get_event_loop().run_forever()
