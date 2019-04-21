


# format active moves, and denote disabled moves as ""
def format_active_move(move):
	if (move["disabled"] == True):
		return ""
	else:
		return format_move(move["move"])


# format move e.g. "U-turn" -> "uturn"
def format_move(move):
	return move.replace("move: ","").strip("\n").lower().replace(" ", "").replace("'", "").replace("-", "").replace(",", "")


mons_with_useless_forms = ['gastrodon', 'shellos', 'florges', 'genesect',
							'deerling', 'sawsbuck', 'burmy', 'furfrou',
							'magearna', 'minior']

def get_formatted_name(pokemon_name):
	formatted = pokemon_name.split(",")[0].lower().replace(' ', '').replace('-', '').replace("'", "").replace(":", "").replace("*","").strip("\n")

	for mon in mons_with_useless_forms:
		if mon in formatted:
			return mon

	return formatted


def format_switch_name(pokemon_name):
	pokemon_name = pokemon_name.split(',')[0]
	if (pokemon_name[-4:] == "mega"):
		return pokemon_name[:-4]
	elif (pokemon_name[-5:] == "megax" or pokemon_name[-5:] == "megay"):
		return pokemon_name[:-5]
	else:
		return pokemon_name


# e.g. convert "hiddenpowerice60" to "hiddenpowerice"
def remove_hp_power(move_name):
	if ("hiddenpower" in move_name):
		return move_name[:-2]
	else:
		return move_name
