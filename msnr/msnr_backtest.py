# -*- coding: utf-8 -*-
"""
Backtest mecánico de una versión simplificada de MSNR "Alchemist" (Malaysian SnR).

Reglas (interpretación mecánica, documentada en el informe):
  1. Niveles en 1 h, solo con cuerpos (open/close), nunca mechas:
       - Nivel A (resistencia): vela alcista seguida de vela bajista. Zona entre
         el cierre de la primera y la apertura de la segunda.
       - Nivel V (soporte): vela bajista seguida de vela alcista.
       - Nivel GAP: hueco entre el último cierre de un día y la apertura del
         siguiente. Gap alcista = soporte; gap bajista = resistencia.
  2. Frescura: un nivel solo se opera en su PRIMER toque (mecha de 5 min dentro
     de la zona). Después queda "unfresh" y se descarta.
  3. Storyline (sesgo, 1 h): alcista si la última ruptura con cierre de cuerpo
     fue por encima de un nivel A; bajista si fue por debajo de un nivel V.
  4. Entrada (5 min): con sesgo alcista, primer toque de un soporte fresco; en
     las 6 velas siguientes (30 min) una vela cierra por encima del máximo de la
     vela de toque sin haber cerrado por debajo de la zona. Se entra en la
     apertura de la vela siguiente. Cortos: espejo.
  5. Stop: extremo de la reacción ± 0,05 %. Distancia mínima 0,15 % del precio.
     Objetivo: 2R (variante 3R). Cierre forzado a las 15:55 Nueva York.
     Ventana de entrada: 9:45-15:00. Costes: 0,02 % por lado.
"""
import json, gzip, sys, datetime as dt, statistics as st, random

SRC = sys.argv[1] if len(sys.argv) > 1 else "TSLA-60d5m.json.gz"
d = json.load(gzip.open(SRC))
r = d["chart"]["result"][0]
q = r["indicators"]["quote"][0]
SYM = r["meta"].get("symbol", "?")

def ny(ts):  # datos jul-oct 2026: horario de verano, UTC-4
    return dt.datetime.utcfromtimestamp(ts) - dt.timedelta(hours=4)

bars = []
for i, ts in enumerate(r["timestamp"]):
    o, h, l, c = q["open"][i], q["high"][i], q["low"][i], q["close"][i]
    if None in (o, h, l, c):
        continue
    t = ny(ts)
    if not (dt.time(9, 30) <= t.time() < dt.time(16, 0)):
        continue
    bars.append(dict(t=t, o=o, h=h, l=l, c=c))

days = sorted({b["t"].date() for b in bars})

