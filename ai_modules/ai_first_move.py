"""
First Move AI
Bot will choose leads and switches in original order of team (ignoring dead Pokemon)
Bot will use first available move, targetting first enemy slot if target is required
Bot will not use Mega evolution / Z-moves / Dynamax
actually could just use /choose default whenever get request

"""

from helper_functions import funcs
from helper_functions import get_info
from helper_functions import senders
from helper_functions import formatting
from battle import Battle
from settings import ai_settings
import json
import random
from operator import itemgetter



# gets called at the start of each turn
async def choose_moves(ws, battle):

    # get active pokemon
    allies = battle.active_pokemon("bot")

    decisions = []
    # for each active pokemon
    for pokemon in allies:
        if pokemon.fainted: # for dead pokemon pass
            decisions.append('pass')
        else: # choose first available move
            decisions.append('move')

    # combine decisions
    command_str = battle.battletag + "|/choose " + ", ".join(decisions)
    # send turn decision
    await senders.send_turn_decision(ws, command_str, battle)



# gets called when forced to switch
async def choose_switch(ws, battle, switches):

    # figure out switches required
    if (switches[0] == switches[1]): # switches in both slots
        switch_str = "switch, switch"
    elif (switches[0]): # switch in 1st slot
        switch_str = "switch, pass"
    else: # switch in 2nd slot
        switch_str = "pass, switch"

    # send switch decision
    command_str = battle.battletag + "|/choose " + switch_str
    await senders.send_forced_switch_decision(ws, command_str, battle)



# gets called at team preview
async def choose_leads(ws, battle):

    # choose first two pokemon
    leads = ["1", "2"]
    # send leads decision
    await senders.send_lead_decision(ws, leads, battle)
