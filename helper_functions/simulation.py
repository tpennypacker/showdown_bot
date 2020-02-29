from helper_functions import calc
import copy
import json



# evaluates battle and returns a single number representing how 'good' it is
def state_heuristic(battle):
	score = 0
	for pokemon in battle.my_team:
		all_dead = True
		if ( not pokemon.fainted ):
			score += 100 + pokemon.health_percentage
			all_dead = False
	if (all_dead):  # if our team dead, then lost battle
		return -10000
	for pokemon in battle.foe_team:
		all_dead = True
		if ( not pokemon.fainted ):
			score -= 100 + pokemon.health_percentage
			all_dead = False
	if (all_dead):  # if their team dead, then won battle
		return 10000
	return score


# return list of possible move combinations for bot/foe
def get_possible_decisions(battle, depth, side):
    choices = []

	# get list of legal moves for each Pokemon
    for pokemon in battle.active_pokemon(side):
        if pokemon.fainted: # for dead pokemon pass
            #print("{} is dead".format(pokemon.id))
            choices.append(['pass'])
        else:
            moves = get_possible_moves(pokemon, battle, depth)
            moves = prune_moves(pokemon, battle, moves, side)
            print(pokemon.id, len(moves))
            #[print(i) for i in moves]
            #[print(i['move_id'], i['target']) for i in moves]
            #print(pokemon.item)
            #print(pokemon.dynamax)
            print(pokemon.abilities)
            print()

            choices.append(moves)

    # get every possible combination of moves between both pokemon
    choices = [ [m1, m2] for m1 in choices[0] for m2 in choices[1] ]

    # test against null move for initial ordering
    choices = order_choices(battle, choices, side)

    return choices


# simulate each move combination against foe doing nothing to get initial ordering
def order_choices(battle, choices, side):
    scored_choices = []
    # get score for each choice by simulating and using heuristic
    for choice in choices:
        battle_copy = copy.deepcopy(battle)
        if (side == "bot"):
            battle_copy.bot_decision = choice
            battle_copy.foe_decision = []
        else:
            battle_copy.bot_decision = []
            battle_copy.foe_decision = choice

        simulate_turn(battle_copy)
        score = state_heuristic(battle_copy)
        scored_choices.append( (choice, score) )
    # sort
    scored_choices = sorted(scored_choices, key=lambda x: x[1], reverse=True)
    scored_choices = [tup[0] for tup in scored_choices]
    return scored_choices


# test
def prune_moves(pokemon, battle, moves, side):
    player_dict = {'bot': 'foe', 'foe': 'bot'}

    with open('data/moves.json') as moves_file:
        moves_dex = json.load(moves_file)

    pruned_moves = []
    moves_1 = []
    moves_2 = []

    for move in moves:
        if (moves_dex[move['move_id']]['category'] == 'Status'): # currently ignore status
            pass
        elif (move['target'] == 1): # for single target attacks need further pruning
            moves_1.append(move)
        elif (move['target'] == 2):
            moves_2.append(move)
        else: # leave in any spread attacks
            pruned_moves.append(move)

    # by calcing damage, find strongest move against each foe and add to pruned list
    for i, movelist in enumerate((moves_1, moves_2)):
        target = battle.get_pokemon(player_dict[side], i+1)
        if (len(movelist) == 0 or target.fainted):
            continue
        elif (len(movelist) == 1):
            pruned_moves.append(movelist[0])
            continue
        best_dmg = -1
        best_move = {}
        for move in movelist:
            dmg = calc.calc_damage(move['move_id'], pokemon, target, battle)
            if (dmg > best_dmg):
                best_dmg = dmg
                best_move = move
        #print(best_dmg, best_move)
        pruned_moves.append(best_move)

    return pruned_moves


