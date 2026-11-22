# -*- coding: utf-8 -*-
"""
Alchemist SnR "completo" mecanizado en XAUUSD 2026 (velas M1 reales con spread).
Partes del método (según las guías públicas del curso) y cómo se mecanizan:
  1. POI de temporalidad alta: niveles A / V frescos de D1 y H4 y gaps diarios (cierre 17:00 -> apertura 18:00 NY).
  2. Storyline multi-temporalidad: dirección por la última ruptura con cuerpo de un nivel A/V en H4 y en H1.
     Solo se opera si H4 y H1 coinciden.
  3. Liquidez de línea de tendencia: antes de llegar al POI, el precio hace al menos 2 swings consecutivos
     contra la storyline (máximos decrecientes antes de un largo / mínimos crecientes antes de un corto),
     es decir, una línea de tendencia que barrer. (El ángulo de 45-60 grados depende de la escala del
     gráfico; se sustituye por exigir al menos 2 swings alineados.)
  4. Quasimodo (QM) en la temporalidad de entrada (M15 o M5): largo = L, H, LL (barre L y toca el POI),
     HH (cierre con cuerpo por encima de H). El nivel QM es L. Cortos, al revés.
  5. Entrada: orden límite en el nivel QM (retesteo), solo en killzones (Londres y Nueva York).
  6. Stop: detrás del LL/HH del QM + 0,05 ATR(H1); se acepta entre 0,15 y 1 ATR(H1).
  7. Salida: 50 % en TP1 (el HH/LL del QM) con stop a la entrada, 50 % a la siguiente liquidez de H1/PDH-PDL.
     Variantes: todo a 3R, todo a 5R.
  8. Una operación a la vez, máximo 2 pérdidas al día.
"""
import json, random, statistics as st, datetime as dt, math, sys
import snt_adaptativo as S

# ---------------- POI de temporalidad alta
D1 = S.agg(lambda u: S.tday(S.ny(u)))
POI = S.classic(D1, "D1", 20) + [L for L in S.LEVELS if L["tf"] == "H4"]
for a, b in zip(D1, D1[1:]):
    lo, hi = sorted((a["c"], b["o"]))
    if hi > lo:
        L = dict(kind="GAP", tf="D1", side="sup" if b["o"] > a["c"] else "res", lo=lo, hi=hi, born=b["t"] + dt.timedelta(minutes=5))
        w = L["lo"] * 0.0002
        if hi - lo < w:
            m = (lo + hi) / 2; L["lo"], L["hi"] = m - w / 2, m + w / 2
        L["dies"] = L["born"] + dt.timedelta(days=20)
        POI.append(L)
POI.sort(key=lambda L: L["born"])

# ---------------- storyline H4 (H1 ya está en S.BIAS_T)
LV4 = [L for L in S.LEVELS if L["tf"] == "H4"]
BIAS4, bias, j, live = [], None, 0, []
for hb in S.H4:
    while j < len(LV4) and LV4[j]["born"] <= hb["t"]:
        live.append(LV4[j]); j += 1
    live = [L for L in live if L["dies"] > hb["t"]]
    for L in live:
        if L["kind"] == "A" and hb["o"] <= L["hi"] < hb["c"]: bias = "up"
        elif L["kind"] == "V" and hb["o"] >= L["lo"] > hb["c"]: bias = "down"
    BIAS4.append((hb["tend"], bias))

def bias_series(bars, table):
    out, k, cur = [], 0, None
    for b in bars:
        while k < len(table) and table[k][0] <= b["t"]:
            cur = table[k][1]; k += 1
        out.append(cur)
    return out

