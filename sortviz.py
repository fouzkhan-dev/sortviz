#!/usr/bin/env python3
"""
sortviz — watch sorting algorithms race in your terminal. 📊

Animated ASCII-bar visualizer for classic sorts, built as a study
companion for Data Structures (CS-511).

Usage:
    python sortviz.py                          # bubble sort, 30 bars
    python sortviz.py --algo quick --size 50
    python sortviz.py --algo merge --order reversed --speed 5
    python sortviz.py --bench                  # race every algorithm
    python sortviz.py --bench --size 200       # bigger race, no animation

No dependencies — pure Python 3. 🐍
"""

import argparse
import random
import sys
import time

# ── colors ──────────────────────────────────────────────────────────────
USE_COLOR = sys.stdout.isatty()

C_CYAN = "\033[96m" if USE_COLOR else ""
C_YELLOW = "\033[93m" if USE_COLOR else ""
C_RED = "\033[91m" if USE_COLOR else ""
C_GREEN = "\033[92m" if USE_COLOR else ""
C_DIM = "\033[2m" if USE_COLOR else ""
C_RESET = "\033[0m" if USE_COLOR else ""

BAR = "█"
MAX_WIDTH = 46


def bar_str(value, lo, hi, color):
    width = max(1, round((value - lo) / max(1, hi - lo) * MAX_WIDTH))
    return f"{color}{BAR * width}{C_RESET} {C_DIM}{value:>3}{C_RESET}"


class Viz:
    """Renders the array as animated bars and counts operations."""

    def __init__(self, n, delay, animate=True):
        self.n = n
        self.delay = delay
        self.animate = animate
        self.comparisons = 0
        self.swaps = 0
        self._drawn = False

    def draw(self, a, hi=(), swapped=(), done=False):
        if not self.animate:
            return
        lo, hi_v = min(a), max(a)
        lines = []
        for i, v in enumerate(a):
            if done:
                color = C_GREEN
            elif i in swapped:
                color = C_RED
            elif i in hi:
                color = C_YELLOW
            else:
                color = C_CYAN
            lines.append(bar_str(v, lo, hi_v, color))
        if self._drawn:
            sys.stdout.write(f"\033[{self.n}A")
        sys.stdout.write("\n".join(lines) + "\n")
        sys.stdout.flush()
        self._drawn = True
        if self.delay:
            time.sleep(self.delay)

    def compare(self, a, i, j):
        self.comparisons += 1
        self.draw(a, hi=(i, j))

    def swap(self, a, i, j):
        self.swaps += 1
        a[i], a[j] = a[j], a[i]
        self.draw(a, swapped=(i, j))

    def write(self, a, i, val):
        self.swaps += 1  # count writes (merge sort) as moves
        a[i] = val
        self.draw(a, swapped=(i,))

    def finish(self, a):
        self.draw(a, done=True)


# ── algorithms (each takes the array + viz, sorts in place) ─────────────
def bubble_sort(a, v):
    n = len(a)
    for end in range(n - 1, 0, -1):
        moved = False
        for i in range(end):
            v.compare(a, i, i + 1)
            if a[i] > a[i + 1]:
                v.swap(a, i, i + 1)
                moved = True
        if not moved:
            break


def selection_sort(a, v):
    n = len(a)
    for i in range(n - 1):
        m = i
        for j in range(i + 1, n):
            v.compare(a, j, m)
            if a[j] < a[m]:
                m = j
        if m != i:
            v.swap(a, i, m)
        else:
            v.draw(a, hi=(i,))


def insertion_sort(a, v):
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0:
            v.compare(a, j, j + 1)
            if a[j] <= key:
                break
            v.write(a, j + 1, a[j])
            j -= 1
        if j + 1 != i:
            v.write(a, j + 1, key)


def merge_sort(a, v):
    def merge(lo, mid, hi):
        left, right = a[lo:mid + 1], a[mid + 1:hi + 1]
        i = j = 0
        for k in range(lo, hi + 1):
            if j >= len(right) or (i < len(left) and left[i] <= right[j]):
                if i < len(left):
                    v.comparisons += 1
                v.write(a, k, left[i])
                i += 1
            else:
                v.comparisons += 1
                v.write(a, k, right[j])
                j += 1

    def rec(lo, hi):
        if lo < hi:
            mid = (lo + hi) // 2
            rec(lo, mid)
            rec(mid + 1, hi)
            merge(lo, mid, hi)

    rec(0, len(a) - 1)


def cocktail_sort(a, v):
    start, end = 0, len(a) - 1
    while start < end:
        moved = False
        for i in range(start, end):
            v.compare(a, i, i + 1)
            if a[i] > a[i + 1]:
                v.swap(a, i, i + 1)
                moved = True
        end -= 1
        if not moved:
            break
        moved = False
        for i in range(end, start, -1):
            v.compare(a, i - 1, i)
            if a[i - 1] > a[i]:
                v.swap(a, i - 1, i)
                moved = True
        start += 1
        if not moved:
            break


