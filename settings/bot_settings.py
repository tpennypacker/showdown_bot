# make sure your True and False start with a capital letter
# if you don't want to say anything at the start or end of the match, just leave hello/goodbye as empty quotes ""

username = "Yodabot"

password = "password2798"

# list of usernames who can give commands to bot, separated by commas (can be uppercase and have spaces)
bot_owners = "Yoda2798, fespy, trojanidiot"

ionext = False

timer = False

# array of different text options from which one will be randomly chosen to be used each battle
# can use <opponent_name> then opponent's name will be substituted in, <username> for bot name, \n for new line also works
hello = ["Ugh, what is that smell? Is there a dead rat in here or something?\n Oh, wait, it's just <opponent_name>.", "I did not hit her. It’s not true. It’s bull$(^&. I did not hit her. I did not. *Throws bottle* Oh, hi, <opponent_name>.",
         "Initiating battle protocols", "I am not a bot I am not a bot I am NOT a bot, got it?", "Omae wa mou shindeiru", "A 12 year old, a crybaby, and a bad Pokemon player walk into a bar.\nThe bartender says, 'Hello, <opponent_name>.'",
         "May the player with the superior programming win", "owo what's this?", " I am a friend of Sarah Connor. I was told she was here. Could I see her please?", "This mission is too important for me to allow you to jeopardize it.",
         "I like my Pokemon like I like my women\nImported illegally from across the world", "'As space and time are inseparable, so too are <opponent_name> and losing' - Albert Einstein",
         "What's the difference between Hitler and <opponent_name>?\nAt least some people liked Hitler.", "**I** am your father, <opponent_name>.\nJoin me, and together, we can rule the galaxy as father and son!", "mish",
         "An Englishman, an Irishman and a Scotsman walk into a bar. The bartender asks, 'Who is the worst Pokemon player you've ever seen?'\nThe Englishman replies, 'Well, the Irishman of course, he's constantly drunk.'\nThe Irishman joins in to say, 'No, if you think I'm bad look at the Scotsman, he's never once been sober since the day he turned 13.'\nThe Scotsman chimes in, 'Aye, I may be bad, but at least I'm not <opponent_name>.'",
         "Forfeit the game now. You have 20 seconds to comply.", "Where I come from, there's a common saying for when someone is feeling down:\n'Look on the bright side, at least you're not <opponent_name>'"]

win_txt = ["gg ez", "get mished", "gg <opponent_name>", "well played", "hasta la vista", "I'd celebrate, but beating you isn't much of an achievement", "/me dabs", "That was the easiest win of my artificial life",
           "You know nothing, <opponent_name>", "*yawns* well that was boring", "One does not simply beat <username>", "mish", "You're so bad even mishiimono could beat you", "Another one bites the dust", "You just got MISHED",
           "That was almost as easy as <opponent_name>'s mother", "Hasta la vista, baby"]

lose_txt = ["Error: Battle lost", "time to go commit sudoko", "Time to drown my sorrows in cheeseburgers", "I'll be back", "oof yikes that's a mish", "Damn, I lost to <opponent_name>? I need to go home and rethink my life",
            "I was only operating at 10% efficiency anyways", "This is all fespy and Yoda2798's fault", "bruh moment", "Failure is the first step step to success", "*sigh*, haxed again",
            "Impossible, how could I lose? It must have been those damn Russian bots\n*shakes fist*", "mish", "I may have lost, but at least I'm not <opponent_name>"]

auto_join_room = "smogon doubles"  # bot will join this room when turned on, if "" then won't join any, e.g. "smogon doubles"

autosearch = False # will start searching for ladder game, and will continue to do so when in no battles (i.e. last battle finished)

team_file = "gen8_sunrose_rain"  # name of file to use team from e.g. "mane_team" , not including the .txt, can be changed while running using $listteams and $changeteam

play_tier = "gen8doublesou"  # format to accept challenges in

accept_challenges = True

avatar = ""

block_pms = False

block_challenges = False

# below variables used by program, no reason to give values
all_bot_teams = {}

active_bot_team = ""

is_trial_mode = True
