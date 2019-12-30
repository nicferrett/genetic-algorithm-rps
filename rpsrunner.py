#!/usr/bin/env python


# A slightly modified version of the PRS framwork available from http://www.rpscontest.com/rpsrunner.py
# The modifications allow the number of rounds to be determined with a command-line option.
#
# Updated by: W. P. du Plessis
# Last update: 2019-02-07

# Command line to run all agents in a given directory.
#./rpsrunner.py -m 10 -r 1000 `ls *.py | egrep -v 'rpsrunner' | tr $'\n' , | sed s/,$//`

# Command line to run all agents in a given directory, except those starting with 3 or 4
#  numbers followed by an underscore.
#./rpsrunner.py -m 10 -r 1000 `ls *.py | egrep '[0-9]{3,4}_' | tr $'\n' , | sed s/,$//`


# Rock-Paper-Scissors runner for http://www.rpscontest.com/

# Copyright (c) 2011 Jonathan Burdge
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject
# to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

try:
	from multiprocessing import Pool, cpu_count
except:
	Pool = None

import getopt
import glob
import os
import random
import sys
import time
import traceback

########

VERSION = "1.0.1"
MATCHES = 10
ROUNDS = 1000
POOL_SIZE = 1

if Pool is not None:
	try:
		POOL_SIZE = cpu_count()
	except:
		pass

WINDOWS = False
try:
	sys.getwindowsversion()
except:
	WINDOWS = False
else:
	WINDOWS = True

########

class Bot:
	"""Basic bot class to wrap bot functions"""
	def __init__(self, name, code=None):
		"""
name should be a unique identifier and must be a readable
filename if code is not specified
"""
		self.name = name
		if code is None:
			self.load_code()
		else:
			self.code = code

		self.reset()

	def __eq__(self, other):
		return self.name == other.name

	def get_move(self, input):
		"""Get the next move for the bot given input
input must be "R", "P", "S" or ""
"""
		if self._code is None:
			self.compile_code()

		self.scope["input"] = input
		exec self._code in self.scope
		self.output = self.scope["output"]
		return self.output

	def compile_code(self):
		self._code = compile(self.code, '<string>', 'exec')

	def reset(self):
		"""Resets bot for another round.  This must be called before trying
to pass the bot between workers, or you may see obscure errors from failures
to pickle the bots scope dictionary."""
		self.scope = dict()

		# this will hold compiled code, but it apparently can't be
		# pickled? so we'll have to do it later.  XXX check into this
		self._code = None

	def load_code(self):
		"""Load bot code from the file specified by the name attribute"""
		f = open(self.name, "r")
		self.code = f.read()
		f.close()

# used to evaluate a pair of moves
# scoring[bot1_move][bot2_move]
# 1 = bot1 won, -1 = bot2 won, 0 = tie
# TODO: move into ContestResult?
scoring = {
	"R": {
		"R": 0,
		"P": -1,
		"S": 1
	},
	"P": {
		"R": 1,
		"P": 0,
		"S": -1
	},
	"S": {
		"R": -1,
		"P": 1,
		"S": 0
	}
}

