class Battle:

	def __init__(self, battletag, my_side):

		self.foes = ["no pokemon", "no pokemon"]
		self.allies = ["no pokemon", "no pokemon"]
		self.team_data = None
		self.battletag = battletag
		self.my_side = my_side
		self.terrain = None # e.g. "Electric Terrain"
		self.weather = None # e.g. "RainDance"
