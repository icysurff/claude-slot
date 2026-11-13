"""
5x4 Slot, 1024 Ways, Wild-Respins mit Multiplikatoren und drei Freispiel-Modi.
Prototyp / Kalibrierung. Die Walzen werden von hier als CSV ins Math SDK exportiert
(python slot5x4.py export <zielordner>).

Alle Gewinne sind Vielfache des GESAMTEINSATZES (bet = 1.0). Die Paytable ist in
SDK-Einheiten (x Einsatz PRO WAY, nur Vielfache von 0.1, wie das SDK sie verlangt).

BASISSPIEL
  * 1024 Ways, links nach rechts, mind. 3 Walzen. Wilds nur auf Walze 2-4.
  * Jedes Wild traegt einen Multi (1x/2x/3x/5x). Gewinn-Multi eines Spins =
    SUMME der Multis aller am Gewinn beteiligten Wilds (1x zaehlt nicht).
  * RESPIN: Ein NEU gelandetes Wild, das an einem Gewinn beteiligt ist, loest
    einen Respin aus. Alle Wilds bleiben, der Rest dreht neu (max. MAX_RESPINS).
    Respin-Walzen enthalten keine Scatter.
  * 3/4/5 Scatter auf dem ersten Board -> NORMAL (10) / SUPER (7) / JACKPOT (10).

FREISPIELE
  * NORMAL : nur erhoehte Wilds (2x-10x), sticky bis zum Ende.
  * SUPER  : landende Wilds expandieren ueber die ganze Walze (oben/unten), sticky.
  * JACKPOT: Eine Kiste je Walze. Felder, die an einem Gewinn beteiligt waren,
             werden aktiviert; ist eine ganze Walze (4 Felder) aktiv, oeffnet
             sich die Kiste (Multi 2-10). Kisten-Multis werden NACHEINANDER
             multipliziert (nicht addiert) und gelten fuer alle weiteren Gewinne.

Aufruf:  python slot5x4.py [spins] [seed]       Kalibrierung / Report
         python slot5x4.py export <ordner>      Walzen als CSV exportieren
"""

import os
import random
import sys
from collections import defaultdict

# --------------------------------------------------------------------------
# Konfiguration
# --------------------------------------------------------------------------
REELS, ROWS = 5, 4
WILD, SCATTER = "W", "S"
PAYING = ["H1", "H2", "H3", "H4", "H5", "L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8"]
STRIP_LEN = 100

# x Gesamteinsatz PRO WAY; Schluessel = Anzahl Walzen (3/4/5); Vielfache von 0.1
PAYTABLE = {
    "H1": {3: 2.5, 4: 5.0, 5: 20.0},
    "H2": {3: 1.5, 4: 3.0, 5: 12.0},
    "H3": {3: 1.0, 4: 2.0, 5: 6.0},
    "H4": {3: 0.6, 4: 1.2, 5: 4.0},
    "H5": {3: 0.4, 4: 0.8, 5: 2.5},
    "L1": {3: 0.3, 4: 0.5, 5: 1.2},
    "L2": {3: 0.2, 4: 0.4, 5: 0.8},
    "L3": {3: 0.2, 4: 0.3, 5: 0.6},
    "L4": {3: 0.1, 4: 0.3, 5: 0.5},
    "L5": {3: 0.1, 4: 0.2, 5: 0.3},
    "L6": {3: 0.1, 4: 0.2, 5: 0.3},
    "L7": {3: 0.1, 4: 0.1, 5: 0.2},
    "L8": {3: 0.1, 4: 0.1, 5: 0.2},
}
SCATTER_PAY = {3: 1.0, 4: 5.0, 5: 25.0}      # x Gesamteinsatz, zahlt ueberall

# Multiplikator-Tabellen: (Wert, Gewicht)
WILD_MULT_BASE = [(1, 60), (2, 24), (3, 10), (5, 6)]
WILD_MULT_ENHANCED = [(2, 60), (3, 25), (5, 12), (10, 3)]      # Normal-Freispiele
WILD_MULT_SUPER = [(1, 35), (2, 35), (3, 20), (5, 10)]         # Super-Freispiele
CHEST_VALUES = [(2, 10), (3, 12), (4, 14), (5, 14), (6, 14),
                (7, 12), (8, 10), (9, 8), (10, 6)]

# Nur fuer gezielte Max-Win-Runden (SDK-Kriterium "wincap"): Kisten tendieren hoeher
CHEST_VALUES_WINCAP = [(2, 2), (3, 4), (4, 6), (5, 9), (6, 12),
                       (7, 15), (8, 17), (9, 17), (10, 18)]

# Ziel-Frequenzen der Feature-Trigger (im SDK ueber hr der Kriterien erzwungen)
TARGET_ODDS = {3: 1 / 140, 4: 1 / 900, 5: 1 / 22000}

