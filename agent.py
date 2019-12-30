import random

# All the possible histories.
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

if input == '':
    with open("best_sequence.txt") as f:
        line = f.readline()
        response = line.split(",")
        response[80] = response[80].strip()
    history = ['X']*4
    output = random.choice(['R', 'P', 'S'])
else:
    history.pop(0)
    history.append(input)
    try:
        index = dictionary.index(history)
        output = response[index]
    except:
        output = random.choice(['R', 'P', 'S'])
    history.pop(0)
    history.append(output)
