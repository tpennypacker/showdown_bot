import re


def clean_up(string_in):
    return string_in.strip("-").strip("\n").strip()


def clean_move(move):
    return move.lower().replace(" ", "").replace("'", "").replace("-", "").replace(",", "").replace("[","").replace("]","")


def read_all_teams(file_names):

    teams = {}  # dictionary of team: message to send for team

    for file_name in file_names:
        team_name = file_name[:-4]  # remove .txt
        teams[team_name] = read_team(file_name)

    return teams


def read_team(team_file):
    read_location = "teams/" + team_file
    with open(read_location, "r") as read_file:
        x = read_file.readlines()
        x = [line.strip() for line in x]  # remove new line characters

    # ensure in format with no blank lines at start, and exactly one at end
    while (x[0] == "" or x[0][0] == "#"):
        x.pop(0)
    while (x[-2] == x[-1] == ""):
        x.pop()
    if (x[-1] != ""):
        x.append("")

    stats_list = ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]
    packed_team = ""
    no_of_pokemon = x.count("")
    i = 0  # position of line currently reading

    #print(x)

    for j in range(no_of_pokemon):
        # item
        if ("@" in x[i]):
            x[i], item = x[i].split("@")
            item = clean_up(item).lower().replace(" ","")
        else:
            item = ""

        # gender
        x_split = x[i].split("(")
        if (x_split[-1].replace(")","").strip() in ["M","F"]):
            gender = x_split.pop().replace(")","").strip()
        else:
            gender = ""

        # name/species
        if (len(x_split) > 1):
            species = x_split.pop().replace(")","").strip()
            name = "(".join(x_split).strip()
        else:
            species = ""
            name = clean_up(x_split[0])
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
        else:
            nature = ""

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
            if (x[i] == ""):
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
    #print("\n" + packed_team)
    return packed_team
