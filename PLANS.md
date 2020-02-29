make other AIs work with new system of move dict


TODO:
consider foe combinations - see how long it takes (~minute per turn right now, >1000 possibilities considered)
consider switching - maybe use ratio and only consider top 2 or something, and only for pokemon that have a losing matchup
remove move options such as tailwind while up, protect if just did, fake out but not first turn, choice locked, only single target if 1 left
have list of mons to consider dmax for
use ratio thing or check if can be KOed/if will be outsped to determine if should consider a pokemon switching
remember to make sure can't switch to same pokemon in both slots
look up lead percentages, weight by true usage? then weight by relative value to team and pick randomly?


Sim:
add minimax (with alpha-beta pruning)
add protect, tailwind, some status moves like wisp/twave?
add activation of sitrus, fiwam, lum, wp, (life orb?)
add follow me/rage powder
add end of turn effects (terrain, weather, status)
if our pokemon tie with an opponent make ours 0.5 slower so assume they win tie?
for multi-turn need to calculate switches for koes at end/start of turn (also volt switch/u-turn)
make how moves are stored include slot e.g. p1a rather than just bot/foe

make depth start at 0 and go up, and set max turn limit (1 for now)
make possible to go higher depths, also make sure battle is used correctly going down but not changing for other branches
make possible moves contain less info until later on where calc speed and do by species etc? also convert to dict so easier to understand
fix stuff so don't have attacks inputted against empty slot or calced against something dead


Calc:
split into quick calc (move dependent) and finish calc (same for user/target)?
add offensive items (life orb, choice, plate/equivalents)
add defensive items (eviolite, assault vest, sash?)
make only consider redirection abilities on active pokemon


Pokemon:
add last used move property (for choice lock) - but ignore dmax moves?
add encore, disable (both equal to move name)


Usage:
combine fiwam berries
use to prune possible abilities?


Parser
items (see below logs) -item
moves


Main:
fix coming back from away (updateuser) breaking bot
fix someone leaving and rejoining battle starting greeting lines


Optimisation:
currently getting possible foe decisions multiple times (each time branch in minimax for for possible bot decisions)

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)

       46    0.000    0.000  464.084   10.089 main.py:109(connect_to_ps)
       63    0.001    0.000  464.074    7.366 main.py:24(parse_response)

       13    0.001    0.000  455.277   35.021 battle.py:74(load_team_data)

        6    0.000    0.000  450.585   75.097 ai_simulate_turn.py:185(choose_moves)
   2569/6    1.139    0.000  450.582   75.097 ai_simulate_turn.py:132(minimax)
                    ~ 3 seconds in total in minimax logic itself
     2480    1.070    0.000  447.514    0.180 simulation.py:95(simulate_turn)
     9449    4.181    0.000  412.720    0.044 simulation.py:83(simulate_attack)
    11188   13.065    0.001  408.539    0.037 simulation.py:71(deal_damage)
35 s                            1 turn ~ 4 attacks (102%)
4 s                            1 attack ~= 1.2 damage (119%)
122 s (20)                            1 damage ~ 1.5 calc (148%)
    11343    8.601    0.001  286.787    0.025 calc.py:163(calc_damage)
287 s  (48)                  ~ 287 seconds in total in calc!!!!!!!!
        3    0.000    0.000    4.690    1.563 ai_simulate_turn.py:277(choose_switch)
        3    0.003    0.001    4.686    1.562 get_info.py:81(calculate_score_ratio_switches)
        8    0.105    0.013    4.682    0.585 get_info.py:100(calculate_score_ratio_single)
        1    0.001    0.001    3.636    3.636 battle.py:48(initialise_teams)
        1    0.005    0.005    3.306    3.306 predict_foe_sets.py:101(update_likely_sets)

NB: the difference in cumtime going down gives how much time is spent within that function in particular (in total)
above for 6 turns (divide by 6 for per turn)


