import websockets

from settings import bot_settings
from helper_functions import formatting


async def ionext(ws):
    await ws.send("|/ionext")
    print("Your next match will be invite-only. \n")

async def change_avatar(ws):
    await ws.send("|/avatar " + bot_settings.avatar)
    print("Your avatar has been changed to " + bot_settings.avatar + ".\n")

async def join_room(ws):
    await ws.send("|/join " + bot_settings.auto_join_room)
    print("Joining the " + bot_settings.auto_join_room + " room\n")

async def timer(ws, battletag):
    await ws.send(battletag + "|/timer on")
    print("Timer started for match: " + battletag + "\n")

async def hello(ws, battletag, phrase):
    await ws.send(battletag + "|" + phrase)
    print("Sending battle greeting: " + phrase + "\n")

async def goodbye(ws, battletag, phrase, winner):
    await ws.send(battletag + "|" + phrase)
    if (winner):
        print("\n" + "Won game, saying: " + phrase + "\n")
    else:
        print("\n" + "Lost game, saying: " + phrase + "\n")

async def leave_battle(ws, battletag):
    await ws.send(battletag + "|/leave")

async def search_for_battle(ws):
    #mode = battletag.split('-')[1]
    mode = bot_settings.play_tier
    await ws.send("|/utm " + bot_settings.active_bot_team)
    await ws.send("|/search " + mode)
    print("Searching for a new {} match. \n".format(mode))

async def blockpms(ws, blocked):
    if (not blocked and not bot_settings.block_pms):
        print("PMs already unblocked")
    elif (blocked and bot_settings.block_pms):
        print("PMs already blocked")
    elif (not blocked):
        await ws.send("|/blockpms")
        print("Blocked PMs")
    else:
        await ws.send("|/unblockpms")
        print("Unblocked PMs")

async def blockchallenges(ws, blocked):
    if (not blocked and not bot_settings.block_challenges):
        print("Challenges already unblocked")
    elif (blocked and bot_settings.block_challenges):
        print("Challenges already blocked")
    elif (not blocked):
        await ws.send("|/blockchallenges")
        print("Blocked challenges")
    else:
        await ws.send("|/unblockchallenges")
        print("Unblocked challenges")

async def accept_challenge(ws, challenger, bot_team):
    await ws.send("|/utm " + bot_team)
    await ws.send("|/accept " + challenger)
    print("Accepting challenge from " + challenger + " in " + bot_settings.play_tier + "\n")

async def send_login_msg(ws, msg):
    await ws.send(msg)
    print("Logging in")

async def send_pm(ws, msg, user):
    await ws.send("|/pm {}, {}".format(user, msg))
    #print("Sending following message to user {}: {}".format(user, msg))

async def save_replay(ws, battletag):
    await ws.send(battletag + "|/savereplay")
    print("Saving replay for " + battletag)

async def send_command(ws, msg):
    await ws.send(msg)

async def send_lead_decision(ws, leads, battle, format_output=False):
    command_str = battle.battletag + "|/choose team " + "".join(leads) + "|" + str(battle.rqid)
    await ws.send(command_str)
    if not format_output:
        print("\nSending lead decision: " + command_str)
        return
    # format output to print nicely
    pokemon_names = [ battle.my_team[int(i) - 1].id for i in command_str.split()[-1] ]
    out_string = "\nLeading {} and {}.".format(pokemon_names[0], pokemon_names[1])
    print(out_string)


async def send_turn_decision(ws, command_str, battle, format_output=False):
    command_str += "|" + str(battle.rqid)
    await ws.send(command_str)
    if not format_output:
        print("Sending turn decision: " + command_str)
        return
    # format output to print nicely
    command_str = command_str.split("|/choose")[-1]
    for i, decision in enumerate( command_str.split(",") ):
        split_dec = decision.strip().split()
        decision_type = split_dec[0]
        pokemon = battle.active_pokemon("bot")[i]
        out_string = pokemon.id + " will "
        if ( decision_type == 'move' ):
            j = 1
            if ( not split_dec[j].isdigit() ):
                j += 1
            move = pokemon.active_info['moves'][ int( split_dec[j] ) - 1 ]['move']
            out_string += "use {}".format(move)
            if ( len(split_dec) > j + 1 ):
                target = battle.active_pokemon("foe")[ int( split_dec[j+1] ) - 1 ].id
                out_string += " against {}.".format(target)
            else:
                out_string += "."
            print(out_string)
        elif ( decision_type == 'switch' ):
            j = split_dec[-1]
            switch = battle.my_team[j - 1].id
            out_string += "switch to {}.".format(switch)
            print(out_string)

async def send_forced_switch_decision(ws, command_str, battle, format_output=False):
    command_str += "|" + str(battle.rqid)
    await ws.send(command_str)
    if not format_output:
        print("\nSending forced switch: " + command_str)
        return
    # format output to print nicely
    command_str = command_str.split("|/choose")[-1]
    switches = []
    for i, decision in enumerate( command_str.split(",") ):
        if (decision.split()[0] != "pass"):
            pokemon_name = [ mon.id for mon in battle.my_team if formatting.get_formatted_name(mon.id) == decision.split()[-1] ]
            switches.append(pokemon_name[0])
    out_string = "\nSwitching to " + " and ".join(switches) + "."
    print(out_string)
