# -*- coding: utf-8 -*-
"""
Backtest mecánico de MSNR "Alchemist" en XAUUSD (oro spot) con RR mínimo 1:5.

Mismas reglas que msnr_backtest.py (TSLA), adaptadas a un mercado de casi 24 h:
  * Datos: velas de 1 minuto BID con spread real (Exness XAUUSDm + relleno Dukascopy),
    agregadas a 5 min (entrada) y 1 h (niveles y storyline).
  * Día de trading del oro: 18:00 a 17:00 Nueva York (pausa diaria 17:00-18:00).
  * Niveles en 1 h solo con cuerpos: A (alcista->bajista, resistencia), V (bajista->alcista,
    soporte) y GAP (cierre de un día de trading -> apertura del siguiente). Caducan a los 5 días.
  * Frescura: solo el primer toque. Storyline: última ruptura de cuerpo de 1 h (A arriba = alcista,
    V abajo = bajista). Solo se opera a favor.
  * Confirmación en 5 min: en las 6 velas siguientes al toque, una vela cierra más allá del extremo
    de la vela de toque. Entrada en la apertura de la vela siguiente.
  * Stop: extremo de la reacción ± 0,05 % (riesgo mínimo 0,15 %). Objetivo: N R (5R = RR 1:5).
  * Ventana de entradas: 03:00-15:00 NY (Londres + Nueva York). Cierre forzado 16:50 NY.
  * Costes: spread real. Largos compran al ASK (bid+spread) y salen al BID; cortos al revés.
    Si una vela toca stop y objetivo, cuenta como stop.
Uso: python3 msnr_xauusd.py XAUUSD_M1_2026.csv.gz
"""
import csv, gzip, sys, json, random, statistics as st, datetime as dt
from zoneinfo import ZoneInfo

NY, UTC = ZoneInfo("America/New_York"), dt.timezone.utc
SRC = sys.argv[1] if len(sys.argv) > 1 else "XAUUSD_M1_2026.csv.gz"

# ---------------------------------------------------------------- datos
m1 = []
for row in csv.DictReader(gzip.open(SRC, "rt")):
    u = dt.datetime.fromisoformat(row["time_utc"]).replace(tzinfo=UTC)
    m1.append((u, float(row["open"]), float(row["high"]), float(row["low"]), float(row["close"]),
               int(row["spread_points"]) * 0.001))

def to_ny(u):
    return u.astimezone(NY).replace(tzinfo=None)

def tday(t):  # día de trading: empieza a las 18:00 NY del día anterior
    return (t + dt.timedelta(hours=6)).date()

