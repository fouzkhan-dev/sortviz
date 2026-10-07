# 📊 sortviz

Watch sorting algorithms **race in your terminal** — animated ASCII bars,
live comparison/move counters, and a benchmark mode. Built as a study
companion for **Data Structures (CS-511)**.

## 🚀 Run

```bash
python sortviz.py                            # bubble sort, 30 bars
python sortviz.py --algo quick --size 50     # quick sort, 50 bars
python sortviz.py --algo merge --order reversed --speed 5
python sortviz.py --bench                    # 🏁 race every algorithm
python sortviz.py --bench --size 100
```

## 🧠 What it does

| Flag | Purpose |
|------|---------|
| `--algo` | `bubble` `cocktail` `selection` `insertion` `merge` `quick` |
| `--size` | number of bars (1–100) |
| `--order` | `random` `sorted` `reversed` `nearly` starting arrangement |
| `--speed` | animation speed 1 (slow) – 5 (fast) |
| `--bench` | race all 5 on the same array, print stats table |
| `--no-anim` | skip animation, just sort + stats |

Bars light up 🟡 while comparing, 🔴 on swap/move, and 🟢 when sorted.

## 📝 Example

```
$ python sortviz.py --bench --size 100

🏁 benchmark — random array, n=100

  algorithm        complexity       comparisons   moves        time
  ──────────────   ────────────────────────────────────────────────
  Quick Sort     🥇 O(n log n) avg           620     250       0.2 ms
  Merge Sort     🥈 O(n log n)               672     672       0.3 ms
  Insertion Sort 🥉 O(n²)                  2,617   2,615       1.0 ms
  Selection Sort    O(n²)                  4,950      94       1.0 ms
  Cocktail Sort     O(n²)                  4,004   2,520       1.5 ms
  Bubble Sort       O(n²)                  4,905   2,520       1.8 ms
```

No dependencies — pure Python 3. 🐍

**Built by [Fouz Khan](https://github.com/fouzkhan-dev)** • BS AI, University of Layyah