class ContestResult:
	"""Used to track and report on the status of a contest.  Shared values
are reported from the perspective of bot1.  For example, score > 0 indicates
that bot1 won by that many points.  score < 0 indicates bot 1 lost by that
many points."""
	# TODO bot-specific data should be a seperate object.  ContestResult
	# should track two of these objects and move most of the bot-specific
	# data below into them.
	def __init__(self, bot1, bot2):
		self.bot1 = bot1
		self.bot2 = bot2
		self.bot1_disqualified = False
		self.bot2_disqualified = False
		self.finalized = False
		self.errors = False
		self.error_string = ""

		self.wins1 = 0
		self.wins2 = 0
		self.ties1 = 0
		self.ties2 = 0
		self.losses1 = 0
		self.losses2 = 0
		self.score = 0
		self.played = 0
		self.history1 = []
		self.history2 = []
		self.score_history = []
		self.start_time = None
		self.end_time = None
		self.run_time = 0.0
		self.winner = None
		self.loser = None

	def start(self):
		self.start_time = time.time()

	def score_moves(self, move1, move2):
		"""This function is called to score and track each pair of moves
from a contest."""

		score = 0
		try:
			score = scoring[move1][move2]
		except KeyError:
			# TODO disqualify bot and exit contest
			if move1 not in "RPS":
				score = -1
			elif move2 not in "RPS":
				score = 1
			else:
				raise Exception("Can't score %s and %s?!" % (move1, move2))

		if score > 0:
			self.wins1 += 1
			self.losses2 += 1
		elif score < 0:
			self.losses1 += 1
			self.wins2 += 1
		else:
			self.ties1 += 1
			self.ties2 += 1

		self.score += score
		self.history1.append(move1)
		self.history2.append(move2)
		self.score_history.append(score)
		self.played += 1

		return score

	def finalize(self, errors=False, error_string=""):
		"""Called once a contest is complete to do some final bookkeeping.
This is REQUIRED if multiprocessing features are in use."""
		# the bots must be reset before being passed between workers
		# see comments under Bot.reset()
		self.bot1.reset()
		self.bot2.reset()

		self.errors = errors
		self.error_string = error_string
		self.history1 = "".join(self.history1)
		self.history2 = "".join(self.history2)
		self.end_time = time.time()
		self.run_time = self.end_time - self.start_time

		if self.wins1 > self.wins2:
			self.winner = self.bot1
			self.loser = self.bot2
		elif self.wins1 < self.wins2:
			self.winner = self.bot2
			self.loser = self.bot1

		self.finalized = True

	def __str__(self):
		game = "%s vs %s:" % (self.bot1.name, self.bot2.name)
		if self.bot1_disqualified:
			return "%s bot 1 disqualified" % game
		elif self.bot2_disqualified:
			return "%s bot 2 disqualified" % game
		elif self.finalized:
			return "%s score %d, took %.2f seconds" % \
					(game, self.score, self.run_time)
		else:
			return "%s score %d -- not final" % (game, self.score)


class Contest:
	"""Contest object handles running a contest between two sets of bots."""
	def __init__(self, bot1, bot2, rounds=1000):
		self.bot1 = bot1
		self.bot2 = bot2
		self.rounds = rounds
		self.result = ContestResult(bot1, bot2)

		# isolate random number generator
		r1 = random.random()
		r2 = random.random()
		base_rng = random.getstate()

		random.seed(r1)
		self.bot1_rng = random.getstate()

		random.seed(r2)
		self.bot2_rng = random.getstate()

		random.setstate(base_rng)

	def run(self):
		"""Runs the configured contest and reports a ContestResult"""
		self.result.start()

		base_rng = random.getstate()
		input1 = input2 = output1 = output2 = ""
		errors = False
		error_string = ""
		for i in xrange(self.rounds):
			random.setstate(self.bot1_rng)
			try:
				output1 = self.bot1.get_move(input1)
			except KeyboardInterrupt:
				raise
			except:
				exc_type, exc_value, exc_traceback = sys.exc_info()
				exc_string = "".join(traceback.format_exception(exc_type,
					exc_value, exc_traceback))
				error_string = "Error from %s\n%s" % (self.bot1.name,
						exc_string)
				errors = True
				self.result.bot1_disqualified = True
			else:
				if output1 not in "RPS":
					errors = True
					self.result.bot1_disqualified = True
					error_string = "bot1 did not make a valid move"
			self.bot1_rng = random.getstate()

			random.setstate(self.bot2_rng)
			try:
				output2 = self.bot2.get_move(input2)
			except KeyboardInterrupt:
				raise
			except:
				exc_type, exc_value, exc_traceback = sys.exc_info()
				exc_string = "".join(traceback.format_exception(exc_type,
					exc_value, exc_traceback))
				error_string = "Error from %s\n%s" % (self.bot1.name,
						exc_string)
				errors = True
				self.result.bot2_disqualified = True
			else:
				if output2 not in "RPS":
					errors = True
					self.result.bot2_disqualified = True
					error_string = "bot2 did not make a valid move"
			self.bot2_rng = random.getstate()

			if errors:
				break

			self.result.score_moves(output1, output2)
			input1 = output2
			input2 = output1

			# TODO add early bail out like official contest

		self.result.finalize(errors=errors, error_string=error_string)

		random.setstate(base_rng)
		return self.result

### Main program logic

def load_bots(names, desc=None, bot_obj=Bot):
	"""Initializes several Bot objects given a list of filenames.
desc is an optional output string."""

	bots = []
	for name in names:
		bots.append(bot_obj(name))
	if desc is not None:
		print "%s:" % (desc),
	print "%d bots loaded" % len(bots)
	return bots


