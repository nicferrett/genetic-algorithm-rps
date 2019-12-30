# An agent to beat the last object the opponent played.
#
# Uses ideas from information in agents submitted to http://www.rpscontest.com
# Written by: W. P. du Plessis
# Last update: 2019-02-07


import random
beat = {"R":"P", "P":"S", "S":"R"}
if not input:
    output = random.choice(["R", "P", "S"])
else:
    output = beat[input]
