import json


# format active moves, and denote disabled moves as ""
def format_active_move(move):
    if (move["disabled"] == True):
        return ""
    else:
        return format_move(move["move"])


# format move e.g. "U-turn" -> "uturn"
def format_move(move):
    return move.replace("move: ","").strip("\n").lower().replace(" ", "").replace("'", "").replace("-", "").replace(",", "")


mons_with_useless_forms = ['gastrodon', 'shellos', 'florges', 'genesect',
                            'deerling', 'sawsbuck', 'burmy', 'furfrou',
                            'magearna', 'minior', 'gourgeist', 'pumpkaboo']

def get_formatted_name(pokemon_name):
    formatted = pokemon_name.split(",")[0].lower().replace(' ', '').replace('-', '').replace("'", "").replace(":", "").replace("*","").strip("\n")

    for mon in mons_with_useless_forms:
        if mon in formatted:
            return mon

    return formatted


def format_switch_name(pokemon_name):
    pokemon_name = pokemon_name.split(',')[0]
    if (pokemon_name[-4:] == "mega"):
        return pokemon_name[:-4]
    elif (pokemon_name[-5:] == "megax" or pokemon_name[-5:] == "megay"):
        return pokemon_name[:-5]
    else:
        return pokemon_name


# e.g. convert "hiddenpowerice60" to "hiddenpowerice"
def remove_hp_power(move_name):
    if ("hiddenpower" in move_name):
        return move_name[:-2]
    else:
        return move_name


def format_move_choice(moves):
    moves_str = []
    for move in moves:
        if ('pass' in move.keys()):
            moves_str.append('pass')
        else:
            target = ' {}'.format(move['target']) if move['target'] != None else ''
            str = 'move {}{}'.format( move['move_id'], target )
            moves_str.append(str)
    best_choice = ', '.join(moves_str)
    return best_choice


def format_move_choice_pretty(moves, battle, opp_side):
    with open('data/moves.json') as moves_file:
        moves_dex = json.load(moves_file)
    moves_str = []
    for move in moves:
        if ('pass' in move.keys()):
            pass
        else:
            move_name = moves_dex[move['move_id']]['name']
            target = ' {}'.format( battle.get_pokemon(opp_side, move['target']).id ) if move['target'] in [1, 2] else ''
            str = '{}{}'.format( move_name, target )
            moves_str.append(str)
    best_choice = ', '.join(moves_str)
    return best_choice
