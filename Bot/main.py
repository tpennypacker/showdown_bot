# Based on the Pokemon Showdown protocol, found here:
# https://github.com/Zarel/Pokemon-Showdown/blob/master/PROTOCOL.md

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

    if (msg_arr[1] == "challstr"):
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

    elif (msg_arr[1] == 'updateuser' and username in msg_arr[2]):
        print("Congrats, you've logged in! Searching for game now.")
        randbat_string = "gen7randombattle"#parsed_formats[8]
        search_msg = "|/search " + randbat_string
        await ws.send(search_msg)

    else:
        print("Unknown message type incominggggggg")
        print(msg)





async def connect_to_ps():
    async with websockets.connect("ws://sim.smogon.com:8000/showdown/websocket") as ws:
        while(True):
            print("_____________________________")
            msg = await ws.recv()
            #print(msg)
            await parse_response(ws, msg)
            print("_____________________________")

















asyncio.get_event_loop().run_until_complete(connect_to_ps())
