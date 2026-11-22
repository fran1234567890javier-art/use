# -*- coding: utf-8 -*-
"""
XAUUSD 2026: modelo mecanizado a partir de los apuntes White SNT (SMC x ICT)
+ niveles Classic A / Classic V como KEY LEVEL. RR de 1:14 a 1:20, stop máximo 50 pips.

Reglas (interpretación mecánica; el resumen en lenguaje llano está en INFORME_SNT_XAUUSD.md):
 1. KEY LEVEL = nivel Classic A (vela alcista + vela bajista, resistencia) o Classic V
    (bajista + alcista, soporte) en H1 y H4, marcado SOLO con cuerpos (cierre de la 1ª
    y apertura de la 2ª). Solo el primer toque (nivel fresco). Caduca: H1 5 días, H4 10 días.
 2. Sesgo ("no ir contra tendencia"): storyline H1, última ruptura con cuerpo de un nivel A/V.
 3. LIQUIDITY / TURTLE SOUP: al tocar el nivel, el precio barre el último swing low (largos)
    o swing high (cortos) de M5 confirmado antes del toque.
 4. MSS: una vela M5 cierra con cuerpo más allá del último swing high (largos) anterior al
    mínimo del barrido, en las 36 velas (3 h) siguientes al toque. Si una vela cierra con
    cuerpo al otro lado del nivel, el setup se anula.
 5. ENTRADA tipo HUNTER MODEL: Fibo del barrido (1) al extremo del impulso (0); orden límite
    en el 0,764 (STRONG ZONE). Espera máxima 36 velas. Solo se llena en KILLZONE
    (Londres 02:00-05:00, NY AM 07:00-11:00, NY PM 13:00-15:00, hora NY). Asia no se opera.
 6. STOP: 2 pips más allá del barrido. Si el stop supera 50 pips (5,00 $) no hay operación.
    Stop mínimo 10 pips (1,00 $) para que el spread no lo invalide. 1 pip = 0,10 $.
 7. OBJETIVO: 14R ... 20R. Salida solo por stop u objetivo (variante: cierre diario 16:50 NY).
 8. Una operación a la vez; tras 2 pérdidas en el día no se opera más ese día (apuntes, "MODEL ENTRY").
 9. Costes: spread real de cada minuto. Largos compran al ask y venden al bid; cortos al revés.
    Si una vela toca stop y objetivo, cuenta stop. Si el precio abre más allá del stop, sale a la apertura.
"""
import csv, gzip, sys, os, json, random, statistics as st, datetime as dt, math
from zoneinfo import ZoneInfo

NY, UTC = ZoneInfo("America/New_York"), dt.timezone.utc
SRC = sys.argv[1] if len(sys.argv) > 1 else "XAUUSD_M1_2026.csv.gz"
PIP = 0.10
LTF = int(os.environ.get("LTF", "5"))                 # minutos de la vela de entrada (M5 por defecto, M1 opcional)
MAX_STOP_PIPS = float(os.environ.get("MAXSTOP", "50"))
MAX_STOP, MIN_STOP, BUF = MAX_STOP_PIPS * PIP, 10 * PIP, 2 * PIP
WIN = 180 // LTF                                       # 3 horas en velas
FIB_ENTRY = 0.764
KZ = [(dt.time(2), dt.time(5)), (dt.time(7), dt.time(11)), (dt.time(13), dt.time(15))]

# ------------------------------------------------------------------ datos
m1 = []
for row in csv.DictReader(gzip.open(SRC, "rt")):
    u = dt.datetime.fromisoformat(row["time_utc"]).replace(tzinfo=UTC)
    m1.append((u, float(row["open"]), float(row["high"]), float(row["low"]), float(row["close"]),
               int(row["spread_points"]) * 0.001))
ny = lambda u: u.astimezone(NY).replace(tzinfo=None)
tday = lambda t: (t + dt.timedelta(hours=6)).date()

