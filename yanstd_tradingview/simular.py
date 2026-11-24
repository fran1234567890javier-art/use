"""Réplica en Python (sin pandas) de YANSTD_indicador.pine para comprobar que salen señales.
Datos: XAUUSD M1 2026 (bid). Gráfico M3, sesgo M15, POI M5, King H4/H1. Modo límite, ajustes por defecto.
Uso: python3 simular.py [--sin-ote] [--g27b]
"""
import gzip, csv, sys, math, bisect
from datetime import datetime, timezone

ARGS = sys.argv[1:]
REQ_OTE = "--sin-ote" not in ARGS
EXP_BARS = 30 if "--g27b" in ARGS else 60
P = dict(dispMin=0.70, fvgMin=0.30, obMax=1.5, zMin=0.2, zMax=25.0, poiAge=96, invalBuf=0.8, invalN=2,
         maxDistA=2.25, dupA=0.5, minRR=1.10, oteTol=0.3, minScore=50, minScCT=75, ctBars=16,
         slMult=2.0, slMinA=0.35, slMaxA=2.5, spread=0.30, tp1R=1.5, tp2R=1.6, mileR=1.2, mileLock=0.3,
         tiBars=16, tiMfeR=0.7, tiMfeA=0.35, maxPos=3, pip=0.10, brkBuf=0.05)

rows = []
with gzip.open("/projects/sandbox/msnr/XAUUSD_M1_2026.csv.gz", "rt") as f:
    for r in csv.DictReader(f):
        t = int(datetime.fromisoformat(r["time_utc"]).replace(tzinfo=timezone.utc).timestamp())
        rows.append((t, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))


def resample(mins):
    out, cur, sec = [], None, mins * 60
    for t, o, h, l, c in rows:
        b = t - t % sec
        if cur and cur[0] == b:
            cur[2] = max(cur[2], h); cur[3] = min(cur[3], l); cur[4] = c
        else:
            if cur: out.append(cur)
            cur = [b, o, h, l, c]
    out.append(cur)
    return out


def rma(vals, n):
    out, s = [], None
    for i, v in enumerate(vals):
        if i < n - 1: out.append(None); continue
        if s is None: s = sum(vals[i - n + 1:i + 1]) / n
        else: s = (s * (n - 1) + v) / n
        out.append(s)
    return out


def atr(B, n=14):
    tr = [B[0][2] - B[0][3]] + [max(B[i][2] - B[i][3], abs(B[i][2] - B[i-1][4]), abs(B[i][3] - B[i-1][4])) for i in range(1, len(B))]
    return rma(tr, n)


def dmi(B, n=14):
    tr, pdm, mdm = [0.0], [0.0], [0.0]
    for i in range(1, len(B)):
        up, dn = B[i][2] - B[i-1][2], B[i-1][3] - B[i][3]
        pdm.append(up if up > dn and up > 0 else 0.0); mdm.append(dn if dn > up and dn > 0 else 0.0)
        tr.append(max(B[i][2] - B[i][3], abs(B[i][2] - B[i-1][4]), abs(B[i][3] - B[i-1][4])))
    a, p, m = rma(tr, n), rma(pdm, n), rma(mdm, n)
    dip = [None if a[i] is None or a[i] == 0 else 100 * p[i] / a[i] for i in range(len(B))]
    dim = [None if a[i] is None or a[i] == 0 else 100 * m[i] / a[i] for i in range(len(B))]
    dx = [0.0 if dip[i] is None or dip[i] + dim[i] == 0 else 100 * abs(dip[i] - dim[i]) / (dip[i] + dim[i]) for i in range(len(B))]
    adx = rma(dx, n)
    return dip, dim, adx


