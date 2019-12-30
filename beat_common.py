# From: http://www.rpscontest.com/submit

import random

if input == "": # initialize variables for the first round
    rockCount = paperCount = scissorsCount = 1
elif input == "R":
    rockCount += 1
elif input == "P":
    paperCount += 1
elif input == "S":
    scissorsCount += 1

if rockCount > paperCount and rockCount > scissorsCount:
    output = "P" # paper beats rock
elif paperCount > scissorsCount:
    output = "S" # scissors beats paper
else:
    output = "R" # rock beats scissors

