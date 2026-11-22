# -*- coding: utf-8 -*-
"""
Búsqueda de una estrategia MSNR/SNT con RR 1:5 y 80 % de acierto en XAUUSD 2026.
Método honesto: se buscan los filtros en ENERO-JUNIO (muestra de aprendizaje) y la mejor
combinación se comprueba después en JUNIO-NOVIEMBRE (datos que la búsqueda no ha visto).
Base: setups de snt_adaptativo.py (Key level Classic A/V H1-H4, barrido, MSS, entrada 0,764,
killzones), en M1, M5 y M15. Salida: objetivo 5R / stop 1R (opcional: BE al llegar a +2R).
"""
import itertools, json, datetime as dt, statistics as st
import snt_adaptativo as S

CUT = dt.datetime(2026, 6, 15)
cands = []
for ltf in (1, 5, 15):
    cands += S.setups(ltf)

def kz_name(t):
    h = t.time()
    return "Londres" if h < dt.time(5) else ("NY AM" if h < dt.time(11) else "NY PM")

rows = []
for c in cands:
    sg = 1 if c["side"] == "long" else -1
    base = dict(c, tp1=c["entry"] + sg * 2 * c["risk"], tp2=c["entry"] + sg * 5 * c["risk"])
    plain = dict(c, tp1=c["entry"] + sg * 5 * c["risk"], tp2=c["entry"] + sg * 5 * c["risk"])
    R_plain = S.run_exit(plain, "tp1")[0]
    R_be = S.run_exit(base, "tp2")[0]
    rows.append(dict(t=c["t"], tf=c["tf"], side=c["side"], level=c["level"], kz=kz_name(c["t"]),
                     wd=c["t"].strftime("%a"), sratio=c["risk"] / c["atr"], R={"sin BE": R_plain, "BE a +2R": R_be}))
q = sorted(r["sratio"] for r in rows); t1, t2 = q[len(q) // 3], q[2 * len(q) // 3]
for r in rows:
    r["stop"] = "corto" if r["sratio"] < t1 else ("medio" if r["sratio"] < t2 else "largo")

F = dict(tf=["M1", "M5", "M15", None], side=["long", "short", None], level=["A-H1", "V-H1", "A-H4", "V-H4", None],
         kz=["Londres", "NY AM", "NY PM", None], wd=["Mon", "Tue", "Wed", "Thu", "Fri", None], stop=["corto", "medio", "largo", None])
def sel(rs, combo):
    return [r for r in rs if all(v is None or r[k] == v for k, v in combo.items())]
def score(rs, mode):
    Rs = [r["R"][mode] for r in rs]
    return dict(n=len(Rs), win=round(100 * sum(x >= 4.9 for x in Rs) / len(Rs), 1) if Rs else 0,
                R_medio=round(st.mean(Rs), 3) if Rs else 0)

train = [r for r in rows if r["t"] < CUT]; test = [r for r in rows if r["t"] >= CUT]
results = []
for mode in ("sin BE", "BE a +2R"):
    for vals in itertools.product(*F.values()):
        combo = dict(zip(F.keys(), vals))
        a = sel(train, combo)
        if len(a) < 5:
            continue
        sa = score(a, mode)
        results.append((sa["win"], sa["n"], mode, combo, sa, score(sel(test, combo), mode)))
results.sort(key=lambda x: (-x[0], -x[1]))
tested = len(results)
top = results[:15]
over80 = [x for x in results if x[0] >= 80]
out = dict(setups_totales=len(rows), aprendizaje=len(train), prueba=len(test), combinaciones_probadas=tested,
           con_80pct_en_aprendizaje=len(over80),
           todas_sin_filtros={m: dict(aprendizaje=score(train, m), prueba=score(test, m), todo=score(rows, m)) for m in ("sin BE", "BE a +2R")},
           mejores_15=[dict(modo=m, filtros={k: v for k, v in c.items() if v}, aprendizaje=a, prueba=b) for _, _, m, c, a, b in top],
           de_las_80pct_en_prueba=dict(n_con_operaciones=sum(1 for x in over80 if x[5]["n"] > 0),
                                       acierto_medio_prueba=round(st.mean(x[5]["win"] for x in over80 if x[5]["n"] > 0), 1) if over80 else None,
                                       cuantas_siguen_80=sum(1 for x in over80 if x[5]["n"] >= 3 and x[5]["win"] >= 80)))
json.dump(out, open("busqueda_80_results.json", "w"), indent=1, ensure_ascii=False, default=str)
print(json.dumps(out, indent=1, ensure_ascii=False, default=str))
