import os
import requests
import re
import json
from settings import ai_settings
from helper_functions import formatting



def get_moves_from_line(line):
	moves_data = line.split("\n")
	moves_data = moves_data[2:len(moves_data)-2]
	likely_moves = []

	for move in moves_data:
		for i in range (len(move)):
			if (move[i].isdigit()):

				probability = move[i:].split(".")[0]
				if(int(probability) >= ai_settings.alpha):
					move_name = formatting.get_formatted_name(move[:i])
					if (move_name != "nothing"):
						likely_moves.append(move_name)
				break


	return (likely_moves)


def get_likely_set(name):
	print("Getting likely moves for " + name)
	site = "https://www.smogon.com/stats/2019-03/moveset/gen7doublesou-1500.txt"
	request = requests.get(site)
	text = request.text

	pokedex = '\n'.join(text.split('\n')[1:])
	pokedex = pokedex.split("+----------------------------------------+ \n +----------------------------------------+")

	#print("Getting sets for " + name)
	for pokemon in pokedex:
		if (formatting.get_formatted_name(name) == formatting.get_formatted_name(pokemon.split("|")[1])):
			condensed_pokemon = pokemon.replace("   ", "").replace("|", "")
			pokemon_info = condensed_pokemon.split("+----------------------------------------+")

			for line in pokemon_info:
				if ("Moves" in line):
					moves = get_moves_from_line(line)
					return moves
				