# ---------- velas de 1 h (9:30-10:30, ..., 15:30-16:00)
def hour_key(t):
    m = (t.hour * 60 + t.minute) - (9 * 60 + 30)
    return (t.date(), m // 60)

hourly = []
for b in bars:
    k = hour_key(b["t"])
    if hourly and hourly[-1]["k"] == k:
        hb = hourly[-1]; hb["h"] = max(hb["h"], b["h"]); hb["l"] = min(hb["l"], b["l"]); hb["c"] = b["c"]; hb["end"] = b["t"]
    else:
        hourly.append(dict(k=k, o=b["o"], h=b["h"], l=b["l"], c=b["c"], start=b["t"], end=b["t"]))

# ---------- niveles
levels = []  # dict(kind, lo, hi, born, side)  side: 'sup' / 'res'
for a, b in zip(hourly, hourly[1:]):
    if a["k"][0] != b["k"][0]:
        continue
    up_a, up_b = a["c"] > a["o"], b["c"] > b["o"]
    lo, hi = sorted((a["c"], b["o"]))
    born = b["end"] + dt.timedelta(minutes=5)
    if up_a and not up_b:
        levels.append(dict(kind="A", side="res", lo=lo, hi=hi, born=born))
    elif not up_a and up_b:
        levels.append(dict(kind="V", side="sup", lo=lo, hi=hi, born=born))
for da, db in zip(days, days[1:]):
    last = [b for b in bars if b["t"].date() == da][-1]
    first = [b for b in bars if b["t"].date() == db][0]
    lo, hi = sorted((last["c"], first["o"]))
    if hi - lo > 0:
        side = "sup" if first["o"] > last["c"] else "res"
        levels.append(dict(kind="GAP", side=side, lo=lo, hi=hi, born=first["t"] + dt.timedelta(minutes=5)))
for L in levels:
    minw = L["lo"] * 0.0005  # una línea fina se trata como zona de 0,05 %
    if L["hi"] - L["lo"] < minw:
        mid = (L["lo"] + L["hi"]) / 2
        L["lo"], L["hi"] = mid - minw / 2, mid + minw / 2
    L["fresh"] = True

# ---------- storyline en 1 h
def bias_at(t):
    """Sesgo según la última ruptura de cuerpo de 1 h cerrada antes de t."""
    bias = None
    for hb in hourly:
        if hb["end"] + dt.timedelta(minutes=5) > t:
            break
        for L in levels:
            if L["born"] > hb["start"]:
                continue
            if L["kind"] == "A" and hb["o"] <= L["hi"] < hb["c"]:
                bias = "up"
            elif L["kind"] == "V" and hb["o"] >= L["lo"] > hb["c"]:
                bias = "down"
    return bias

COST = 0.0002

def run(target_r=2.0, use_bias=True, sides=("long", "short")):
    for L in levels:
        L["fresh"] = True
    trades, i = [], 0
    n = len(bars)
    while i < n:
        b = bars[i]
        t = b["t"]
        if not (dt.time(9, 45) <= t.time() <= dt.time(15, 0)):
            # los toques fuera de ventana también gastan la frescura
            for L in levels:
                if L["fresh"] and L["born"] <= t and b["l"] <= L["hi"] and b["h"] >= L["lo"]:
                    L["fresh"] = False
            i += 1
            continue
        touched = [L for L in levels if L["fresh"] and L["born"] <= t and b["l"] <= L["hi"] and b["h"] >= L["lo"]]
        for L in touched:
            L["fresh"] = False
        bias = bias_at(t) if use_bias else None
        took = False
        for L in touched:
            side = "long" if L["side"] == "sup" else "short"
            if side not in sides:
                continue
            if use_bias and ((side == "long" and bias != "up") or (side == "short" and bias != "down")):
                continue
            ext = b["l"] if side == "long" else b["h"]
            for j in range(i + 1, min(i + 7, n)):
                x = bars[j]
                if x["t"].date() != t.date() or x["t"].time() > dt.time(15, 0):
                    break
                ext = min(ext, x["l"]) if side == "long" else max(ext, x["h"])
                if (side == "long" and x["c"] < L["lo"]) or (side == "short" and x["c"] > L["hi"]):
                    break  # nivel roto: sin confirmación
                if (side == "long" and x["c"] > b["h"]) or (side == "short" and x["c"] < b["l"]):
                    if j + 1 >= n or bars[j + 1]["t"].date() != t.date():
                        break
                    e = bars[j + 1]["o"]
                    stop = ext * (1 - 0.0005) if side == "long" else ext * (1 + 0.0005)
                    risk = abs(e - stop)
                    if risk < e * 0.0015 or (side == "long" and stop >= e) or (side == "short" and stop <= e):
                        break
                    tgt = e + target_r * risk if side == "long" else e - target_r * risk
                    k, out, why = j + 1, None, None
                    while k < n and bars[k]["t"].date() == t.date():
                        y = bars[k]
                        hit_s = y["l"] <= stop if side == "long" else y["h"] >= stop
                        hit_t = y["h"] >= tgt if side == "long" else y["l"] <= tgt
                        if hit_s:            # si una vela toca ambos, se asume el stop (conservador)
                            out, why = stop, "stop"; break
                        if hit_t:
                            out, why = tgt, "objetivo"; break
                        if y["t"].time() >= dt.time(15, 55):
                            out, why = y["c"], "cierre"; break
                        k += 1
                    if out is None:
                        out, why = bars[k - 1]["c"], "cierre"
                    gross = (out - e) if side == "long" else (e - out)
                    net = gross - COST * (e + out)
                    trades.append(dict(date=str(t.date()), time=bars[j + 1]["t"].strftime("%H:%M"), side=side, level=L["kind"],
                                       entry=round(e, 2), stop=round(stop, 2), target=round(tgt, 2), exit=round(out, 2),
                                       why=why, R=round(net / risk, 2), pct=round(100 * net / e, 3)))
                    i = k  # una operación a la vez
                    took = True
                    break
            if took:
                break
        i += 1
    return trades

def summary(tr):
    if not tr:
        return dict(n=0)
    Rs = [x["R"] for x in tr]
    eq, peak, dd = 0, 0, 0
    for v in Rs:
        eq += v; peak = max(peak, eq); dd = min(dd, eq - peak)
    wins = [v for v in Rs if v > 0]; losses = [v for v in Rs if v <= 0]
    pf = sum(wins) / -sum(losses) if losses and sum(losses) < 0 else float("inf")
    # intervalo de confianza 90 % del R medio por bootstrap
    rnd = random.Random(19); boots = sorted(st.mean(rnd.choices(Rs, k=len(Rs))) for _ in range(5000))
    return dict(n=len(tr), win=round(100 * len(wins) / len(tr), 1), avgR=round(st.mean(Rs), 3), totalR=round(sum(Rs), 2),
                pf=round(pf, 2), maxDD_R=round(dd, 2), ci90=(round(boots[250], 2), round(boots[4750], 2)),
                stop=sum(x["why"] == "stop" for x in tr), obj=sum(x["why"] == "objetivo" for x in tr), cierre=sum(x["why"] == "cierre" for x in tr))

variants = {
    "MSNR completa (storyline, 2R, largos+cortos)": dict(target_r=2, use_bias=True),
    "MSNR completa, objetivo 3R": dict(target_r=3, use_bias=True),
    "Sin storyline (todos los niveles frescos), 2R": dict(target_r=2, use_bias=False),
    "Solo largos, storyline, 2R": dict(target_r=2, use_bias=True, sides=("long",)),
    "Solo cortos, storyline, 2R": dict(target_r=2, use_bias=True, sides=("short",)),
}
out = dict(symbol=SYM, first=str(days[0]), last=str(days[-1]), days=len(days), bars5m=len(bars),
           levels=dict(A=sum(L["kind"] == "A" for L in levels), V=sum(L["kind"] == "V" for L in levels), GAP=sum(L["kind"] == "GAP" for L in levels)),
           buyhold_pct=round(100 * (bars[-1]["c"] / bars[0]["o"] - 1), 2), results={}, trades={})
for name, kw in variants.items():
    tr = run(**kw)
    out["results"][name] = summary(tr)
    out["trades"][name] = tr
json.dump(out, open("msnr_results.json", "w"), indent=1, ensure_ascii=False, default=str)
print(json.dumps({k: v for k, v in out.items() if k != "trades"}, indent=1, ensure_ascii=False, default=str))