def pivots(B, w):
    ph, pl = [None] * len(B), [None] * len(B)
    for i in range(2 * w, len(B)):
        c = i - w
        hs = [B[j][2] for j in range(c - w, c + w + 1)]
        ls = [B[j][3] for j in range(c - w, c + w + 1)]
        # TradingView: estricto a la derecha, no estricto a la izquierda
        if B[c][2] == max(hs) and all(B[j][2] < B[c][2] for j in range(c + 1, c + w + 1)): ph[i] = (B[c][2], B[c][0])
        if B[c][3] == min(ls) and all(B[j][3] > B[c][3] for j in range(c + 1, c + w + 1)): pl[i] = (B[c][3], B[c][0])
    return ph, pl


def bias15(B, sec):
    ph, pl = pivots(B, 6); a = atr(B); dip, dim, adx = dmi(B)
    swH = prvH = swL = prvL = None; swHt = swLt = 0
    trend = pend = pendT = lastBrk = 0; protH = protL = None
    out = []
    for i, (t, o, h, l, c) in enumerate(B):
        if ph[i]: prvH, (swH, swHt) = swH, ph[i]
        if pl[i]: prvL, (swL, swLt) = swL, pl[i]
        c2 = B[i-1][4] if i else c
        rg = h - l; br = abs(c - o) / rg if rg > 0 else 0
        dBu, dBe = br >= 0.55 and c > o, br >= 0.55 and c < o
        bb = P["brkBuf"]
        if pend and t > pendT + 12 * sec: pend = pendT = 0
        if None not in (swH, swL, prvH, prvL):
            if trend == 0:
                if swH > prvH and swL > prvL: trend, pend, protL, protH = 1, 0, swL, swH
                elif swH < prvH and swL < prvL: trend, pend, protH, protL = -1, 0, swH, swL
            elif trend == 1:
                if pend == -1:
                    conf = swHt > pendT and swH < protH and swLt > pendT and c2 >= swL and c < swL - bb and dBe
                    inv = protH is not None and c2 <= protH and c > protH + bb and dBu
                    if conf: trend, pend, pendT, protH, protL, lastBrk = -1, 0, 0, swH, swL, t
                    elif inv: pend, pendT, protL, protH, lastBrk = 0, 0, swL, swH, t
                elif protL is not None and c2 >= protL and c < protL - bb and dBe: pend, lastBrk, pendT = -1, t, t
                elif c2 <= swH and c > swH + bb and dBu: protL, protH, lastBrk = swL, swH, t
            else:
                if pend == 1:
                    conf = swLt > pendT and swL > protL and swHt > pendT and c2 <= swH and c > swH + bb and dBu
                    inv = protL is not None and c2 >= protL and c < protL - bb and dBe
                    if conf: trend, pend, pendT, protH, protL, lastBrk = 1, 0, 0, swH, swL, t
                    elif inv: pend, pendT, protL, protH, lastBrk = 0, 0, swL, swH, t
                elif protH is not None and c2 <= protH and c > protH + bb and dBu: pend, lastBrk, pendT = 1, t, t
                elif c2 >= swL and c < swL - bb and dBe: protL, protH, lastBrk = swL, swH, t
        bs = (t - lastBrk) / sec + 1 if lastBrk else 999
        out.append((trend, pend, bs, adx[i], dip[i], dim[i], a[i], swH, swL))
    return out


def king(B):
    a = atr(B); sOn = rOn = False; sBot = sBuf = rTop = rBuf = 0; sT = rT = 0; out = []
    for i, (t, o, h, l, c) in enumerate(B):
        if i >= 3 and a[i] is not None:
            p1 = B[i-1]; rg = h - l; br = abs(c - o) / rg if rg > 0 else 0
            genL = p1[3] <= B[i-2][3] and p1[3] <= B[i-3][3]
            genH = p1[2] >= B[i-2][2] and p1[2] >= B[i-3][2]
            kS = p1[4] < p1[1] and c > o and l < p1[3] and c > p1[3] and br >= 0.55 and genL and o - l >= 0.05 * a[i]
            kR = p1[4] > p1[1] and c < o and h > p1[2] and c < p1[2] and br >= 0.55 and genH and h - o >= 0.05 * a[i]
            if sOn and c < sBot - sBuf: sOn = False
            if rOn and c > rTop + rBuf: rOn = False
            if kS: sBot, sBuf, sT, sOn = l, 0.1 * a[i], t, True
            if kR: rTop, rBuf, rT, rOn = h, 0.1 * a[i], t, True
        out.append((1 if sT >= rT else -1) if sOn and rOn else 1 if sOn else -1 if rOn else 0)
    return out


