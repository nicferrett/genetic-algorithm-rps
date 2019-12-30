# P,S,P,P,R,P,P,P,S,S,S,S,R,S,S,S,S,S,R,S,R,R,R,R,R,P,R,P,R,S,P,P,R,P,P,P,R,S,S,S,S,R,R,S,P,R,P,R,R,P,R,S,R,R,P,P,S,P,R,S,P,R,P,S,S,P,R,S,P,P,S,P,S,R,R,R,R,R,P,R,R
import random

POPULATION_SIZE = 50
# Edit to define how many iterations of the genetic algorithm should be run
number_of_iterations = 50

# Class for each agent
class agent(object):
    def __init__(self, sequence, score = 0, probability = 0.0):
        self.sequence = sequence
        self.score = score
        self.prob = probability

# All possible histories, taken from agent.py
dictionary = [['R', 'R', 'R', 'R'], ['R', 'R', 'R', 'P'],
              ['R', 'R', 'R', 'S'], ['R', 'R', 'P', 'R'],
              ['R', 'R', 'P', 'P'], ['R', 'R', 'P', 'S'],
              ['R', 'R', 'S', 'R'], ['R', 'R', 'S', 'P'],
              ['R', 'R', 'S', 'S'], ['R', 'P', 'R', 'R'],
              ['R', 'P', 'R', 'P'], ['R', 'P', 'R', 'S'],
              ['R', 'P', 'P', 'R'], ['R', 'P', 'P', 'P'],
              ['R', 'P', 'P', 'S'], ['R', 'P', 'S', 'R'],
              ['R', 'P', 'S', 'P'], ['R', 'P', 'S', 'S'],
              ['R', 'S', 'R', 'R'], ['R', 'S', 'R', 'P'],
              ['R', 'S', 'R', 'S'], ['R', 'S', 'P', 'R'],
              ['R', 'S', 'P', 'P'], ['R', 'S', 'P', 'S'],
              ['R', 'S', 'S', 'R'], ['R', 'S', 'S', 'P'],
              ['R', 'S', 'S', 'S'], ['P', 'R', 'R', 'R'],
              ['P', 'R', 'R', 'P'], ['P', 'R', 'R', 'S'],
              ['P', 'R', 'P', 'R'], ['P', 'R', 'P', 'P'],
              ['P', 'R', 'P', 'S'], ['P', 'R', 'S', 'R'],
              ['P', 'R', 'S', 'P'], ['P', 'R', 'S', 'S'],
              ['P', 'P', 'R', 'R'], ['P', 'P', 'R', 'P'],
              ['P', 'P', 'R', 'S'], ['P', 'P', 'P', 'R'],
              ['P', 'P', 'P', 'P'], ['P', 'P', 'P', 'S'],
              ['P', 'P', 'S', 'R'], ['P', 'P', 'S', 'P'],
              ['P', 'P', 'S', 'S'], ['P', 'S', 'R', 'R'],
              ['P', 'S', 'R', 'P'], ['P', 'S', 'R', 'S'],
              ['P', 'S', 'P', 'R'], ['P', 'S', 'P', 'P'],
              ['P', 'S', 'P', 'S'], ['P', 'S', 'S', 'R'],
              ['P', 'S', 'S', 'P'], ['P', 'S', 'S', 'S'],
              ['S', 'R', 'R', 'R'], ['S', 'R', 'R', 'P'],
              ['S', 'R', 'R', 'S'], ['S', 'R', 'P', 'R'],
              ['S', 'R', 'P', 'P'], ['S', 'R', 'P', 'S'],
              ['S', 'R', 'S', 'R'], ['S', 'R', 'S', 'P'],
              ['S', 'R', 'S', 'S'], ['S', 'P', 'R', 'R'],
              ['S', 'P', 'R', 'P'], ['S', 'P', 'R', 'S'],
              ['S', 'P', 'P', 'R'], ['S', 'P', 'P', 'P'],
              ['S', 'P', 'P', 'S'], ['S', 'P', 'S', 'R'],
              ['S', 'P', 'S', 'P'], ['S', 'P', 'S', 'S'],
              ['S', 'S', 'R', 'R'], ['S', 'S', 'R', 'P'],
              ['S', 'S', 'R', 'S'], ['S', 'S', 'P', 'R'],
              ['S', 'S', 'P', 'P'], ['S', 'S', 'P', 'S'],
              ['S', 'S', 'S', 'R'], ['S', 'S', 'S', 'P'],
              ['S', 'S', 'S', 'S']]
data = []
population = []

