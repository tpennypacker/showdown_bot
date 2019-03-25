# https://github.com/Zarel/Pokemon-Showdown/blob/master/PROTOCOL.md

import asyncio
import websockets
import requests


async def message():
	async with websockets.connect("ws://sim.smogon.com:8000/showdown/websocket") as socket:
		# msg = input("What do you want to send: ")
		# await socket.send(msg)

		response = await socket.recv()
		string_tab = response.split('|')
		print(string_tab)
		print(len(string_tab))


asyncio.get_event_loop().run_until_complete(message())