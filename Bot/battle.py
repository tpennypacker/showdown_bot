class Battle:

	def __init__(self, battletag):

		self.foes = ["no pokemon", "no pokemon"]
		self.allies = ["no pokemon", "no pokemon"]
		self.team_data = None
		self.battletag = battletag
		self.my_side = None # p1 or p2
		self.opponent_name = None
		self.terrain = None # e.g. "Electric Terrain"
		self.weather = None # e.g. "RainDance"
