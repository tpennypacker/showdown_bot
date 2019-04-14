from pokemon import Pokemon

class Battle:

	def __init__(self, battletag):

		self.foes = ["no pokemon", "no pokemon"]
		self.allies = ["no pokemon", "no pokemon"]
		self.my_team = []
		self.foe_team = []
		self.team_data = None
		self.battletag = battletag
		self.my_side = None # p1 or p2
		self.opponent_name = None
		self.terrain = None # e.g. "Electric Terrain"
		self.weather = None # e.g. "RainDance"
		self.my_tailwind = 0 # number of turns field conditions have left
		self.foe_tailwind = 0 # 0 if not active
		self.trick_room = 0


	def initialise_teams(self, msg_arr):
		
		for i in range(3, len(msg_arr)):
			if (msg_arr[i-3] == "poke"):
				# get name/id of pokemon and if has item
				id = msg_arr[i-1].split(',')[0]
				has_item = (msg_arr[i] == "item\n")

				# add to appropriate team
				if (msg_arr[i-2] == self.my_side):
					self.my_team.append(Pokemon(id, has_item))
				else:
					self.foe_team.append(Pokemon(id, has_item))



	def print_teams(self):
		print("MY TEAM:")
		for pokemon in self.my_team:
			pokemon.print()

		print("_________________\n")
		print("THEIR TEAM:")

		for pokemon in self.foe_team:
			pokemon.print()

		print("\n")
