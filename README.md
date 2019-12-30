# Genetic Algorithm for Rock, Paper, Scissors
Genetic Algorithm was built to play rock paper scissors against simple bots using in the RPS Contest (http://www.rpscontest.com/).

The genetic algorithm is built from first principles using arrays in python2.7. 

The genetic algorithm is accompanied by an agent to play the game rock, paper, scissors on the rpsrunner.py. The genetic algorithm was trained using the provided data.cvs. The genetic algorithm can learn to play and beat the following bots:
- only_rock (only plays rock)
- only_scissors (only plays scissors)
- only_paper (only plays paper)
- beat_previous (plays the move to beat you previous move)
- beat_common (plays the move to beat the most commonly played move)

# How to train:
Run the RPS_GA.py for the desired number of iterations to develop a playable sequence. The mutation rate is fixed at 10% however the population size can be varied.

# How to play:
Run the following command in the terminal to play the agent.py vs any of the other bots. Note, that training needs to take place before hand, or manually copy the best sequence from the top of RPS_GA.py into the best_sequence.txt.

python rps_runner.py -m <#matches> -r <#rounds> agent.py desiredbot.py

Replace the <#> with the desired number of matches and rounds respectively.

# Disclaimer 
This project was completed for a university class for EAI 320 - Intelligent Systems, University of Pretoria and may not be copied. The project has been slightly adpated.
