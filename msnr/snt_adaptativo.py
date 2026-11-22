# -*- coding: utf-8 -*-
"""
XAUUSD 2026: apuntes White SNT + Key level Classic A/V, con STOP y TAKE PROFIT ADAPTADOS AL MERCADO
(sin RR fijo). Entrada en M1, M5 y M15 ("todas las temporalidades") y versión combinada.

Igual que snt_xauusd.py (nivel Classic A/V H1-H4 fresco, storyline H1, barrido de liquidez,
MSS con cuerpo, entrada límite en el 0,764 del impulso, solo killzones, 2 pérdidas/día máx.),
pero:
  STOP  : detrás del barrido + colchón de 0,05 x ATR(H1,14). Se acepta si está entre
          0,15 x ATR y 1 x ATR de H1 (se adapta a la volatilidad del momento, sin tope en pips).
  TP1   : el extremo del impulso (nivel 0 del Fibo = liquidez interna). Debe dar al menos 1R.
  TP2   : la liquidez externa más cercana aún NO barrida más allá del TP1: swing high/low de H1
          o máximo/mínimo del día anterior (PDH/PDL). Si no hay ninguna antes de la extensión
          STD -4, se usa la STD -2 del impulso (apuntes: Standard Deviation).
  GESTIÓN (apuntes, "Cómo poner TP/SL"): 50 % se cierra en TP1 y el stop pasa a la entrada (BE);
          el otro 50 % va a TP2 o sale en BE.
  Las salidas se simulan SIEMPRE minuto a minuto (velas M1), con spread real.
  Cuenta: 100 $, 5 % del saldo por operación (y 1 % como comparación).
"""
import csv, gzip, sys, os, json, random, statistics as st, datetime as dt, math
from zoneinfo import ZoneInfo

NY, UTC = ZoneInfo("America/New_York"), dt.timezone.utc
SRC = sys.argv[1] if len(sys.argv) > 1 else "XAUUSD_M1_2026.csv.gz"
PIP = 0.10
FIB_ENTRY = 0.764
KZ = [(dt.time(2), dt.time(5)), (dt.time(7), dt.time(11)), (dt.time(13), dt.time(15))]
in_kz = lambda t: any(a <= t.time() < b for a, b in KZ)
ny = lambda u: u.astimezone(NY).replace(tzinfo=None)
tday = lambda t: (t + dt.timedelta(hours=6)).date()

M1 = []
for row in csv.DictReader(gzip.open(SRC, "rt")):
    u = dt.datetime.fromisoformat(row["time_utc"]).replace(tzinfo=UTC)
    M1.append((u, float(row["open"]), float(row["high"]), float(row["low"]), float(row["close"]), int(row["spread_points"]) * 0.001))
M1_T = [ny(r[0]) for r in M1]
M1_IDX = {r[0]: i for i, r in enumerate(M1)}

def agg(keyf):
    out = []
    for i, (u, o, h, l, c, s) in enumerate(M1):
        k = keyf(u)
        if out and out[-1]["k"] == k:
            b = out[-1]; b["h"] = max(b["h"], h); b["l"] = min(b["l"], l); b["c"] = c; b["s"] = max(b["s"], s); b["end"] = u; b["m1_hi"] = i
        else:
            out.append(dict(k=k, u=u, o=o, h=h, l=l, c=c, s=s, end=u, m1_lo=i, m1_hi=i))
    for b in out:
        b["t"] = ny(b["u"]); b["d"] = tday(b["t"]); b["tend"] = ny(b["end"]) + dt.timedelta(minutes=1)
    return out

H1 = agg(lambda u: u.replace(minute=0, second=0))
def h4key(u):
    t = ny(u); hh = t.hour - ((t.hour - 1) % 4)
    return (tday(t), (hh + 24) % 24)
H4 = agg(h4key)

# ---------------- ATR(H1,14) conocido en cada momento
atr_t, trs = [], []
for i, b in enumerate(H1):
    pc = H1[i - 1]["c"] if i else b["o"]
    trs.append(max(b["h"] - b["l"], abs(b["h"] - pc), abs(b["l"] - pc)))
    atr_t.append((b["tend"], st.mean(trs[-14:])))
