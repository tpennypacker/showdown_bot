import json
from helper_functions import formatting


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
    res["possibleAbilities"] = list(pokemon["abilities"].values())
    res["baseStats"] = pokemon["baseStats"]
    return res


class Pokemon:

    def __init__(self, id, has_item, side):

        self.id = id  # species of Pokemon, e.g. Manectric or Manectric-Mega
        self.side = side  # will be "bot" or "foe"
        self.active = 0  # 0 for not active, 1 or 2 means active and gives slot
        self.health = 100  # percentage of hp left
        self.fainted = False
        self.status = None
        self.types = []  # list of types, e.g. ["Grass","Poison"]
        self.base_stats = {}  # dictionary e.g. {"hp":45,"atk":49,"def":49,"spa":65,"spd":65,"spe":45}
        self.stats = {}  # dictionary of actual stat numbers for pokemon
        self.possible_abilities = []  # list of possible abilities for pokemon species, e.g. ["Overgrow", "Chlorophyll"]
        self.base_ability = None  # known base ability
        self.active_ability = None  # actual ability could be different from skill swap/role play/entrainment
        self.moves = []  # list of move names, e.g. "earthpower"
        self.active_info = None  # information about possible moves and if trapped etc for active pokemon
        self.has_item = has_item  # true or false
        self.item = None  # e.g. "magoberry"
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
        self.possible_abilities = infos["possibleAbilities"]
        self.base_stats = infos["baseStats"]


    def clear_boosts(self):

        # reset boosts
        self.buff = {"atk": [0, 1], "def": [0, 1], "spa": [0, 1], "spd": [0, 1],
            "spe": [0, 1], "accuracy": [0, 1], "evasion": [0, 1]}


    def switch_out(self):

        # reset boosts
        self.clear_boosts()
        # make inactive
        self.active = 0


    def switch_in(self, position):

        # make active in given slot
        self.active = position
