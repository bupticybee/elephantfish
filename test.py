#!/usr/bin/env pypy
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import re
import sys
import time
import subprocess
import signal
import argparse
import importlib
import itertools
import multiprocessing
import random
import unittest
import warnings

import elephantfish
import tools

###############################################################################
# Benchmarking
###############################################################################

def benchmark(cnt=20, depth=3):
    path = os.path.join(os.path.dirname(__file__), 'data/fen/random_openings.fen')
    random.seed(0)
    start = time.time()
    nodes = 0
    for i, line in enumerate(random.sample(list(open(path)), cnt)):
        pos = tools.parseFEN(line)
        searcher = elephantfish.Searcher()
        start1 = time.time()
        for search_depth, _, _ in searcher.search(pos):
            speed = int(round(searcher.nodes/(time.time()-start1 + 1e-6)))
            print('Benchmark: {}/{}, Depth: {}, Speed: {:,}N/s'.format(
                i+1, cnt, search_depth, speed), end='\r')
            sys.stdout.flush()
            if search_depth == depth:
                nodes += searcher.nodes
                break
    print()
    total_time = time.time() - start
    speed = int(round(nodes/total_time))
    print('Total time: {}, Total nodes: {}, Average speed: {:,}N/s'.format(
        total_time, nodes, speed))


###############################################################################
# Playing test
###############################################################################

def selfplay(secs=1):
    """ Start a game elephantfish vs. elephantfish """
    pos = tools.parseFEN(tools.FEN_INITIAL)
    for d in range(200):
        # Always print the board from the same direction
        board = pos.board if d % 2 == 0 else pos.rotate().board
        print(pos.score)
        print(' '.join(board))
        m, _, _ = tools.search(elephantfish.Searcher(), pos, secs)
        if m is None:
            print("Game over")
            break
        print("\nmove", tools.mrender(pos, m))
        pos = pos.move(m)

def self_arena(version1, version2, games, secs, plus):
    print('Playing {} games of {} vs. {} at {} secs/game + {} secs/move'
            .format(games, version1, version2, secs, plus))
    openings_file = os.path.join(os.path.dirname(__file__), 'data/fen/random_openings.fen')
    openings = random.sample(list(open(openings_file)), games)
    pool = multiprocessing.Pool()
    instances = [random.choice([
        (version1, version2, secs, plus, fen),
        (version2, version1, secs, plus, fen),
        ]) for fen in openings]
    wins = 0
    losses = 0
    for i, r in enumerate(pool.imap_unordered(play, instances)):
        if r is None:
            print('-', end='', flush=True)
        if r == version1:
            wins += 1
            print('w', end='', flush=True)
        if r == version2:
            losses += 1
            print('l', end='', flush=True)
        if i % 80 == 79:
            print()
            print('{} wins, {} draws, {} losses out of {}'.format(wins,i+1-wins-losses,losses,i+1))
    print()

    print('Result: {} wins, {} draws, {} losses out of {}'.format(wins,games-wins-losses,losses,games))


