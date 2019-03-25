# https://github.com/Zarel/Pokemon-Showdown/blob/master/PROTOCOL.md

import asyncio
import websockets
import requests
import json
import os

username = "AskKey"
password = "ascii"

async def message():
	async with websockets.connect("ws://sim.smogon.com:8000/showdown/websocket") as ws:

		raw_formats = await ws.recv() # just a list of game formats
		parsed_formats = raw_formats.split('|')
		randbat_string = "| / Search gen7randombattle"#parsed_formats[8]


		response = await ws.recv() # get challstr
		array = response.split('|') # parse challstr
		challid = array[2]
		chall = array[3]

		resp = requests.post("https://play.pokemonshowdown.com/action.php?",
                         data={
                            'act': 'login',
                            'name': username,
                            'pass': password,
                            'challstr': challid + "%7C" + chall
                         })
		jdata = json.loads(resp.text[1:]) # load response into json array. [1:] is to get rid of the first character
		login_msg = "/trn " + username + ",0," + jdata['assertion']

		await ws.send(login_msg)

		search_msg = "/search " + randbat_string
		await ws.send(search_msg)

		response = await ws.recv()
		print(response)



os.system('clear')
asyncio.get_event_loop().run_until_complete(message())
#asyncio.get_event_loop().run_forever()