def atr_at(t, _c=[0]):
    i = _c[0]
    if i >= len(atr_t) or atr_t[i][0] > t:
        i = 0
    while i + 1 < len(atr_t) and atr_t[i + 1][0] <= t:
        i += 1
    _c[0] = i
    return atr_t[i][1]

# ---------------- liquidez externa: swings H1 (fractal 2-2) y PDH/PDL
H1_SW = []   # (conocido_desde, tipo, precio, idx)
for p in range(2, len(H1) - 2):
    if all(H1[p]["h"] > H1[q]["h"] for q in (p - 2, p - 1, p + 1, p + 2)):
        H1_SW.append((H1[p + 2]["tend"], "H", H1[p]["h"], p))
    if all(H1[p]["l"] < H1[q]["l"] for q in (p - 2, p - 1, p + 1, p + 2)):
        H1_SW.append((H1[p + 2]["tend"], "L", H1[p]["l"], p))
DAY = {}
for b in H1:
    x = DAY.setdefault(b["d"], [b["h"], b["l"]]); x[0] = max(x[0], b["h"]); x[1] = min(x[1], b["l"])
DAYS = sorted(DAY)
H1_START = [b["t"] for b in H1]

def max_high_between(i0, t1):        # máximo / mínimo de H1 desde la vela i0+1 hasta t1
    hi, lo = -1e18, 1e18
    for b in H1[i0 + 1:]:
        if b["t"] >= t1:
            break
        hi, lo = max(hi, b["h"]), min(lo, b["l"])
    return hi, lo

def external_target(long, tp1, t, leg_size, leg_end):
    cands = []
    for known, kind, px, idx in H1_SW:
        if known > t or (t - known).days > 20:
            continue
        if long and kind == "H" and px > tp1:
            hi, _ = max_high_between(idx + 2, t)
            if hi < px: cands.append(px)
        if not long and kind == "L" and px < tp1:
            _, lo = max_high_between(idx + 2, t)
            if lo > px: cands.append(px)
    d = tday(t); prev = [x for x in DAYS if x < d]
    if prev:
        pdh, pdl = DAY[prev[-1]]
        if long and pdh > tp1: cands.append(pdh)
        if not long and pdl < tp1: cands.append(pdl)
    lim = leg_end + 4 * leg_size if long else leg_end - 4 * leg_size
    cands = [c for c in cands if (c <= lim if long else c >= lim)]
    if cands:
        return (min(cands) if long else max(cands)), "liquidez H1/PDH-PDL"
    return (leg_end + 2 * leg_size if long else leg_end - 2 * leg_size), "STD -2"

# ---------------- niveles Classic A / V y storyline (idéntico a snt_xauusd.py)
def classic(hb, tf, life):
    out = []
    for a, b in zip(hb, hb[1:]):
        if a["d"] != b["d"]:
            continue
        up_a, up_b = a["c"] > a["o"], b["c"] > b["o"]
        lo, hi = sorted((a["c"], b["o"]))
        if up_a and not up_b:
            out.append(dict(kind="A", tf=tf, side="res", lo=lo, hi=hi, born=b["tend"]))
        elif not up_a and up_b:
            out.append(dict(kind="V", tf=tf, side="sup", lo=lo, hi=hi, born=b["tend"]))
    for L in out:
        w = L["lo"] * 0.0002
        if L["hi"] - L["lo"] < w:
            m = (L["lo"] + L["hi"]) / 2; L["lo"], L["hi"] = m - w / 2, m + w / 2
        L["dies"] = L["born"] + dt.timedelta(days=life)
    return out
LEVELS = sorted(classic(H1, "H1", 5) + classic(H4, "H4", 10), key=lambda L: L["born"])
LV1 = [L for L in LEVELS if L["tf"] == "H1"]
BIAS_T, bias, j, live = [], None, 0, []
for hb in H1:
    while j < len(LV1) and LV1[j]["born"] <= hb["t"]:
        live.append(LV1[j]); j += 1
    live = [L for L in live if L["dies"] > hb["t"]]
    for L in live:
        if L["kind"] == "A" and hb["o"] <= L["hi"] < hb["c"]: bias = "up"
        elif L["kind"] == "V" and hb["o"] >= L["lo"] > hb["c"]: bias = "down"
    BIAS_T.append((hb["tend"], bias))

