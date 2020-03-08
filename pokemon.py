import json
from helper_functions import formatting
from helper_functions import predict_foe_sets


def infos_for_pokemon(pkm_name):
    """
    Filtrate, regroup and translate data from json files.
    :param pkm_name: Pokemon's name
    :return: Dict. {types, possibleAbilities, baseStats}
    """
    #pkm_name = pkm_name.lower().replace('-', '').replace(' ', '').replace('%', '').replace('\'', '').replace('.', '')
    pkm_name = formatting.get_formatted_name(pkm_name)
    res = {
        "types": [],
        "possibleAbilities": [],
        "baseStats": {}
    }
    with open('data/pokedex.json') as data_file:
        json_dict = json.load(data_file) # load json file
    # if pokemon in file, use correct stats
    if (pkm_name in json_dict.keys() ):
        pokemon = json_dict[pkm_name]
        res["types"] = pokemon["types"]
        res["possibleAbilities"] = [ formatting.get_formatted_name(ability) for ability in list(pokemon["abilities"].values()) ]
        res["baseStats"] = pokemon["baseStats"]
    else: # if unrecognised, assume Normal with with Illuminate (does nothing) and 70 BST in each stat
        res["types"] = ["Normal"]
        res["possibleAbilities"] = [ formatting.get_formatted_name("Illuminate") ]
        res["baseStats"] = {"hp":70, "atk":70, "def":70, "spa":70, "spd":70, "spe":70}

    return res


class Pokemon:

    def __init__(self, side, id, has_item, level, gender):

        self.id = id  # species of Pokemon, e.g. Manectric or Manectric-Mega
        self.side = side  # will be "bot" or "foe"
        self.active = 0  # 0 for not active, 1 or 2 means active and gives slot

        self.level = level  # integer, usually 100
        self.gender = gender  # "M", "F", or None
        #self.shiny = shiny  # true or false, could get from when pokemon is switched out, but not from team preview

        self.health_percentage = 100  # percentage of hp left
        self.health_points = None  # actual hp, will only know for our pokemon, string, e.g. "234/435"
        self.fainted = False  # true if fainted
        self.status = None  # could be "brn", "psn", "tox" etc

        self.types = []  # list of types, e.g. ["Grass","Poison"]
        self.original_types = []  # before any soak etc. shenanigans, pokemon.types reset to this on switching out
        self.base_stats = {}  # dictionary e.g. {"hp":45,"atk":49,"def":49,"spa":65,"spd":65,"spe":45}
        self.stats = {}  # dictionary of actual stat numbers for pokemon, here hp is maximum hp
        self.abilities = []  # list of possible abilities for pokemon species, e.g. ["overgrow", "chlorophyll"]
        self.EVs = {} # dictionary e.g. {"hp":252, "atk":252, "def":4, "spa":252, "spd":100, "spe":252} (note: does not have to add up to 508/510, since it's based on conservative predictions)
        self.nature_buffs = {} # dictionary of buffs for possible natures e.g. {"hp":1.0, "atk":1.1, "def": 1.1, "spa":1.0, "spd":1.0 "spe":1.1} ("hp" for filler)

        self.moves = []
        self.active_info = None  # information about possible moves and if trapped etc for active pokemon

        self.has_item = has_item  # true or false
        self.item = []  # list of likely items e.g. ["magoberry"]

        self.can_fake_out = True  # false after making a move, reset on switch
        self.can_protect = True  # if can use a guaranteed protect
        self.dynamax = 0  # 0 if not dynamaxed, otherwise counts down turns left

        self.flinched = 0  # chance to flinch, either 0 or 1
        self.protect = 0  # current protect status, 0 for none, 1 for normal, 2 for max guard

        # stat changes, values from -6 to 6
        self.buff = {  # first number boost from -6 to 6, second number is equivalent modifier
            "atk": [0, 1],
            "def": [0, 1],
            "spa": [0, 1],
            "spd": [0, 1],
            "spe": [0, 1],
            "accuracy": [0, 1],
            "evasion": [0, 1]
        }

        self.load_stats()  # load types, base stats, possible abilities from pokedex


    def load_stats(self):
        """
        Load every information of pokemon from datafiles and store them
        """
        infos = infos_for_pokemon(formatting.get_formatted_name(self.id))
        self.types = infos["types"]
        self.original_types = infos["types"]
        self.abilities = infos["possibleAbilities"]
        self.base_stats = infos["baseStats"]


    def calc_stats(self):

        # calculate actual stat numbers, assume 31 IVs, use int() to round down
        self.stats["hp"] = int( (2*self.base_stats["hp"] + 31 + self.evs["hp"]/4) * self.level/100 + self.level + 10)
        for stat in ["atk", "def", "spa", "spd", "spe"]:
            self.stats[stat] = int( ( (2*self.base_stats[stat] + 31 + self.evs[stat]/4) * self.level/100 + 5) * self.nature_buffs[stat])
        if self.nature_buffs["spe"] < 1: # if determined to be min speed
            self.stats["spe"] = int( ( (2*self.base_stats[stat] + 0 + 0) * self.level/100 + 5) * self.nature_buffs[stat])
            #print(self.stats["spe"])


    def clear_boosts(self):

        # reset boosts
        self.buff = {"atk": [0, 1], "def": [0, 1], "spa": [0, 1], "spd": [0, 1],
            "spe": [0, 1], "accuracy": [0, 1], "evasion": [0, 1]}


    def switch_out(self):

        # reset boosts
        self.clear_boosts()
        # reset ability to use fake out and protect
        self.can_fake_out = True
        self.can_protect = True
        # reset types
        self.types = self.original_types
        # make inactive
        self.active = 0
        # remove Dynamax
        self.dynamax = 0
        # reset flinch/protect
        self.flinched = 0
        self.protect = 0


    def switch_in(self, position):

        # make active in given slot
        self.active = position


    def calc_speed(self, battle):

        # speed stat and buff
        speed = self.stats['spe'] * self.buff['spe'][1]

        # choice scarf
        if (self.has_item and 'choicescarf' in self.item):
            speed *= 1.5

        # paralysis
        if (self.status == 'par'):
            speed /= 2

        speed = int(speed) # round down after above, everything else will give int

        if (battle.tailwind[self.side] > 0):
            speed *= 2

        # surge surfer
        if ("surgesurfer" in self.abilities and battle.terrain == "electricterrain"):
            speed *= 2
        # weather, can skip checks if none up
        elif (battle.weather == None):
            pass
        elif ("chlorophyll" in self.abilities and battle.weather == "sunnyday"):
            speed *= 2
        elif ("swiftswim" in self.abilities and battle.weather == "raindance"):
            speed *= 2
        elif ("sandrush" in self.abilities and battle.weather == "sandstorm"):
            speed *= 2
        elif ("slushrush" in self.abilities and battle.weather == "hail"):
            speed *= 2

        return speed
