"""
Simulate Bot Turn AI
Bot will choose first two Pokemon on team for leads
Bot switch to Pokemon with best ratio of calculated damage dealt/received against opposing active Pokemon
Bot will simulate each possible combination of attacks (without considering foe) and choose by heuristic prioritising KOs, then total damage
Bot will never use Mega Evolution, Z-moves, or Dynamax
Bot does not 'see' Dynamax


logic process:
- get legal moves (don't include switches)
- for each possible combination of moves:
    - calculate move order
    - calc and deal damage for attacks (don't consider status/secondary effects; or moves that hit partner properly)
    - if KO foe, then mark as fainted and remove from move queue
    - after all moves completed, evaluate new battle state with heuristic (100 per alive mon, and 1 per % hp, + your team - foe's team)
    - use move combination leading to highest state evalution
"""

from helper_functions import calc
from helper_functions import funcs
from helper_functions import get_info
from helper_functions import senders
from helper_functions import formatting
from battle import Battle
from settings import ai_settings
import copy
import sys
import json
import random
from operator import itemgetter


mega_dic = {True: ' mega', False: ''}
dyna_dic = {True: ' dynamax', False: ''}


# gets called at the start of each turn
async def choose_moves(ws, battle):

    with open('data/moves.json') as moves_file:
        moves_dex = json.load(moves_file)

    # get active pokemon
    allies = battle.active_pokemon("bot")
    foes = battle.active_pokemon("foe")

    bot_choices = []

    # get list of legal moves for each Pokemon
    for pokemon in allies:
        if pokemon.fainted: # for dead pokemon pass
            bot_choices.append(['pass'])
        else:
            #print(pokemon.id, pokemon.item)
            moves = []

            # calculate pokemon speed, using stat, buff, item,
            speed = pokemon.calc_speed(battle)

            # get each legal move, store in following format
            # [user_id, move_id, target_slot, priority, user_speed]
            for move in pokemon.active_info['moves']:
                # ignore disabled moves
                if ( 'disabled' in move.keys() and move['disabled'] ):
                    continue
                if ( 'target' not in move.keys() or move['target'] not in ['normal', 'any', 'adjacentFoe', 'adjacentAlly'] ):
                    # moves with no target required
                    moves.append( ["bot", pokemon.id, move['id'], None,  moves_dex[move['id']]['priority'], speed] )
                elif (move['target'] == 'adjacentAlly'):
                    # move targetting teammate (e.g. Helping Hand)
                    moves.append( ["bot", pokemon.id, move['id'], -1,  moves_dex[move['id']]['priority'], speed] )
                else:
                    # moves with an individual target (ignore targetting teammate)
                    moves.append( ["bot", pokemon.id, move['id'], 1,  moves_dex[move['id']]['priority'], speed] )
                    moves.append( ["bot", pokemon.id, move['id'], 2,  moves_dex[move['id']]['priority'], speed] )

            bot_choices.append(moves)

    best_choice = ""
    best_state = None

    player_dict = {"bot": "foe", "foe":"bot"}

    #pos = len(bot_choices[0]) * len(bot_choices[1]) #* len(foe_choices[0]) * len(foe_choices[1])
    #ind = 0

    # simulate each possible user move combination
    for move_1 in bot_choices[0]:
        for move_2 in bot_choices[1]:
            #ind += 1
            #print("Simulation {}/{}".format(ind,pos))
            moves = [move_1, move_2]
            moves = [move for move in moves if move != "pass"] # remove moves from dead pokemon
            moves = sorted(moves, key=lambda x: (x[-2], x[-1])) # sort by priority then by speed
            battle_copy = copy.deepcopy(battle)
            # while moves left
            while ( len(moves) > 0 ):
                # get move and remove from list
                move = moves.pop(0)
                # currently only consider attacks by bot
                if (moves_dex[move[2]]['category'] == 'Status' or move[0] == "foe"):
                    continue
                # get user and targets to deal with attack
                user = next((mon for mon in battle_copy.active_pokemon(move[0]) if mon.id == move[1]))
                foes = battle_copy.active_pokemon(player_dict[move[0]])
                if (foes[0].fainted and foes[1].fainted): # if both foes dead then no target
                    continue
                elif (move[3] == None and not foes[0].fainted and not foes[1].fainted): # spread move against multiple targets
                    # calculate and deal damage (with spread reduction) against first target
                    dmg = calc.calc_damage(move[2], user, foes[0], battle)
                    foes[0].health_percentage -= 0.75 * dmg
                    # if below 0 hp, then faint Pokemon, and remove its move from action list
                    if (foes[0].health_percentage <= 0):
                        foes[0].fainted = True
                        moves = [i for i in moves if i[0] != move[0] or i[1] != move[1]]
                    # same for second target
                    dmg = calc.calc_damage(move[2], user, foes[1], battle)
                    foes[1].health_percentage -= 0.75 * dmg
                    if (foes[1].health_percentage <= 0):
                        foes[1].fainted = True
                        moves = [i for i in moves if i[0] != move[0] or i[1] != move[1]]
                elif (foes[1].fainted or move[3] == 1): # target slot 1
                    dmg = calc.calc_damage(move[2], user, foes[0], battle)
                    foes[0].health_percentage -= dmg
                    if (foes[0].health_percentage <= 0):
                        foes[0].fainted = True
                        moves = [i for i in moves if i[0] != move[0] or i[1] != move[1]]
                else: # target slot 2
                    dmg = calc.calc_damage(move[2], user, foes[1], battle)
                    foes[1].health_percentage -= dmg
                    if (foes[1].health_percentage <= 0):
                        foes[1].fainted = True
                        moves = [i for i in moves if i[0] != move[0] or i[1] != move[1]]
            # moves done, would do end of turn effects here
            # evaluate new state with heuristic function based on hp/alive pokemon
            score = 0
            for pokemon in battle_copy.my_team:
                if ( not pokemon.fainted ):
                    score += 100 + pokemon.health_percentage
            for pokemon in battle_copy.foe_team:
                if ( not pokemon.fainted ):
                    score -= 100 + pokemon.health_percentage
            # if better than current best choice, then update
            if (best_state == None or score > best_state):
                best_state = score
                if (move_1 != 'pass' and move_2 != 'pass'): # both Pokemon alive
                    target1 = " {}".format(move_1[3]) if move_1[3] != None else ""
                    target2 = " {}".format(move_2[3]) if move_2[3] != None else ""
                    best_choice = "move " + move_1[2] + target1 + ", move " + move_2[2] + target2
                elif (move_2 == 'pass'): # only 1st Pokemon alive
                    target1 = " {}".format(move_1[3]) if move_1[3] != None else ""
                    best_choice = "move " + move_1[2] + target1 + ", pass"
                else: # only 2nd Pokemon alive
                    target2 = " {}".format(move_2[3]) if move_2[3] != None else ""
                    best_choice = "pass, move " + move_2[2] + target2

    command_str = battle.battletag + "|/choose " + best_choice
    # send turn decision
    await senders.send_turn_decision(ws, command_str, battle)