MAX_RESPINS = 6
FREE_SPINS = {"normal": 10, "super": 7, "jackpot": 10}
MODE_BY_SCATTERS = {3: "normal", 4: "super", 5: "jackpot"}
MAX_WIN = 50000.0

# --------------------------------------------------------------------------
# Walzenbaender (je Walze: Anzahl Scatter, Anzahl Wilds; Rest nach SYM_WEIGHTS)
# --------------------------------------------------------------------------
SYM_WEIGHTS = {"H1": 3, "H2": 4, "H3": 5, "H4": 5, "H5": 6,
               "L1": 7, "L2": 8, "L3": 8, "L4": 9, "L5": 9, "L6": 9, "L7": 10, "L8": 10}


def strip_spec(scatters, wilds):
    """scatters/wilds: je 5 Zahlen (eine pro Walze)."""
    return {"S": scatters, "W": wilds}


STRIP_SPECS = {
    # Basisspiel: Scatter auf allen Walzen, Wilds nur auf 2-4
    "BR0": strip_spec([2, 3, 2, 3, 2], [0, 1, 1, 1, 0]),
    # Respin: keine Scatter, etwas mehr Wilds
    "RR0": strip_spec([0, 0, 0, 0, 0], [0, 2, 2, 2, 0]),
    # Normal-Freispiele (sticky erhoehte Wilds)
    "NFR": strip_spec([0, 0, 0, 0, 0], [0, 1, 1, 1, 0]),
    # Super-Freispiele (expandierende Wilds)
    "SFR": strip_spec([0, 0, 0, 0, 0], [0, 1, 1, 1, 0]),
    # Jackpot-Freispiele
    "JFR": strip_spec([0, 0, 0, 0, 0], [0, 6, 6, 6, 0]),
    # Jackpot "Wincap"-Walzen (nur fuer das SDK, gezielte Hoechstgewinn-Runden)
    "JWC": strip_spec([0, 0, 0, 0, 0], [0, 12, 12, 12, 0]),
}


def _spaced_positions(count, length, min_gap, rng, taken=()):
    """Gleichmaessig verteilte Positionen mit Mindestabstand (zyklisch)."""
    if count == 0:
        return []
    for _ in range(2000):
        base = rng.randrange(length)
        step = length / count
        pos = [int(round(base + i * step + rng.uniform(-step * 0.2, step * 0.2))) % length
               for i in range(count)]
        allp = sorted(pos + list(taken))
        gaps = [(allp[(i + 1) % len(allp)] - allp[i]) % length or length for i in range(len(allp))]
        if len(set(pos)) == count and len(set(pos) & set(taken)) == 0 and min(gaps) >= min_gap:
            return pos
    raise RuntimeError("Konnte Positionen nicht platzieren")


def build_strip(n_scatter, n_wild, rng):
    strip = [None] * STRIP_LEN
    sc = _spaced_positions(n_scatter, STRIP_LEN, 5, rng)
    for p in sc:
        strip[p] = SCATTER
    wl = _spaced_positions(n_wild, STRIP_LEN, 4, rng, taken=sc)
    for p in wl:
        strip[p] = WILD
    free = [i for i, s in enumerate(strip) if s is None]
    total_w = sum(SYM_WEIGHTS.values())
    syms = []
    for name, w in SYM_WEIGHTS.items():
        syms += [name] * max(1, round(len(free) * w / total_w))
    while len(syms) < len(free):
        syms.append(rng.choice(PAYING))
    syms = syms[:len(free)]
    best = None
    for _ in range(200):                      # moeglichst keine gleichen Nachbarn
        rng.shuffle(syms)
        trial = strip[:]
        for i, s in zip(free, syms):
            trial[i] = s
        bad = sum(trial[i] == trial[(i + 1) % STRIP_LEN] for i in range(STRIP_LEN))
        if best is None or bad < best[0]:
            best = (bad, trial)
        if bad == 0:
            break
    return best[1]


def build_all_strips(seed=2026):
    rng = random.Random(seed)
    out = {}
    for name, spec in STRIP_SPECS.items():
        out[name] = [build_strip(spec["S"][r], spec["W"][r], rng) for r in range(REELS)]
    return out


STRIPS = build_all_strips()


def export_reels(folder):
    os.makedirs(folder, exist_ok=True)
    for name, strips in STRIPS.items():
        with open(os.path.join(folder, f"{name}.csv"), "w", encoding="UTF-8") as f:
            for i in range(STRIP_LEN):
                f.write(",".join(strips[r][i] for r in range(REELS)) + "\n")
    print(f"{len(STRIPS)} Walzen-Dateien nach {folder} exportiert")


# --------------------------------------------------------------------------
# Hilfsfunktionen
# --------------------------------------------------------------------------
def pick(table, rng):
    values, weights = zip(*table)
    return rng.choices(values, weights)[0]