# ---------------- setups en una temporalidad de entrada
def setups(ltf):
    bars = agg(lambda u: u.replace(minute=u.minute // ltf * ltf, second=0)) if ltf < 60 else None
    N, WIN = len(bars), max(180 // ltf, 6)
    bias_bar, k, cur = [], 0, None
    for b in bars:
        while k < len(BIAS_T) and BIAS_T[k][0] <= b["t"]:
            cur = BIAS_T[k][1]; k += 1
        bias_bar.append(cur)
    sw_hi, sw_lo, lh, ll = [None] * N, [None] * N, None, None
    for i in range(N):
        p = i - 2
        if p >= 2 and p + 2 < N:
            if all(bars[p]["h"] > bars[q]["h"] for q in (p - 2, p - 1, p + 1, p + 2)): lh = (p, bars[p]["h"])
            if all(bars[p]["l"] < bars[q]["l"] for q in (p - 2, p - 1, p + 1, p + 2)): ll = (p, bars[p]["l"])
        sw_hi[i], sw_lo[i] = lh, ll
    out, fresh, j = [], [], 0
    for i in range(1, N):
        b = bars[i]; t = b["t"]
        while j < len(LEVELS) and LEVELS[j]["born"] <= t:
            fresh.append(LEVELS[j]); j += 1
        touched = [L for L in fresh if b["l"] <= L["hi"] and b["h"] >= L["lo"]]
        if touched or (i % 50 == 0):
            fresh = [L for L in fresh if L not in touched and L["dies"] > t]
        for L in touched:
            long = L["side"] == "sup"
            liq = sw_lo[i - 1] if long else sw_hi[i - 1]
            if liq is None:
                continue
            ext, ext_i, mss_i, w = (b["l"] if long else b["h"]), i, None, L["hi"] - L["lo"]
            for q in range(i, min(i + WIN + 1, N)):
                x = bars[q]
                if (long and x["l"] < ext) or (not long and x["h"] > ext):
                    ext, ext_i = (x["l"] if long else x["h"]), q
                if (long and x["c"] < L["lo"] - w) or (not long and x["c"] > L["hi"] + w):
                    break
                swept = ext < liq[1] if long else ext > liq[1]
                ref = sw_hi[q] if long else sw_lo[q]
                if swept and ref and ref[0] < ext_i and q > ext_i and ((long and x["c"] > ref[1]) or (not long and x["c"] < ref[1])):
                    mss_i = q; break
            if mss_i is None or bias_bar[mss_i] != ("up" if long else "down"):
                continue
            atr = atr_at(bars[mss_i]["t"])
            stop = ext - 0.05 * atr if long else ext + 0.05 * atr
            leg = bars[mss_i]["h"] if long else bars[mss_i]["l"]
            for q in range(mss_i + 1, min(mss_i + WIN + 1, N)):
                x = bars[q]
                entry = leg - FIB_ENTRY * (leg - ext) if long else leg + FIB_ENTRY * (ext - leg)
                risk = (entry - stop) if long else (stop - entry)
                if risk > atr:
                    break
                hit = (x["l"] + x["s"] <= entry) if long else (x["h"] >= entry)
                if hit:
                    if not in_kz(x["t"]) or risk < 0.15 * atr:
                        break
                    # minuto exacto del llenado
                    mi = None
                    for m in range(x["m1_lo"], x["m1_hi"] + 1):
                        u, o, h, l, c, s = M1[m]
                        if (long and l + s <= entry) or (not long and h >= entry):
                            mi = m; fill = min(entry, o + s) if long else max(entry, o); break
                    if mi is None:
                        break
                    r = (fill - stop) if long else (stop - fill)
                    tp1 = leg
                    if r <= 0 or ((tp1 - fill) if long else (fill - tp1)) < r:
                        break                                   # TP1 < 1R: no compensa
                    tp2, why2 = external_target(long, tp1, M1_T[mi], abs(leg - ext), leg)
                    out.append(dict(m1=mi, t=M1_T[mi], side="long" if long else "short", entry=fill, stop=stop,
                                    risk=r, tp1=tp1, tp2=tp2, tp2_src=why2, tf=f"M{ltf}", level=L["kind"] + "-" + L["tf"], atr=atr))
                    break
                if (long and x["l"] <= stop) or (not long and x["h"] >= stop):
                    break
                leg = max(leg, x["h"]) if long else min(leg, x["l"])
    return out

# ---------------- salida minuto a minuto con parciales
def run_exit(c, mode="parcial"):
    """mode: 'parcial' (50 % TP1 + BE + 50 % TP2), 'tp1' (todo en TP1), 'tp2' (todo a TP2, BE tras TP1)."""
    long = c["side"] == "long"; e, s0, r = c["entry"], c["stop"], c["risk"]
    tp1, tp2 = c["tp1"], c["tp2"]
    stop, got1, R = s0, False, 0.0
    for m in range(c["m1"], len(M1)):
        u, o, h, l, cl, sp = M1[m]
        first = m == c["m1"]
        bid_lo, ask_hi = l, h + sp
        hs = bid_lo <= stop if long else ask_hi >= stop
        if hs:
            gap = (not first) and ((o < stop) if long else (o + sp > stop))
            px = (o if long else o + sp) if gap else stop
            rr = ((px - e) if long else (e - px)) / r
            frac = 0.5 if (got1 and mode == "parcial") else 1.0
            R += frac * rr
            return R, m, ("BE" if got1 else "stop"), got1
        if first:
            continue
        h1 = (h >= tp1) if long else (l + sp <= tp1)
        h2 = (h >= tp2) if long else (l + sp <= tp2)
        if not got1 and h1:
            r1 = abs(tp1 - e) / r
            if mode == "tp1":
                return r1, m, "TP1", True
            if mode == "parcial":
                R += 0.5 * r1
            got1, stop = True, e
        if got1 and h2:
            r2 = abs(tp2 - e) / r
            R += (0.5 if mode == "parcial" else 1.0) * r2
            return R, m, "TP2", True
    u, o, h, l, cl, sp = M1[-1]
    px = cl if long else cl + sp
    R += (0.5 if (got1 and mode == "parcial") else 1.0) * ((px - e) if long else (e - px)) / r
    return R, len(M1) - 1, "abierta", got1

def simulate(cands, mode="parcial", max_losses_day=2):
    tr, busy, losses = [], -1, {}
    for c in sorted(cands, key=lambda x: x["m1"]):
        if c["m1"] <= busy:
            continue
        d = tday(c["t"])
        if losses.get(d, 0) >= max_losses_day:
            continue
        R, m, why, got1 = run_exit(c, mode)
        if R <= 0:
            losses[d] = losses.get(d, 0) + 1
        tr.append(dict(fecha=str(c["t"]), tf=c["tf"], lado=c["side"], nivel=c["level"], entrada=round(c["entry"], 2),
                       stop=round(c["stop"], 2), stop_pips=round(c["risk"] / PIP, 1), tp1=round(c["tp1"], 2),
                       tp1_R=round(abs(c["tp1"] - c["entry"]) / c["risk"], 2), tp2=round(c["tp2"], 2),
                       tp2_R=round(abs(c["tp2"] - c["entry"]) / c["risk"], 2), tp2_origen=c["tp2_src"],
                       salida=why, salida_fecha=str(M1_T[m]), R=round(R, 3)))
        busy = m
    return tr

def compound(tr, start=100.0, risk=0.05, lot_step=False):
    eq, peak, mdd, curve, skip = start, start, 0.0, [], 0
    for t in tr:
        if lot_step:
            lots = math.floor(eq * risk / (t["stop_pips"] * PIP * 100) * 100) / 100
            if lots < 0.01:
                skip += 1; curve.append(round(eq, 2)); continue
            eq += lots * 100 * t["R"] * t["stop_pips"] * PIP
        else:
            eq *= 1 + risk * t["R"]
        eq = max(eq, 0.0); peak = max(peak, eq); mdd = min(mdd, eq / peak - 1 if peak else 0)
        curve.append(round(eq, 2))
    return dict(final=round(eq, 2), multiplicador=round(eq / start, 3), maxDD_pct=round(100 * mdd, 1), sin_lote=skip, curva=curve)

def stats(tr):
    if not tr:
        return dict(n=0)
    Rs = [t["R"] for t in tr]; w = [r for r in Rs if r > 0]; ls = [r for r in Rs if r <= 0]
    streak = cur = 0
    for r in Rs:
        cur = cur + 1 if r <= 0 else 0; streak = max(streak, cur)
    rnd = random.Random(19); bo = sorted(st.mean(rnd.choices(Rs, k=len(Rs))) for _ in range(5000))
    return dict(n=len(tr), win_pct=round(100 * len(w) / len(tr), 1), R_medio=round(st.mean(Rs), 3), R_total=round(sum(Rs), 2),
                pf=round(sum(w) / -sum(ls), 2) if ls and sum(ls) < 0 else None, racha_perdidas=streak,
                ic90=(round(bo[250], 3), round(bo[4750], 3)), prob_R_le_0=round(sum(x <= 0 for x in bo) / 5000, 3),
                stop_medio_pips=round(st.mean(t["stop_pips"] for t in tr), 1),
                tp1_R_medio=round(st.mean(t["tp1_R"] for t in tr), 2), tp2_R_medio=round(st.mean(t["tp2_R"] for t in tr), 2),
                salidas={k: sum(t["salida"] == k for t in tr) for k in ("stop", "BE", "TP1", "TP2", "abierta")})

if __name__ == "__main__":
    allc = {}
    for ltf in (1, 5, 15):
        allc[f"M{ltf}"] = setups(ltf)
        print("setups", ltf, len(allc[f"M{ltf}"]), file=sys.stderr)
    allc["Multi (M1+M5+M15)"] = allc["M1"] + allc["M5"] + allc["M15"]
    res = dict(reglas=__doc__, resultados={}, cuenta={}, operaciones={})
    for name, cands in allc.items():
        tr = simulate(cands)
        res["resultados"][name] = stats(tr)
        res["cuenta"][name] = {"5% ideal": compound(tr), "5% lote 0,01": compound(tr, lot_step=True), "1% ideal": compound(tr, risk=0.01)}
        res["operaciones"][name] = tr
    res["variantes_salida_Multi"] = {m: stats(simulate(allc["Multi (M1+M5+M15)"], mode=m)) for m in ("tp1", "tp2")}
    for m in ("tp1", "tp2"):
        res["variantes_salida_Multi"][m]["cuenta_5pct"] = compound(simulate(allc["Multi (M1+M5+M15)"], mode=m))["final"]
    # mitades y meses (Multi)
    trm = res["operaciones"]["Multi (M1+M5+M15)"]
    res["Multi_por_mes"] = {}
    for t in trm:
        k = t["fecha"][:7]; x = res["Multi_por_mes"].setdefault(k, dict(n=0, R=0.0)); x["n"] += 1; x["R"] = round(x["R"] + t["R"], 2)
    res["Multi_mitades"] = {"ene-jun": stats([t for t in trm if t["fecha"] < "2026-06-15"]), "jun-nov": stats([t for t in trm if t["fecha"] >= "2026-06-15"])}
    # azar: mismas horas de killzone, mismo stop en pips, mismos TP1/TP2 en R, lado al azar
    rnd = random.Random(7); kz = [i for i in range(len(M1) - 20000) if in_kz(M1_T[i])]
    sims = []
    for s in range(100):
        Rs = []
        for t in trm:
            i = rnd.choice(kz); long = rnd.random() < 0.5; u, o, h, l, c, sp = M1[i]
            e = o + sp if long else o; r = t["stop_pips"] * PIP; sg = 1 if long else -1
            cc = dict(m1=i, side="long" if long else "short", entry=e, stop=e - sg * r, risk=r,
                      tp1=e + sg * t["tp1_R"] * r, tp2=e + sg * t["tp2_R"] * r)
            Rs.append(run_exit(cc)[0])
        sims.append(st.mean(Rs))
    sims.sort(); real = st.mean(t["R"] for t in trm)
    res["azar_Multi"] = dict(carteras=100, mediana_R=round(sims[50], 3), p5=round(sims[5], 3), p95=round(sims[95], 3),
                             estrategia_R=round(real, 3), pct_azar_igual_o_mejor=round(sum(x >= real for x in sims), 1))
    json.dump(res, open("snt_adaptativo_results.json", "w"), indent=1, ensure_ascii=False, default=str)
    brief = {k: v for k, v in res.items() if k not in ("operaciones", "reglas")}
    for n in brief["cuenta"]:
        for m in brief["cuenta"][n]:
            brief["cuenta"][n][m] = {a: b for a, b in brief["cuenta"][n][m].items() if a != "curva"}
    print(json.dumps(brief, indent=1, ensure_ascii=False, default=str))