def setups(ltf, need_tl=True, need_h1=True, window_h=4, poi_h1=False):
    bars = S.agg(lambda u: u.replace(minute=u.minute // ltf * ltf, second=0))
    N, WIN = len(bars), max(window_h * 60 // ltf, 8)
    b1, b4 = bias_series(bars, S.BIAS_T), bias_series(bars, BIAS4)
    # swings fractal 2-2 conocidos en cada vela: lista de los últimos swings
    SH, SL, sh_list, sl_list = [None] * N, [None] * N, [], []
    for i in range(N):
        p = i - 2
        if p >= 2 and p + 2 < N:
            if all(bars[p]["h"] > bars[q]["h"] for q in (p - 2, p - 1, p + 1, p + 2)): sh_list.append((p, bars[p]["h"]))
            if all(bars[p]["l"] < bars[q]["l"] for q in (p - 2, p - 1, p + 1, p + 2)): sl_list.append((p, bars[p]["l"]))
        SH[i], SL[i] = len(sh_list), len(sl_list)
    PP = sorted(POI + ([L for L in S.LEVELS if L["tf"] == "H1"] if poi_h1 else []), key=lambda L: L["born"])
    out, fresh, j = [], [], 0
    for i in range(1, N):
        b = bars[i]; t = b["t"]
        while j < len(PP) and PP[j]["born"] <= t:
            fresh.append(PP[j]); j += 1
        touched = [L for L in fresh if b["l"] <= L["hi"] and b["h"] >= L["lo"]]
        if touched or i % 50 == 0:
            fresh = [L for L in fresh if L not in touched and L["dies"] > t]
        for P in touched:
            long = P["side"] == "sup"
            want = "up" if long else "down"
            if b4[i] != want or (need_h1 and b1[i] != want):
                continue
            highs = sh_list[:SH[i - 1]]; lows = sl_list[:SL[i - 1]]
            if len(highs) < 3 or len(lows) < 3:
                continue
            # QM: largo -> último swing L (mínimo) y el swing H posterior; el toque barre L
            if long:
                Hs = [h for h in highs[-1:]]
                Lps = [l for l in lows if l[0] < Hs[0][0]]
                if not Lps: continue
                Lp = Lps[-1]
                H = Hs[-1]; qm = Lp[1]
                if b["l"] >= qm: pass
                tl_ok = len(highs) >= 2 and highs[-1][1] < highs[-2][1] and (len(highs) < 3 or highs[-2][1] < highs[-3][1] or True)
            else:
                Ls = [l for l in lows[-1:]]
                Hps = [h for h in highs if h[0] < Ls[0][0]]
                if not Hps: continue
                Hp = Hps[-1]
                H = Ls[-1]; qm = Hp[1]
                tl_ok = len(lows) >= 2 and lows[-1][1] > lows[-2][1]
            if need_tl and not tl_ok:
                continue
            ext, ext_i, mss_i = (b["l"] if long else b["h"]), i, None
            for q in range(i, min(i + WIN + 1, N)):
                x = bars[q]
                if (long and x["l"] < ext) or (not long and x["h"] > ext): ext, ext_i = (x["l"] if long else x["h"]), q
                if (long and x["c"] < P["lo"] - (P["hi"] - P["lo"]) - 0.5 * S.atr_at(x["t"])) or \
                   (not long and x["c"] > P["hi"] + (P["hi"] - P["lo"]) + 0.5 * S.atr_at(x["t"])):
                    break                                   # POI roto con claridad
                swept = ext < qm if long else ext > qm      # LL por debajo de L (o HH por encima de H)
                if swept and q > ext_i and ((long and x["c"] > H[1]) or (not long and x["c"] < H[1])):
                    mss_i = q; break
            if mss_i is None:
                continue
            atr = S.atr_at(bars[mss_i]["t"])
            stop = ext - 0.05 * atr if long else ext + 0.05 * atr
            risk0 = (qm - stop) if long else (stop - qm)
            if not (0.15 * atr <= risk0 <= atr):
                continue
            leg = bars[mss_i]["h"] if long else bars[mss_i]["l"]
            for q in range(mss_i + 1, min(mss_i + WIN + 1, N)):
                x = bars[q]
                hit = (x["l"] + x["s"] <= qm) if long else (x["h"] >= qm)
                if hit:
                    if not S.in_kz(x["t"]):
                        break
                    mi = None
                    for m in range(x["m1_lo"], x["m1_hi"] + 1):
                        u, o, h, l, c, s = S.M1[m]
                        if (long and l + s <= qm) or (not long and h >= qm):
                            mi = m; fill = min(qm, o + s) if long else max(qm, o); break
                    if mi is None: break
                    r = (fill - stop) if long else (stop - fill)
                    if r <= 0 or ((leg - fill) if long else (fill - leg)) < r:
                        break
                    tp2, src = S.external_target(long, leg, S.M1_T[mi], abs(leg - ext), leg)
                    out.append(dict(m1=mi, t=S.M1_T[mi], side="long" if long else "short", entry=fill, stop=stop, risk=r,
                                    tp1=leg, tp2=tp2, tp2_src=src, tf=f"M{ltf}", level=P["kind"] + "-" + P["tf"], atr=atr))
                    break
                if (long and x["l"] <= stop) or (not long and x["h"] >= stop):
                    break
                leg = max(leg, x["h"]) if long else min(leg, x["l"])
    return out

def fixed(cands, rr):
    out = []
    for c in cands:
        sg = 1 if c["side"] == "long" else -1
        out.append(dict(c, tp1=c["entry"] + sg * rr * c["risk"], tp2=c["entry"] + sg * rr * c["risk"]))
    return out

def year_mc(Rs, risk, n_per_year, sims=20000, start=100.0):
    rnd = random.Random(11); finals = []
    for _ in range(sims):
        eq = start
        for _ in range(n_per_year):
            eq *= 1 + risk * rnd.choice(Rs); eq = max(eq, 0)
        finals.append(eq)
    finals.sort()
    return dict(p10=round(finals[sims // 10], 2), mediana=round(finals[sims // 2], 2), p90=round(finals[9 * sims // 10], 2),
                prob_perder=round(100 * sum(f < start for f in finals) / sims, 1),
                prob_perder_mitad=round(100 * sum(f < start / 2 for f in finals) / sims, 1),
                prob_x10=round(100 * sum(f >= 10 * start for f in finals) / sims, 2),
                prob_x1000=round(100 * sum(f >= 1000 * start for f in finals) / sims, 3))

if __name__ == "__main__":
    configs = {
        "Alchemist completo M15": dict(ltf=15),
        "Alchemist completo M5": dict(ltf=5),
        "Alchemist M15+M5": None,
        "M15 sin línea de tendencia": dict(ltf=15, need_tl=False),
        "M15 solo storyline H4": dict(ltf=15, need_h1=False),
        "M15 + POI de H1": dict(ltf=15, poi_h1=True),
        "M5 + POI de H1": dict(ltf=5, poi_h1=True),
    }
    C = {}
    for k, v in configs.items():
        if v: C[k] = setups(**v); print(k, len(C[k]), file=sys.stderr)
    C["Alchemist M15+M5"] = C["Alchemist completo M15"] + C["Alchemist completo M5"]
    days = (S.M1_T[-1] - S.M1_T[0]).days
    res = dict(reglas=__doc__, periodo=f"{S.M1_T[0]:%Y-%m-%d} a {S.M1_T[-1]:%Y-%m-%d} ({days} días)", resultados={}, operaciones={})
    for k, cands in C.items():
        res["resultados"][k] = {}
        for salida, cc, mode in (("parcial TP1+BE+TP2", cands, "parcial"), ("todo a 3R", fixed(cands, 3), "tp1"), ("todo a 5R", fixed(cands, 5), "tp1")):
            tr = S.simulate(cc, mode=mode)
            stt = S.stats(tr)
            acc = {f"{int(r*100)}%": S.compound(tr, risk=r) for r in (0.01, 0.05)}
            for a in acc.values(): a.pop("curva")
            res["resultados"][k][salida] = dict(stats=stt, cuenta_100=acc)
            if k == "Alchemist M15+M5" and salida == "parcial TP1+BE+TP2":
                res["operaciones"] = tr
                Rs = [t["R"] for t in tr]; npy = max(1, round(len(tr) * 365 / days))
                res["proyeccion_1_anio"] = {f"riesgo {int(r*100)}%": year_mc(Rs, r, npy) for r in (0.01, 0.02, 0.05, 0.10)}
                res["proyeccion_1_anio"]["operaciones_por_anio"] = npy
    # azar con los mismos stops y TP en R
    tr = res["operaciones"]; rnd = random.Random(5)
    kz = [i for i in range(len(S.M1) - 20000) if S.in_kz(S.M1_T[i])]; sims = []
    for _ in range(100):
        Rs = []
        for t in tr:
            i = rnd.choice(kz); long = rnd.random() < 0.5; u, o, h, l, c, sp = S.M1[i]
            e = o + sp if long else o; r = t["stop_pips"] * S.PIP; sg = 1 if long else -1
            Rs.append(S.run_exit(dict(m1=i, side="long" if long else "short", entry=e, stop=e - sg * r, risk=r,
                                      tp1=e + sg * t["tp1_R"] * r, tp2=e + sg * t["tp2_R"] * r))[0])
        sims.append(st.mean(Rs))
    sims.sort(); real = st.mean(t["R"] for t in tr) if tr else 0
    res["azar"] = dict(mediana=round(sims[50], 3), estrategia=round(real, 3), pct_azar_igual_o_mejor=sum(x >= real for x in sims))
    meses = {}
    for t in tr:
        m = meses.setdefault(t["fecha"][:7], [0, 0.0]); m[0] += 1; m[1] = round(m[1] + t["R"], 2)
    res["por_mes"] = meses
    json.dump(res, open("alchemist_full_results.json", "w"), indent=1, ensure_ascii=False, default=str)
    print(json.dumps({k: v for k, v in res.items() if k not in ("operaciones", "reglas")}, indent=1, ensure_ascii=False, default=str))