def poi5(B):
    a = atr(B); out = []
    for i in range(len(B)):
        if i < 15 or a[i] is None: out.append(None); continue
        t, o, h, l, c = B[i]; b1, b2 = B[i-1], B[i-2]
        hiPrev = max(x[2] for x in B[i-13:i-1]); loPrev = min(x[3] for x in B[i-13:i-1])
        hiSw = max(x[2] for x in B[i-14:i-2]); loSw = min(x[3] for x in B[i-14:i-2])
        rg1 = b1[2] - b1[3]; br1 = abs(b1[4] - b1[1]) / rg1 if rg1 > 0 else 0
        obW = b2[2] - b2[3]
        bull = b1[4] > b1[1] and br1 >= P["dispMin"] and b1[4] > hiPrev and l > b2[2] and l - b2[2] > P["fvgMin"] * a[i] and obW <= P["obMax"] * a[i]
        bear = b1[4] < b1[1] and br1 >= P["dispMin"] and b1[4] < loPrev and h < b2[3] and b2[3] - h > P["fvgMin"] * a[i] and obW <= P["obMax"] * a[i]
        fTop = l if bull else b2[3]; fBot = b2[2] if bull else h
        fHi = max(h, b1[2]) if bull else hiPrev; fLo = loPrev if bull else min(l, b1[3])
        swp = b2[3] < loSw if bull else b2[2] > hiSw
        out.append((bull, bear, t, b2[2], b2[3], fTop, fBot, fHi, fLo, swp, a[i]))
    return out


def aligner(B, vals, sec):
    """valor 'security(..., x[1], lookahead_on)' para un instante T de apertura de vela del gráfico."""
    starts = [b[0] for b in B]
    def get(T):
        k = bisect.bisect_right(starts, T) - 1  # vela HTF que contiene T
        return vals[k - 1] if k >= 1 else None
    return get


M3, M5, M15, H1, H4 = resample(3), resample(5), resample(15), resample(60), resample(240)
gB = aligner(M15, bias15(M15, 900), 900)
gP = aligner(M5, poi5(M5), 300)
gK1 = aligner(H4, king(H4), 14400)
gK2 = aligner(H1, king(H1), 3600)
a3 = atr(M3)
ph3, pl3 = pivots(M3, 2)

pois, ords, closed = [], [], []
lastPoiT = 0; nPoi = nOrd = nFill = nCanc = 0; rej = {}
m3H = m3Hp = m3L = m3Lp = None; swB = [False] * 3; swS = [False] * 3
MS5 = 300