# gets called when forced to switch
async def choose_switch(ws, battle, switches):

    # get score ratios used for determining best switch
    sorted_scores = get_info.calculate_score_ratio_switches(battle)
    switch1, switch2 = switches  # each True or False

    # if only one mon left
    if (len(sorted_scores) < 2):
        if (switch1 == switch2): # 2 switches required
            switch_str = "switch, switch"
        elif (switch1): # switch in 1st slot
            switch_str = "switch, pass"
        else: # switch in 2nd slot
            switch_str = "pass, switch"

    # switch both, multiple mons left
    elif (switch1 == switch2):
        switch_str = "switch " + formatting.format_switch_name(sorted_scores[0]['name']) + ", switch " +  formatting.format_switch_name(sorted_scores[1]['name'])

    # switch one, multiple mons left
    elif (switch1):
        switch_str = "switch " +  formatting.format_switch_name(sorted_scores[0]['name']) + ", pass"
    else:
        switch_str = "pass, switch " +  formatting.format_switch_name(sorted_scores[0]['name'])
    # send switch decision
    command_str = battle.battletag + "|/choose " + switch_str
    await senders.send_forced_switch_decision(ws, command_str, battle)



# gets called at team preview
async def choose_leads(ws, battle):
    # pick 2 random pokemon on team
    #num_pokemon = len(battle.my_team)
    #leads = random.sample(range(1, num_pokemon+1), 2)  # e.g. 2 unique numbers from 1-6
    #leads = [str(i) for i in leads]
    leads = ["1", "2"] # choose first two pokemon
    # send leads decision
    await senders.send_lead_decision(ws, leads, battle)