# given a pokemon, returns a list of all legal move/target combinations
def get_possible_moves(pokemon, battle, depth):
    with open('data/moves.json') as moves_file:
        moves_dex = json.load(moves_file)

    move_decisions = []
    speed = pokemon.calc_speed(battle)
    side = pokemon.side
    use_request = (side == "bot" and depth < 2)

    if use_request: # for current turn use information from request for bot
        moves = pokemon.active_info['moves']
    else:
        moves = pokemon.moves

    # get each legal move, store in following format
    # [user_id, move_id, target_slot, priority, user_speed]
    for move in moves:
        # ignore disabled moves
        if ( use_request and 'disabled' in move.keys() and move['disabled'] ): # unnecessary condition on end?
            continue

        if use_request:
            if ( 'target' not in move.keys() ):
                target = 'none'
            else:
                target = move['target']
            move_id = move['id']
        else:
            target = moves_dex[move]['target']
            move_id = move
        priority = moves_dex[move_id]['priority']

        if ( target not in ['normal', 'any', 'adjacentFoe', 'adjacentAlly', 'adjacentAllyOrSelf', 'none'] ):
            # moves with no target required
            move_decisions.append( {'side': side, 'mon_id': pokemon.id, 'move_id': move_id, 'target': None,  'priority': priority, 'speed': speed} )
        elif (target in ['adjacentAlly', 'adjacentAllyOrSelf'] or move_id == 'beatup'):
            # move targeting teammate (e.g. Helping Hand), Beat Up hardcoded to be used for this
            move_decisions.append( {'side': side, 'mon_id': pokemon.id, 'move_id': move_id, 'target': -1,  'priority': priority, 'speed': speed} )
        else:
            # moves with an individual target (ignore targetting teammate)
            move_decisions.append( {'side': side, 'mon_id': pokemon.id, 'move_id': move_id, 'target': 1,  'priority': priority, 'speed': speed} )
            move_decisions.append( {'side': side, 'mon_id': pokemon.id, 'move_id': move_id, 'target': 2,  'priority': priority, 'speed': speed} )

    return move_decisions


def deal_damage(move, user, target, battle, move_order, spread_modifier=1):
    with open('data/moves.json') as moves_file:
        moves_dex = json.load(moves_file)

    dmg = calc.calc_damage(move['move_id'], user, target, battle)
    target.health_percentage -= spread_modifier * dmg
    # if below 0 hp, then faint Pokemon, and remove its move from action list
    if (target.health_percentage <= 0):
        target.fainted = True
        move_order = [i for i in move_order if i['side'] != move['side'] or i['mon_id'] != move['mon_id']]


def simulate_attack(move, user, target, battle, move_order):
    if (type(target) is list):
        if (len(target) > 1):
            spread = 0.75
        else:
            spread = 1
        [deal_damage(move, user, pokemon, battle, move_order, 0.75) for pokemon in target]


def simulate_turn(battle):
    player_dict = {'bot': 'foe', 'foe': 'bot'}
    pos_dict = {1: 2, 2: 1}
    with open('data/moves.json') as moves_file:
        moves_dex = json.load(moves_file)

    move_order = battle.bot_decision + battle.foe_decision
    #print(move_order)
    move_order = [move for move in move_order if move != 'pass'] # remove moves from dead pokemon
    move_order = sorted(move_order, key=lambda x: (x['priority'], x['speed'])) # sort by priority then by speed
    #battle_copy = copy.deepcopy(battle)

    # while moves left
    while ( len(move_order) > 0 ):
        # sort order after each move due to new speed mechanics (need to recalculate speeds first!)
        #moves = sorted(unsorted, key=lambda x: (x[1], x[2]))

        # get move and remove from list
        move = move_order.pop(0)
        side = move['side']
        opp_side = player_dict[move['side']]

        # figuring out target/s
        target = None
        # single target moves
        if (move['target'] != None):
            # consider redirection
            if (battle.redirection[opp_side]): # currently doesn't consider grass/goggles or stalwart exceptions
                target = next((mon for mon in battle.active_pokemon(opp_side) if mon.id == battle.redirection[opp_side][user_id]))
                if (target.fainted): target = None
            # if not being redirected
            if (target == None):
                # move targetting teammate
                if (move['target'] == -1):
                    target = next((mon for mon in battle.active_pokemon(side) if mon.id != move['mon_id']))
                    if (target.fainted): continue
                # targeting foe
                else:
                    # if original target dead then move to other foe, if both dead then pass on move
                    target = battle.get_pokemon(opp_side, move['target'])
                    if (target.fainted):
                        target = battle.get_pokemon(opp_side, pos_dict[move['target']])
                        if (target.fainted): continue

        # self targetting moves always work
        elif (moves_dex[move['move_id']]['target'] == 'self'):
            pass

        # spread moves
        elif (moves_dex[move['move_id']]['target'] in ['allAdjacent', 'allAdjacentFoes']):
            if (moves_dex[move['move_id']]['target'] == 'allAdjacent'):
                target = [mon for mon in battle.active_pokemon('both') if mon.id != move['mon_id'] or mon.side != side]
                target = [mon for mon in target if not mon.fainted]
                if (len(target) == 0): continue

        # random target like outrage or target side like tailwind
        else:
            continue


        # currently only consider attacks
        if (moves_dex[move['move_id']]['category'] == 'Status'):
            continue

        # get user and targets to deal with attack
        user = next((mon for mon in battle.active_pokemon(side) if mon.id == move['mon_id']))
        simulate_attack(move, user, target, battle, move_order)

    #return battle_copy
