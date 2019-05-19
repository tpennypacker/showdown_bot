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

nature_matrix = {"atk": ["lonely", "brave", "adamant", "naughty"],
		   "def": ["bold", "relaxed", "impish", "lax"],
		   "spa": ["modest", "mild", "quiet", "rash"],
		   "spd": ["calm", "gentle", "sassy", "careful"],
		   "spe": ["timid", "hasty", "jolly", "naive"]}
def get_spread_from_line(line):
	spreads_arr = line.split('\n')[2:]
	highest_evs = {"hp":0,"atk":0,"def":0,"spa":0,"spd":0,"spe":0}
	possible_natures = []
	for spread in spreads_arr:
		# skip entries that we don't want
		if ('Other' in spread or spread.replace(' ', '') == ''):
			continue
		else:
			ev_arr = spread.split(':')[1].split(' ')[0].split('/')
			ev_arr = list(map(int, ev_arr)) # convert to list of ints
			if (ev_arr[0] > highest_evs["hp"]):
				highest_evs["hp"] = ev_arr[0]
			if (ev_arr[1] > highest_evs["atk"]):
				highest_evs["atk"] = ev_arr[1]
			if (ev_arr[2] > highest_evs["def"]):
				highest_evs["def"] = ev_arr[2]
			if (ev_arr[3] > highest_evs["spa"]):
				highest_evs["spa"] = ev_arr[3]
			if (ev_arr[4] > highest_evs["spd"]):
				highest_evs["spd"] = ev_arr[4]
			if (ev_arr[5] > highest_evs["spe"]):
				highest_evs["spe"] = ev_arr[5]

			nature = spread.split(':')[0]
			possible_natures.append(nature.lower().replace(' ', ''))

	nature_buffs = {"hp":1.0,"atk":1.0,"def":1.0,"spa":1.0,"spd":1.0,"spe":1.0}

	for stat, natures in nature_matrix.items():
		for nature in natures:
			if nature in possible_natures:
				nature_buffs[stat] = 1.1

	return highest_evs, nature_buffs



# get the likely sets of just one pokemon
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

	return ["tackle"]




#  get likely sets for the entire opposing team
def update_likely_sets(battle):
	site = "https://www.smogon.com/stats/2019-03/moveset/gen7doublesou-1500.txt"
	request = requests.get(site)
	text = request.text

	pokedex = '\n'.join(text.split('\n')[1:])
	pokedex = pokedex.split("+----------------------------------------+ \n +----------------------------------------+")


	for foe_pokemon in battle.foe_team:

		print("Getting likely moves for " + foe_pokemon.id)
		for pokemon in pokedex:

			if (formatting.get_formatted_name(foe_pokemon.id) == formatting.get_formatted_name(pokemon.split("|")[1])):
				condensed_pokemon = pokemon.replace("   ", "").replace("|", "")
				pokemon_info = condensed_pokemon.split("+----------------------------------------+")
				

				for line in pokemon_info:
					if ("Moves" in line):
						moves = get_moves_from_line(line)
						foe_pokemon.moves = moves

					elif ("Spreads" in line):
						highest_evs, nature_buffs = get_spread_from_line(line)
						foe_pokemon.evs = highest_evs
						foe_pokemon.nature_buffs = nature_buffs


		if (foe_pokemon.moves == []):
			foe_pokemon.moves = ["tackle"]


		















				

