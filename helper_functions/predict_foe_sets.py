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
minus_speed_natures = ["brave", "relaxed", "quiet", "sassy"]
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

	# check for minus speed stuff
	num_min_speed_natures = 0
	for nature in possible_natures:
		if nature.lower().replace(' ', '') in minus_speed_natures:
			num_min_speed_natures += 1

	if num_min_speed_natures > 1:
		nature_buffs["spe"] = 0.9

	return highest_evs, nature_buffs


def get_items_from_line(line):
	items_data = line.split("\n")[2:]
	likely_items = []

	for item in items_data:
		for i in range (len(item)):
			if (item[i].isdigit()):

				probability = item[i:].split(".")[0]
				if(int(probability) >= ai_settings.beta):
					item_name = formatting.get_formatted_name(item[:i])
					if (item_name != "nothing"):
						likely_items.append(item_name)
				break


	return (likely_items)

#  get likely sets for the entire opposing team
def update_likely_sets(battle, pokemon):
	#site = "https://www.smogon.com/stats/2019-03/moveset/gen7doublesou-1500.txt"
	site = "https://www.smogon.com/stats/2019-11/moveset/gen8doublesou-1500.txt"
	request = requests.get(site)
	text = request.text

	pokedex = '\n'.join(text.split('\n')[1:])
	pokedex = pokedex.split("+----------------------------------------+ \n +----------------------------------------+")


	for foe_pokemon in pokemon:

		print("Getting likely moveset for " + foe_pokemon.id)
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
						foe_pokemon.calc_stats()

					elif ("Items" in line):
						items = get_items_from_line(line)
						foe_pokemon.item = items

				continue  # once found pokemon then move onto next one

		# default moves/stats if don't find in usage
		if (foe_pokemon.moves == []):
			foe_pokemon.moves = ["tackle"]
			foe_pokemon.evs = {"hp":252,"atk":252,"def":252,"spa":252,"spd":252,"spe":252}
			foe_pokemon.nature_buffs = {"hp":1.0,"atk":1.0,"def":1.0,"spa":1.0,"spd":1.0,"spe":1.0}
			foe_pokemon.calc_stats()