def draw_grid(strips, rng):
    """grid[reel][row], eine Stopp-Position pro Walze."""
    grid = []
    for strip in strips:
        stop = rng.randrange(STRIP_LEN)
        grid.append([strip[(stop + r) % STRIP_LEN] for r in range(ROWS)])
    return grid


def count_scatters(grid):
    return sum(col.count(SCATTER) for col in grid)


def evaluate(grid):
    """1024-Ways-Bewertung. Gibt (Gewinn ohne Multi, Gewinnfelder, Wild-Felder) zurueck."""
    total = 0.0
    win_cells, wild_cells = set(), set()
    for sym in PAYING:
        counts = []
        for r in range(REELS):
            c = sum(1 for s in grid[r] if s == sym or s == WILD)
            if c == 0:
                break
            counts.append(c)
        n = len(counts)
        if n < 3:
            continue
        ways = 1
        for c in counts:
            ways *= c
        total += PAYTABLE[sym][n] * ways
        for r in range(n):
            for row, s in enumerate(grid[r]):
                if s == sym or s == WILD:
                    win_cells.add((r, row))
                    if s == WILD:
                        wild_cells.add((r, row))
    return round(total, 2), win_cells, wild_cells


def wild_multiplier(wild_cells, wilds):
    """Summe der Multis aller beteiligten Wild-OBJEKTE (expandierte Walze zaehlt
    einmal). 1x-Wilds erhoehen nichts. Ohne Multi-Wild: 1."""
    seen, m = set(), 0
    for cell in wild_cells:
        obj, mult = wilds[cell]
        if obj in seen:
            continue
        seen.add(obj)
        if mult > 1:
            m += mult
    return m if m else 1


def register_new_wilds(grid, wilds, table, rng):
    """Gibt allen neu gelandeten Wilds einen Multi. Liefert die neuen Felder."""
    new = set()
    for r in range(REELS):
        for row in range(ROWS):
            if grid[r][row] == WILD and (r, row) not in wilds:
                wilds[(r, row)] = ((r, row), pick(table, rng))
                new.add((r, row))
    return new


# --------------------------------------------------------------------------
# Basisspiel inkl. Wild-Respins
# --------------------------------------------------------------------------
def play_base(rng):
    grid = draw_grid(STRIPS["BR0"], rng)
    scatters = count_scatters(grid)
    total = SCATTER_PAY[min(scatters, 5)] if scatters >= 3 else 0.0

    wilds = {}
    new = register_new_wilds(grid, wilds, WILD_MULT_BASE, rng)
    respins = 0
    while True:
        win, _, wcells = evaluate(grid)
        total += win * wild_multiplier(wcells, wilds)
        if win > 0 and (wcells & new) and respins < MAX_RESPINS:
            respins += 1
            grid = draw_grid(STRIPS["RR0"], rng)
            for (r, row) in wilds:               # Wilds festhalten
                grid[r][row] = WILD
            new = register_new_wilds(grid, wilds, WILD_MULT_BASE, rng)
            continue
        break
    return {"win": total, "respins": respins, "scatters": scatters}


# --------------------------------------------------------------------------
# Freispiele
# --------------------------------------------------------------------------
def play_normal(rng, spins=FREE_SPINS["normal"]):
    """Nur erhoehte Wilds (2x-10x), bleiben bis zum Ende stehen."""
    wilds, total = {}, 0.0
    for _ in range(spins):
        grid = draw_grid(STRIPS["NFR"], rng)
        register_new_wilds(grid, wilds, WILD_MULT_ENHANCED, rng)
        for (r, row) in wilds:
            grid[r][row] = WILD
        win, _, wcells = evaluate(grid)
        total += win * wild_multiplier(wcells, wilds)
    return total


def play_super(rng, spins=FREE_SPINS["super"]):
    """Landende Wilds expandieren ueber die ganze Walze und bleiben stehen."""
    wilds, expanded, total = {}, set(), 0.0
    for _ in range(spins):
        grid = draw_grid(STRIPS["SFR"], rng)
        for r in range(REELS):
            if r not in expanded and WILD in grid[r]:
                expanded.add(r)
                mult = pick(WILD_MULT_SUPER, rng)
                for row in range(ROWS):
                    wilds[(r, row)] = (("col", r), mult)
        for r in expanded:
            grid[r] = [WILD] * ROWS
        win, _, wcells = evaluate(grid)
        total += win * wild_multiplier(wcells, wilds)
    return total


