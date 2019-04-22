from battle import Battle
from helper_functions import formatting

# status = ["brn", "frz", "par", "psn", "tox", "slp"]
# pos_dict = {"a": 1, "b": 2}  # converts letter position to number, e.g. (p1)a is first pokemon
# will also have other dictionary converting player to side, e.g. p1 is bot p2 is foe
# side_dict = {battle.my_side: "bot", battle.foe_side: "foe"}


def major_actions(battle: Battle, split_line, side_dict):
    status = ["brn", "frz", "par", "psn", "tox", "slp"]
    pos_dict = {"a": 1, "b": 2}
    # move, used to decide that a pokemon can't fake out anymore
    if split_line[0] == "move":
        side = side_dict[split_line[1][0:2]]
        position = pos_dict[split_line[1][2]]
        move = formatting.format_move(split_line[2])  # unused
        pokemon = battle.get_pokemon(side, position)
        pokemon.can_fake_out = False
    # switch
    elif split_line[0] == "switch":
        side = side_dict[split_line[1][0:2]]
        pokemon_id = split_line[2].split(',')[0]
        position = pos_dict[split_line[1][2]]
        battle.update_switch(side, pokemon_id, position)
    # swap i.e. ally switch
    elif split_line[0] == "swap":
        side = side_dict[split_line[1][0:2]]
        pokemon1, pokemon2 = battle.active_pokemon(side)
        pokemon1.active, pokemon2.active = pokemon2.active, pokemon1.active
    # details change i.e. mega evolution
    elif split_line[0] == "detailschange":
        new_id = split_line[2].split(',')[0]
        position = pos_dict[split_line[1][2]]
        if (split_line[1][0:2] == battle.my_side):
            battle.form_change("bot", position, new_id)
        else:
            battle.form_change("foe", position, new_id)
    # includes flinches - use for stomping tantrum boost?
    elif split_line[0] == "cant":
        pass
    # pokemon fainting, currently do for bot team with team_data anyways
    elif split_line[0] == "faint":
        position = pos_dict[split_line[1][2]]
        side = side_dict[split_line[1][0:2]]
        pokemon = battle.get_pokemon(side, position)
        pokemon.fainted = True
    # pokemon on team at preview, currently handled otherwise with battle.initialise_teams() called from main
    elif split_line[0] == "poke":
        pass
        '''
        if battle.player_id not in split_line[1]:
            pkm = split_line[2].split(', ')
            battle.update_enemy(pkm[0], pkm[1][1:] if len(pkm) > 1 and 'L' in pkm[1] else '100', 100)
        '''
    # indicates updating counter for things like tr/tw/weather/terrain
    elif split_line[0] == "upkeep":
        battle.upkeep_counters()
    # new turn, if turn 1 then start switching out old pokemon on new switches
    elif split_line[0] == "turn":
        if (split_line[1] == "1"):
            battle.at_team_preview = False
        print("Turn {}".format(split_line[1]))  # print turn number
    else:
        pass


