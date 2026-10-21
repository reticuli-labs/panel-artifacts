# Chomp brute force: position = tuple of row lengths, non-increasing, row 0 contains the poison at col 0.
# A move at (r,c) removes every square (r',c') with r'>=r and c'>=c. Taking (0,0) loses.
import functools, json, sys
sys.setrecursionlimit(10000)
@functools.lru_cache(maxsize=None)
def win(pos):
    # pos: tuple of row lengths (non-increasing), poison at (0,0). Player to move; True if forced win.
    if pos == (1,): return False          # only the poison left: you must take it and lose
    for r, L in enumerate(pos):
        for c in range(L):
            if r == 0 and c == 0: continue
            new = tuple(min(l, c) if i >= r else l for i, l in enumerate(pos))
            new = tuple(l for l in new if l > 0)
            if not win(new): return True
    return False
def winning_moves(rows, cols):
    pos = tuple([cols]*rows); out = []
    for r in range(rows):
        for c in range(cols):
            if r == 0 and c == 0: continue
            new = tuple(min(l, c) if i >= r else l for i, l in enumerate(pos)); new = tuple(l for l in new if l > 0)
            if not win(new): out.append((r+1, c+1))   # 1-indexed (row, col)
    return out
res = {}
for rows in range(1, 7):
    for cols in range(rows, 8):
        if rows * cols <= 1: continue
        wm = winning_moves(rows, cols); res[f"{rows}x{cols}"] = wm
        print(f"{rows}x{cols}: winning first moves {wm}")
json.dump({k: [list(m) for m in v] for k, v in res.items()}, open("chomp.json", "w"), indent=1)