def play_jackpot(rng, spins=FREE_SPINS["jackpot"], strips="JFR", chest_table=None):
    """Kisten unter den Walzen. Alle 4 Felder einer Walze gewinnen = Kiste auf.
    Kisten-Multis werden nacheinander multipliziert."""
    chest_table = chest_table or CHEST_VALUES
    activated, opened = set(), []
    running, total = 1, 0.0
    for _ in range(spins):
        grid = draw_grid(STRIPS[strips], rng)
        wilds = {}
        register_new_wilds(grid, wilds, WILD_MULT_BASE, rng)
        win, wcells_all, wcells = evaluate(grid)
        activated |= wcells_all
        for r in range(REELS):                      # Reihenfolge links -> rechts
            if r not in opened and all((r, row) in activated for row in range(ROWS)):
                opened.append(r)
                running *= pick(chest_table, rng)
        total += win * wild_multiplier(wcells, wilds) * running
        if total >= MAX_WIN:
            break
    return min(total, MAX_WIN), len(opened), running


# --------------------------------------------------------------------------
# Natuerliche Scatter-Wahrscheinlichkeit (nur zur Info) und Kalibrierung
# --------------------------------------------------------------------------
def natural_scatter_odds():
    """P(3), P(4), P(5) Scatter im ersten Board aus den Basis-Walzen -- exakt."""
    dist = [1.0]
    for strip in STRIPS["BR0"]:
        per = [0.0] * (ROWS + 1)
        for stop in range(STRIP_LEN):
            k = sum(1 for r in range(ROWS) if strip[(stop + r) % STRIP_LEN] == SCATTER)
            per[k] += 1.0 / STRIP_LEN
        new = [0.0] * (len(dist) + ROWS)
        for i, a in enumerate(dist):
            for k, b in enumerate(per):
                new[i + k] += a * b
        dist = new
    return {3: dist[3], 4: dist[4], 5: sum(dist[5:])}


def stats(values):
    n = len(values)
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    return mean, (var / n) ** 0.5


def estimate(n_base=300_000, n_mode=40_000, seed=1, odds=None):
    """Stratifiziert: Basisspiel (ohne Trigger) und jeder Feature-Modus werden einzeln
    gross simuliert und mit den ZIEL-Frequenzen gewichtet. So bleibt auch der seltene
    Jackpot-Anteil stabil. Trigger-Spiele zahlen zusaetzlich Scatter-Gewinn + ein
    normales Board (Naeherung: Basis-Mittelwert)."""
    rng = random.Random(seed)
    odds = odds or TARGET_ODDS

    wins, respin_spins, hits = [], 0, 0
    for _ in range(n_base):
        r = play_base(rng)
        if r["scatters"] >= 3:
            continue                                   # Trigger-Boards zaehlen im Modus
        wins.append(r["win"])
        hits += r["win"] > 0
        respin_spins += r["respins"] > 0
    base_mean, base_se = stats(wins)
    p_trig = sum(odds.values())

    modes = {}
    for name, k, fn in (("normal", 3, play_normal), ("super", 4, play_super),
                        ("jackpot", 5, lambda g: play_jackpot(g)[0])):
        vals = [min(MAX_WIN, fn(rng)) for _ in range(n_mode)]
        mean, se = stats(vals)
        total_avg = mean + base_mean + SCATTER_PAY[k]     # Bonus + Trigger-Board
        modes[name] = {"avg": total_avg, "se": se, "p": odds[k], "rtp": odds[k] * total_avg,
                       "rtp_se": odds[k] * se}
    rtp = (1 - p_trig) * base_mean + sum(m["rtp"] for m in modes.values())
    rtp_se = (((1 - p_trig) * base_se) ** 2 + sum(m["rtp_se"] ** 2 for m in modes.values())) ** 0.5
    return {"rtp": rtp, "rtp_se": rtp_se, "base": (1 - p_trig) * base_mean, "modes": modes,
            "hit": hits / len(wins), "respin": respin_spins / len(wins),
            "natural": natural_scatter_odds()}


def report(e):
    print(f"RTP gesamt:          {e['rtp']*100:.2f} %  (+/- {e['rtp_se']*100:.2f})")
    print(f"  Basisspiel+Respins {e['base']*100:.2f} %")
    for name, m in e["modes"].items():
        print(f"  {name:<8} Freispiele {m['rtp']*100:6.2f} %   Ziel-Frequenz 1:{1/m['p']:,.0f}   "
              f"Ø Runde {m['avg']:.1f}x (+/- {m['se']:.1f})")
    print(f"Trefferquote Basis:  {e['hit']*100:.1f} %   Respin-Frequenz: {e['respin']*100:.1f} % der Spins")
    nat = e["natural"]
    print("Natuerliche Scatter-Quoten der Walzen (Info): "
          + ", ".join(f"{k}x 1:{1/v:,.0f}" for k, v in nat.items()))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        export_reels(sys.argv[2] if len(sys.argv) > 2 else "reels")
    else:
        nb = int(sys.argv[1]) if len(sys.argv) > 1 else 300_000
        sd = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        report(estimate(nb, max(20_000, nb // 8), sd))
