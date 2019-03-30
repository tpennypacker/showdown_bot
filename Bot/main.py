# Based on the Pokemon Showdown protocol, found here:
# https://github.com/Zarel/Pokemon-Showdown/blob/master/PROTOCOL.md

# Inspired by Synedh's bot, found here: 
# https://www.smogon.com/forums/threads/showdown-battle-bot-a-socket-battle-bot-for-showdown.3644033/

import asyncio
import websockets
import requests
import json
import os

os.system('clear')
username = "Ask Key"
password = "ascii"


async def parse_response(ws, msg):   
    msg_arr = msg.split('|')

    if(len(msg_arr) < 2):
        print(msg)

    # log in
    elif (msg_arr[1] == "challstr"):
        print("Challstr received")
        ID = msg_arr[2]
        challstr = msg_arr[3]
        response = requests.post("https://play.pokemonshowdown.com/action.php?",
                         data={
                            'act': 'login',
                            'name': username,
                            'pass': password,
                            'challstr': ID + "%7C" + challstr
                         })
        jdata = json.loads(response.text[1:]) # load response into json array. [1:] is to get rid of the first character
        login_msg = "|/trn " + username + ",0," + jdata['assertion']
        await ws.send(login_msg)

    # if haven't logged in yet
    elif (msg_arr[1] == 'updateuser' and "Guest" in msg_arr[2]):
        print("Currently registered as guest")

    # login successful!
    elif (msg_arr[1] == 'updateuser' and username in msg_arr[2]):
        print("Congrats, you've logged in! Typing /ionext now.")
        to_send = "|/ionext"
        await ws.send(to_send)
        # randbat_string = "gen7randombattle"#parsed_formats[8]
        # search_msg = "|/search " + randbat_string
        # await ws.send(search_msg)
        # await ws.send("|/help")
        # await ws.send("|/help msg")

    # on receiving a message in battle chat
    elif ('|c|' in msg):
        print("battle chat message incoming")
        print(msg)
        #await ws.send("|/msg GenOne, I am a robot and GenOne sucks at pokemon")

    # upon receiving a private message
    elif ('|pm|' in msg):
        print("private message incoming")
        print(msg)

    # when a new battle starts
    elif ('battle' in msg_arr[0] and msg_arr[1] == 'init'):
        to_send = "|/ionext"
        await ws.send(to_send)        
        battle_tag = msg_arr[0].split('>')[1].split('\n')[0]
        print("Battle started: " + battle_tag)

    else:
        print("Unknown message type incominggggggg")
        print(msg)
        if ('>' in msg_arr[0]):
            battle_tag = msg_arr[0].split('>')[1].split('\n')[0]
            to_send = battle_tag + "|hello!"
            print("SENDING: " + to_send)





async def connect_to_ps():
    async with websockets.connect("ws://sim.smogon.com:8000/showdown/websocket") as ws:
        while(True):
            print("_____________________________")
            msg = await ws.recv()
            #print(msg)
            await parse_response(ws, msg)
            print("_____________________________")

















asyncio.get_event_loop().run_until_complete(connect_to_ps())
