from helper_functions import calc
import json

# given a pokemon, returns a list of all legal move/target combinations
def get_possible_moves(pokemon, battle, level):
    with open('data/moves.json') as moves_file:
        moves_dex = json.load(moves_file)

    move_decisions = []
    speed = pokemon.calc_speed(battle)
    side = pokemon.side
    use_request = (side == "bot" and level == 0)

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
                target = "none"
            else:
                target = move['target']
            move_id = move['id']
        else:
            target = moves_dex[move]["target"]
            move_id = move
        priority = moves_dex[move_id]['priority']

        if ( target not in ['normal', 'any', 'adjacentFoe', 'adjacentAlly', 'none'] ):
            # moves with no target required
            move_decisions.append( [side, pokemon.id, move_id, None,  priority, speed] )
        elif (target == 'adjacentAlly'):
            # move targetting teammate (e.g. Helping Hand)
            move_decisions.append( [side, pokemon.id, move_id, -1,  priority, speed] )
        else:
            # moves with an individual target (ignore targetting teammate)
            move_decisions.append( [side, pokemon.id, move_id, 1,  priority, speed] )
            move_decisions.append( [side, pokemon.id, move_id, 2,  priority, speed] )

    return move_decisions


def deal_damage(move, user, target, battle, move_order, spread_modifier=1):
    with open('data/moves.json') as moves_file:
        moves_dex = json.load(moves_file)

    dmg = calc.calc_damage(move[2], user, target, battle)
    target.health_percentage -= spread_modifier * dmg
    # if below 0 hp, then faint Pokemon, and remove its move from action list
    if (target.health_percentage <= 0):
        target.fainted = True
        move_order = [i for i in move_order if i[0] != move[0] or i[1] != move[1]]


def simulate_attack(move, user, foes, battle, move_order):
    if (foes[0].fainted and foes[1].fainted): # if both foes dead then no target
        pass
    elif (move[3] == None and not foes[0].fainted and not foes[1].fainted): # spread move against multiple targets
        deal_damage(move, user, foes[0], battle, move_order, 0.75)
        deal_damage(move, user, foes[1], battle, move_order, 0.75)
    elif (foes[1].fainted or move[3] == 1): # target slot 1
        deal_damage(move, user, foes[0], battle, move_order, 1)
    else: # target slot 2
        deal_damage(move, user, foes[0], battle, move_order, 1)
