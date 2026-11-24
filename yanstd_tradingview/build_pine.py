"""Genera YANSTD_indicador.pine y YANSTD_estrategia.pine desde plantilla.pine.

Marcadores de línea:
  //I  solo en el indicador      //S  solo en la estrategia
  "//X texto"  (un espacio)  -> línea de nivel 0
  "//X     texto"            -> el marcador se sustituye por 3 espacios (conserva la columna)
"""
import re, sys
from pathlib import Path

base = Path(__file__).parent
src = (base / "plantilla.pine").read_text(encoding="utf-8").splitlines()


def build(keep, drop):
    out = []
    for ln in src:
        if ln.startswith(drop):
            continue
        if ln.startswith(keep):
            rest = ln[3:]
            ln = rest[1:] if re.match(r"^ \S", rest) else "   " + rest
        out.append(ln)
    return out


errs = 0
for name, keep, drop in [("YANSTD_indicador.pine", "//I", "//S"), ("YANSTD_estrategia.pine", "//S", "//I")]:
    lines = build(keep, drop)
    for n, ln in enumerate(lines, 1):
        if ln.strip() and not ln.lstrip().startswith("//"):
            ind = len(ln) - len(ln.lstrip(" "))
            if ind % 4:
                print(f"{name}:{n}: sangría {ind} -> {ln.strip()[:60]}")
                errs += 1
        if "\t" in ln:
            print(f"{name}:{n}: tabulador")
            errs += 1
    (base / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(name, len(lines), "líneas")
sys.exit(1 if errs else 0)