# Simple function to rewrite the best sequence file in a common seperated list.
def write_best_sequence(sequence):
    f = open("best_sequence.txt", "w+")
    f.write("{0}".format(','.join(sequence)))
    f.close()

# Function that reads in the data from the cvs file, and orders in into a specified data structure.
# This structure is a list of 81 items, at each index it contains another list containing the move for that history
# This structure allows for an 0(1) look up for a history, with a 0(n) lookup for each move in that history
# This is much better compared to running through the file each time for each gene, which would be 0(n^2)
# While there are other implementations to achieve just 0(n) I found this to be the must structured in terms of lookup.
def get_data(data):
    while len(data) != 81:
        data.append([])
    with open("data.csv") as f:
        line = f.readline()
        while line:
            line_data = line.split(",")
            line_data[0] = list(line_data[0])
            x = dictionary.index(line_data[0])
            data[x].append(line_data[1].rstrip())
            line = f.readline()


# Function to initialize the population with random values
def initalize_population(population):
    for x in range(0, POPULATION_SIZE):
        random_sequence = []
        for counter in range(0, 81):
            random_sequence.append(random.choice(["R","P","S"]))
        population.append(agent(random_sequence))

# Fitness function that compares what is in a gene with what the file has for that gene, if they are the same then add
# Otherwise don't do anything, a rather simple fitness function. It then goes on to calculate the probability for each
# agent to be reselected for cross over.
def fitness_function(data, population):
    score = 0
    total = 0
    for single_agent in population:
        for x in range(0, 81):
            agent_move = single_agent.sequence[x]
            for y in data[x]:
                if agent_move == y:
                    score += 1

        single_agent.score = score
        total += score
        score = 0

    for single_agent in population:
        single_agent.prob = (single_agent.score)/float(total)

# A simple function that randoms a probability and finds the first agent with probability that tips the sum over the
# probability number allowing the probabilities to weigh in on the selection. The agents are not sorted, as this would
# begin to counter act the chance of allowing a lower probability agent to be selected.
def select_agent(population):
    random_probability = random.uniform(0, 1)
    sum = 0
    for single_agent in population:
        sum += single_agent.prob
        if sum >= random_probability:
            return single_agent
    return single_agent

# The cross over function, it randoms a number between 0 and 79, to ensure that at least one gene from each agent is
# used in the cross over, it then creates the child sequence using the parent sequences and returns the new child agent.
def reproduce(one, two):
    cross_over = random.randint(0,79)
    child_sequence = one.sequence[0:cross_over] + two.sequence[cross_over-81:]
    return agent(child_sequence)

# Function that compares the scores of all agents in a population to find the highest scoring agent
def find_best(population):
    best = population[0]
    for x in range(1, POPULATION_SIZE):
        if population[x].score > best.score:
            best = population[x]
    return best

# Mutate function, that randoms a position to mutate and then changes what is in that gene to one of the
# other two moves.
def mutate(child):
    new_child = child
    index = random.randint(0, 80)

    move = child.sequence[index]
    if move == "R":
        new_move = random.choice(['P', 'S'])
    elif move == "P":
        new_move = random.choice(['R', 'S'])
    else:
        new_move = random.choice(['R', 'P'])
    new_child.sequence[index] = new_move

    return new_child

# The genetic algorithm works as follows:
# 1, find the fitness of each agent in the population
# 2, add the best agent to the next population
# 3, pick two agents to cross over using select_agent, however ensure that they are not the same agent
# 4, cross over these two agents
# 5, random a number, if it is less than 10% then mutate
# 6, add agent to population. repeat until population full
# 7, repeat this until the number of iterations is completed - writing the best agents genes to a file for playing
def genetic_algorithm(population, data):
    working_pop = population
    iteration = 1
    while iteration < number_of_iterations:
        new_pop = []
        fitness_function(data, working_pop)

        best_so_far = find_best(working_pop)

        new_pop.append(best_so_far)

        print "ITERATION: {0}".format(iteration)
        print "BEST SO FAR: {0}".format(best_so_far.score)

        for x in range(0, POPULATION_SIZE-1):
            parent1 = select_agent(working_pop)
            parent2 = select_agent(working_pop)
            while parent2.sequence == parent1.sequence:
                parent2 = select_agent(working_pop)
            child = reproduce(parent1, parent2)
            mutation_chance = random.uniform(0, 1)
            if (mutation_chance <= 0.1):
                child = mutate(child)
            new_pop.append(child)

        working_pop = new_pop
        iteration += 1

    write_best_sequence(best_so_far.sequence)

# Start of the program, basically just calls the functions to run the algorithm
get_data(data)
initalize_population(population)

genetic_algorithm(population, data)