Logs:
"""
">battle-gen8doublesou-1045063230↵↵|↵|start↵|switch|p1a: Dusclops|Dusclops, M|284/284↵|switch|p1b: Excadrill|Excadrill, F|362/362↵|switch|p2a: Tyranitar|Tyranitar, M|100/100↵|switch|p2b: Excadrill|Excadrill, F|100/100↵|-ability|p1b: Excadrill|Mold Breaker↵|-weather|Sandstorm|[from] ability: Sand Stream|[of] p2a: Tyranitar↵|-item|p2a: Tyranitar|Weakness Policy|[from] ability: Frisk|[of] p1a: Dusclops|[identify]↵|-item|p2b: Excadrill|Life Orb|[from] ability: Frisk|[of] p1a: Dusclops|[identify]↵|turn|1↵"

">battle-gen8doublesou-1045063230↵↵|↵|move|p2b: Excadrill|Iron Head|p1a: Dusclops↵|-damage|p1a: Dusclops|202/284↵|-damage|p2b: Excadrill|91/100|[from] item: Life Orb↵|move|p1b: Excadrill|Rock Slide|p2a: Tyranitar|[spread] p2a,p2b↵|-resisted|p2b: Excadrill↵|-damage|p2a: Tyranitar|74/100↵|-damage|p2b: Excadrill|82/100↵|-damage|p1b: Excadrill|326/362|[from] item: Life Orb↵|move|p2a: Tyranitar|Crunch|p1a: Dusclops↵|-supereffective|p1a: Dusclops↵|-damage|p1a: Dusclops|68/284↵|move|p1a: Dusclops|Trick Room|p1a: Dusclops↵|-fieldstart|move: Trick Room|[of] p1a: Dusclops↵|↵|-weather|Sandstorm|[upkeep]↵|-damage|p1a: Dusclops|51/284|[from] Sandstorm↵|upkeep↵|turn|2↵"

">battle-gen8doublesou-1045063230↵↵|↵|move|p1a: Dusclops|Pain Split|p2b: Excadrill↵|-sethp|p2b: Excadrill|48/100|[from] move: Pain Split|[silent]↵|-sethp|p1a: Dusclops|173/284|[from] move: Pain Split↵|move|p2a: Tyranitar|Rock Slide|p1a: Dusclops|[spread] p1a,p1b↵|-resisted|p1b: Excadrill↵|-damage|p1a: Dusclops|130/284↵|-damage|p1b: Excadrill|287/362↵|move|p1b: Excadrill|High Horsepower|p2a: Tyranitar|[miss]↵|-miss|p1b: Excadrill|p2a: Tyranitar↵|move|p2b: Excadrill|Iron Head|p1a: Dusclops↵|-damage|p1a: Dusclops|48/284↵|-damage|p2b: Excadrill|38/100|[from] item: Life Orb↵|↵|-weather|Sandstorm|[upkeep]↵|-damage|p1a: Dusclops|31/284|[from] Sandstorm↵|upkeep↵|turn|3↵"

">battle-gen8doublesou-1045063230↵↵|↵|switch|p1a: Corviknight|Corviknight, M|400/400↵|move|p2a: Tyranitar|Rock Slide|p1b: Excadrill|[spread] p1a,p1b↵|-resisted|p1b: Excadrill↵|-damage|p1a: Corviknight|283/400↵|-damage|p1b: Excadrill|245/362↵|move|p1b: Excadrill|High Horsepower|p2a: Tyranitar↵|-supereffective|p2a: Tyranitar↵|-damage|p2a: Tyranitar|0 fnt↵|-damage|p1b: Excadrill|209/362|[from] item: Life Orb↵|faint|p2a: Tyranitar↵|move|p2b: Excadrill|Iron Head|p1a: Corviknight↵|-resisted|p1a: Corviknight↵|-damage|p1a: Corviknight|200/400↵|-damage|p2b: Excadrill|28/100|[from] item: Life Orb↵|↵|-weather|Sandstorm|[upkeep]↵|-heal|p1a: Corviknight|225/400|[from] item: Leftovers↵|upkeep↵"

">battle-gen8doublesou-1045063230↵↵|↵|-start|p1b: Excadrill|Dynamax↵|-heal|p1b: Excadrill|418/724|[silent]↵|move|p1a: Corviknight|Roost|p1a: Corviknight↵|-heal|p1a: Corviknight|400/400↵|-singleturn|p1a: Corviknight|move: Roost↵|move|p2a: Braviary|Close Combat|p1a: Corviknight↵|-supereffective|p1a: Corviknight↵|-damage|p1a: Corviknight|176/400↵|-unboost|p2a: Braviary|def|1↵|-unboost|p2a: Braviary|spd|1↵|move|p1b: Excadrill|Max Rockfall|p2a: Braviary↵|-supereffective|p2a: Braviary↵|-damage|p2a: Braviary|0 fnt↵|-damage|p1b: Excadrill|382/724|[from] item: Life Orb↵|faint|p2a: Braviary↵|move|p2b: Excadrill|Rock Slide|p1b: Excadrill|[spread] p1a,p1b↵|-resisted|p1a: Corviknight↵|-resisted|p1b: Excadrill↵|-crit|p1b: Excadrill↵|-damage|p1a: Corviknight|133/400↵|-damage|p1b: Excadrill|335/724↵|-damage|p2b: Excadrill|18/100|[from] item: Life Orb↵|↵|-weather|Sandstorm|[upkeep]↵|-heal|p1a: Corviknight|158/400|[from] item: Leftovers↵|upkeep↵"

">battle-gen8doublesou-1045063230↵|request|{"active":[{"moves":[{"move":"Brave Bird","id":"bravebird","pp":24,"maxpp":24,"target":"any","disabled":false},{"move":"Body Press","id":"bodypress","pp":16,"maxpp":16,"target":"normal","disabled":false},{"move":"Bulk Up","id":"bulkup","pp":32,"maxpp":32,"target":"self","disabled":false},{"move":"Roost","id":"roost","pp":15,"maxpp":16,"target":"self","disabled":false}]},{"moves":[{"move":"Iron Head","id":"ironhead","pp":24,"maxpp":24,"target":"normal","disabled":false},{"move":"High Horsepower","id":"highhorsepower","pp":14,"maxpp":16,"target":"normal","disabled":false},{"move":"Rock Slide","id":"rockslide","pp":14,"maxpp":16,"target":"allAdjacentFoes","disabled":false},{"move":"Protect","id":"protect","pp":16,"maxpp":16,"target":"self","disabled":false}],"maxMoves":{"maxMoves":[{"move":"maxsteelspike","target":"adjacentFoe"},{"move":"maxquake","target":"adjacentFoe"},{"move":"maxrockfall","target":"adjacentFoe"},{"move":"maxguard","target":"self"}]}}],"side":{"name":"Yoda≧◡≦2798","id":"p1","pokemon":[{"ident":"p1: Corviknight","details":"Corviknight, M","condition":"158/400","active":true,"stats":{"atk":244,"def":246,"spa":127,"spd":206,"spe":222},"moves":["bravebird","bodypress","bulkup","roost"],"baseAbility":"mirrorarmor","item":"leftovers","pokeball":"pokeball","ability":"mirrorarmor"},{"ident":"p1: Excadrill","details":"Excadrill, F","condition":"335/724","active":true,"stats":{"atk":369,"def":156,"spa":122,"spd":166,"spe":302},"moves":["ironhead","highhorsepower","rockslide","protect"],"baseAbility":"moldbreaker","item":"lifeorb","pokeball":"pokeball","ability":"moldbreaker"},{"ident":"p1: Dusclops","details":"Dusclops, M","condition":"31/284","active":false,"stats":{"atk":145,"def":394,"spa":156,"spd":297,"spe":77},"moves":["trickroom","wonderroom","painsplit"],"baseAbility":"frisk","item":"eviolite","pokeball":"pokeball","ability":"frisk"},{"ident":"p1: Aegislash","details":"Aegislash, M","condition":"292/292","active":false,"stats":{"atk":136,"def":316,"spa":136,"spd":316,"spe":156},"moves":["brickbreak"],"baseAbility":"stancechange","item":"","pokeball":"pokeball","ability":"stancechange"}]},"rqid":16}"

">battle-gen8doublesou-1045063230↵↵|↵|switch|p2b: Rotom|Rotom-Wash|100/100↵|switch|p1a: Dusclops|Dusclops, M|31/284↵|-item|p2a: Dragapult|Life Orb|[from] ability: Frisk|[of] p1a: Dusclops|[identify]↵|-item|p2b: Rotom|Sitrus Berry|[from] ability: Frisk|[of] p1a: Dusclops|[identify]↵|turn|6↵"

">battle-gen8doublesou-1045063230↵↵|↵|move|p1b: Excadrill|Max Guard||[still]↵|-fail|p1b: Excadrill↵|move|p2a: Dragapult|Dragon Pulse|p1a: Dusclops↵|-damage|p1a: Dusclops|0 fnt↵|-damage|p2a: Dragapult|91/100|[from] item: Life Orb↵|faint|p1a: Dusclops↵|move|p2b: Rotom|Volt Switch|p1b: Excadrill↵|-immune|p1b: Excadrill↵|↵|-end|p1b: Excadrill|Dynamax↵|-heal|p1b: Excadrill|168/362|[silent]↵|upkeep↵"
"""
