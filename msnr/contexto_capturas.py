# -*- coding: utf-8 -*-
"""Contexto de mercado (MSNR / SMC) de cada operación vista en las capturas del canal."""
import datetime as dt, json, statistics as st
import snt_adaptativo as S
import alchemist_full as A

UTC = dt.timezone.utc
# (id, entrada aprox. en UTC, lado, precio, lotes, resultado visible)
TRADES = [
    ("1 oct", dt.datetime(2026, 10, 1, 12, 47), "short", 4185.57, "100", "+280.500 $ abiertos"),
    ("2 oct (dibujo TV)", dt.datetime(2026, 10, 2, 0, 5), "short", 4182.0, "-", "RR 74 dibujado"),
    ("7 oct", dt.datetime(2026, 10, 7, 7, 33), "short", 4137.71, "2,39", "precio hasta 4.081"),
    ("13 oct", dt.datetime(2026, 10, 13, 13, 50), "short", 4174.80, "10", "+5.620 $"),
    ("26 oct", dt.datetime(2026, 10, 26, 11, 21), "long", 4011.2, "120 (3 órdenes)", "precio a 4.023"),
    ("3-4 nov (dibujo TV)", dt.datetime(2026, 11, 3, 14, 0), "long", 3898.0, "-", "subida a 4.047"),
    ("13 nov", dt.datetime(2026, 11, 13, 13, 30), "long", 3880.18, "100", "+110.300 $"),
]

def ny(t): return t.replace(tzinfo=UTC).astimezone(S.NY).replace(tzinfo=None)

def m1_index(t_ny):
    lo, hi = 0, len(S.M1_T) - 1
    while lo < hi:
        m = (lo + hi) // 2
        if S.M1_T[m] < t_ny: lo = m + 1
        else: hi = m
    return lo

def bias(table, t):
    b = None
    for k, v in table:
        if k > t: break
        b = v
    return b

def session(t):
    h = t.hour + t.minute / 60
    if 20 <= h or h < 0: return "Asia"
    if 0 <= h < 2: return "Asia (tras medianoche NY)"
    if 2 <= h < 5: return "Killzone Londres"
    if 5 <= h < 7: return "Londres (fuera de killzone)"
    if 7 <= h < 11: return "Killzone NY AM"
    if 11 <= h < 13: return "NY mediodía"
    if 13 <= h < 15: return "Killzone NY PM"
    return "NY tarde"

out = []
for name, tu, side, px, lots, res in TRADES:
    t = ny(tu); i = m1_index(t); long = side == "long"
    atr = S.atr_at(t)
    d = S.tday(t); prev = [x for x in S.DAYS if x < d]
    pdh, pdl = S.DAY[prev[-1]] if prev else (None, None)
    # apertura de medianoche NY y rango de Asia (20:00-00:00 NY) del día
    mid = dt.datetime.combine(t.date(), dt.time(0))
    if t < mid: mid -= dt.timedelta(days=1)
    mi = m1_index(mid); midnight_open = S.M1[mi][1]
    a0, a1 = m1_index(mid - dt.timedelta(hours=4)), mi
    asia_h = max(S.M1[k][2] for k in range(a0, a1)) if a1 > a0 else None
    asia_l = min(S.M1[k][3] for k in range(a0, a1)) if a1 > a0 else None
    # extremo previo 4 h y movimiento 4 h después
    p0 = m1_index(t - dt.timedelta(hours=4))
    pre_h = max(S.M1[k][2] for k in range(p0, i)); pre_l = min(S.M1[k][3] for k in range(p0, i))
    post = [S.M1[k] for k in range(i, min(i + 240, len(S.M1)))]
    fav = (px - min(r[3] for r in post)) if not long else (max(r[2] for r in post) - px)
    adv = (max(r[2] for r in post) - px) if not long else (px - min(r[3] for r in post))
    # niveles MSNR frescos cerca (H1, H4, D1, gaps diarios)
    lv = [L for L in A.POI + [L for L in S.LEVELS if L["tf"] == "H1"] if L["born"] <= t < L["dies"]]
    near = []
    for L in lv:
        dist = 0 if L["lo"] <= px <= L["hi"] else min(abs(px - L["lo"]), abs(px - L["hi"]))
        if dist <= 0.25 * atr:
            # ¿fresco? no tocado entre su nacimiento y la entrada
            b0 = m1_index(L["born"])
            touched = any(S.M1[k][3] <= L["hi"] and S.M1[k][2] >= L["lo"] for k in range(b0, max(b0, i - 5)))
            near.append(f'{L["kind"]}-{L["tf"]} {L["lo"]:.2f}-{L["hi"]:.2f} ({"fresco" if not touched else "usado"}, a {dist:.2f} $)')
    near = sorted(set(near))[:6]
    # barrido de liquidez: ¿la vela de entrada (±15 min) rebasa el extremo de las 4 h previas?
    w0 = m1_index(t - dt.timedelta(minutes=15)); w1 = min(i + 15, len(S.M1) - 1)
    pre0 = m1_index(t - dt.timedelta(hours=4))
    before_h = max(S.M1[k][2] for k in range(pre0, w0)); before_l = min(S.M1[k][3] for k in range(pre0, w0))
    hi_w = max(S.M1[k][2] for k in range(w0, w1)); lo_w = min(S.M1[k][3] for k in range(w0, w1))
    sweep = (f"barre máximos de 4 h ({before_h:.2f} -> {hi_w:.2f})" if hi_w > before_h else "no barre máximos") if not long else \
            (f"barre mínimos de 4 h ({before_l:.2f} -> {lo_w:.2f})" if lo_w < before_l else "no barre mínimos")
    sess = session(t)
    news = "posible dato de las 8:30 NY" if (t.hour == 8 and 20 <= t.minute <= 59) else ""
    out.append(dict(operacion=name, lado="venta" if not long else "compra", lotes=lots, precio=px, hora_NY=t.strftime("%a %d-%m %H:%M"),
                    sesion=sess, noticia=news, storyline_H1=bias(S.BIAS_T, t), storyline_H4=bias(A.BIAS4, t), ATR_H1=round(atr, 2),
                    PDH=round(pdh, 2), PDL=round(pdl, 2), apertura_medianoche=round(midnight_open, 2),
                    asia_alto=round(asia_h, 2) if asia_h else None, asia_bajo=round(asia_l, 2) if asia_l else None,
                    barrido=sweep, niveles_msnr_cerca=near, a_favor_4h=round(fav, 2), en_contra_4h=round(adv, 2),
                    resultado_visible=res))
json.dump(out, open("contexto_capturas.json", "w"), indent=1, ensure_ascii=False, default=str)
for o in out:
    print("\n==", o["operacion"], o["lado"], o["precio"], "|", o["hora_NY"], "NY |", o["sesion"], o["noticia"])
    print("   storyline H1/H4:", o["storyline_H1"], "/", o["storyline_H4"], "| ATR H1:", o["ATR_H1"])
    print("   PDH/PDL:", o["PDH"], o["PDL"], "| medianoche:", o["apertura_medianoche"], "| Asia:", o["asia_alto"], o["asia_bajo"])
    print("   ", o["barrido"]); print("   niveles:", o["niveles_msnr_cerca"])
    print("   4 h después: a favor", o["a_favor_4h"], "$ | en contra", o["en_contra_4h"], "$")