def match_maker(bots, bots2=None, matches=1, rounds=1000):
        """generates matches between all the bots in bots or in the union of
bots and bots2.  matches specifies the number of matches played for each
pairing.  a bot will never play itself."""
	if not bots:
		raise Exception("Must specify bots")
	if not bots2:
		for i in xrange(len(bots)):
			bot1 = bots[i]
			for j in xrange(i+1, len(bots)):
				bot2 = bots[j]
				if bot1 == bot2:
					continue
				for k in xrange(matches):
					# TODO modify contest to allow for multiple matches?
					yield Contest(bot1, bot2, rounds)
	else:
		for bot1 in bots:
			for bot2 in bots2:
				if bot1 == bot2:
					continue
				for i in xrange(matches):
					# TODO modify contest to specify multiple matches?
					yield Contest(bot1, bot2, rounds)

def report_results(bots, results):
	"""Summarizes a list of ContestResults"""
	# TODO this is ugly, streamline.

	botnames = [i.name for i in bots]
	matches_played = dict.fromkeys(botnames, 0)
	matches_won = dict.fromkeys(botnames, 0)
	scores = dict.fromkeys(botnames, 0)
	rounds_won = dict.fromkeys(botnames, 0)
	rounds_played = dict.fromkeys(botnames, 0)
	bot_results = dict(zip(botnames, [list() for i in botnames]))

	for result in results:
		if result.errors:
			print "errors in contest:", result
			print result.error_string

		matches_played[ result.bot1.name ] += 1
		matches_played[ result.bot2.name ] += 1
		if result.winner is not None:
			matches_won[ result.winner.name ] += 1

		scores[ result.bot1.name ] += result.score
		scores[ result.bot2.name ] -= result.score # invert score for bot2

		rounds_won[ result.bot1.name ] += result.wins1
		rounds_won[ result.bot2.name ] += result.wins2
		rounds_played[ result.bot1.name ] += result.played
		rounds_played[ result.bot2.name ] += result.played

	# sort results for output - sort list by 
	win_ratio = dict(zip(botnames, 
		map(lambda x: float(matches_won[x]) / matches_played[x], botnames)))
	botnames.sort(lambda x,y: cmp(win_ratio[y], win_ratio[x]))

	print
	for bot in botnames:
		# float casting is necessary below, because we can import division
		# from __future__; that causes some of the bots to misbehave who
		# are not expecting it.
		print "%s: won %.1f%% of matches (%d of %d)\n" \
			  "	won %.1f%% of rounds (%d of %d)\n" \
			  "	avg score %.1f, net score %.1f\n" % \
			  (bot, float(matches_won[bot]) / matches_played[bot] * 100,
					  matches_won[bot], matches_played[bot],
					  float(rounds_won[bot]) / rounds_played[bot] * 100,
					  rounds_won[bot], rounds_played[bot],
					  float(scores[bot]) / matches_played[bot],
					  scores[bot])

def runner(contest):
	"""Contest wrapper, needed for multiprocessing implementation"""
	try:
		result = contest.run()
	except KeyboardInterrupt:
		# need to raise a non-keyboard interrupt error here to get
		# the pool to die cleanly.
		# XXX Is there a better way to handle this?
		raise Exception("Got Keyboard Interrupt!")
	return result

def pool_start(threads):
	"""Starts a worker pool and returns that pool"""
	if Pool is None or threads == 1:
		raise Exception("Invalid configuration for worker threads")
	return Pool(processes=threads)

def pool_stop(pool):
	"""Stops a worker pool."""
	pool.close()
	pool.join()

def run_contests(contests, threads):
	"""Runs through a set of contests, using multiprocessing if available
contests must be iterable return Contest objects."""
	# TODO instead of passing contests directly into pool.map, we should
	# use a multi process queue of some kind that is fed into by the
	# parent process
	# TODO process results real time through a callback or something?
	print "Running matches in", threads, "threads"
	results = []
	if Pool is not None and threads != 1:
		pool = pool_start(threads)
		results = pool.map(runner, contests)
		pool_stop(pool)
	else:
		for contest in contests:
			results.append(contest.run())
	return results

def low_priority():
	"""Sets process (and its children) to have a very low priority."""
	if WINDOWS:
		import win32api, win32con, win32process
		pid = win32api.GetCurrentProcessId()
		handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
		win32process.SetPriorityClass(handle, win32process.IDLE_PRIORITY_CLASS)
	else:
		os.nice(19)

