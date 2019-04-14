import re


def clean_up(string_in):
    return string_in.strip("-").strip("\n").strip()


def clean_move(move):
    return move.lower().replace(" ", "").replace("'", "").replace("-", "").replace(",", "").replace("[","").replace("]","")



def read_team():
    with open("settings/team.txt", "r") as team_file:
        x = team_file.readlines()[2:]

    stats_list = ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]
    packed_team = ""
    no_of_pokemon = x.count("\n")
    i = 0  # position of line currently reading

    for j in range(no_of_pokemon):
        # item
        if ("@" in x[i]):
            x[i], item = x[i].split("@")
            item = clean_up(item).lower()
        else:
            item = ""

        # species
        species_search = re.findall("(?<=\()\w\w+(?=\))", x[i])
        if (len(species_search) > 0):
            species = species_search[0]
            l = len(species) + 2
            name = x[i].strip()[:-l].strip()
        else:
            name = clean_up(x[i])
            species = ""

        # gender
        if ("(M)" in x[i]):
            gender = "M"
        elif ("(F)" in x[i]):
            gender = "F"
        else:
            gender = ""
        i += 1

        # ability
        ability = clean_move(clean_up(x[i][9:]))
        i += 1

        # level
        if (x[i][:5] == "Level"):
            level = clean_up(x[i][6:])
            i += 1
        else:
            level = ""

        # shiny
        if (x[i][:5] == "Shiny"):
            shiny = "S"
            i += 1
        else:
            shiny = ""

        # happiness
        if (x[i][:9] == "Happiness"):
            happiness = clean_up(x[i][10:])
            i += 1
        else:
            happiness = ""

        # EVs
        if (x[i][:3] == "EVs"):
            evs = []
            for stat in stats_list:
                if (stat in x[i]):
                    evs.append(re.search("\d+(?= stat)".replace("stat", stat), x[i])[0])
                else:
                    evs.append("")
            evs = ",".join(evs)
            i += 1
        else:
            evs = ""

        # nature
        if (clean_up(x[i])[-6:] == "Nature"):
            nature = clean_up(x[i])[:-7]
            i += 1

        # IVs
        if (x[i][:3] == "IVs"):
            ivs = []
            for stat in stats_list:
                if (stat in x[i]):
                    ivs.append(re.search("\d+(?= stat)".replace("stat", stat), x[i])[0])
                else:
                    ivs.append("")
            ivs = ",".join(ivs)
            i += 1
        else:
            ivs = ""

        # moves
        moves = []
        while True:
            if (x[i] == "\n"):
                i += 1
                break
            move = clean_up(x[i])
            moves.append(clean_move(move))
            i += 1
        moves = ",".join(moves)

        # add pokemon information to string
        packed_team += "|".join([name, species, item, ability, moves, nature, evs, gender, ivs, shiny, level, happiness])

        # character at end of each pokemon apart from last
        if (j < no_of_pokemon - 1):
            packed_team += "]"

    return packed_team