def quick_sort(a, v):
    def partition(lo, hi):
        pivot = a[hi]
        i = lo
        for j in range(lo, hi):
            v.compare(a, j, hi)
            if a[j] < pivot:
                if i != j:
                    v.swap(a, i, j)
                i += 1
        if i != hi:
            v.swap(a, i, hi)
        return i

    def rec(lo, hi):
        if lo < hi:
            p = partition(lo, hi)
            rec(lo, p - 1)
            rec(p + 1, hi)

    rec(0, len(a) - 1)


ALGOS = {
    "bubble": ("Bubble Sort", bubble_sort, "O(n²)"),
    "cocktail": ("Cocktail Sort", cocktail_sort, "O(n²)"),
    "selection": ("Selection Sort", selection_sort, "O(n²)"),
    "insertion": ("Insertion Sort", insertion_sort, "O(n²)"),
    "merge": ("Merge Sort", merge_sort, "O(n log n)"),
    "quick": ("Quick Sort", quick_sort, "O(n log n) avg"),
}

SPEED_DELAY = {1: 0.08, 2: 0.04, 3: 0.015, 4: 0.005, 5: 0.001}


def make_array(size, order):
    a = list(range(1, size + 1))
    if order == "random":
        random.shuffle(a)
    elif order == "reversed":
        a.reverse()
    elif order == "nearly":
        random.shuffle(a)
        a.sort()
        for _ in range(max(1, size // 10)):
            i, j = random.randrange(size), random.randrange(size)
            a[i], a[j] = a[j], a[i]
    return a  # "sorted" stays as-is


def cmd_watch(args):
    name, fn, bigo = ALGOS[args.algo]
    delay = SPEED_DELAY[args.speed]
    animate = sys.stdout.isatty() and not args.no_anim
    a = make_array(args.size, args.order)
    v = Viz(len(a), delay, animate=animate)
    v.draw(a)
    print(f"{C_DIM}▶ {name} {C_DIM}({bigo}) — {args.order}, n={args.size}{C_RESET}")
    t0 = time.perf_counter()
    fn(a, v)
    dt = (time.perf_counter() - t0) * 1000
    v.finish(a)
    print(f"{C_GREEN}✓ sorted{C_RESET}  "
          f"{C_DIM}comparisons:{C_RESET} {v.comparisons}  "
          f"{C_DIM}moves:{C_RESET} {v.swaps}  "
          f"{C_DIM}time:{C_RESET} {dt:.1f} ms")


def cmd_bench(args):
    base = make_array(args.size, args.order)
    rows = []
    for key, (name, fn, bigo) in ALGOS.items():
        a = base[:]
        v = Viz(len(a), 0, animate=False)
        t0 = time.perf_counter()
        fn(a, v)
        dt = (time.perf_counter() - t0) * 1000
        assert a == sorted(base), f"{name} failed to sort!"
        rows.append((name, bigo, v.comparisons, v.swaps, dt))
    rows.sort(key=lambda r: r[4])
    print(f"\n{C_YELLOW}🏁 benchmark — {args.order} array, n={args.size}{C_RESET}\n")
    print(f"  {'algorithm':<14}   {'complexity':<16}{'comparisons':>12}{'moves':>8}{'time':>12}")
    print(f"  {'─' * 14}   {'─' * 16}{'─' * 12}{'─' * 8}{'─' * 12}")
    for i, (name, bigo, comps, moves, dt) in enumerate(rows):
        medal = ["🥇", "🥈", "🥉"][i] if i < 3 else "  "
        print(f"  {name:<14} {medal} {bigo:<16}{comps:>12,}{moves:>8,}{dt:>10.1f} ms")
    print()


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="sortviz",
        description="Watch sorting algorithms race in your terminal 📊",
    )
    p.add_argument("--algo", choices=sorted(ALGOS), default="bubble",
                   help="which algorithm to visualize")
    p.add_argument("--size", type=int, default=30,
                   help="number of bars (1-100)")
    p.add_argument("--order", choices=["random", "sorted", "reversed", "nearly"],
                   default="random", help="starting arrangement")
    p.add_argument("--speed", type=int, choices=[1, 2, 3, 4, 5], default=3,
                   help="animation speed 1 (slow) – 5 (fast)")
    p.add_argument("--bench", action="store_true",
                   help="race all algorithms, print stats table (no animation)")
    p.add_argument("--no-anim", action="store_true",
                   help="skip animation, just sort and show stats")
    args = p.parse_args(argv)

    if not 1 <= args.size <= 100:
        raise SystemExit("❌ --size must be between 1 and 100")

    if args.bench:
        cmd_bench(args)
    else:
        cmd_watch(args)


if __name__ == "__main__":
    main()
