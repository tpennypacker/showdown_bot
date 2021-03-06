import json
import random
from operator import itemgetter
from settings import ai_settings
from helper_functions import formatting
from helper_functions import calc
import numpy as np


# find best move for a given pokemon against the active foes
# returns (move_name, foe_index, effective base power)
def find_best_move_active_foes(battle, user):
    possible_moves = []
    foes = battle.active_pokemon("foe")
    for i, foe in enumerate(foes, 1):
        if (foe.fainted): # ignore dead foe
            continue
        moves_damage = find_best_move_against_foe(battle, user, foe)
        possible_moves.append(moves_damage)

    # deal with spread moves which only hit opponents (e.g. Muddy Water)
    for i in range (len(possible_moves[0])):
        move = possible_moves[0][i]
        if (is_spread_move(move[0])):
            possible_moves[0][i][1] = 3  # indicate that target is both foes
            if (len(possible_moves) > 1):  # apply spread calculations if both foes alive
                possible_moves[0][i][2] += possible_moves[1][i][2]  # add base power against second target
                possible_moves[0][i][2] = round (possible_moves[0][i][2], 1)
                possible_moves[1][i][2] = 0  # set second instance of spread move to 0 damage

    # combine lists of moves against each foe into single list of possible moves
    possible_moves = [move for sublist in possible_moves for move in sublist]

    # sort based on power
    possible_moves = sorted(possible_moves, key=itemgetter(2), reverse=True)
    # return (move name, target index, effective bp) of strongest move/target combination
    return possible_moves[0]


# user is a pokemon object, foe is a pokemon object
# returns list of (move_name, foe_index, effective base power) for each usable move
def find_best_move_against_foe(battle, user, foe):
    with open('data/moves.json') as moves_file:
        moves = json.load(moves_file)
        user_index = user.active
        my_types = user.types
        foe_types = foe.types
        possible_moves = [] # list of possible moves in format [move, target, effective bp]

        if (user_index > 0): # active pokemon
            user_active = True
            my_moves = user.active_info["moves"]
            my_moves = [formatting.format_active_move(move) for move in my_moves]
            if (my_moves[0] == "struggle"): # if only have struggle, then send set response
                return (1, None, 50)
        else: # pokemon in back
            user_active = False
            my_moves = [formatting.remove_hp_power(move) for move in user.moves]

        if (foe.active > 0): # if target foe active then give position
            foe_index = foe.active
        else:  # otherwise return None
            foe_index = None

        # for each move
        for move in my_moves:
            if (move == ""): # don't consider disabled moves
                continue
            # move_category = moves[move]["category"]
            # move_type = moves[move]["type"]
            # base_power = moves[move]["basePower"]
            # effective_bp = base_power * get_stab_effectiveness(move_type, my_types) * get_type_effectiveness(move_type, foe_types) * get_ability_effectiveness(my_ability, move_type, battle.active_pokemon("foe"), foe) * get_field_modifier(battle, my_types, my_ability, move_type, move_category, foe, foe_types)
            effective_bp = calc.calc_damage (move, user, foe, battle)
            possible_moves.append([move, foe_index, effective_bp])

    # return (move name, target index, effective bp) of each move
    return possible_moves


# calculate scores used for switching, uses strongest move for each available pokemon
def calculate_score_ratio_switches(battle):
    scores = []
    pokemons = battle.my_team
    # for each pokemon on team
    for pokemon in pokemons:
        # skip if the pokemon is already out, or if fainted
        if (pokemon.active > 0 or pokemon.fainted):
            continue
        # otherwise calculate score ratio and append to list with name
        name = formatting.get_formatted_name(pokemon.id)
        ratio = calculate_score_ratio_single(battle, pokemon)
        scores.append({'name':name, 'ratio':ratio})
    # sort if required from highest to lowest ratio
    if (len(scores) > 0):
        scores = sorted(scores, key = lambda i: i['ratio'], reverse=True)
    return(scores)


