from helper_functions import formatting

from pokemon import Pokemon
import ai
import json


class Battle:

	def __init__(self, battletag):

		self.next_team_data = None  # data from request message to be parsed
		self.my_team = []  # list of pokemon objects
		self.foe_team = []
		self.team_data = None  # data from request message
		self.battletag = battletag
		self.my_side = None  # p1 or p2
		self.foe_side = None  # p1 or p2
		self.opponent_name = "opponent"  # string of opponent's name, used for sending messages
		self.at_team_preview = True  # true at team preview, otherwise false, used for switches
		self.terrain = None  # e.g. "Electric Terrain"
		self.terrain_turns_left = 0
		self.weather = None  # e.g. "RainDance"
		self.weather_turns_left = 0
		self.tailwind = {"bot": 0, "foe": 0}  # number of turns field conditions have left, 0 if inactive
		self.trick_room = 0
		# dictionary of dictionary of entry hazards, e.g. battle.entry_hazards["bot"]["stealthrock"] would return 0, note "bot" means hazards bot has up on opponent's side
		self.entry_hazards = {"bot": {"spikes": 0, "stealthrock": 0, "stickyweb": 0, "toxicspikes": 0}, "foe": {"spikes": 0, "stealthrock": 0, "stickyweb": 0, "toxicspikes": 0}}


	# load pokemon into teams from team preview
	def initialise_teams(self, msg_arr):

		for i in range(3, len(msg_arr)):
			if (msg_arr[i-3] == "poke"):
				# get name/id of pokemon and if has item
				id = msg_arr[i-1].split(',')[0]
				has_item = (msg_arr[i] == "item\n")

				# add to appropriate team
				if (msg_arr[i-2] == self.my_side):
					self.my_team.append(Pokemon(id, has_item, "bot"))
				else:
					self.foe_team.append(Pokemon(id, has_item, "foe"))


	# load data from request message about team, and prompt any appropriate decision from ai
	async def load_team_data(self, ws):

		# load data
		json_obj = json.loads(self.next_team_data)
		have_active = "active" in json_obj.keys() # each true or false
		have_team_preview = "teamPreview" in json_obj.keys()
		have_switch = "forceSwitch" in json_obj.keys()
		# list of status abbreviations
		status_list = ["brn", "frz", "par", "psn", "tox", "slp"]
		# for each pokemon, update with new data
		for i, mon_data in enumerate(json_obj["side"]["pokemon"], 1):
			pokemon = next((mon for mon in self.my_team if mon.id == mon_data["details"].split(",")[0]))
			# for active pokemon add detailed information about possible moves
			if (i <= 2 and have_active):
				pokemon.active_info = json_obj["active"][i-1]
			# set if each pokemon is active
			if (i <= 2 and not have_team_preview):
				pokemon.active = i
			else:
				pokemon.active = 0
			# update health
			condition = mon_data["condition"]
			if (condition[-3:] == "fnt"): # fainted
				pokemon.health_points = "0"
				pokemon.health_percentage = 0
				pokemon.has_fainted = True
				pokemon.status = "fnt"
			else:
				# set status
				if (condition[-3:] in status_list):
					pokemon.status = condition[-3:]
					condition = condition[:-4]
				else:
					pokemon.status = None
				pokemon.health_points = condition
				hp1, hp2 = condition.split("/")
				pokemon.health_percentage = round(100*int(hp1)/int(hp2), 1)
			# update stats, moves, items, ability
			pokemon.stats = mon_data["stats"]
			pokemon.moves = mon_data["moves"]
			pokemon.item = mon_data["item"]
			pokemon.base_ability = mon_data["baseAbility"]
			pokemon.active_ability = mon_data["ability"]
		# prompt appropriate decision if needed
		if (have_active):  # move
			self.debug_prints()
			await ai.choose_moves(ws, self)
		elif (have_switch):  # switch
			await ai.choose_switch(ws, self, json_obj["forceSwitch"])
		elif (have_team_preview):  # leads
			await ai.choose_leads(ws, self)


	# return the pokemon object in a given position and side
	def get_pokemon(self, side, position):

		# get list of bot or foe's pokemon
		if (side == "bot"):
			pokemons = self.my_team
		elif (side == "foe"):
			pokemons = self.foe_team
		# return pokemon in desired position
		return next((mon for mon in pokemons if mon.active == position))


	# get list of active pokemon for either or both sides
	def active_pokemon(self, side):

		active_mons = []
		# get list of bot or foe's pokemon, or both
		if (side == "bot"):
			pokemons = self.my_team
		elif (side == "foe"):
			pokemons = self.foe_team
		elif (side == "both"):
			pokemons = self.my_team[:]
			pokemons.extend(self.foe_team)
		# add active pokemon to start or end of list respective to their position (1 or 2)
		for pokemon in pokemons:
			if (pokemon.active == 1):
				active_mons.insert(0, pokemon)
			elif (pokemon.active == 2):
				active_mons.append(pokemon)
		# return list of objects of active pokemon
		return active_mons


	# complete a switch, updating old and new pokemon
	def update_switch(self, side, pokemon_name, position):

		# get list of bot or foe's pokemon
		if (side == "bot"):
			pokemons = self.my_team
		elif (side == "foe"):
			pokemons = self.foe_team
		# make previous active pokemon (if exists) inactive
		if (self.at_team_preview == False):
			old_mon = next((mon for mon in pokemons if mon.active == position))
			old_mon.switch_out()
		# make new pokemon active
		#print("Side: " + side)
		#print("Foe team: ")
		#[print(pokemon.id) for pokemon in self.foe_team]
		#print("Pokemon name: " + pokemon_name)
		formatted_name = formatting.get_formatted_name(pokemon_name)
		#print("Formatted name: " + formatted_name)
		new_mon = next(mon for mon in pokemons if formatting.get_formatted_name(mon.id) == formatting.get_formatted_name(pokemon_name))
		new_mon.switch_in(position)


	# add buff (stat change) to pokemon
	def add_buff(self, side, position, stat, quantity):

		# get pokemon
		pokemon = self.get_pokemon(side, position)
		# dictionary converting stat stage to modifier, different for accuracy/evasion
		if (stat == "accuracy" or stat == "evasion"):
			modifs = {"-6": 1/3, "-5": 3/8, "-4": 3/7, "-3": 1/2, "-2": 3/5, "-1": 3/4, "0": 1, "1": 4/3, "2": 5/3, "3": 2,
					"4": 7/3, "5": 8/3, "6": 9/3}
		else:
			modifs = {"-6": 1/4, "-5": 2/7, "-4": 1/3, "-3": 2/5, "-2": 1/2, "-1": 2/3, "0": 1, "1": 3/2, "2": 2, "3": 5/2,
					"4": 3, "5": 7/2, "6": 4}
		# add buff
		buff = pokemon.buff[stat][0] + quantity
		# make sure buff is between -6 and 6
		if (buff > 6):
			buff = 6
		elif (buff < -6):
			buff = -6
		# update buff and modifier on pokemon
		pokemon.buff[stat] = [buff, modifs[str(buff)]]


	# update form change (e.g. mega)
	def form_change(self, side, position, new_id):

		# get pokemon
		pokemon = self.get_pokemon(side, position)
		# change to new id, and update types/abilities/stats from pokedex
		pokemon.id = new_id
		pokemon.load_stats()


	# update counters for things like tr/tw/terrain/weather
	def upkeep_counters(self):

		# trick room
		if (self.trick_room > 0):
			self.trick_room -= 1
		# tailwind
		if (self.tailwind["bot"] > 0):
			self.tailwind["bot"] -= 1
		if (self.tailwind["foe"] > 0):
			self.tailwind["foe"] -= 1
		# terrain
		if (self.terrain_turns_left > 0):
			self.terrain_turns_left -= 1
		# weather
		if (self.weather_turns_left > 0):
			self.weather_turns_left -= 1
		# protect
		for pokemon in self.active_pokemon("both"):
			if (pokemon.can_protect > 0):
				pokemon.can_protect -= 1


	# print stuff for debugging here, will be called before making move at start of each turn
	def debug_prints(self):

		#print(self.entry_hazards)
		#print("Turns of: TR: {}, bot TW: {}, foe TW: {}, terrain: {}, weather: {}".format(self.trick_room, self.tailwind["bot"], self.tailwind["foe"], self.terrain_turns_left, self.weather_turns_left))
		#[print("Pokemon: {}, can_fake_out: {}, can_protect: {}".format(pokemon.id, pokemon.can_fake_out, pokemon.can_protect)) for pokemon in self.active_pokemon("both")]
		[print("Pokemon {} has {} status and {}% HP".format(pokemon.id, pokemon.status, pokemon.health_percentage)) for pokemon in self.my_team]
