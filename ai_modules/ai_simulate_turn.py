"""
Simulate Turn AI (WIP)
Bot will choose first two Pokemon on team for leads
Bot switch to Pokemon with best ratio of calculated damage dealt/received against opposing active Pokemon
Bot will simulate each possible combination of attacks (without considering foe) and choose by heuristic prioritising KOs, then total damage
Bot will never use Mega Evolution, Z-moves, or Dynamax
Bot does not 'see' Dynamax


process:
- get legal moves (don't include switches)
- for each possible combination of moves:
    - calculate move order ()
    - calc and deal damage for attacks (don't consider status; or moves that hit partner properly)
    - if KO foe, then mark as fainted and remove from move queue
    - after all moves completed, evaluate new battle state with heuristic (100 per alive mon, and 1 per % hp, + your team - foe's team)
    - use move combination leading to highest state evalution
"""



from helper_functions import calc
from helper_functions import funcs
from helper_functions import get_info
from helper_functions import simulation
from helper_functions import senders
from helper_functions import formatting
from battle import Battle
from settings import ai_settings
import copy
import sys
import json
import random
from operator import itemgetter


# should be able to replace this with entry for mega/zmove/dmax in move dict and single line if statements in output function
mega_dic = {True: ' mega', False: ''}
dyna_dic = {True: ' dynamax', False: ''}


# alpha = best score for bot (highest) out of all explored
# beta = best score for foe (lowest)
sim_depth = 1  # how many turns deep to simulate
def minimax(battle, depth, alpha, beta, maximising_player):
    # here would want to get decisions for either side and simulate turn on even numbers
    # simulate turn and return heuristic evaluation
    if (depth == sim_depth * 2): #or game over in position
        #battle_copy = simulation.simulate_turn(battle)
        battle_copy = copy.deepcopy(battle)
        simulation.simulate_turn(battle_copy)
        eval = simulation.state_heuristic(battle_copy)
        return eval, []

    if maximising_player: # bot (maximise)
        max_eval = float("-inf")
        best_decision = []

        # for each possible decision by bot
        for bot_decision in battle.possible_bot_decisions: # each child of position
            # get evaluation assuming foe plays best move to counter
            battle.bot_decision = bot_decision
            evall, best_foe_decision = minimax(battle, depth + 1, alpha, beta, False)
            #print("score of {:.1f} for {}".format(evall, bot_decision))

            # if this is higher (better) than previous best move gives then update
            if (evall > max_eval):
                max_eval = evall
                best_decision = bot_decision + best_foe_decision

            alpha = max(alpha, evall)

            if beta <= alpha:
                break

        return max_eval, best_decision

    else: # foe (minimise)
        min_eval = float("inf")
        best_decision = []

        # for each possible decision by foe
        for foe_decision in battle.possible_foe_decisions: # each child of position
            # call self recursively which will simulate turn
            battle.foe_decision = foe_decision
            evall, best_bot_decision = minimax(battle, depth + 1, alpha, beta, True)

            # if this is lower (better) than previous best move gives then update
            if (evall < min_eval):
                min_eval = evall
                best_decision = foe_decision + best_bot_decision

            beta = min(beta, evall)

            if beta <= alpha:
                break

        return min_eval, best_decision


# gets called at the start of each turn
async def choose_moves(ws, battle):

    # should ideally do this in minimax
    battle.possible_bot_decisions = simulation.get_possible_decisions(battle, 0, "bot")
    battle.possible_foe_decisions = simulation.get_possible_decisions(battle, 0, "foe")
    #battle_2 = copy.deepcopy(battle)

    cur_eval = simulation.state_heuristic(battle)
    eval, choices = minimax(battle, 0, float("-inf"), float("inf"), True)
    best_choice, best_foe_choice = choices[:2], choices[2:]

    command_str = battle.battletag + "|/choose " + formatting.format_move_choice(best_choice)

    best_choice = formatting.format_move_choice_pretty(best_choice, battle, 'foe')
    best_foe_choice = formatting.format_move_choice_pretty(best_foe_choice, battle, 'bot')
    
    print('Best move for Bot and best response:\n{}\n{}\nPredicted change to evaluation: {}\n'.format(best_choice, best_foe_choice, round(eval-cur_eval,1)))

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
