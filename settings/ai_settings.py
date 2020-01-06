# pokemon must have a strongest move with effective damage percentage (e.g. 20%) below this to manually switch
# lower -> less likely to manually switch
damage_floor = 30

# factor by which manual switch's strongest move must be compared to current pokemon, e.g. for switch_mult = 2 switch-in must have a strongest move with twice the base power
# higher -> less likely to manually switch
switch_mult = 3

# if the probability of a foe's pokemon having a certain move is
# >= alpha, then it is assumed the foe has that move
# (based on usage stats)
alpha = 20
