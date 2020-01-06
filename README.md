# showdown_bot
A battle bot for Pokemon Showdown (https://play.pokemonshowdown.com/) made in Python 3.

This is a bot which battles in Smogon Doubles tiers (i.e. DOU), currently focused on Gen 8 DOU, but previously made for Gen 7 DOU. It has managed to reach ~1500 on the Gen 7 ladder and ~1450 on the Gen 8 ladder so far.

The bot, when using the actual AI beyond just random/first move, will basically calculate what attack does the most damage (by %) and use that. Only attacks, including spread moves, will be used, no status moves. Manual switches are sometimes made, but very conservatively. Leads are always the first two Pokemon on the team, switches are decided using a ratio of damage dealt/received by the given Pokemon vs the active foes. In Gen 7 the bot will always Mega Evolve when possible but never use Z-moves; in Gen 8 it will only ever Dynamax with Braviary.

To use, download the files, then run the file 'main.py' with Python. (If on Windows using command prompt with Python 3 installed, then typing the command "cd (containing folder)", followed by "python3 main.py" should work)
