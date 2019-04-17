from pokemon import Pokemon
import ai
import json


class Battle:

	def __init__(self, battletag):

		self.next_team_data = None  # data from request message to be parsed
		self.my_team = [] # list of pokemon objects
		self.foe_team = []
		self.team_data = None
		self.battletag = battletag
		self.my_side = None  # p1 or p2
		self.foe_side = None  # p1 or p2
		self.opponent_name = None  # string of opponent's name, used for sending messages
		self.team_preview = True  # true at team preview, otherwise false, used for switches
		self.terrain = None  # e.g. "Electric Terrain"
		self.weather = None  # e.g. "RainDance"
		self.my_tailwind = 0  # number of turns field conditions have left
		self.foe_tailwind = 0  # 0 if not active
		self.trick_room = 0


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


	async def load_team_data(self, ws):

		# load data
		json_obj = json.loads(self.next_team_data)
		have_active = "active" in json_obj.keys() # each true or false
		at_team_preview = "teamPreview" in json_obj.keys()
		have_switch = "forceSwitch" in json_obj.keys()
		# for each pokemon, update with new data
		for i, mon_data in enumerate(json_obj["side"]["pokemon"], 1):
			pokemon = next((mon for mon in self.my_team if mon.id == mon_data["details"].split(",")[0]))
			# for active pokemon add detailed information about possible moves
			if (i <= 2 and have_active):
				pokemon.active_info = json_obj["active"][i-1]
			# set if each pokemon is active
			if (i <= 2 and not at_team_preview):
				pokemon.active = i
			else:
				pokemon.active = 0
			# update health
			if ("fnt" not in mon_data["condition"]):
				pokemon.health = int(mon_data["condition"].split("/")[0])
			else:
				pokemon.health = 0
				pokemon.has_fainted = True
			# update stats, moves, items, ability
			pokemon.stats = mon_data["stats"]
			pokemon.moves = mon_data["moves"]
			pokemon.item = mon_data["item"]
			pokemon.base_ability = mon_data["baseAbility"]
			pokemon.active_ability = mon_data["ability"]
		# prompt appropriate decision if needed
		if (have_active):  # move
			await ai.choose_moves(ws, self)
		elif (have_switch):  # switch
			await ai.choose_switch(ws, self, json_obj["forceSwitch"])
		elif (at_team_preview):  # leads
			await ai.choose_leads(ws, self)


	def get_pokemon(self, side, position):

		# get list of bot or foe's pokemon
		if (side == "bot"):
			pokemons = self.my_team
		elif (side == "foe"):
			pokemons = self.foe_team
		# return pokemon in desired position
		return next((mon for mon in pokemons if mon.active == position))


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


	def update_switch(self, side, pokemon_name, position):

		# get list of bot or foe's pokemon
		if (side == "bot"):
			pokemons = self.my_team
		elif (side == "foe"):
			pokemons = self.foe_team
		# make previous active pokemon (if exists) inactive
		if (self.team_preview == False):
			old_mon = next((mon for mon in pokemons if mon.active == position))
			old_mon.switch_out()
		# make new pokemon active
		new_mon = next((mon for mon in pokemons if mon.id == pokemon_name))
		new_mon.switch_in(position)


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


	def form_change(self, side, position, new_id):

		# get pokemon
		pokemon = self.get_pokemon(side, position)
		# change to new id, and update types/abilities/stats from pokedex
		pokemon.id = new_id
		pokemon.load_stats()