# calculate score ratio for a single pokemon object
def calculate_score_ratio_single(battle, pokemon):
    foes = battle.active_pokemon("foe")
    # fail safe for if foe has no currently active pokemon
    if (foes[0].fainted and foes[1].fainted):
        return 1

    # get pokemon's "score" against the opponent
    move, target, power = find_best_move_active_foes(battle, pokemon)

    # get the sum of the opponent's scores against us
    with open('data/moves.json') as moves_file:
        all_moves = json.load(moves_file)
    foes_score = []
    for foe in foes:
        if (foe.fainted): # ignore dead foes
            continue

        foe_score = []
        for move in foe.moves:
            # move_data = all_moves[move]
            # bp = move_data["basePower"]
            # move_type = move_data["type"]
            # stab = get_stab_effectiveness(move_type, foe.types)
            # # NEED TO TAKE INTO ACCOUNT WEATHER / TERRAIN / ABILITIES
            # damage = bp * stab * get_type_effectiveness(move_type, pokemon.types)
            damage = calc.calc_damage (move, foe, pokemon, battle)
            foe_score.append(damage)

        index, value = max(enumerate(foe_score), key=itemgetter(1))
        foes_score.append(value)
    foes_total_score = np.sum(foes_score)

    if (foes_total_score == 0):  # avoid division by zero
        foes_total_score = 1

    ratio = power / foes_total_score
    return ratio


def is_spread_move(formatted_move):
    with open('data/moves.json') as moves_file:
        moves = json.load(moves_file)
        move_data = moves[formatted_move]
        return (move_data['target'] == 'allAdjacentFoes')



# apparently special cases already have attribute gmax power in moves.json?
def get_max_move_bp(move_id):
    # special move cases
    if (move_id in ["crushgrip", "wringout", "magnitude", "doubleironbash"]):
        return 140
    elif(move_id in ["pinmissile", "powertrip", "punishment", "dragondarts", "dualchop", "electroball", "heatcrash", "bulletseed", "grassknot", "bonemerang", "bonerush", "fissure", "iciclespear", "sheercold", "weatherball", "tailslap", "guillotine", "horndrill", "flail", "return", "frustration", "endeavor", "naturalgift", "trumpcard", "storedpower", "rockblast", "geargrind", "gyroball", "heavyslam"]):
        return 130
    elif(move_id in ["doublehit", "spikecannon"]):
        return 120
    elif(move_id in ["twineedle", "beatup", "fling", "dragonrage", "nature'smadness", "nightshade", "cometpunch", "furyswipes", "sonicboom", "bide", "superfang", "present", "spitup", "psywave", "mirrorcoat", "metalburst", "lowkick", "reversal", "finalgambit"]):
        return 100
    elif(move_id in ["doublekick", "triplekick"]):
        return 80
    elif(move_id in ["counter", "seismictoss"]):
        return 75

    with open('data/moves.json') as moves_file:
        moves_dex = json.load(moves_file)

    move_type = moves_dex[move_id]['type']
    move_bp = moves_dex[move_id]['basePower']

    # fighting and poison (lower BPs)
    if (move_type in ['Fighting', 'Poison']):
        if (move_bp >= 150):
            return 100
        elif (move_bp >= 110):
            return 95
        elif (move_bp >= 75):
            return 90
        elif (move_bp >= 65):
            return 85
        elif (move_bp >= 55):
            return 80
        elif (move_bp >= 45):
            return 75
        elif (move_bp >= 10):
            return 70
    else: # any other type
        if (move_bp >= 150):
            return 150
        elif (move_bp >= 110):
            return 140
        elif (move_bp >= 75):
            return 130
        elif (move_bp >= 65):
            return 120
        elif (move_bp >= 55):
            return 110
        elif (move_bp >= 45):
            return 100
        elif (move_bp >= 10):
            return 90

    # don't think this should happen
    print("move with <10bp? ",move_id)
    return 0
