# -*- coding: utf-8 -*-
"""Réplica en Python de la lógica del script Pine (preset Ajustado) sobre XAUUSD 2026 M1,
para ver cuántas señales salen y qué capa o filtro las bloquea."""
import csv, gzip, datetime as dt, statistics as st, collections, sys
SRC = "/projects/sandbox/msnr/XAUUSD_M1_2026.csv.gz"
PIP = 0.1
M1 = []
for r in csv.DictReader(gzip.open(SRC, "rt")):
    u = dt.datetime.fromisoformat(r["time_utc"])
    M1.append([u, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"]), float(r["tick_volume"])])

def agg(minutes):
    out = []
    for u, o, h, l, c, v in M1:
        if minutes == 240:
            k = u.replace(minute=0) - dt.timedelta(hours=u.hour % 4)
        else:
            k = u.replace(minute=(u.hour * 60 + u.minute) % 60 // minutes * minutes) if minutes < 60 else u.replace(minute=0)
            if minutes < 60:
                k = u.replace(minute=u.minute // minutes * minutes)
        if out and out[-1][0] == k:
            b = out[-1]; b[2] = max(b[2], h); b[3] = min(b[3], l); b[4] = c; b[5] += v
        else:
            out.append([k, o, h, l, c, v])
    return out

def pivots(b, n):
    ph = [None] * len(b); pl = [None] * len(b)
    for i in range(n, len(b) - n):
        if all(b[i][2] > b[j][2] for j in range(i - n, i + n + 1) if j != i): ph[i + n] = b[i][2]
        if all(b[i][3] < b[j][3] for j in range(i - n, i + n + 1) if j != i): pl[i + n] = b[i][3]
    return ph, pl

def sma(x, n, i):
    if i < n - 1 or any(v is None for v in x[i - n + 1:i + 1]): return None
    return sum(x[i - n + 1:i + 1]) / n

# ---------- H4 bias por vela H4 cerrada
H4 = agg(240); ph, pl = pivots(H4, 5)
hs, ls = [], []; bias4 = []
for i in range(len(H4)):
    if ph[i] is not None: hs.append((i - 5, ph[i]))
    if pl[i] is not None: ls.append((i - 5, pl[i]))
    w = [p for j, p in hs if j >= i - 99]; wl = [p for j, p in ls if j >= i - 99]
    bull = sum(1 for a, b in zip(w, w[1:]) if b > a) + sum(1 for a, b in zip(wl, wl[1:]) if b > a)
    bear = (len(w) - 1 if w else 0) + (len(wl) - 1 if wl else 0) - bull
    tot = bull + bear; bz = 0
    if len(w) >= 2 and len(wl) >= 2 and tot > 0:
        bz = 1 if bull / tot > 0.6 else -1 if bear / tot > 0.6 else 0
    bias4.append(bz)

# ---------- H1: OB/FVG + ADX/ATR
H1 = agg(60); n1 = len(H1)
bOB, sOB, FV = [], [], []
vB, vS, adxL, atrL = [False] * n1, [False] * n1, [None] * n1, [None] * n1
tr = [None] * n1; pdm = [0.0] * n1; mdm = [0.0] * n1
for i in range(n1):
    o, h, l, c = H1[i][1:5]; rng = h - l + 1e-10
    if i >= 10:
        if c > o and (c - o) / rng >= 0.5:
            for j in range(1, 10):
                if H1[i - j][4] < H1[i - j][1]: bOB.append((i, H1[i - j][2], H1[i - j][3])); bOB = bOB[-3:]; break
        if c < o and (o - c) / rng >= 0.5:
            for j in range(1, 10):
                if H1[i - j][4] > H1[i - j][1]: sOB.append((i, H1[i - j][2], H1[i - j][3])); sOB = sOB[-3:]; break
    if i >= 2:
        if l > H1[i - 2][2]: FV.append((i, l, H1[i - 2][2], 1))
        elif h < H1[i - 2][3]: FV.append((i, H1[i - 2][3], h, -1))
        FV = FV[-3:]
    ob_b = [x for x in bOB if x[0] >= i - 99]; ob_s = [x for x in sOB if x[0] >= i - 99]
    un = sum(1 for k, t, bb, d in FV if k >= i - 99 and ((d == 1 and c > t) or (d == -1 and c < bb)))
    vB[i] = bool(ob_b) and (any(bb <= c <= t for _, t, bb in ob_b) or un > 0)
    vS[i] = bool(ob_s) and (any(bb <= c <= t for _, t, bb in ob_s) or un > 0)
    if i >= 1:
        pc = H1[i - 1][4]; tr[i] = max(h - l, abs(h - pc), abs(l - pc))
        up = h - H1[i - 1][2]; dn = H1[i - 1][3] - l
        pdm[i] = up if (up > dn and up > 0) else 0.0
        mdm[i] = dn if (dn > pdm[i] and dn > 0) else 0.0
dxs = [None] * n1
for i in range(n1):
    a = sma(tr, 14, i)
    if a:
        atrL[i] = a
        p = 100 * sma(pdm, 14, i) / a; m = 100 * sma(mdm, 14, i) / a
        dxs[i] = 100 * abs(p - m) / (p + m) if p + m else None
    adxL[i] = sma(dxs, 14, i)

# ---------- M30: barrido de Asia + swing
M30 = agg(30); n30 = len(M30); ph30, pl30 = pivots(M30, 3)
f30 = [False] * n30; sw30L = [None] * n30; sw30H = [None] * n30
cHi = cLo = aHi = aLo = None; prevA = False; sweeps = []; sL = sH = None
for i in range(n30):
    u, o, h, l, c, v = M30[i]; inA = u.hour >= 20
    if inA and not prevA: cHi, cLo = h, l
    elif inA: cHi, cLo = max(cHi, h), min(cLo, l)
    if not inA and prevA: aHi, aLo = cHi, cLo
    prevA = inA
    body = abs(c - o); uw = h - max(o, c); lw = min(o, c) - l
    s = (aLo is not None and l < aLo and lw / (body + 1e-10) > 1.5) or (aHi is not None and h > aHi and uw / (body + 1e-10) > 1.5)
    sweeps.append(s); f30[i] = any(sweeps[-10:])
    if ph30[i] is not None: sH = ph30[i]
    if pl30[i] is not None: sL = pl30[i]
    sw30L[i] = sL if sL is not None else min(x[3] for x in M30[max(0, i - 4):i + 1])
    sw30H[i] = sH if sH is not None else max(x[2] for x in M30[max(0, i - 4):i + 1])

# ---------- M15: CRT
M15 = agg(15); n15 = len(M15); ph15, pl15 = pivots(M15, 3)
cB = [False] * n15; cS = [False] * n15
for i in range(1, n15):
    o, h, l, c = M15[i][1:5]; po, ph_, pl_, pc = M15[i - 1][1:5]; rng = h - l
    cB[i] = l < pl_ - 0.0001 and c > pl_ and c > o and rng > 0 and (c - o) / rng >= 0.4
    cS[i] = h > ph_ + 0.0001 and c < ph_ and c < o and rng > 0 and (o - c) / rng >= 0.4
crt = []; sL = sH = None
for i in range(n15):
    frB = anB = frS = anS = None
    for k in range(2, 32):
        if i - k < 0: break
        if anB is None and cB[i - k]:
            anB = M15[i - k][3]; frB = anB if k <= 16 else None
        if anS is None and cS[i - k]:
            anS = M15[i - k][2]; frS = anS if k <= 16 else None
    if ph15[i] is not None: sH = ph15[i]
    if pl15[i] is not None: sL = pl15[i]
    swL = sL if sL is not None else min(x[3] for x in M15[max(0, i - 4):i + 1])
    swH = sH if sH is not None else max(x[2] for x in M15[max(0, i - 4):i + 1])
    crt.append((frB, anB, swL, frS, anS, swH))

# ---------- M5: MSS
M5 = agg(5); n5 = len(M5); ph5, pl5 = pivots(M5, 3)
mss = []; sh = sl = None
for i in range(n5):
    if ph5[i] is not None: sh = ph5[i]
    if pl5[i] is not None: sl = pl5[i]
    ok = sh is not None and sl is not None
    hc = max(x[4] for x in M5[max(0, i - 4):i + 1]); lc = min(x[4] for x in M5[max(0, i - 4):i + 1])
    mss.append((ok and hc > sh, ok and lc < sl))

# ---------- índice "última vela cerrada" de cada TF para cada minuto
def last_closed_index(bars, minutes):
    starts = [b[0] for b in bars]; idx = []; j = 0
    for u, *_ in M1:
        while j + 1 < len(starts) and starts[j + 1] <= u: j += 1
        idx.append(j - 1)   # vela anterior a la que contiene el minuto = última cerrada
    return idx
I4, I1, I30, I15, I5 = (last_closed_index(b, m) for b, m in ((H4, 240), (H1, 60), (M30, 30), (M15, 15), (M5, 5)))

def run(slmax=60.0, atrmin=40, atrmax=300, minscore=5, adxthr=25):
    cnt = collections.Counter(); sigs = []; last = None
    for i in range(20, len(M1)):
        u, o, h, l, c, v = M1[i]
        tmin = u.hour * 60 + u.minute
        if not ((420 <= tmin <= 720) or (780 <= tmin <= 1020)): continue
        cnt["minutos en sesión"] += 1
        d = bias4[I4[i]] if I4[i] >= 0 else 0
        if d == 0: cnt["bloqueo: H4 neutral"] += 1; continue
        j1 = I1[i]; adx, atr = adxL[j1], atrL[j1]
        if not (adx and adx > adxthr and atr and atrmin <= atr / PIP <= atrmax): cnt["bloqueo: filtro ADX/ATR"] += 1; continue
        l2 = vB[j1] if d == 1 else vS[j1]
        l3 = f30[I30[i]]
        frB, anB, swL, frS, anS, swH = crt[I15[i]]
        l4 = (frB is not None) if d == 1 else (frS is not None)
        l5 = mss[I5[i]][0] if d == 1 else mss[I5[i]][1]
        b1 = abs(c - o); r1 = h - l; uw = h - max(o, c); lw = min(o, c) - l
        mom = (c - M1[i - 4][4]) / M1[i - 4][4]
        pc, po = M1[i - 1][4], M1[i - 1][1]
        if d == 1:
            eng = c > o and pc < po and o <= pc and c >= po; pin = r1 > 0 and lw > b1 * 2 and c > o and b1 / r1 < 0.3; mo = mom > 0
        else:
            eng = c < o and pc > po and o >= pc and c <= po; pin = r1 > 0 and uw > b1 * 2 and c < o and b1 / r1 < 0.3; mo = mom < 0
        v20 = sum(x[5] for x in M1[i - 19:i + 1]) / 20; v3 = sum(x[5] for x in M1[i - 2:i + 1]) / 3
        l6 = (mo + eng + pin + (v20 == 0 or v3 >= 0.8 * v20)) >= 2
        score = 1 + l2 + l3 + l4 + l5 + l6
        for name, ok in (("2 H1", l2), ("3 M30", l3), ("4 M15", l4), ("5 M5", l5), ("6 M1", l6)):
            cnt["capa " + name + " ok"] += ok
        if score < minscore: cnt["bloqueo: puntuación < %d" % minscore] += 1; continue
        if last and (u - last).total_seconds() < 1800: cnt["bloqueo: cooldown"] += 1; continue
        lvl = (anB if anB is not None else swL) if d == 1 else (anS if anS is not None else swH)
        slp = lvl - 2 * PIP if d == 1 else lvl + 2 * PIP
        if abs(c - slp) / PIP < 15:
            slp = (M30 and sw30L[I30[i]] - 2 * PIP) if d == 1 else sw30H[I30[i]] + 2 * PIP
        dist = abs(c - slp) / PIP
        side = slp < c if d == 1 else slp > c
        if not side: cnt["bloqueo: SL al lado equivocado"] += 1; continue
        if dist > slmax: cnt["bloqueo: SL > %.0f pips" % slmax] += 1; continue
        sigs.append((u, d, c, slp, dist)); last = u
    return cnt, sigs

if __name__ == "__main__":
    for slmax in (60, 150, 300):
        cnt, sigs = run(slmax=slmax)
        print("\n=== SL máx", slmax, "pips → señales:", len(sigs))
        for k, v in cnt.most_common(): print("  ", k, v)
        if sigs: print("   ejemplo:", sigs[-1], " SL medio", round(st.mean(s[4] for s in sigs), 1))
    for ms in (4,):
        cnt, sigs = run(slmax=150, minscore=ms); print("\n=== minScore 4, SL 150 → señales:", len(sigs))
