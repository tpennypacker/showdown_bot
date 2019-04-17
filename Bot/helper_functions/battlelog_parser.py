from battle import Battle


pos_dict = {"a": 1, "b": 2}  # converts letter position to number, e.g. (p1)a is first pokemon
# will also have other dictionary converting player to side, e.g. p1 is bot p2 is foe
# side_dict = {battle.my_side: "bot", battle.foe_side: "foe"}


def major_actions(battle: Battle, split_line, side_dict):
    if split_line[0] == "move":
        pass
    # switch
    elif split_line[0] == "switch":
        pokemon_id = split_line[2].split(',')[0]
        position = pos_dict[split_line[1][2]]
        if (split_line[1][0:2] == battle.my_side):
            battle.update_switch("bot", pokemon_id, position)
        else:
            battle.update_switch("foe", pokemon_id, position)
    # swap i.e. ally switch
    elif split_line[0] == "swap":
        if (split_line[1][0:2] == battle.my_side):
            pokemon1, pokemon2 = battle.active_pokemon("bot")
        else:
            pokemon1, pokemon2 = battle.active_pokemon("foe")
        pokemon1.active, pokemon2.active = pokemon2.active, pokemon1.active
    # details change i.e. mega evolution
    elif split_line[0] == "detailschange":
        new_id = split_line[2].split(',')[0]
        position = pos_dict[split_line[1][2]]
        if (split_line[1][0:2] == battle.my_side):
            battle.form_change("bot", position, new_id)
        else:
            battle.form_change("foe", position, new_id)
    # includes flinches
    elif split_line[0] == "cant":
        pass
    # pokemon fainting, currently do for bot team with team_data anyways
    elif split_line[0] == "faint":
        position = pos_dict[split_line[1][2]]
        side = side_dict[split_line[1][0:2]]
        pokemon = battle.get_pokemon(side, position)
        pokemon.fainted = True
    # pokemon on team at preview, currently handled otherwise with battle.initialise_teams()
    elif split_line[0] == "poke":
        pass
        '''
        if battle.player_id not in split_line[1]:
            pkm = split_line[2].split(', ')
            battle.update_enemy(pkm[0], pkm[1][1:] if len(pkm) > 1 and 'L' in pkm[1] else '100', 100)
        '''
    elif split_line[0] == "upkeep":
        pass
    # new turn, if turn 1 then start switching out old pokemon on new switches
    elif split_line[0] == "turn":
        if (split_line[1] == "1"):
            battle.team_preview = False
    else:
        pass


def minor_actions(battle: Battle, split_line, side_dict):
    if split_line[0] == "-fail":
        pass
    # pokemon takes damage (not just from attacks but also recoil, etc)
    elif split_line[0] == "-damage":
        position = pos_dict[split_line[1][2]]
        side = side_dict[split_line[1][0:2]]
        # currently only updates foes' health
        if (side == battle.foe_side):
            pokemon = battle.get_pokemon(side, position)
            if ("fnt" not in split_line[2]):
                pokemon.health = int(split_line[2].split("/"))
            else:
                pokemon.health = 0
    # pokemon heals hp (does same as damage)
    elif split_line[0] == "-heal":
        position = pos_dict[split_line[1][2]]
        side = side_dict[split_line[1][0:2]]
        # currently only updates foes' health
        if (side == battle.foe_side):
            pokemon = battle.get_pokemon(side, position)
            if ("fnt" not in split_line[2]):
                pokemon.health = int(split_line[2].split("/"))
            else:
                pokemon.health = 0
    elif split_line[0] == "-status":
        pass
        '''
        if battle.player_id in split_line[1]:
            battle.update_status(battle.bot_team.active(), split_line[2])
        else:
            battle.update_status(battle.enemy_team.active(), split_line[2])
        '''
    elif split_line[0] == "-curestatus":
        pass
        '''
        if battle.player_id in split_line[1]:
            battle.update_status(battle.bot_team.active())
        else:
            battle.update_status(battle.enemy_team.active())
        '''
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
        '''
        if (split_line[1][0:2] == battle.my_side):
            battle.add_buff("bot", position, stat, amount)
        else:
            battle.add_buff("foe", position, stat, amount)
        '''
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
    # weather
    elif split_line[0] == "-weather":
        if (split_line[1][0:4] == "none"):
            battle.weather = None
        else:
            battle.weather = split_line[1]
    # terrain start
    elif split_line[0] == "-fieldstart":
        battle.terrain = split_line[1][6:]
    # terrain end
    elif split_line[0] == "-fieldend":
        battle.terrain = None
    # includes screens, entry hazards
    elif split_line[0] == "-sidestart":
        pass
        '''
        if "Reflect" in split_line[2] or "Light Screen" in split_line[2]:
            battle.screens[split_line[2].split(":")[1].lower().replace(" ", "")] = True
            print("** " + battle.screens)
        '''
    elif split_line[0] == "-sideend":
        pass
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
        pass
    # includes making substitute, protect, heal bell
    elif split_line[0] == "-activate":
        pass
    # includes substitute breaking
    elif split_line[0] == "-end":
        pass
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