def agg(keyf):
    out = []
    for u, o, h, l, c, s in m1:
        k = keyf(u)
        if out and out[-1]["k"] == k:
            b = out[-1]; b["h"] = max(b["h"], h); b["l"] = min(b["l"], l); b["c"] = c; b["s"] = max(b["s"], s); b["end"] = u
        else:
            out.append(dict(k=k, u=u, o=o, h=h, l=l, c=c, s=s, end=u))
    for b in out:
        b["t"] = ny(b["u"]); b["d"] = tday(b["t"])
    return out

bars = agg(lambda u: u.replace(minute=u.minute // LTF * LTF, second=0))
h1 = agg(lambda u: u.replace(minute=0, second=0))
def h4key(u):
    t = ny(u); hh = t.hour - ((t.hour - 1) % 4)          # velas H4 a la 1-5-9 NY (CRT)
    return (tday(t), (hh + 24) % 24)
h4 = agg(h4key)
m1_by_5 = {}
for r in m1:
    m1_by_5.setdefault(r[0].replace(minute=r[0].minute // LTF * LTF, second=0), []).append(r)
N = len(bars)

# ------------------------------------------------------------------ key levels Classic A / V
def classic(hb, tf, life):
    out = []
    for a, b in zip(hb, hb[1:]):
        if a["d"] != b["d"]:
            continue
        up_a, up_b = a["c"] > a["o"], b["c"] > b["o"]
        lo, hi = sorted((a["c"], b["o"]))
        born = ny(b["end"]) + dt.timedelta(minutes=1)
        if up_a and not up_b:
            out.append(dict(kind="A", tf=tf, side="res", lo=lo, hi=hi, born=born))
        elif not up_a and up_b:
            out.append(dict(kind="V", tf=tf, side="sup", lo=lo, hi=hi, born=born))
    for L in out:
        w = L["lo"] * 0.0002                          # una línea fina = zona mínima de 0,02 %
        if L["hi"] - L["lo"] < w:
            m = (L["lo"] + L["hi"]) / 2; L["lo"], L["hi"] = m - w / 2, m + w / 2
        L["dies"] = L["born"] + dt.timedelta(days=life)
    return out
levels = sorted(classic(h1, "H1", 5) + classic(h4, "H4", 10), key=lambda L: L["born"])
lv1 = [L for L in levels if L["tf"] == "H1"]

# ------------------------------------------------------------------ storyline H1
bias_after, bias, j, live = [], None, 0, []
for hb in h1:
    while j < len(lv1) and lv1[j]["born"] <= hb["t"]:
        live.append(lv1[j]); j += 1
    live = [L for L in live if L["dies"] > hb["t"]]
    for L in live:
        if L["kind"] == "A" and hb["o"] <= L["hi"] < hb["c"]:
            bias = "up"
        elif L["kind"] == "V" and hb["o"] >= L["lo"] > hb["c"]:
            bias = "down"
    bias_after.append((ny(hb["end"]) + dt.timedelta(minutes=1), bias))
bias_at_bar, k, cur = [], 0, None
for b in bars:
    while k < len(bias_after) and bias_after[k][0] <= b["t"]:
        cur = bias_after[k][1]; k += 1
    bias_at_bar.append(cur)

# ------------------------------------------------------------------ swings M5 (fractal 2-2)
sw_hi, sw_lo = [None] * N, [None] * N          # último swing confirmado conocido en la vela i
last_h = last_l = None
for i in range(N):
    p = i - 2
    if p >= 2 and p + 2 < N:
        if all(bars[p]["h"] > bars[q]["h"] for q in (p - 2, p - 1, p + 1, p + 2)):
            last_h = (p, bars[p]["h"])
        if all(bars[p]["l"] < bars[q]["l"] for q in (p - 2, p - 1, p + 1, p + 2)):
            last_l = (p, bars[p]["l"])
    sw_hi[i], sw_lo[i] = last_h, last_l

in_kz = lambda t: any(a <= t.time() < b for a, b in KZ)

# ------------------------------------------------------------------ setups (independientes del RR)
def find_setups(use_bias=True):
    cands, fresh, j = [], [], 0
    for i in range(N):
        b = bars[i]; t = b["t"]
        while j < len(levels) and levels[j]["born"] <= t:
            fresh.append(levels[j]); j += 1
        touched = [L for L in fresh if b["l"] <= L["hi"] and b["h"] >= L["lo"]]
        if touched:
            fresh = [L for L in fresh if L not in touched]
        fresh = [L for L in fresh if L["dies"] > t]
        for L in touched:
            long = L["side"] == "sup"
            liq = sw_lo[i - 1] if long else sw_hi[i - 1]      # liquidez previa al toque
            if liq is None:
                continue
            ext, ext_i, mss_i, w = (b["l"], i, None, L["hi"] - L["lo"])
            for q in range(i, min(i + WIN + 1, N)):
                x = bars[q]
                if (long and x["l"] < ext) or (not long and x["h"] > ext):
                    ext, ext_i = (x["l"] if long else x["h"]), q
                if (long and x["c"] < L["lo"] - w) or (not long and x["c"] > L["hi"] + w):
                    break                                       # nivel roto con cuerpo
                swept = ext < liq[1] if long else ext > liq[1]
                ref = sw_hi[q] if long else sw_lo[q]
                if swept and ref and ref[0] < ext_i and q > ext_i and \
                   ((long and x["c"] > ref[1]) or (not long and x["c"] < ref[1])):
                    mss_i = q; break
            if mss_i is None:
                continue
            side = "long" if long else "short"
            if use_bias and bias_at_bar[mss_i] != ("up" if long else "down"):
                continue
            # Hunter: Fibo del barrido al extremo del impulso, entrada límite en 0,764
            stop = ext - BUF if long else ext + BUF
            leg = bars[mss_i]["h"] if long else bars[mss_i]["l"]
            for q in range(mss_i + 1, min(mss_i + WIN + 1, N)):
                x = bars[q]
                entry = leg - FIB_ENTRY * (leg - ext) if long else leg + FIB_ENTRY * (ext - leg)
                risk = (entry - stop) if long else (stop - entry)
                if risk > MAX_STOP:
                    break                                       # el impulso ya exige stop > 50 pips
                hit = (x["l"] + x["s"] <= entry) if long else (x["h"] >= entry)
                if hit and risk >= MIN_STOP and in_kz(x["t"]):
                    o = x["o"] + x["s"] if long else x["o"]     # si abre ya por debajo/encima
                    fill = min(entry, o) if long else max(entry, o)
                    r2 = (fill - stop) if long else (stop - fill)
                    if r2 >= MIN_STOP:
                        cands.append(dict(i=q, side=side, entry=fill, stop=stop, risk=r2, level=L["kind"] + "-" + L["tf"],
                                          t=x["t"], touch=t, mss=bars[mss_i]["t"]))
                    break
                if hit:          # tocó la entrada fuera de killzone o con stop < 10 pips: setup gastado
                    break
                if (long and x["l"] <= stop) or (not long and x["h"] >= stop):
                    break
                leg = max(leg, x["h"]) if long else min(leg, x["l"])
    cands.sort(key=lambda c: c["i"])
    return cands

# ------------------------------------------------------------------ simulación de salidas
def exit_of(c, rr, daily_close=False):
    long = c["side"] == "long"; e, s = c["entry"], c["stop"]
    tgt = e + rr * c["risk"] if long else e - rr * c["risk"]
    for k in range(c["i"], N):
        y = bars[k]
        if daily_close and k > c["i"] and (y["d"] != bars[c["i"]]["d"] or (dt.time(16, 50) <= y["t"].time() < dt.time(18))):
            px = y["o"] if long else y["o"] + y["s"]
            return k, px, "cierre"
        lo_b, hi_a = y["l"], y["h"] + y["s"]
        hs = lo_b <= s if long else hi_a >= s
        ht = (y["h"] >= tgt if long else y["l"] + y["s"] <= tgt) and k > c["i"]
        if hs:
            gap = (y["o"] < s) if long else (y["o"] + y["s"] > s)
            px = (y["o"] if long else y["o"] + y["s"]) if (gap and k > c["i"]) else s
            return k, px, "stop"
        if ht:
            return k, tgt, "objetivo"
    y = bars[-1]
    return N - 1, (y["c"] if long else y["c"] + y["s"]), "abierta"

def simulate(cands, rr, daily_close=False, max_losses_day=2):
    trades, busy_until, losses = [], -1, {}
    for c in cands:
        if c["i"] <= busy_until:
            continue
        d = bars[c["i"]]["d"]
        if losses.get(d, 0) >= max_losses_day:
            continue
        k, px, why = exit_of(c, rr, daily_close)
        long = c["side"] == "long"
        R = ((px - c["entry"]) if long else (c["entry"] - px)) / c["risk"]
        trades.append(dict(fecha=str(c["t"]), lado=c["side"], nivel=c["level"], entrada=round(c["entry"], 3),
                           stop=round(c["stop"], 3), stop_pips=round(c["risk"] / PIP, 1),
                           objetivo=round(c["entry"] + (rr if long else -rr) * c["risk"], 3),
                           salida=round(px, 3), salida_fecha=str(bars[k]["t"]), motivo=why, R=round(R, 3), i=c["i"], k=k))
        if R <= 0:
            losses[d] = losses.get(d, 0) + 1
        busy_until = k
    return trades

def compound(trades, start=100.0, risk=0.05, lot_step=False):
    eq, peak, mdd, curve, skipped = start, start, 0.0, [], 0
    for t in trades:
        if lot_step:                               # 1 lote = 100 oz; mínimo y paso 0,01 lote (1 oz)
            lots = math.floor(eq * risk / (t["stop_pips"] * PIP * 100) * 100) / 100
            if lots < 0.01:
                skipped += 1; curve.append(round(eq, 2)); continue
            eq += lots * 100 * t["R"] * t["stop_pips"] * PIP
        else:
            eq *= 1 + risk * t["R"]
        eq = max(eq, 0.0)
        peak = max(peak, eq); mdd = min(mdd, eq / peak - 1 if peak else 0)
        curve.append(round(eq, 2))
    return dict(final=round(eq, 2), ret_pct=round(100 * (eq / start - 1), 1), maxDD_pct=round(100 * mdd, 1),
                no_cabe_lote=skipped, curva=curve)

def stats(tr, rr):
    if not tr:
        return dict(n=0)
    Rs = [t["R"] for t in tr]
    w = sum(r > 0 for r in Rs); streak = cur = 0
    for r in Rs:
        cur = cur + 1 if r <= 0 else 0; streak = max(streak, cur)
    rnd = random.Random(19); bo = sorted(st.mean(rnd.choices(Rs, k=len(Rs))) for _ in range(5000))
    return dict(n=len(tr), ganadoras=w, win_pct=round(100 * w / len(tr), 1), breakeven_pct=round(100 / (1 + rr), 1),
                objetivos=sum(t["motivo"] == "objetivo" for t in tr), stops=sum(t["motivo"] == "stop" for t in tr),
                otras=sum(t["motivo"] not in ("objetivo", "stop") for t in tr), R_medio=round(st.mean(Rs), 3),
                R_total=round(sum(Rs), 2), racha_perdidas=streak, ic90=(round(bo[250], 3), round(bo[4750], 3)),
                prob_R_medio_le_0=round(sum(x <= 0 for x in bo) / 5000, 3),
                stop_medio_pips=round(st.mean(t["stop_pips"] for t in tr), 1))

def verify_m1(tr, rr):
    """Rehace stop/objetivo minuto a minuto (resuelve las velas M5 que tocan ambos)."""
    changed = 0
    for t in tr:
        long = t["lado"] == "long"; e, s, g = t["entrada"], t["stop"], t["objetivo"]
        res = None
        for k in range(t["i"], t["k"] + 1):
            for (u, o, h, l, c, sp) in m1_by_5.get(bars[k]["u"], []):
                if (long and l <= s) or (not long and h + sp >= s):
                    res = "stop"; break
                if k > t["i"] and ((long and h >= g) or (not long and l + sp <= g)):
                    res = "objetivo"; break
            if res:
                break
        if res and res != t["motivo"]:
            changed += 1
    return changed

# ------------------------------------------------------------------ análisis del año
def year_overview():
    days = {}
    for u, o, h, l, c, s in m1:
        d = tday(ny(u))
        x = days.setdefault(d, dict(o=o, h=h, l=l, c=c, s=[]))
        x["h"] = max(x["h"], h); x["l"] = min(x["l"], l); x["c"] = c; x["s"].append(s)
    ds = sorted(days)
    months = {}
    for d in ds:
        m = months.setdefault(d.strftime("%Y-%m"), dict(o=days[d]["o"], h=days[d]["h"], l=days[d]["l"], c=days[d]["c"], rng=[]))
        m["h"] = max(m["h"], days[d]["h"]); m["l"] = min(m["l"], days[d]["l"]); m["c"] = days[d]["c"]
        m["rng"].append(days[d]["h"] - days[d]["l"])
    hi_d = max(ds, key=lambda d: days[d]["h"]); lo_d = min(ds, key=lambda d: days[d]["l"])
    rets = [(ds[i], days[ds[i]]["c"] / days[ds[i - 1]]["c"] - 1) for i in range(1, len(ds))]
    allsp = [s for d in ds for s in days[d]["s"]]
    return dict(
        desde=str(ds[0]), hasta=str(ds[-1]), dias=len(ds), apertura=round(days[ds[0]]["o"], 2), ultimo=round(days[ds[-1]]["c"], 2),
        cambio_pct=round(100 * (days[ds[-1]]["c"] / days[ds[0]]["o"] - 1), 2),
        maximo=(round(days[hi_d]["h"], 2), str(hi_d)), minimo=(round(days[lo_d]["l"], 2), str(lo_d)),
        rango_diario_medio_usd=round(st.mean(days[d]["h"] - days[d]["l"] for d in ds), 2),
        rango_diario_medio_pips=round(st.mean(days[d]["h"] - days[d]["l"] for d in ds) / PIP),
        volatilidad_anual_pct=round(100 * st.pstdev(r for _, r in rets) * math.sqrt(252), 1),
        mejor_dia=(str(max(rets, key=lambda x: x[1])[0]), round(100 * max(r for _, r in rets), 2)),
        peor_dia=(str(min(rets, key=lambda x: x[1])[0]), round(100 * min(r for _, r in rets), 2)),
        spread_mediano_pips=round(sorted(allsp)[len(allsp) // 2] / PIP, 1),
        meses={k: dict(apertura=round(v["o"], 1), maximo=round(v["h"], 1), minimo=round(v["l"], 1), cierre=round(v["c"], 1),
                       cambio_pct=round(100 * (v["c"] / v["o"] - 1), 2), rango_medio_pips=round(st.mean(v["rng"]) / PIP))
               for k, v in months.items()})

# ------------------------------------------------------------------ ejecución
if __name__ == "__main__":
    out = dict(datos=dict(fuente=SRC, velas_m1=len(m1), velas_m5=N, primera=str(bars[0]["t"]), ultima=str(bars[-1]["t"]),
                          niveles=dict(A_H1=sum(1 for L in levels if L["kind"] == "A" and L["tf"] == "H1"),
                                       V_H1=sum(1 for L in levels if L["kind"] == "V" and L["tf"] == "H1"),
                                       A_H4=sum(1 for L in levels if L["kind"] == "A" and L["tf"] == "H4"),
                                       V_H4=sum(1 for L in levels if L["kind"] == "V" and L["tf"] == "H4"))))
    out["analisis_anual"] = year_overview()
    cands = find_setups(True)
    cands_nobias = find_setups(False)
    out["setups_validos"] = len(cands)
    out["resultados"], out["cuenta_100usd_5pct"], out["operaciones"] = {}, {}, {}
    for rr in range(14, 21):
        tr = simulate(cands, rr)
        key = f"1:{rr}"
        out["resultados"][key] = stats(tr, rr)
        out["resultados"][key]["velas_m1_cambian"] = verify_m1(tr, rr)
        out["cuenta_100usd_5pct"][key] = dict(ideal=compound(tr), lote_minimo_0_01=compound(tr, lot_step=True))
        out["operaciones"][key] = [{k: v for k, v in t.items() if k not in ("i", "k")} for t in tr]
    # variantes de control (1:14 y 1:20)
    out["variantes"] = {}
    for rr in (14, 20):
        out["variantes"][f"1:{rr} cierre diario 16:50 NY"] = stats(simulate(cands, rr, daily_close=True), rr)
        out["variantes"][f"1:{rr} sin storyline"] = stats(simulate(cands_nobias, rr), rr)
        out["variantes"][f"1:{rr} sin limite de 2 perdidas/dia"] = stats(simulate(cands, rr, max_losses_day=99), rr)
    # mitades del año (1:14)
    tr14 = simulate(cands, 14); mid = bars[N // 2]["t"]
    out["mitades_1:14"] = {"1a mitad": stats([t for t in tr14 if t["fecha"] < str(mid)], 14),
                           "2a mitad": stats([t for t in tr14 if t["fecha"] >= str(mid)], 14), "corte": str(mid)}
    # entradas al azar con los mismos stops y objetivo 14R
    rnd = random.Random(7); kz_idx = [i for i in range(N - 2000) if in_kz(bars[i]["t"])]
    sims = []
    for s in range(200):
        Rs = []
        for t in tr14:
            i = rnd.choice(kz_idx); long = rnd.random() < 0.5; y = bars[i]
            e = y["o"] + y["s"] if long else y["o"]; r = t["stop_pips"] * PIP
            c = dict(i=i, side="long" if long else "short", entry=e, stop=e - r if long else e + r, risk=r)
            k, px, why = exit_of(c, 14)
            Rs.append(((px - e) if long else (e - px)) / r)
        sims.append(st.mean(Rs))
    sims.sort(); real = st.mean(t["R"] for t in tr14)
    out["azar_1:14"] = dict(carteras=200, mediana_R=round(sims[100], 3), p5=round(sims[10], 3), p95=round(sims[190], 3),
                            estrategia_R=round(real, 3), pct_azar_igual_o_mejor=round(100 * sum(x >= real for x in sims) / 200, 1))
    out["config"] = dict(LTF_min=LTF, stop_max_pips=MAX_STOP_PIPS, pip_usd=PIP, fib_entrada=FIB_ENTRY)
    tag = "" if (LTF == 5 and MAX_STOP_PIPS == 50) else f"_M{LTF}_SL{int(MAX_STOP_PIPS)}"
    json.dump(out, open(f"snt_xauusd_results{tag}.json", "w"), indent=1, ensure_ascii=False, default=str)
    brief = {k: v for k, v in out.items() if k not in ("operaciones",)}
    for k in brief["cuenta_100usd_5pct"]:
        for m in ("ideal", "lote_minimo_0_01"):
            brief["cuenta_100usd_5pct"][k][m] = {a: b for a, b in brief["cuenta_100usd_5pct"][k][m].items() if a != "curva"}
    print(json.dumps(brief, indent=1, ensure_ascii=False, default=str))