def agg(minutes):
    out = []
    for u, o, h, l, c, s in m1:
        k = u.replace(minute=(u.minute // minutes) * minutes, second=0) if minutes < 60 else u.replace(minute=0, second=0)
        if out and out[-1]["u"] == k:
            b = out[-1]; b["h"] = max(b["h"], h); b["l"] = min(b["l"], l); b["c"] = c; b["s"] = s
        else:
            out.append(dict(u=k, o=o, h=h, l=l, c=c, s=s))
    for b in out:
        b["t"] = to_ny(b["u"]); b["d"] = tday(b["t"])
    return out

bars = agg(5)
hourly = agg(60)
m1_by_5 = {}
for u, o, h, l, c, s in m1:
    m1_by_5.setdefault(u.replace(minute=(u.minute // 5) * 5, second=0), []).append((u, o, h, l, c, s))
days = sorted({b["d"] for b in bars})

# ---------------------------------------------------------------- niveles
levels = []
for a, b in zip(hourly, hourly[1:]):
    if b["u"] - a["u"] != dt.timedelta(hours=1) or a["d"] != b["d"]:
        continue
    up_a, up_b = a["c"] > a["o"], b["c"] > b["o"]
    lo, hi = sorted((a["c"], b["o"]))
    born = b["t"] + dt.timedelta(hours=1)
    if up_a and not up_b:
        levels.append(dict(kind="A", side="res", lo=lo, hi=hi, born=born))
    elif not up_a and up_b:
        levels.append(dict(kind="V", side="sup", lo=lo, hi=hi, born=born))
for da, db in zip(days, days[1:]):
    last = max((b for b in bars if b["d"] == da), key=lambda b: b["u"])
    first = min((b for b in bars if b["d"] == db), key=lambda b: b["u"])
    lo, hi = sorted((last["c"], first["o"]))
    if hi > lo:
        levels.append(dict(kind="GAP", side="sup" if first["o"] > last["c"] else "res", lo=lo, hi=hi,
                           born=first["t"] + dt.timedelta(minutes=5)))
for L in levels:
    w = L["lo"] * 0.0005
    if L["hi"] - L["lo"] < w:
        m = (L["lo"] + L["hi"]) / 2; L["lo"], L["hi"] = m - w / 2, m + w / 2
    L["dies"] = L["born"] + dt.timedelta(days=5)
levels.sort(key=lambda L: L["born"])

# ---------------------------------------------------------------- storyline precalculada
bias_after = []  # (momento en que se conoce, sesgo)
bias, j, live = None, 0, []
for hb in hourly:
    while j < len(levels) and levels[j]["born"] <= hb["t"]:
        live.append(levels[j]); j += 1
    live = [L for L in live if L["dies"] > hb["t"]]
    for L in live:
        if L["kind"] == "A" and hb["o"] <= L["hi"] < hb["c"]:
            bias = "up"
        elif L["kind"] == "V" and hb["o"] >= L["lo"] > hb["c"]:
            bias = "down"
    bias_after.append((hb["t"] + dt.timedelta(hours=1), bias))

def bias_at(t, _c=[0]):
    i = _c[0] if _c[0] < len(bias_after) and bias_after[_c[0]][0] <= t else 0
    last = None
    while i < len(bias_after) and bias_after[i][0] <= t:
        last = bias_after[i][1]; i += 1
    _c[0] = max(i - 1, 0)
    return last

# ---------------------------------------------------------------- motor
def in_window(t, w):
    return w[0] <= t.time() <= w[1]

def run(target_r=5.0, use_bias=True, sides=("long", "short"), window=(dt.time(3), dt.time(15)),
        flat=dt.time(16, 50), max_days=0, lo_t=None, hi_t=None):
    """max_days=0: cierre forzado intradía a `flat`. max_days>0: deja correr hasta N días."""
    bias_at.__defaults__[0][0] = 0
    fresh, j, trades, i, n = [], 0, [], 0, len(bars)
    while i < n:
        b = bars[i]; t = b["t"]
        while j < len(levels) and levels[j]["born"] <= t:
            fresh.append(levels[j]); j += 1
        if (lo_t and t < lo_t) or (hi_t and t > hi_t):
            i += 1; continue
        touched = [L for L in fresh if b["l"] <= L["hi"] and b["h"] >= L["lo"]]
        fresh = [L for L in fresh if L not in touched and L["dies"] > t]
        if not in_window(t, window) or not touched:
            i += 1; continue
        bz = bias_at(t) if use_bias else None
        took = False
        for L in touched:
            side = "long" if L["side"] == "sup" else "short"
            if side not in sides or (use_bias and bz != ("up" if side == "long" else "down")):
                continue
            ext = b["l"] if side == "long" else b["h"]
            for jj in range(i + 1, min(i + 7, n)):
                x = bars[jj]
                if x["d"] != b["d"] or not in_window(x["t"], window):
                    break
                ext = min(ext, x["l"]) if side == "long" else max(ext, x["h"])
                if (side == "long" and x["c"] < L["lo"]) or (side == "short" and x["c"] > L["hi"]):
                    break
                if not ((side == "long" and x["c"] > b["h"]) or (side == "short" and x["c"] < b["l"])):
                    continue
                if jj + 1 >= n or bars[jj + 1]["d"] != b["d"]:
                    break
                eb = bars[jj + 1]
                e = eb["o"] + eb["s"] if side == "long" else eb["o"]          # largo compra al ask
                stop = ext * (1 - 0.0005) if side == "long" else ext * (1 + 0.0005)
                risk = (e - stop) if side == "long" else (stop - e)
                if risk < e * 0.0015:
                    break
                tgt = e + target_r * risk if side == "long" else e - target_r * risk
                out, why, k = None, None, jj + 1
                end_day = eb["d"] + dt.timedelta(days=max_days) if max_days else None
                while k < n:
                    y = bars[k]
                    if not max_days and (y["d"] != eb["d"] or y["t"].time() >= flat and y["t"].time() < dt.time(18)):
                        out, why = (y["o"] if side == "long" else y["o"] + y["s"]), "cierre"; break
                    if max_days and y["d"] > end_day:
                        out, why = (y["o"] if side == "long" else y["o"] + y["s"]), "cierre"; break
                    hs = y["l"] <= stop if side == "long" else y["h"] + y["s"] >= stop
                    ht = y["h"] >= tgt if side == "long" else y["l"] + y["s"] <= tgt
                    if hs:
                        # hueco más allá del stop: se ejecuta a la apertura, no al stop
                        gap = (y["o"] < stop) if side == "long" else (y["o"] + y["s"] > stop)
                        out, why = ((y["o"] if side == "long" else y["o"] + y["s"]) if gap else stop), "stop"
                        amb = ht; break
                    if ht:
                        out, why, amb = tgt, "objetivo", False; break
                    k += 1
                if out is None:
                    out, why, k = bars[-1]["c"], "cierre", n - 1
                net = (out - e) if side == "long" else (e - out)
                trades.append(dict(date=str(eb["t"].date()), time=eb["t"].strftime("%H:%M"), side=side, level=L["kind"],
                                   entry=round(e, 3), stop=round(stop, 3), target=round(tgt, 3), exit=round(out, 3),
                                   why=why, R=round(net / risk, 3), risk_usd=round(risk, 2), spread=round(eb["s"], 3),
                                   ambiguous=bool(why == "stop" and amb), i_entry=jj + 1, i_exit=k))
                i = k; took = True; break
            if took:
                break
        i += 1
    return trades

def summary(tr, target_r):
    if not tr:
        return dict(n=0)
    Rs = [x["R"] for x in tr]
    eq = peak = dd = 0
    for v in Rs:
        eq += v; peak = max(peak, eq); dd = min(dd, eq - peak)
    w = [v for v in Rs if v > 0]; ls = [v for v in Rs if v <= 0]
    rnd = random.Random(19); boots = sorted(st.mean(rnd.choices(Rs, k=len(Rs))) for _ in range(5000))
    streak = cur = 0
    for v in Rs:
        cur = cur + 1 if v <= 0 else 0; streak = max(streak, cur)
    return dict(n=len(tr), win=round(100 * len(w) / len(tr), 1), breakeven_win=round(100 / (1 + target_r), 1),
                avgR=round(st.mean(Rs), 3), totalR=round(sum(Rs), 2),
                pf=round(sum(w) / -sum(ls), 2) if ls and sum(ls) < 0 else None, maxDD_R=round(dd, 2),
                worst_losing_streak=streak, ci90=(round(boots[250], 2), round(boots[4750], 2)),
                p_avgR_le_0=round(sum(1 for x in boots if x <= 0) / len(boots), 3),
                stop=sum(x["why"] == "stop" for x in tr), objetivo=sum(x["why"] == "objetivo" for x in tr),
                cierre=sum(x["why"] == "cierre" for x in tr), ambiguas=sum(x["ambiguous"] for x in tr))

# ---------------------------------------------------------------- verificación con velas de 1 minuto
def verify_m1(tr):
    """Rehace cada salida con velas de 1 min (resuelve las velas de 5 min ambiguas)."""
    out = []
    for x in tr:
        side, e, stop, tgt = x["side"], x["entry"], x["stop"], x["target"]
        risk = abs(e - stop); res = None
        for k in range(x["i_entry"], x["i_exit"] + 1):
            mins = m1_by_5.get(bars[k]["u"], [])
            for (u, o, h, l, c, s) in mins:
                if k == x["i_exit"] and x["why"] == "cierre":
                    break
                hs = l <= stop if side == "long" else h + s >= stop
                ht = h >= tgt if side == "long" else l + s <= tgt
                if hs:
                    res = "stop"; break
                if ht:
                    res = "objetivo"; break
            if res:
                break
        res = res or "cierre"
        R = x["R"] if res == x["why"] else (round(((tgt - e) if side == "long" else (e - tgt)) / risk, 3) if res == "objetivo" else -1.0)
        out.append(dict(x, why_m1=res, R_m1=R))
    return out

# ---------------------------------------------------------------- ejecución
T5 = 5
variants = {
    "A. MSNR completa 1:5 (storyline, largos+cortos, intradía)": dict(target_r=T5),
    "B. Solo largos 1:5": dict(target_r=T5, sides=("long",)),
    "C. Solo cortos 1:5": dict(target_r=T5, sides=("short",)),
    "D. Sin storyline 1:5": dict(target_r=T5, use_bias=False),
    "E. Solo sesión NY (08:00-15:00) 1:5": dict(target_r=T5, window=(dt.time(8), dt.time(15))),
    "F. 1:5 dejando correr hasta 3 días": dict(target_r=T5, max_days=3),
    "Ref. MSNR completa 1:2": dict(target_r=2),
}
res = dict(symbol="XAUUSD", source=SRC, first=str(days[0]), last=str(days[-1]), trading_days=len(days),
           bars5m=len(bars), bars1m=len(m1),
           levels={k: sum(L["kind"] == k for L in levels) for k in ("A", "V", "GAP")},
           buyhold_pct=round(100 * (bars[-1]["c"] / bars[0]["o"] - 1), 2), results={}, trades={})
for name, kw in variants.items():
    tr = run(**kw)
    res["results"][name] = summary(tr, kw["target_r"])
    res["trades"][name] = [{k: v for k, v in x.items() if not k.startswith("i_")} for x in tr]

# barrido de RR (estrategia completa)
res["rr_sweep"] = {f"1:{r}": summary(run(target_r=r), r) for r in (1, 2, 3, 4, 5, 6, 8)}

# comprobación 1: verificación con 1 minuto
base = run(target_r=T5)
v = verify_m1(base)
res["check_m1"] = dict(changed=sum(x["why_m1"] != x["why"] for x in v),
                       avgR_5m=round(st.mean(x["R"] for x in v), 3), avgR_1m=round(st.mean(x["R_m1"] for x in v), 3),
                       win_1m=round(100 * sum(x["R_m1"] > 0 for x in v) / len(v), 1))
# comprobación 2: mitades (fuera de muestra sencillo)
mid = bars[len(bars) // 2]["t"]
res["halves"] = {f"1ª mitad (hasta {mid.date()})": summary(run(target_r=T5, hi_t=mid), T5),
                 f"2ª mitad (desde {mid.date()})": summary(run(target_r=T5, lo_t=mid), T5)}
# comprobación 3: por trimestres
qs = {}
for x in base:
    qs.setdefault(x["date"][:7], []).append(x["R"])
res["by_month"] = {k: dict(n=len(v_), totalR=round(sum(v_), 2)) for k, v_ in sorted(qs.items())}
# comprobación 4: entradas aleatorias con el mismo stop/objetivo (¿aporta algo el nivel?)
def random_run(seed):
  rnd = random.Random(seed); rand_R = []
  for x in base:
    k = rnd.randrange(len(bars) - 300)
    while not in_window(bars[k]["t"], (dt.time(3), dt.time(15))):
        k = rnd.randrange(len(bars) - 300)
    side = rnd.choice(("long", "short")); eb = bars[k]
    risk = abs(x["entry"] - x["stop"]) / x["entry"] * eb["o"]
    e = eb["o"] + eb["s"] if side == "long" else eb["o"]
    stop = e - risk if side == "long" else e + risk; tgt = e + T5 * risk if side == "long" else e - T5 * risk
    out = None
    for y in bars[k:]:
        if y["d"] != eb["d"] or (y["t"].time() >= dt.time(16, 50) and y["t"].time() < dt.time(18)):
            out = y["o"] if side == "long" else y["o"] + y["s"]; break
        if (side == "long" and y["l"] <= stop) or (side == "short" and y["h"] + y["s"] >= stop):
            out = stop; break
        if (side == "long" and y["h"] >= tgt) or (side == "short" and y["l"] + y["s"] <= tgt):
            out = tgt; break
    rand_R.append(((out - e) if side == "long" else (e - out)) / risk)
  return st.mean(rand_R)

sims = sorted(random_run(s) for s in range(300))
strat = st.mean(x["R"] for x in base)
res["random_entries_same_risk"] = dict(
    note="300 carteras de 209 entradas al azar (hora y lado aleatorios) con el mismo riesgo % y objetivo 5R",
    median_avgR=round(sims[150], 3), p5=round(sims[15], 3), p95=round(sims[285], 3),
    strategy_avgR=round(strat, 3), pct_random_better=round(100 * sum(s >= strat for s in sims) / len(sims), 1))
res["last_trades_A"] = res["trades"][list(variants)[0]][-5:]

json.dump(res, open("msnr_xauusd_results.json", "w"), indent=1, ensure_ascii=False, default=str)
print(json.dumps({k: v for k, v in res.items() if k != "trades"}, indent=1, ensure_ascii=False, default=str))
