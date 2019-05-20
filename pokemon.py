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
        pokemon = json.load(data_file)[pkm_name]
    res["types"] = pokemon["types"]
    res["possibleAbilities"] = [formatting.get_formatted_name(ability) for ability in list(pokemon["abilities"].values())]
    res["baseStats"] = pokemon["baseStats"]
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
        self.item = None  # e.g. "magoberry"

        self.can_fake_out = True  # false after making a move, reset on switch
        self.can_protect = 0  # 0 if can protect, above 0 means it can't (will be 2 on turn of use, 1 on the following turn), reset on switch

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
            print(self.stats["spe"])

    def clear_boosts(self):

        # reset boosts
        self.buff = {"atk": [0, 1], "def": [0, 1], "spa": [0, 1], "spd": [0, 1],
            "spe": [0, 1], "accuracy": [0, 1], "evasion": [0, 1]}


    def switch_out(self):

        # reset boosts
        self.clear_boosts()
        # reset ability to use fake out and protect
        self.can_fake_out = True
        self.can_protect = 0
        # reset types
        self.types = self.original_types
        # make inactive
        self.active = 0


    def switch_in(self, position):

        # make active in given slot
        self.active = position