def play(version1_version2_secs_plus_fen):
    ''' returns 1 if fish1 won, 0 for draw and -1 otherwise '''
    version1, version2, secs, plus, fen = version1_version2_secs_plus_fen
    modules = [importlib.import_module(version1), importlib.import_module(version2)]
    searchers = []
    for module in modules:
        if hasattr(module, 'Searcher'):
            searchers.append(module.Searcher())
        else: searchers.append(module)
    times = [secs, secs]
    efactor = [1, 1]
    pos = tools.parseFEN(fen)
    seen = set()
    for d in range(200):
        moves_remain = 30
        use = times[d%2]/moves_remain + plus
        # Use a bit more time, if we have more on the clock than our opponent
        use += (times[d%2] - times[(d+1)%2])/10
        use = max(use, plus)
        t = time.time()
        m, score, depth = tools.search(searchers[d%2], pos, use*efactor[d%2])
        efactor[d%2] *= (use/(time.time() - t + 1e-3))**.5
        times[d%2] -= time.time() - t
        times[d%2] += plus
        #print('Used {:.2} rather than {:.2}. Off by {:.2}. Remaining: {}'
            #.format(time.time()-t, use, (time.time()-t)/use, times[d%2]))
        if times[d%2] < 0:
            print('{} ran out of time'.format(version2 if d%2 == 1 else version1))
            return version1 if d%2 == 1 else version2
            pass

        if m is None:
            name = version1 if d%2 == 0 else version2
            print('Game not done, but no move? Score', score)
            print(version1, tools.renderFEN(pos))
            return version2 if d%2 == 0 else version1
            #assert False

        # Test move
        is_dead = lambda pos: any(pos.value(m) >= elephantfish.MATE_LOWER for m in pos.gen_moves())
        if is_dead(pos.move(m)):
            name = version1 if d%2 == 0 else version2
            print('{} made an illegal move {} in position {}. Depth {}, Score {}'.
                    format(name, tools.mrender(pos,m), tools.renderFEN(pos), depth, score))
            return version2 if d%2 == 0 else version1
            #assert False

        # Make the move
        pos = pos.move(m)

        # Test repetition draws
        # This is by far the most common type of draw
        if pos in seen:
            #print('Rep time at end', times)
            return None
        seen.add(pos)

        any_moves = not all(is_dead(pos.move(m)) for m in pos.gen_moves())
        in_check = is_dead(pos.nullmove())
        if not any_moves:
            if not in_check:
                # This is actually a bit interesting. Why would we ever throw away a win like this?
                name = version1 if d%2 == 0 else version2
                print('{} stalemated? depth {} {}'.format(
                    name, depth, tools.renderFEN(pos)))
                if score != 0:
                    print('it got the wrong score: {} != 0'.format(score))
                return None
            else:
                name = version1 if d%2 == 0 else version2
                if score < elephantfish.MATE_LOWER:
                    print('{} mated, but did not realize. Only scored {} in position {}, depth {}'.format(name, score, tools.renderFEN(pos), depth))
                return name
    print('Game too long', tools.renderFEN(pos))
    return None


###############################################################################
# Perft test
###############################################################################

def allperft(f, depth=4, verbose=True):
    import gc
    lines = f.readlines()
    for d in range(1, depth+1):
        if verbose:
            print("Going to depth {}/{}".format(d, depth))
        for line in lines:
            parts = line.split(';')
            if len(parts) <= d:
                continue
            if verbose:
                print(parts[0])

            pos, score = tools.parseFEN(parts[0]), int(parts[d])
            res = sum(1 for _ in tools.collect_tree_depth(tools.expand_position(pos), d))
            if res != score:
                print('=========================================')
                print('ERROR at depth %d. Gave %d rather than %d' % (d, res, score))
                print('=========================================')
                print(tools.renderFEN(pos,0))
                for move in pos.gen_moves():
                    split = sum(1 for _ in tools.collect_tree_depth(tools.expand_position(pos.move(move)),1))
                    print('{}: {}'.format(tools.mrender(pos, move), split))
                return False
        if verbose:
            print('')
    return True

###############################################################################
# Generate some random opening
###############################################################################
def random_move(pos):
    moves = []
    for one_move in pos.gen_moves():
        moves.append(one_move)
    return random.choice(moves)

def generate_random_opening():
    pos = tools.parseFEN(tools.FEN_INITIAL)
    steps = 6
    for i in range(steps):
        pos = pos.move(random_move(pos))
    return pos

def main():
    # test fen
    pos = tools.parseFEN(tools.FEN_INITIAL)
    assert(pos.board == elephantfish.initial)
    fen = tools.renderFEN(pos)
    assert(fen == tools.FEN_INITIAL)

    benchmark(5,6)

    self_arena("elephantfish", "algorithms.elephantfish_improve",100 , 20, .1)

# Old Python compatability
if sys.version_info < (3,5):
    old_print = print
    def print(*args, **kwargs):
        flush = kwargs.get('flush', False)
        if 'flush' in kwargs:
            del kwargs['flush']
        old_print(*args, **kwargs)
        if flush:
            file = kwargs.get('file', sys.stdout)
            file.flush()

if __name__ == '__main__':
    main()

