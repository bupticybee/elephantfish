import itertools
import re
import time
import sys

import elephantfish

################################################################################
# This module contains functions used by test.py and xboard.py.
# Nothing from here is imported into sunfish.py which is entirely self-sufficient
################################################################################

# Sunfish doesn't have to know about colors, but for more advanced things, such
# as xboard support, we have to.
WHITE, BLACK = range(2)

FEN_INITIAL = 'rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1'

def search(searcher, pos, secs, history=()):
    """ This used to be in the Searcher class """
    start = time.time()
    for depth, move, score in searcher.search(pos, history):
        if time.time() - start > secs:
            break
    return move, score, depth


################################################################################
# Parse and Render moves
################################################################################

def gen_legal_moves(pos):
    ''' pos.gen_moves(), but without those that leaves us in check.
        Also the position after moving is included. '''
    for move in pos.gen_moves():
        pos1 = pos.move(move)
        if not can_kill_king(pos1):
            yield move, pos1

def can_kill_king(pos):
    # If we just checked for opponent moves capturing the king, we would miss
    # captures in case of illegal castling.
    return any(pos.value(m) >= elephantfish.MATE_LOWER for m in pos.gen_moves())

def mrender(pos, m):
    # Sunfish always assumes promotion to queen
    p = 'q' if elephantfish.A9 <= m[1] <= elephantfish.I9 and pos.board[m[0]] == 'P' else ''
    m = m if get_color(pos) == WHITE else (254-m[0], 254-m[1])
    return elephantfish.render(m[0]) + elephantfish.render(m[1]) + p

def mparse(color, move):
    m = (elephantfish.parse(move[0:2]), elephantfish.parse(move[2:4]))
    return m if color == WHITE else (254-m[0], 254-m[1])

################################################################################
# Parse and Render positions
################################################################################

def get_color(pos):
    ''' A slightly hacky way to to get the color from a elephantfish position '''
    return BLACK if pos.board.startswith('\n') else WHITE

def parseFEN(fen):
    """ Parses a string in Forsyth-Edwards Notation into a Position """
    board, color, _, __, ___, ____ = fen.split()
    board = re.sub(r'\d', (lambda m: '.'*int(m.group(0))), board)
    board = list((16*3 + 3)*' ' + '       '.join(board.split('/')) + (16*3 + 4)*' ')
    board[15::16] = ['\n']*16
    #if color == 'w': board[::10] = ['\n']*12
    #if color == 'b': board[9::10] = ['\n']*12
    board = ''.join(board)
    score = sum(elephantfish.pst[p][i] for i,p in enumerate(board) if p.isupper())
    score -= sum(elephantfish.pst[p.upper()][254-i] for i,p in enumerate(board) if p.islower())
    pos = elephantfish.Position(board, score)
    return pos if color == 'w' else pos.rotate()

def renderFEN(pos, half_move_clock=0, full_move_clock=1):
    color = 'wb'[get_color(pos)]
    if get_color(pos) == BLACK:
        pos = pos.rotate()
    board = '/'.join(pos.board.split())
    board = re.sub(r'\.+', (lambda m: str(len(m.group(0)))), board)
    castling = '-'
    ep = '-'
    clock = '{} {}'.format(half_move_clock, full_move_clock)
    return ' '.join((board, color, castling, ep, clock))

################################################################################
# Pretty print
################################################################################

def pv(searcher, pos, include_scores=True, include_loop=False):
    res = []
    seen_pos = set()
    color = get_color(pos)
    origc = color
    if include_scores:
        res.append(str(pos.score))
    while True:
        move = searcher.tp_move.get(pos)
        # The tp may have illegal moves, given lower depths don't detect king killing
        if move is None or can_kill_king(pos.move(move)):
            break
        res.append(mrender(pos, move))
        pos, color = pos.move(move), 1-color
        if pos in seen_pos:
            if include_loop:
                res.append('loop')
            break
        seen_pos.add(pos)
        if include_scores:
            res.append(str(pos.score if color==origc else -pos.score))
    return ' '.join(res)

################################################################################
# Bulk move generation
################################################################################

def expand_position(pos):
    ''' Yields a tree of generators [p, [p, [...], ...], ...] rooted at pos '''
    yield pos
    for _, pos1 in gen_legal_moves(pos):
        yield expand_position(pos1)

def collect_tree_depth(tree, depth):
    ''' Yields positions exactly at depth '''
    root = next(tree)
    if depth == 0:
        yield root
    else:
        for subtree in tree:
            for pos in collect_tree_depth(subtree, depth-1):
                yield pos

def flatten_tree(tree, depth):
    ''' Yields positions exactly at less than depth '''
    if depth == 0:
        return
    yield next(tree)
    for subtree in tree:
        for pos in flatten_tree(subtree, depth-1):
            yield pos

################################################################################
# Non chess related tools
################################################################################

# Disable buffering
class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream
    def write(self, data):
        self.stream.write(data)
        self.stream.flush()
        sys.stderr.write(data)
        sys.stderr.flush()
    def __getattr__(self, attr):
        return getattr(self.stream, attr)