for i, (t, o, h, l, c) in enumerate(M3):
    b = gB(t); pz = gP(t)
    if b is None or a3[i] is None: continue
    trend, pend, bars15, adx15, diP, diM, atr15, swH15, swL15 = b
    k1, k2 = gK1(t) or 0, gK2(t) or 0
    kingB = k1 if k1 else k2
    atr5 = pz[10] if pz else None
    if atr15 is None or atr5 is None or adx15 is None: continue
    dt = datetime.fromtimestamp(t, timezone.utc)
    dow, hr = dt.weekday(), dt.hour  # 0=lunes
    bloq = dow >= 5 or 20 <= hr <= 22
    friC = dow == 4 and hr >= 20

    # 1) órdenes
    for od in list(ords):
        d = od["dir"]
        if not od["filled"]:
            if t > od["t0"] + EXP_BARS * MS5 or od["p"]["dead"] or friC:
                ords.remove(od); nCanc += 1; continue
            if (l <= od["e"]) if d == 1 else (h >= od["e"]):
                od["filled"] = True; od["tF"] = t; nFill += 1
        if od["filled"]:
            fav = h if d == 1 else l
            done = False
            if (l <= od["sl"]) if d == 1 else (h >= od["sl"]):
                od["R"] += od["rem"] * (od["sl"] - od["e"]) * d / od["r"]; done = True
            elif od["tF"] != t:
                if not od["t1"] and (fav - od["tp1"]) * d >= 0:
                    od["t1"] = True; od["R"] += 0.5 * P["tp1R"]; od["rem"] -= 0.5
                    if (od["e"] - od["sl"]) * d > 0: od["sl"] = od["e"]
                if not od["t2"] and (fav - od["tp2"]) * d >= 0:
                    od["t2"] = True; od["R"] += 0.25 * P["tp2R"]; od["rem"] -= 0.25
                od["mfe"] = max(od["mfe"], (fav - od["e"]) * d)
                lock = od["e"] + d * P["mileLock"] * od["r"]
                if od["mfe"] >= P["mileR"] * od["r"] and (lock - od["sl"]) * d > 0: od["sl"] = lock
                ti = t - od["tF"] >= P["tiBars"] * MS5 and od["mfe"] < P["tiMfeR"] * od["r"] and od["mfe"] < P["tiMfeA"] * atr5
                if ti or friC:
                    od["R"] += od["rem"] * (c - od["e"]) * d / od["r"]; done = True
            if done:
                ords.remove(od); closed.append(od)

    # M3 barrido / CHoCH (para gatillos; aquí solo modo límite)
    # 2) POIs
    for p in list(pois):
        d = p["dir"]; ce = (p["fTop"] + p["fBot"]) / 2
        if (c < p["bot"] - P["invalBuf"]) if d == 1 else (c > p["top"] + P["invalBuf"]): p["out"] += 1
        if p["out"] >= P["invalN"]: p["dead"] = True
        if not p["hasOrd"] and ((l <= ce) if d == 1 else (h >= ce)):
            p["dead"] = True; p["why"] = p["why"] or "toque"
        if t - p["t0"] > P["poiAge"] * MS5: p["dead"] = True
        if p["dead"]:
            if not p["hasOrd"]: rej[p["why"] or "otro"] = rej.get(p["why"] or "otro", 0) + 1
            pois.remove(p)

    # 3) POIs nuevos
    if pz and pz[2] != lastPoiT:
        lastPoiT = pz[2]
        bull, bear, pt, obH, obL, fTop, fBot, fHi, fLo, swp, _ = pz
        for isB in (True, False):
            if (isB and bull) or (not isB and bear):
                top = fTop if isB else obH; bot = obL if isB else fBot; w = top - bot
                psych = math.floor(top / 5) * 5 >= bot
                if P["zMin"] <= w <= P["zMax"] and (swp or psych):
                    pois.append(dict(dir=1 if isB else -1, top=top, bot=bot, fTop=fTop, fBot=fBot, fHi=fHi, fLo=fLo,
                                     t0=pt, sweep=swp, out=0, dead=False, hasOrd=False, why=""))
                    nPoi += 1
                    if len(pois) > 20: pois.pop(0)

    # 4) colocar
    def ote(d, edge):
        if swH15 is None or swL15 is None: return False
        R = swH15 - swL15
        if R <= 0: return False
        if d == 1: return swH15 - 0.786 * R - P["oteTol"] <= edge <= swH15 - 0.618 * R + P["oteTol"]
        return swL15 + 0.618 * R - P["oteTol"] <= edge <= swL15 + 0.786 * R + P["oteTol"]

    def ev(p, e, isF):
        d = p["dir"]; aligned = trend == 0 or trend == d
        allowed = aligned or pend == d or bars15 >= P["ctBars"]
        counter = (not aligned) or (kingB != 0 and kingB != d)
        dist = abs(c - e); side = e < c if d == 1 else e > c
        slRaw = p["bot"] - atr15 * P["slMult"] - P["spread"] if d == 1 else p["top"] + atr15 * P["slMult"] + P["spread"]
        dCl = min(max(abs(e - slRaw), atr15 * P["slMinA"]), atr15 * P["slMaxA"])
        sl = e - d * dCl
        tgt = max(p["fHi"], swH15 if swH15 else p["fHi"]) if d == 1 else min(p["fLo"], swL15 if swL15 else p["fLo"])
        rr = (tgt - e) * d / dCl
        o_ = ote(d, p["fTop"] if d == 1 else p["fBot"])
        if not allowed: return None, sl, "dir"
        if not side: return None, sl, "lado"
        if dist > P["maxDistA"] * atr5: return None, sl, "dist"
        if rr < P["minRR"]: return None, sl, "rr"
        if REQ_OTE and not o_: return None, sl, "ote"
        age = (t - p["t0"]) / MS5
        s = 50 + (15 if isF else 0) + max(0, (20 - age) / 20) * 15 + max(0, (100 - dist / P["pip"]) / 100) * 20
        s += (20 if p["sweep"] else 0) + (15 if o_ else 0)
        lvl = swL15 if d == 1 else swH15
        if o_ and lvl is not None and p["bot"] - 0.1 * atr15 <= lvl <= p["top"] + 0.1 * atr15: s += 15
        s -= 10 if counter else 0
        s -= (20 - adx15) / 20 * 10 if adx15 < 20 else 0
        s += 5 if ((diP or 0) > (diM or 0)) == (d == 1) else -5
        if s < (P["minScCT"] if counter else P["minScore"]): return None, sl, "score"
        return s, sl, ""

    if not bloq:
        for p in pois:
            if p["dead"] or p["hasOrd"]: continue
            d = p["dir"]; ce = (p["fTop"] + p["fBot"]) / 2
            f79 = p["fHi"] - 0.786 * (p["fHi"] - p["fLo"]) if d == 1 else p["fLo"] + 0.786 * (p["fHi"] - p["fLo"])
            best = None; why = ""
            for e, isF in ((ce, True), (f79, False)):
                s, sl, w = ev(p, e, isF)
                why = why or w
                if s is not None and (best is None or s > best[0]): best = (s, e, sl)
            if best:
                dup = any((not q["filled"]) and abs(q["e"] - best[1]) < P["dupA"] * atr5 for q in ords)
                opp = any(q["dir"] != d for q in ords)
                if len(ords) >= P["maxPos"]: why = "max"
                elif dup or opp: why = "dup"
                else:
                    r = abs(best[1] - best[2]); p["hasOrd"] = True; nOrd += 1
                    ords.append(dict(dir=d, e=best[1], sl=best[2], r=r, tp1=best[1] + d * P["tp1R"] * r,
                                     tp2=best[1] + d * P["tp2R"] * r, t0=t, p=p, filled=False, tF=0, t1=False,
                                     t2=False, mfe=0.0, rem=1.0, R=0.0))
            if why: p["why"] = why

Rs = [x["R"] for x in closed]
w = sum(1 for x in Rs if x > 0.05); lo = sum(1 for x in Rs if x < -0.05)
print(f"OTE exigido={REQ_OTE} expira={EXP_BARS}  POIs={nPoi} órdenes={nOrd} ejecutadas={nFill} canceladas={nCanc} cerradas={len(Rs)}")
print(f"ganadas={w} perdidas={lo} BE={len(Rs)-w-lo}  sumaR={sum(Rs):.2f}  mediaR={sum(Rs)/max(1,len(Rs)):.3f}")
print("POIs sin orden por motivo:", dict(sorted(rej.items(), key=lambda x: -x[1])))
months = {}
for x in closed:
    m = datetime.fromtimestamp(x["tF"], timezone.utc).strftime("%Y-%m"); months.setdefault(m, []).append(x["R"])
print(" ".join(f"{m}:{len(v)}/{sum(v):+.1f}R" for m, v in sorted(months.items())))