def usage(msg, exit=0):
	print """
Rock-Paper-Scissors Runner v%s (http://www.rpscontest.com/)
   rpsrunner.py [options] <POOL1> [POOL2]
   rpsrunner.py [options] bot1.py bot2.py bot3.py

   Options:
	 -h|--help		 Print this usage output
	 -l|--low		  Run the process at a lower priority to keep the
					   system responsive.
	 -m|--matches <N>  How many matches to play for each pairing [def: %d]
	 -r|--rounds <N>   How many rounds to play for each pairing [def: %d]
	 -t|--threads <N>  How many execution threads to use [def: %d]
		The multiprocessing module must be available to use more than one
		execution thread.  On this host, multiprocessing is: %s

	Additional arguments:

	  Pool format:	bot1.py,bot2.py[,bot3.py,...]
	  or		 :	"bot*.py"

	You must specify at least two bot files in one or two pools.  If one
	pool is specified, all bots in that pool will play against every other
	bot for the number of matches specified.

	If two pools are specified, all the bots in each pool will play all the
	bots in the other pool.

	Example:
		rpsrunner.py -t 4 -m 100 mybot.py 'rpsbots/*.py'
		rpsrunner.py mybot1.py,mybot2.py 'rpsbots/*.py'

NOTE: Bots run through this script have full access to the Python
interpreter, so they could use it to do all sorts of nasty things to your
computer.  You must review the code for any bot you want to run, and if
you're not sure what the bot does, then you shouldn't run it.""" % \
	(VERSION, MATCHES, ROUNDS, POOL_SIZE,
		Pool is not None and "AVAILABLE" or "UNAVAILABLE")
	if msg:
		print "\n\n%s" % msg
	return exit


def main(prog_args):
	# defaults
	matches = MATCHES
	rounds = ROUNDS
	threads = POOL_SIZE
	set_low_priority = False

	try:
		opts, args = getopt.getopt(prog_args, "ht:m:r:l",
				["help", "threads", "matches", "rounds", "low"])
	except getopt.GetoptError, e:
		return usage(str(e), exit=2)

	for o, a in opts:
		if o in ("-t", "--threads"):
			try:
				threads = int(a)
			except:
				return usage("Threads must be a positive integer")
			if threads < 1:
				return usage("Threads must be a positive integer")
			elif threads > 1 and Pool is None:
				return usage("Thread count must be 1 if multiprocessing is " \
						"unavailable.", exit=1)
		elif o in ("-l", "--low"):
			set_low_priority = True
		elif o in ("-m", "--matches"):
			try:
				matches = int(a)
			except:
				return usage("Matches must be a positive integer")
			if matches < 1:
				return usage("Matches must be a positive integer")
		elif o in ("-r", "--rounds"):
			try:
				rounds = int(a)
			except:
				return usage("Rounds must be a positive integer")
			if rounds < 1:
				return usage("Rounds must be a positive integer")
		elif o in ("-h", "--help"):
			return usage("", exit=0)
		else:
			return usage("Unknown option: %s" % o)

	if len(args) == 0:
		return usage("Must specify at least two bots.")
	if len(args) > 2:
		return usage("Must only specify two bot pools.")

	if set_low_priority:
		print "Setting low priority"
		low_priority()

	# load bot data
	bots1_files = []
	bots2_files = []

	if "*" in args[0]:
		bots1_files = glob.glob(args[0])
	else:
		bots1_files = args[0].split(",")

	if len(args) > 1:
		if "*" in args[1]:
			bots2_files = glob.glob(args[1])
		else:
			bots2_files = args[1].split(",")

	# unique the bot list and ensure there are at least two (or match_maker
	# will misbehave.)
	checkbots = dict.fromkeys(bots1_files + bots2_files)
	if len(checkbots.keys()) < 2:
		return usage("Must specify at least two distinct bots.")

	bots1 = load_bots(bots1_files, "Pool 1")
	bots2 = []
	if bots2_files:
		bots2 = load_bots(bots2_files, "Pool 2")

	# run contests
	print "Playing %d matches per pairing." % matches
	start_time = time.time()
	contests = match_maker(bots1, bots2, matches=matches, rounds=rounds)
	results = run_contests(contests, threads)
	end_time = time.time()

	print "%d matches run" % len(results)
	print "total run time: %.2f seconds" % (end_time - start_time)
	report_results(bots1+bots2, results)

	return 0

if __name__ == "__main__":
	sys.exit( main(sys.argv[1:]))