def minor_actions(battle: Battle, split_line, side_dict):
    status_list = ["brn", "frz", "par", "psn", "tox", "slp"]
    pos_dict = {"a": 1, "b": 2}
    # if move fails, e.g. protect
    if split_line[0] == "-fail":
        pass
    # pokemon takes damage (not just from attacks but also recoil, etc), do for foe only
    elif split_line[0] == "-damage" or split_line[0] == "-heal":
        side = side_dict[split_line[1][0:2]]
        # currently only updates foes' health
        if (side == "foe"):
            position = pos_dict[split_line[1][2]]
            pokemon = battle.get_pokemon(side, position)
            condition = split_line[2].strip("\n")
            if (condition[-3:] == "fnt"): # fainted
                pokemon.health_percentage = 0
                pokemon.has_fainted = True
                pokemon.status = "fnt"
            else:
                # set status, should get with -status anyways apart from natural cure!
                if (condition[-3:] in status_list):
                    pokemon.status = condition[-3:]
                    condition = condition[:-4]
                else:
                    pokemon.status = None
                pokemon.health_percentage = int(split_line[2].split("/")[0])
    # pokemon heals hp (does same as damage so deal with above)
    elif split_line[0] == "-heal":
        pass
    # status, only do for foes
    elif split_line[0] == "-status":
        position = pos_dict[split_line[1][2]]
        side = side_dict[split_line[1][0:2]]
        status = split_line[2].strip("\n")
        if (side == "foe"):
            pokemon = battle.get_pokemon(side, position)
            pokemon.status = status
    # status, only do for foes
    elif split_line[0] == "-curestatus":
        side = side_dict[split_line[1][0:2]]
        if (side == "foe"):
            pokemons = battle.foe_team
            pokemon_name = split_line[1].split(":")[1].strip()
            pokemon = next(mon for mon in pokemons if formatting.get_formatted_name(mon.id) == formatting.get_formatted_name(pokemon_name))
            pokemon.status = None
    # status, heal bell uses above and doesn't actually have this tag
    elif split_line[0] == "-cureteam":
        pass
    # stat boost
    elif split_line[0] == "-boost":
        side = side_dict[split_line[1][0:2]]
        position = pos_dict[split_line[1][2]]
        stat = split_line[2]
        amount = int(split_line[3])
        battle.add_buff(side, position, stat, amount)
    # stat unboost (same as boost with -ve boost)
    elif split_line[0] == "-unboost":
        side = side_dict[split_line[1][0:2]]
        position = pos_dict[split_line[1][2]]
        stat = split_line[2]
        amount = -int(split_line[3])  # unboost so negative
        battle.add_buff(side, position, stat, amount)
    # includes belly drum
    elif split_line[0] == "-setboost":
        side = side_dict[split_line[1][0:2]]
        position = pos_dict[split_line[1][2]]
        stat = split_line[2]
        amount = int(split_line[3])
        # set boost to +6 by adding boost of 12 (meaning -6 and above goes to 6)
        if (amount == 6):
            battle.add_buff(side, position, stat, 12)
        else:
            print("Oh no! I don't know what this move is but here is the info:", split_line)
    # includes haze
    elif split_line[0] == "-clearallboost":
        # reset boosts for all active pokemon
        pokemons = battle.active_pokemon("both")
        [pokemon.clear_boosts() for pokemon in pokemons]
    # weather, ignore on upkeep messages
    elif split_line[0] == "-weather" and len(split_line) >= 3 and split_line[2].strip("\n") != "[upkeep]":
        if (split_line[1][0:4] == "none"):
            battle.weather = None
            battle.weather_turns_left = 0
        else:
            battle.weather = formatting.format_move(split_line[1])
            battle.weather_turns_left = 5
    # terrain, trick room start
    elif split_line[0] == "-fieldstart":
        move = formatting.format_move(split_line[1])
        if (move == "trickroom"):
            battle.trick_room = 5
        elif ("terrain" in move):
            battle.terrain = move
            battle.terrain_turns_left = 5
    # terrain, trick room end
    elif split_line[0] == "-fieldend":
        move = formatting.format_move(split_line[1])
        if (move == "trickroom"):
            battle.trick_room = 0
        elif ("terrain" in move):
            battle.terrain = None
            battle.terrain_turns_left = 0
    # includes screens, entry hazards, tailwind
    elif split_line[0] == "-sidestart":
        side = side_dict[split_line[1][0:2]]
        move = formatting.format_move(split_line[2])
        if (move == "tailwind"): # tailwind
            battle.tailwind[side] = 4
        elif (move in battle.entry_hazards[side].keys()): # entry hazards
            battle.entry_hazards[side][move] += 1
        '''
        if "Reflect" in split_line[2] or "Light Screen" in split_line[2]:
            battle.screens[split_line[2].split(":")[1].lower().replace(" ", "")] = True
            print("** " + battle.screens)
        '''
    # includes screens, entry hazards, tailwind
    elif split_line[0] == "-sideend":
        side = side_dict[split_line[1][0:2]]
        move = formatting.format_move(split_line[2])
        if (move == "tailwind"): # tailwind
            battle.tailwind[side] = 0
        elif (move in battle.entry_hazards[side].keys()): # entry hazards
            battle.entry_hazards[side][move] = 0
        '''
        if "Reflect" in split_line[2] or "Light Screen" in split_line[2]:
            battle.screens[split_line[2].split(":")[1].lower().replace(" ", "")] = False
            print("** " + battle.screens)
        '''
    # move crits
    elif split_line[0] == "-crit":
        pass
    # move misses
    elif split_line[0] == "-miss":
        pass
    # move super effective
    elif split_line[0] == "-supereffective":
        pass
    # move resisted
    elif split_line[0] == "-resisted":
        pass
    # move hit immunity
    elif split_line[0] == "-immune":
        pass
    elif split_line[0] == "-item":
        pass
        '''
        if battle.player_id in split_line[1]:
            battle.bot_team.active().item = split_line[2].lower().replace(" ", "")
        else:
            battle.enemy_team.active().item = split_line[2].lower().replace(" ", "")
        '''
    # when lose item, e.g. eat berry or get knocked off
    elif split_line[0] == "-enditem":
        position = pos_dict[split_line[1][2]]
        if (split_line[1][0:2] == battle.my_side):
            pokemon = battle.get_pokemon("bot", position)
        else:
            pokemon = battle.get_pokemon("foe", position)
        pokemon.has_item = False
    elif split_line[0] == "-ability":
        pass
    elif split_line[0] == "-endability":
        pass
    elif split_line[0] == "-transform":
        pass
    # mega evolution, currently deal with under "detailschange"
    elif split_line[0] == "-mega":
        pass
    # includes protect
    elif split_line[0] == "-singleturn":
        side = side_dict[split_line[1][0:2]]
        position = pos_dict[split_line[1][2]]
        move = formatting.format_move(split_line[2])
        if (move == "protect"):
            pokemon = battle.get_pokemon(side, position)
            pokemon.can_protect = 2
    # includes making substitute, protect, heal bell, skill swap (if between opponent and us get info about both abilities, if between foes get nothing)
    elif split_line[0] == "-activate":
        pass
    # includes type change from moves like soak/burn up/conversion
    elif split_line[0] == "-start":
        side = side_dict[split_line[1][0:2]]
        position = pos_dict[split_line[1][2]]
        pokemon = battle.get_pokemon(side, position)
        if (split_line[2] == "typeadd"):
            type = split_line[3].strip("\n")
            pokemon.types.append(type)
        elif (split_line[2] == "typechange"):
            if ("[from]" not in split_line[3]):
                types = split_line[3].split("/")
                types = [type.strip("\n") for type in types if type.strip("\n") != "???"]
                pokemon.types = types
            else:  # deal with reflect type differently
                copy_side = side_dict[split_line[4][5:7]]
                copy_position = pos_dict[split_line[4][7]]
                copy_pokemon = battle.get_pokemon(copy_side, copy_position)
                if (len(copy_pokemon.types) > 0):  # if target is only ??? then move fails, so don't change type
                    pokemon.types = copy_pokemon.types
    # includes substitute breaking
    elif split_line[0] == "-end":
        pass

    # using the move transform
    elif split_line[0] == "-transform":
        pass
    elif split_line[0] == "-hitcount":
        pass
    # forewarn and anticipation maybe?
    elif split_line[0] == "-hint":
        pass
    elif split_line[0] == "-center":
        pass
    elif split_line[0] == "-message":
        pass
    else:
        pass


# takes a battle and message, and parses information which is used to update battle
def battlelog_parsing(battle: Battle, msg):
    # dictionary converting e.g. p1 to bot
    side_dict = {battle.my_side: "bot", battle.foe_side: "foe"}

    lines = msg.split("\n")[1:-1]  # split by line, ignore first and last
    split_lines = [line.split('|')[1:] for line in lines]  # split line by "|"
    split_lines = [line for line in split_lines if len(line[0]) > 0]  # ignore empty lines
    for split_line in split_lines:
        if split_line[0][0] != "-":
            major_actions(battle, split_line, side_dict)
        else:
            minor_actions(battle, split_line, side_dict)
