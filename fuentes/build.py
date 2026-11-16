# -*- coding: utf-8 -*-
"""Genera tema2_apuntes_visuales.html (luego se imprime a PDF con Chromium)."""
import html, os

C = {
    "rosa": "#b65c72", "teal": "#4f8487", "ocre": "#a97f3f",
    "morado": "#7f6ea3", "verde": "#647f52", "terra": "#b0654a",
}
INK = "#2b3240"
SOFT = "#f3efe8"

# ---------------------------------------------------------------- SVG helpers
def svg(w, h, body):
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
            f'font-family="Noto Sans, sans-serif">'
            '<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#4a5262"/></marker></defs>'
            f'{body}</svg>')

def txt(x, y, s, fs=13, fill=INK, w="normal", anchor="middle", italic=False):
    lines = s.split("\n")
    lh = fs * 1.25
    y0 = y - (len(lines) - 1) * lh / 2
    st = ' font-style="italic"' if italic else ""
    out = f'<text x="{x}" y="{y0}" font-size="{fs}" fill="{fill}" font-weight="{w}" text-anchor="{anchor}" dominant-baseline="middle"{st}>'
    for i, ln in enumerate(lines):
        out += f'<tspan x="{x}" dy="{0 if i == 0 else lh}">{html.escape(ln)}</tspan>'
    return out + "</text>"

def box(x, y, w, h, fill, label="", tc="#fff", fs=13, rx=10, weight="bold", stroke=None):
    s = f' stroke="{stroke}" stroke-width="2"' if stroke else ""
    r = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{s}/>'
    if label:
        r += txt(x + w / 2, y + h / 2, label, fs, tc, weight)
    return r

def arrow(x1, y1, x2, y2, col="#4a5262", wdt=2.2, dash=False):
    d = ' stroke-dasharray="5 4"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{wdt}" marker-end="url(#ar)"{d}/>'

def circle(cx, cy, r, fill="none", stroke=None, sw=3):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"{s}/>'

def person(cx, cy, s, col):
    return (circle(cx, cy - 34 * s, 22 * s, col) +
            f'<path d="M{cx-40*s},{cy+50*s} Q{cx-40*s},{cy} {cx},{cy} Q{cx+40*s},{cy} {cx+40*s},{cy+50*s} Z" fill="{col}"/>')

def doc_icon(x, y, w, h, col, lines=3, light="#fff"):
    f = w * 0.28
    out = f'<path d="M{x},{y} h{w-f} l{f},{f} v{h-f} h{-w} z" fill="{col}"/>'
    out += f'<path d="M{x+w-f},{y} v{f} h{f} z" fill="{light}" opacity=".45"/>'
    for i in range(lines):
        ly = y + h * 0.45 + i * h * 0.15
        out += f'<rect x="{x+w*0.18}" y="{ly}" width="{w*0.64}" height="{h*0.06}" rx="2" fill="{light}" opacity=".85"/>'
    return out

# ---------------------------------------------------------------- figures
def fig_hub(col, center, labels):
    cols = [C["morado"], C["verde"], C["teal"], C["ocre"]]
    b = circle(160, 130, 62, "#fff", col, 4) + txt(160, 130, center, 17, col, "bold")
    pos = [(20, 20), (200, 20), (20, 190), (200, 190)]
    for (x, y), lab, c in zip(pos, labels, cols):
        b += box(x, y, 100, 50, c, lab, fs=12)
    return svg(320, 260, b)

def fig_levels():
    data = [("1 · Transmisión física", "señales, cables, ondas", C["teal"]),
            ("2 · Lenguaje o código", "alfabeto, bits, idioma", C["verde"]),
            ("3 · Significado", "qué dice el mensaje", C["ocre"]),
            ("4 · Relevancia", "qué importa a quien lo recibe", C["rosa"])]
    b = ""
    for i, (a, s, c) in enumerate(reversed(data)):
        y = 10 + i * 62
        w = 300 - (3 - i) * 0
        b += box(10 + i * 0, y, 300, 52, c, "", rx=8)
        b += txt(160, y + 18, a, 14, "#fff", "bold") + txt(160, y + 37, s, 11, "#fff")
    b += txt(160, 268, "Los cuatro niveles actúan a la vez", 11, "#666", italic=True)
    return svg(320, 280, b)

def fig_surprise():
    b = txt(160, 16, "¿Cuánta información trae el mensaje?", 13, INK, "bold")
    b += box(10, 40, 140, 70, "#e9e4da", "«Mañana sale\nel sol»", INK, 12)
    b += box(170, 40, 140, 70, C["ocre"], "«Mañana nieva\nen Sevilla»", "#fff", 12)
    b += txt(80, 128, "muy probable", 11, "#555") + txt(240, 128, "muy improbable", 11, "#555")
    b += f'<rect x="20" y="145" width="120" height="16" rx="8" fill="#e9e4da"/><rect x="20" y="145" width="18" height="16" rx="8" fill="{C["ocre"]}"/>'
    b += f'<rect x="180" y="145" width="120" height="16" rx="8" fill="#e9e4da"/><rect x="180" y="145" width="112" height="16" rx="8" fill="{C["ocre"]}"/>'
    b += txt(80, 178, "poca sorpresa = poca información", 10, "#555")
    b += txt(240, 178, "mucha sorpresa = mucha información", 10, "#555")
    b += txt(160, 215, "Shannon mide probabilidad, no significado:", 11, INK, "bold")
    b += txt(160, 233, "una cadena aleatoria de letras «informa» mucho", 11, INK)
    b += txt(160, 250, "aunque no quiera decir nada.", 11, INK)
    return svg(320, 262, b)

def fig_shannon(col):
    b = ""
    labels = ["Fuente de\ninformación", "Transmisor", "Canal", "Receptor", "Destino"]
    xs = [5, 135, 265, 395, 525]
    for i, (x, l) in enumerate(zip(xs, labels)):
        fill = "#fff" if i == 2 else col
        tc = col if i == 2 else "#fff"
        b += box(x, 40, 110, 60, fill, l, tc, 13, stroke=col if i == 2 else None)
    msgs = ["mensaje", "señal", "señal\nrecibida", "mensaje"]
    for i in range(4):
        x1 = xs[i] + 110; x2 = xs[i + 1]
        b += arrow(x1 + 2, 70, x2 - 2, 70)
        b += txt((x1 + x2) / 2, 120 if i in (1, 2) else 25, msgs[i], 10, "#555", italic=True)
    b += box(255, 150, 130, 44, C["terra"], "Fuente de ruido", "#fff", 12)
    b += arrow(320, 150, 320, 104, C["terra"])
    b += txt(320, 215, "Shannon y Weaver (1949): modelo lineal de la comunicación", 12, "#555", italic=True)
    return svg(640, 230, b)

def fig_entropy():
    b = txt(80, 14, "Ordenado", 13, INK, "bold") + txt(240, 14, "Desordenado", 13, INK, "bold")
    b += f'<rect x="5" y="28" width="150" height="150" rx="10" fill="#fff" stroke="#ddd"/>'
    b += f'<rect x="165" y="28" width="150" height="150" rx="10" fill="#fff" stroke="#ddd"/>'
    for i in range(5):
        for j in range(5):
            b += circle(25 + i * 27, 48 + j * 27, 8, C["verde"])
    import random
    random.seed(7)
    for _ in range(25):
        b += circle(random.randint(180, 300), random.randint(42, 165), 8,
                    random.choice([C["verde"], C["ocre"], C["teal"], C["terra"]]))
    b += txt(80, 200, "«25 círculos verdes\nen cuadrícula 5×5»", 11, "#555")
    b += txt(240, 200, "hay que describir\ncada círculo uno a uno", 11, "#555")
    b += txt(160, 240, "más desorden (entropía) → descripción más larga", 12, C["verde"], "bold")
    return svg(320, 255, b)

def fig_dna():
    import math
    b = ""
    pts1, pts2 = [], []
    for k in range(0, 61):
        y = 10 + k * 4
        x1 = 90 + 45 * math.sin(k / 6)
        x2 = 90 - 45 * math.sin(k / 6)
        pts1.append(f"{x1:.1f},{y}"); pts2.append(f"{x2:.1f},{y}")
        if k % 4 == 0:
            cc = [C["terra"], C["teal"], C["ocre"], C["verde"]][(k // 4) % 4]
            b += f'<line x1="{x1:.1f}" y1="{y}" x2="{x2:.1f}" y2="{y}" stroke="{cc}" stroke-width="4"/>'
    b += f'<polyline points="{" ".join(pts1)}" fill="none" stroke="{C["terra"]}" stroke-width="5"/>'
    b += f'<polyline points="{" ".join(pts2)}" fill="none" stroke="#7a3e2c" stroke-width="5"/>'
    items = [("ADN", "código genético"), ("Células", "señales químicas"),
             ("Animales", "comunicación"), ("Memoria\nexterna", "marcas, nidos, rastros")]
    for i, (a, s) in enumerate(items):
        y = 20 + i * 62
        b += box(185, y, 130, 50, [C["terra"], C["teal"], C["ocre"], C["verde"]][i], "", rx=8)
        b += txt(250, y + 18, a.replace("\n", " "), 12, "#fff", "bold")
        b += txt(250, y + 36, s, 10, "#fff")
    return svg(320, 262, b)

def fig_matrix():
    b = txt(200, 14, "¿Hay intención de dañar?", 13, INK, "bold")
    b += txt(140, 36, "No", 12, "#555", "bold") + txt(270, 36, "Sí", 12, "#555", "bold")
    b += f'<text x="18" y="140" font-size="13" font-weight="bold" fill="{INK}" text-anchor="middle" transform="rotate(-90 18 140)">¿Es verdad?</text>'
    b += txt(52, 95, "Sí", 12, "#555", "bold") + txt(52, 195, "No", 12, "#555", "bold")
    b += box(75, 50, 128, 90, C["verde"], "Información\nveraz", fs=13)
    b += box(207, 50, 128, 90, C["morado"], "Malinformación", fs=13)
    b += box(75, 145, 128, 90, C["ocre"], "Información\nerrónea", fs=13)
    b += box(207, 145, 128, 90, C["rosa"], "Desinformación", fs=13)
    b += txt(200, 256, "Wardle y Derakhshan (2017), Consejo de Europa", 10, "#666", italic=True)
    return svg(345, 268, b)

def fig_tree():
    b = box(110, 5, 140, 40, INK, "¿Es verdad?", fs=13)
    b += arrow(150, 45, 80, 85) + arrow(210, 45, 280, 85)
    b += txt(100, 62, "Sí", 11, "#555", "bold") + txt(262, 62, "No", 11, "#555", "bold")
    b += box(10, 88, 140, 40, "#5d6577", "¿Quiere dañar?", fs=12)
    b += box(210, 88, 140, 40, "#5d6577", "¿Quiere dañar?", fs=12)
    b += arrow(50, 128, 40, 165) + arrow(110, 128, 120, 165)
    b += arrow(250, 128, 240, 165) + arrow(310, 128, 320, 165)
    b += txt(35, 146, "No", 10, "#555") + txt(127, 146, "Sí", 10, "#555")
    b += txt(235, 146, "No", 10, "#555") + txt(327, 146, "Sí", 10, "#555")
    b += box(0, 168, 85, 50, C["verde"], "Veraz", fs=12)
    b += box(90, 168, 85, 50, C["morado"], "Malinfor-\nmación", fs=11)
    b += box(185, 168, 85, 50, C["ocre"], "Errónea", fs=12)
    b += box(275, 168, 85, 50, C["rosa"], "Desinfor-\nmación", fs=11)
    return svg(360, 225, b)

def fig_relevance():
    b = ""
    for i in range(5):
        x = 10 + i * 60
        col = C["ocre"] if i == 1 else "#cfc6b6"
        b += doc_icon(x, 40, 48, 64, col)
    b += circle(98, 72, 44, "none", INK, 6)
    b += f'<line x1="130" y1="104" x2="165" y2="140" stroke="{INK}" stroke-width="10" stroke-linecap="round"/>'
    rows = [("Tema", "¿trata de lo que busco?"), ("Novedad", "¿aporta algo que no tenga ya?"),
            ("Idioma y nivel", "¿puedo leerlo y entenderlo?"), ("Actualidad", "¿está vigente?")]
    for i, (a, s) in enumerate(rows):
        y = 160 + i * 26
        b += box(10, y, 95, 22, C["ocre"], a, fs=10, rx=5)
        b += txt(115, y + 11, s, 11, INK, anchor="start")
    return svg(320, 270, b)

def fig_body(col, labels):
    b = person(160, 120, 1.7, col)
    pos = [(5, 20, 115, 150), (215, 20, 205, 150), (5, 210, 110, 210), (215, 210, 210, 210)]
    for (x, y, lx, ly), lab in zip(pos, labels):
        b += box(x, y, 100, 44, "#fff", lab, col, 11, stroke=col)
    return svg(320, 270, b)

def fig_three_uses():
    b = ""
    items = [("Cosa", "documento,\nobjeto, dato", C["rosa"]),
             ("Proceso", "acto de\ninformarse", C["teal"]),
             ("Conocimiento", "lo que se\ncomunica", C["ocre"])]
    for i, (a, s, c) in enumerate(items):
        y = 10 + i * 82
        b += box(10, y, 300, 70, c, "", rx=10)
        b += txt(110, y + 35, a, 16, "#fff", "bold")
        b += txt(240, y + 35, s, 11, "#fff")
    b += doc_icon(26, 22, 30, 42, "#ffffff", 2, C["rosa"])
    b += f'<path d="M30,127 a20,20 0 1,1 8,15" fill="none" stroke="#fff" stroke-width="4"/>'
    b += circle(42, 209, 16, "#fff") + circle(42, 209, 6, C["ocre"])
    b += txt(160, 262, "Buckland (1991), «Information as thing»", 10, "#666", italic=True)
    return svg(320, 272, b)

def fig_pyramid(col_list, labels, notes=None, w=320):
    b = ""
    n = len(labels)
    H = 46
    top = 10
    cx = 145
    for i, lab in enumerate(labels):
        y = top + i * H
        half_t = 24 * i
        half_b = 24 * (i + 1)
        if i == 0:
            half_t = 2
        pts = f"{cx-half_t},{y} {cx+half_t},{y} {cx+half_b},{y+H-4} {cx-half_b},{y+H-4}"
        b += f'<polygon points="{pts}" fill="{col_list[i]}"/>'
        b += txt(cx, y + H / 2 + 2, lab, 12 if i else 9, "#fff", "bold")
        if notes:
            b += txt(cx + half_b + 12, y + H / 2, notes[i], 10, INK, anchor="start")
    b += arrow(w - 14, top + n * H - 6, w - 14, top + 4, "#888")
    b += f'<text x="{w-4}" y="{top + n*H/2}" font-size="10" fill="#777" text-anchor="middle" transform="rotate(-90 {w-4} {top + n*H/2})">más significado y contexto</text>'
    return svg(w, top + n * H + 10, b)

def fig_bellinger():
    b = f'<line x1="70" y1="230" x2="420" y2="230" stroke="{INK}" stroke-width="2" marker-end="url(#ar)"/>'
    b += f'<line x1="70" y1="230" x2="70" y2="10" stroke="{INK}" stroke-width="2" marker-end="url(#ar)"/>'
    ys = ["Reunir\nlas partes", "Conectar\nlas partes", "Formar\nun todo", "Unir\nel todo"]
    xs = ["Investigar", "Absorber", "Hacer", "Interactuar", "Reflexionar"]
    for i, l in enumerate(ys):
        b += txt(35, 200 - i * 50, l, 9, "#444")
    for i, l in enumerate(xs):
        b += txt(100 + i * 75, 246, l, 10, "#444")
    steps = [("Datos", "#2f5f8f"), ("Información", "#6a4c93"), ("Conocimiento", "#c94b4b"), ("Sabiduría", "#e08b2a")]
    for i, (l, c) in enumerate(steps):
        b += box(85 + i * 82, 182 - i * 50, 92, 32, c, l, fs=11, rx=6)
    b += f'<path d="M110,150 L330,30" stroke="{C["teal"]}" stroke-width="16" stroke-linecap="round" opacity=".35"/>'
    b += txt(205, 78, "Comprensión", 12, C["teal"], "bold")
    b += f'<line x1="120" y1="222" x2="400" y2="90" stroke="#3b7fbf" stroke-width="1.5" stroke-dasharray="4 4"/>'
    b += txt(245, 200, "pasado", 10, "#3b7fbf", italic=True) + txt(385, 118, "futuro", 10, "#3b7fbf", italic=True)
    return svg(430, 258, b)

def fig_bates():
    steps = [("Información 1", "patrón de organización\nde materia y energía"),
             ("Datos 1", "parte que un\norganismo percibe"),
             ("Información 2", "patrón al que un ser\nvivo da significado"),
             ("Datos 2", "información seleccionada\no registrada por humanos"),
             ("Conocimiento", "información con significado,\nintegrada con lo que sabemos")]
    cols = [C["teal"], C["ocre"], C["morado"], C["terra"], C["verde"]]
    b = ""
    for i, ((a, s), c) in enumerate(zip(steps, cols)):
        y = 5 + i * 52
        b += box(5, y, 120, 40, c, a, fs=12)
        b += txt(140, y + 20, s, 10, INK, anchor="start")
        if i < 4:
            b += arrow(65, y + 40, 65, y + 51)
    return svg(320, 265, b)

def fig_floridi():
    b = ""
    items = [("Bien formados", "sintaxis correcta", C["terra"]),
             ("Significativos", "tienen sentido en un código", C["ocre"]),
             ("Verídicos", "se corresponden con la realidad", C["verde"])]
    b += box(20, 5, 280, 34, "#d9d2c5", "DATOS", INK, 13)
    for i, (a, s, c) in enumerate(items):
        y = 55 + i * 58
        inset = 15 + i * 22
        b += arrow(160, y - 14, 160, y - 2)
        b += box(inset, y, 320 - 2 * inset, 44, c, "", rx=8)
        b += txt(160, y + 15, a, 13, "#fff", "bold") + txt(160, y + 32, s, 10, "#fff")
    b += arrow(160, 231, 160, 244)
    b += box(95, 246, 130, 30, INK, "INFORMACIÓN", "#fff", 12)
    return svg(320, 282, b)

def fig_semantic():
    b = box(70, 5, 180, 44, C["rosa"], "Contenido semántico\n(bien formado + significativo)", fs=11)
    b += arrow(110, 49, 50, 92) + arrow(160, 49, 160, 92) + arrow(210, 49, 270, 92)
    b += box(0, 95, 100, 50, C["verde"], "Información", fs=12)
    b += box(110, 95, 100, 50, C["ocre"], "Información\nerrónea", fs=11)
    b += box(220, 95, 100, 50, C["morado"], "Desinfor-\nmación", fs=11)
    b += txt(50, 160, "verdadera", 10, "#555") + txt(160, 160, "falsa, sin querer", 10, "#555") + txt(270, 160, "falsa, a propósito", 10, "#555")
    b += f'<rect x="0" y="180" width="320" height="70" rx="10" fill="#fff" stroke="{C["rosa"]}" stroke-dasharray="5 4"/>'
    b += txt(160, 200, "¿Y la malinformación?", 12, C["rosa"], "bold")
    b += txt(160, 225, "Es verdadera (información para Floridi),\npero se difunde para hacer daño.", 10, INK)
    return svg(320, 255, b)

def fig_theories():
    b = circle(160, 130, 52, "#fff", C["teal"], 4) + txt(160, 130, "Información\nen todos\nlos ámbitos", 11, C["teal"], "bold")
    items = [(5, 10, "Burgin", "Teoría General\nde la Información", C["teal"]),
             (195, 10, "Brenner y Wu", "Metafilosofía\ncentrada en la inf.", C["ocre"]),
             (5, 195, "Hofkirchner", "Teoría Unificada\nde la Información", C["verde"]),
             (195, 195, "Brier", "Cibersemiótica", C["morado"])]
    for x, y, a, s, c in items:
        b += box(x, y, 120, 58, c, "", rx=8)
        b += txt(x + 60, y + 16, a, 12, "#fff", "bold") + txt(x + 60, y + 39, s, 10, "#fff")
    return svg(320, 260, b)

def fig_conclusions():
    items = [("1", "Concepto central", C["rosa"]), ("2", "Complejo y\nmultifacético", C["teal"]),
             ("3", "Base: Shannon", C["verde"]), ("4", "Enfoque CID:\nFloridi", C["terra"])]
    b = ""
    for i, (n, l, c) in enumerate(items):
        x = 10 + (i % 2) * 155; y = 10 + (i // 2) * 120
        b += box(x, y, 145, 105, c, "", rx=12)
        b += txt(x + 72, y + 30, n, 26, "#fff", "bold") + txt(x + 72, y + 72, l, 12, "#fff", "bold")
    return svg(320, 245, b)

def fig_briet():
    b = txt(80, 14, "No es documento", 12, "#888", "bold") + txt(250, 14, "Es documento", 12, C["verde"], "bold")
    rows = [("★", "Estrella en el cielo", "Fotografía o catálogo\nde estrellas"),
            ("◆", "Piedra en el torrente", "Piedra etiquetada\nen un museo"),
            ("●", "Antílope en la sabana", "Antílope registrado\nen un zoo")]
    for i, (ic, a, s) in enumerate(rows):
        y = 34 + i * 72
        b += box(5, y, 150, 58, "#ebe6dd", a, "#666", 11, weight="normal")
        b += arrow(160, y + 29, 182, y + 29, C["verde"])
        b += box(185, y, 135, 58, C["verde"], s, fs=11)
    b += txt(160, 262, "Briet (1951): lo que convierte algo en documento\nes que se trate como evidencia", 10, "#555", italic=True)
    return svg(320, 282, b)

def fig_spectrum():
    b = f'<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{C["terra"]}"/><stop offset="1" stop-color="#e3d6c9"/></linearGradient></defs>'
    b += f'<rect x="10" y="40" width="300" height="18" rx="9" fill="url(#g)"/>'
    b += txt(10, 22, "claramente documento", 10, C["terra"], "bold", "start")
    b += txt(310, 22, "dudoso", 10, "#999", "bold", "end")
    items = ["Libro", "Foto de\nla Luna", "Muestra\netiquetada", "Escultura", "Antílope\nen el zoo", "Luna en el\ntelescopio"]
    for i, it in enumerate(items):
        x = 25 + i * 54
        b += circle(x, 49, 6, "#fff", INK, 2)
        y = 95 if i % 2 == 0 else 135
        b += f'<line x1="{x}" y1="57" x2="{x}" y2="{y-16}" stroke="#aaa"/>'
        b += txt(x, y, it, 10, INK)
    b += txt(160, 190, "docere (enseñar, informar)", 13, C["terra"], "bold")
    b += txt(160, 212, "+ -mentum (medio, instrumento)", 13, C["terra"], "bold")
    b += txt(160, 240, "«medio para enseñar o informar»", 11, "#555", italic=True)
    return svg(320, 255, b)

def fig_pioneers():
    data = [("PO", "Paul Otlet", "1868–1944", C["rosa"]), ("HL", "Henri La Fontaine", "1854–1943", C["teal"]),
            ("FD", "Frits Donker Duyvis", "1894–1961", C["ocre"]), ("SB", "Suzanne Briet", "1894–1989", C["morado"])]
    b = ""
    for i, (ini, n, d, c) in enumerate(data):
        y = 8 + i * 64
        b += circle(35, y + 26, 26, c) + txt(35, y + 27, ini, 14, "#fff", "bold")
        b += txt(72, y + 17, n, 13, INK, "bold", "start") + txt(72, y + 36, d, 11, "#666", anchor="start")
    return svg(320, 265, b)

def fig_shift():
    b = box(10, 30, 130, 70, "#d9d2c5", "Comunicación\n(textos impresos)", INK, 12)
    b += arrow(145, 65, 175, 65, C["teal"], 4)
    b += box(180, 30, 130, 70, C["teal"], "Evidencia\n(cualquier objeto)", fs=12)
    b += txt(160, 130, "Buckland: información como cosa", 12, C["teal"], "bold")
    b += f'<rect x="10" y="150" width="300" height="96" rx="10" fill="#fff" stroke="{C["teal"]}"/>'
    b += txt(160, 172, "Ejemplo", 11, C["teal"], "bold")
    b += txt(160, 205, "Un hacha de sílex no se hizo para informar,\npero en un museo es evidencia de cómo\nvivían sus autores: funciona como documento.", 10, INK)
    return svg(320, 255, b)

def fig_neodoc():
    b = box(85, 5, 150, 50, C["ocre"], "Teoría del\ndocumento", fs=13)
    b += arrow(130, 55, 70, 95) + arrow(190, 55, 250, 95)
    b += box(5, 98, 140, 60, "#fff", "Naturaleza y\natributos", C["ocre"], 12, stroke=C["ocre"])
    b += box(175, 98, 140, 60, "#fff", "Procesos de\ndocumentación", C["ocre"], 12, stroke=C["ocre"])
    b += arrow(75, 158, 75, 190) + arrow(245, 158, 245, 190)
    b += box(5, 193, 140, 50, C["morado"], "Intencionales", fs=12)
    b += box(175, 193, 140, 50, C["verde"], "crear, organizar,\nusar…", fs=11)
    b += txt(75, 258, "+ atributivos", 11, C["morado"], "bold")
    return svg(320, 270, b)

def fig_intent():
    b = box(5, 5, 150, 36, C["morado"], "Intencional", fs=13)
    b += box(165, 5, 150, 36, C["verde"], "Atributivo", fs=13)
    b += doc_icon(50, 60, 60, 80, C["morado"])
    # leaf
    b += f'<path d="M240,145 C190,120 195,70 245,55 C290,75 290,125 240,145 Z" fill="{C["verde"]}"/>'
    b += f'<path d="M240,145 L245,58" stroke="#fff" stroke-width="3"/>'
    b += txt(80, 165, "se crea para\nser documento", 11, INK)
    b += txt(240, 165, "pasa a serlo al\nusarse como evidencia", 11, INK)
    b += txt(80, 210, "libro · fotografía", 11, C["morado"], "bold")
    b += txt(240, 210, "planta de herbario", 11, C["verde"], "bold")
    b += txt(160, 245, "Lo decisivo es la función, no la forma física.", 11, "#555", italic=True)
    return svg(320, 258, b)

def fig_pentagon():
    import math
    labels = ["Indizabilidad", "Documentalidad", "Complemen-\ntariedad", "Fijeza", "Productividad"]
    cols = [C["teal"], C["ocre"], C["terra"], C["rosa"], C["morado"]]
    cx, cy, R = 160, 135, 95
    pts = []
    b = ""
    for i in range(5):
        a = -math.pi / 2 + i * 2 * math.pi / 5
        pts.append((cx + R * math.cos(a), cy + R * math.sin(a)))
    b += f'<polygon points="{" ".join(f"{x:.0f},{y:.0f}" for x, y in pts)}" fill="none" stroke="{C["verde"]}" stroke-width="3"/>'
    b += txt(cx, cy, "Documento", 14, C["verde"], "bold")
    for (x, y), l, c in zip(pts, labels, cols):
        b += box(x - 55, y - 20, 110, 40, c, l, fs=11)
    return svg(320, 265, b)

def fig_cycle():
    import math
    labels = ["1 Creación", "2 Selección", "3 Organización", "4 Difusión", "5 Preservación", "6 Destrucción"]
    cols = [C["rosa"], C["teal"], C["ocre"], C["morado"], C["verde"], C["terra"]]
    cx, cy, R = 160, 130, 92
    b = circle(cx, cy, R, "none", "#d3cbbd", 10)
    b += txt(cx, cy, "Cadena de la\ninformación\nregistrada", 11, INK, "bold")
    for i, (l, c) in enumerate(zip(labels, cols)):
        a = -math.pi / 2 + i * math.pi / 3
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        b += box(x - 55, y - 17, 110, 34, c, l, fs=11)
    return svg(320, 262, b)

def fig_biblio():
    items = [("1", "Descripción"), ("2", "Selección"), ("3", "Organización"), ("4", "Difusión")]
    cols = [C["rosa"], C["teal"], C["ocre"], C["morado"]]
    b = txt(160, 14, "Qué hace la bibliografía", 13, INK, "bold")
    for i, ((n, l), c) in enumerate(zip(items, cols)):
        x = 5 + i * 79
        b += box(x, 34, 72, 72, c, "", rx=36)
        b += txt(x + 36, 62, n, 20, "#fff", "bold") + txt(x + 36, 86, l, 9, "#fff", "bold")
        if i < 3:
            b += arrow(x + 72, 70, x + 79, 70)
    b += box(5, 130, 145, 60, "#fff", "Bibliografía\ndesde el s. XVIII", C["rosa"], 11, stroke=C["rosa"])
    b += arrow(152, 160, 168, 160)
    b += box(170, 130, 145, 60, C["rosa"], "Documentación\n(finales s. XIX)", fs=11)
    b += txt(160, 220, "Del 0 (información en bruto)\nal 5 (listas de listas de listas)", 11, "#555", italic=True)
    return svg(320, 250, b)

def fig_levels_stack():
    labels = ["5 · Quinario", "4 · Cuaternario", "3 · Terciario", "2 · Secundario", "1 · Primario", "0 · Cero"]
    b = ""
    for i, l in enumerate(labels):
        y = 5 + i * 40
        w = 160 + i * 28
        op = 0.45 + i * 0.11
        b += f'<rect x="{160-w/2}" y="{y}" width="{w}" height="34" rx="6" fill="{C["teal"]}" opacity="{op:.2f}"/>'
        b += txt(160, y + 17, l, 12, "#fff", "bold")
    b += txt(160, 258, "cada nivel apunta al de abajo", 11, "#555", italic=True)
    return svg(320, 270, b)

def fig_collections():
    b = circle(110, 115, 85, C["ocre"]) + txt(85, 115, "Colección\nfísica", 13, "#fff", "bold")
    b += f'<circle cx="215" cy="115" r="85" fill="{C["teal"]}" opacity=".85"/>' + txt(240, 115, "Colección\ndigital", 13, "#fff", "bold")
    b += txt(110, 222, "propiedad · ubicación", 11, C["ocre"], "bold")
    b += txt(215, 245, "acceso · vínculos · criterios", 11, C["teal"], "bold")
    return svg(320, 258, b)

def fig_domain():
    b = f'<polygon points="160,20 300,240 20,240" fill="none" stroke="{C["verde"]}" stroke-width="4"/>'
    b += box(95, 5, 130, 46, C["verde"], "Ontológica\n¿de qué trata?", fs=11)
    b += box(0, 215, 130, 46, C["ocre"], "Epistemológica\n¿cómo se conoce?", fs=11)
    b += box(190, 215, 130, 46, C["morado"], "Sociológica\n¿quiénes intervienen?", fs=10)
    b += txt(160, 165, "DOMINIO", 16, C["verde"], "bold")
    return svg(320, 268, b)

def fig_terms():
    items = ["Generales", "Temáticos", "Uso especial", "Nombres\npropios", "Nombres\nespecíficos", "Recuperación"]
    cols = [C["terra"], C["ocre"], C["teal"], C["verde"], C["morado"], C["rosa"]]
    b = ""
    for i, (l, c) in enumerate(zip(items, cols)):
        x = 5 + (i % 3) * 105; y = 5 + (i // 3) * 115
        b += box(x, y, 98, 100, c, "", rx=10)
        b += txt(x + 49, y + 30, str(i + 1), 22, "#fff", "bold") + txt(x + 49, y + 70, l, 11, "#fff", "bold")
    b += txt(160, 250, "de lo general a lo especializado →", 11, "#555", italic=True)
    return svg(320, 262, b)

def fig_chem():
    b = f'<rect x="0" y="0" width="320" height="260" rx="10" fill="#fff" stroke="#ddd"/>'
    b += txt(160, 22, "Dapsona: una sustancia, muchas representaciones", 11, INK, "bold")
    # two benzene rings + S
    import math
    def ring(cx, cy, r):
        pts = " ".join(f"{cx + r*math.cos(math.pi/6 + k*math.pi/3):.1f},{cy + r*math.sin(math.pi/6 + k*math.pi/3):.1f}" for k in range(6))
        return f'<polygon points="{pts}" fill="none" stroke="{INK}" stroke-width="2.5"/>' + circle(cx, cy, r * 0.55, "none", INK, 1.5)
    b += ring(90, 85, 30) + ring(230, 85, 30)
    b += f'<line x1="116" y1="85" x2="148" y2="85" stroke="{INK}" stroke-width="2.5"/><line x1="172" y1="85" x2="204" y2="85" stroke="{INK}" stroke-width="2.5"/>'
    b += txt(160, 86, "S", 16, C["ocre"], "bold")
    b += f'<line x1="157" y1="76" x2="157" y2="62" stroke="{INK}" stroke-width="2"/><line x1="163" y1="76" x2="163" y2="62" stroke="{INK}" stroke-width="2"/>'
    b += f'<line x1="157" y1="96" x2="157" y2="110" stroke="{INK}" stroke-width="2"/><line x1="163" y1="96" x2="163" y2="110" stroke="{INK}" stroke-width="2"/>'
    b += txt(160, 54, "O", 12, C["terra"], "bold") + txt(160, 119, "O", 12, C["terra"], "bold")
    b += f'<line x1="64" y1="85" x2="40" y2="85" stroke="{INK}" stroke-width="2.5"/><line x1="256" y1="85" x2="280" y2="85" stroke="{INK}" stroke-width="2.5"/>'
    b += txt(26, 86, "H₂N", 11, C["teal"], "bold") + txt(298, 86, "NH₂", 11, C["teal"], "bold")
    rows = [("Fórmula", "C₁₂H₁₂N₂O₂S"), ("Masa media", "248,30 Da"),
            ("SMILES", "Nc1ccc(cc1)S(=O)(=O)c1ccc(N)cc1"), ("InChIKey", "MQJKPEGWNLWLTK-UHFFFAOYSA-N")]
    for i, (a, v) in enumerate(rows):
        y = 150 + i * 26
        b += txt(14, y, a, 10, "#777", "bold", "start") + txt(95, y, v, 10, INK, anchor="start")
    return svg(320, 260, b)

def fig_history():
    b = box(5, 5, 150, 40, C["teal"], "Ciencia social", fs=13)
    b += box(165, 5, 150, 40, C["ocre"], "Humanidad", fs=13)
    # trend chart
    b += f'<rect x="5" y="55" width="150" height="110" rx="8" fill="#fff" stroke="#ddd"/>'
    b += f'<polyline points="20,145 50,130 80,120 110,95 140,75" fill="none" stroke="{C["teal"]}" stroke-width="3"/>'
    for x, y in [(20, 150), (35, 128), (50, 138), (70, 112), (90, 125), (110, 100), (125, 82), (140, 88)]:
        b += circle(x, y, 3.5, C["teal"])
    b += f'<rect x="165" y="55" width="150" height="110" rx="8" fill="#fff" stroke="#ddd"/>'
    b += doc_icon(205, 70, 40, 54, C["ocre"])
    b += f'<path d="M255,120 q20,-30 40,-10" fill="none" stroke="{C["ocre"]}" stroke-width="3"/>'
    b += txt(80, 185, "tendencias y\n«leyes» generales", 11, INK)
    b += txt(240, 185, "eventos únicos y\nrelatos individuales", 11, INK)
    b += txt(160, 240, "Dos maneras de entender la disciplina\n→ dos maneras de usar sus fuentes", 11, "#555", italic=True)
    return svg(320, 265, b)

def fig_synthesis():
    items = [("1", "Información", "concepto central;\nShannon + Floridi", C["teal"]),
             ("2", "Documentos", "evidencia que funciona\ncomo información", C["ocre"]),
             ("3", "Dominios", "el contexto que\ncondiciona el uso", C["rosa"])]
    b = ""
    for i, (n, a, s, c) in enumerate(items):
        y = 5 + i * 85
        b += box(5, y, 310, 75, c, "", rx=12)
        b += circle(45, y + 37, 24, "#fff") + txt(45, y + 38, n, 20, c, "bold")
        b += txt(90, y + 24, a, 15, "#fff", "bold", "start") + txt(90, y + 52, s.replace("\n", " "), 10, "#fff", anchor="start")
    return svg(320, 262, b)

# ---------------------------------------------------------------- page template
def page(num, col, block, title, orig, body, fig=None, remember=(), hint="", layout="split", figcap=""):
    remember_html = "".join(f"<li>{r}</li>" for r in remember)
    if fig is None:
        main = f'<div class="main full">{body}</div>'
    elif layout == "split":
        main = (f'<div class="main split"><div class="text">{body}</div>'
                f'<figure class="fig">{fig}{f"<figcaption>{figcap}</figcaption>" if figcap else ""}</figure></div>')
    elif layout == "splitL":
        main = (f'<div class="main split left"><figure class="fig">{fig}{f"<figcaption>{figcap}</figcaption>" if figcap else ""}</figure>'
                f'<div class="text">{body}</div></div>')
    elif layout == "below":
        main = (f'<div class="main"><div class="text">{body}</div>'
                f'<figure class="fig below">{fig}</figure></div>')
    else:  # stacked: figure wide on top
        main = (f'<div class="main"><figure class="fig wide">{fig}{f"<figcaption>{figcap}</figcaption>" if figcap else ""}</figure>'
                f'<div class="text">{body}</div></div>')
    return f'''
<section class="page" style="--c:{col}">
  <div class="band"></div>
  <header><div class="kicker">TEMA 2 · {block}</div><h1>{title}</h1>
  <div class="orig">Ideas clave · diapositiva original {orig}</div></header>
  {main}
  <div class="remember"><h2>Para entenderlo y recordarlo</h2><ul>{remember_html}</ul></div>
  <div class="hint"><b>Pista visual</b> {hint}</div>
  <div class="num">{num:02d}</div>
</section>'''

B1 = "1. INFORMACIÓN"
B2 = "2. DOCUMENTOS Y DOCUMENTACIÓN"
B3 = "3. ANÁLISIS DEL DOMINIO"

P = []
add = P.append

# 1
add(page(1, C["rosa"], B1, "Un concepto complejo y controvertido", 4, """
<blockquote><cite>Claude Shannon (1953/1993)</cite>Ningún concepto único de información explica satisfactoriamente todas sus posibles aplicaciones.</blockquote>
<blockquote><cite>Capurro y Hjørland (2003)</cite>Casi todas las disciplinas usan el concepto de información en su propio contexto. Hay muchos conceptos de información, insertos en marcos teóricos más o menos explícitos.</blockquote>
<p>Por eso, en este tema no buscamos <em>la</em> definición de información, sino entender las principales y saber cuál conviene a las Ciencias de la Información y la Documentación (CID).</p>
""", fig_hub(C["rosa"], "i → ?", ["Física", "Biología", "Sociedad", "Documentación"]),
["La información no tiene una definición única: cada disciplina la entiende a su manera.",
 "Hasta el creador de la teoría de la información, Shannon, advirtió de ello."],
"El signo <b>i → ?</b> rodeado de cuatro disciplinas: una misma palabra, cuatro respuestas distintas."))

# 2
add(page(2, C["teal"], B1, "Cuatro niveles en cualquier comunicación", 5, """
<p>El diccionario recoge dos sentidos actuales de <b>información</b>: la transmisión de conocimiento y la acción de dar forma o carácter a algo.</p>
<p>Cualquier comunicación de información puede entenderse a la vez en <b>cuatro niveles</b>:</p>
<ol class="steps">
<li><b>La transmisión física</b>: el soporte y la señal.</li>
<li><b>El lenguaje o la codificación</b> utilizada.</li>
<li><b>El significado</b> del mensaje.</li>
<li><b>La importancia</b> del mensaje para un receptor en un contexto concreto.</li>
</ol>
<p>Como recuerda Shannon, no debemos esperar una idea única y simple de información que funcione en todas las circunstancias.</p>
""", fig_levels(),
["Física → código → significado → relevancia: los cuatro niveles conviven en cada mensaje.",
 "Las teorías difieren según el nivel en el que se fijan."],
"Una torre de cuatro pisos: abajo la señal física, arriba lo que el mensaje importa a quien lo recibe."))

# 3
add(page(3, C["ocre"], B1, "Shannon: la primera definición formal", 6, """
<ul class="dots">
<li>Hasta mediados del siglo XX, la información se entendía como la comunicación de hechos o conocimientos significativos, sin ninguna definición formal.</li>
<li>Claude Shannon (1916-2001) dio la <b>primera definición cuantitativa</b> en «Una teoría matemática de la comunicación» (1948), ampliada como libro con Warren Weaver (Shannon y Weaver, 1949).</li>
<li>En su teoría, un mensaje tiene más información cuanto <b>menos probable</b> es la combinación de símbolos. La información se equipara con la sorpresa, la imprevisibilidad y la aleatoriedad.</li>
<li>Shannon buscaba transmitir mensajes de forma eficiente por telégrafo y teléfono, así que <b>no se ocupaba del significado</b> de los mensajes.</li>
</ul>
""", fig_surprise(),
["Información según Shannon = sorpresa: lo improbable informa más.",
 "Su teoría mide la eficiencia de la transmisión e ignora el significado."],
"Dos mensajes con su barra de «sorpresa»: el que casi nunca ocurre llena la barra."))

# 4
add(page(4, C["morado"], B1, "La teoría matemática de Shannon", 7, """
<div class="cards3">
<div><h3>Formalismo estadístico</h3>Relaciona el contenido de información de un mensaje con la probabilidad de sus símbolos, sin atender al significado.</div>
<div><h3>Información = sorpresa</h3>Las combinaciones de símbolos poco probables tienen más contenido informativo: imprevisibilidad y aleatoriedad.</div>
<div><h3>Base de toda teoría</h3>Se acepta universalmente. Sus extensiones para tratar el significado no han tenido un éxito completo.</div>
</div>
""", fig_shannon(C["morado"]),
["Cinco elementos: fuente, transmisor, canal, receptor y destino. El ruido interfiere en el canal.",
 "Es la base aceptada de cualquier teoría general de la información."],
"Una cadena de cinco cajas con una flecha de ruido que entra por el medio, en el canal.",
layout="stacked"))

# 5
add(page(5, C["verde"], B1, "Información en el mundo físico", 8, """
<ul class="dots">
<li>En las últimas décadas, la física ha incorporado la información como una <b>cantidad explícita</b>, igual que la energía o la materia.</li>
<li>Describir con detalle un sistema desordenado exige muchas más palabras que describir uno ordenado y simple. Esas palabras de más corresponden a la <b>entropía</b> (o información) adicional del sistema. La relación entre información y entropía es sutil.</li>
<li>En informática y telecomunicaciones, la información se procesa con dispositivos físicos. Por eso parece natural tratarla como una cantidad física: la información <b>siempre está en algún sistema físico</b>.</li>
</ul>
""", fig_entropy(),
["La física trata la información como una magnitud, al nivel de la materia y la energía.",
 "Clave: su relación con la entropía. Un sistema desordenado necesita una descripción más larga: contiene más información."],
"Dos cajas de círculos: la ordenada se describe en una frase; la desordenada, punto por punto."))

# 6
add(page(6, C["terra"], B1, "Información en el mundo biológico", 9, """
<ul class="dots">
<li>Erwin Schrödinger, pionero de la mecánica cuántica, propuso en <i>¿Qué es la vida?</i> (1944) que los organismos vivos se alimentan de <b>entropía negativa</b>.</li>
<li>Léon Brillouin popularizó en 1956 la etiqueta <b>negentropía</b> para la idea de la información como lo opuesto a la entropía.</li>
</ul>
<p class="lead">Instancias concretas de información en biología:</p>
<ul class="dots">
<li>La codificación de la información genética en el <b>ADN</b>, quizá la más evidente.</li>
<li>La comunicación entre células, plantas y animales.</li>
<li>El uso de <b>memoria externa</b> por especies no humanas (rastros, marcas, construcciones).</li>
</ul>
<p>Desde entonces, la información es un concepto central en biología, y la capacidad de procesarla y transmitirla se considera parte de la definición de vida.</p>
""", fig_dna(),
["Vida = capacidad de procesar y transmitir información.",
 "Schrödinger (1944) → Brillouin (1956): la información como negentropía."],
"La doble hélice del ADN junto a otras tres formas de información biológica."))

# 7
add(page(7, C["rosa"], B1, "Información en el mundo social", 10, """
<p>En el ámbito social, la información se asocia al <b>significado</b> y a la comunicación de hechos y conocimientos. Según su veracidad y la intención de quien la difunde, distinguimos:</p>
<dl class="defs">
<dt>Información veraz</dt><dd>verdadera y correcta.</dd>
<dt>Información errónea</dt><dd>incorrecta, pero difundida sin mala intención.</dd>
<dt>Desinformación</dt><dd>deliberadamente incorrecta.</dd>
<dt>Malinformación</dt><dd>verdadera, pero comunicada con malas intenciones.</dd>
</dl>
<p>Todas forman parte del <b>contenido semántico</b>: la información registrada de la que se ocupa la ciencia de la información.</p>
<p class="q">¿Es la información «la misma cosa» en física, biología y sociedad? Sigue siendo una pregunta abierta (Bawden y Robinson, 2020).</p>
""", fig_matrix(),
["Cuatro tipos que salen de cruzar dos variables: veracidad e intención de dañar.",
 "Si la información es lo mismo en todos los dominios sigue sin respuesta."],
"Una matriz 2 × 2: verdad en un eje, intención de dañar en el otro."))

# 8
add(page(8, C["teal"], B1, "Cómo distinguir los cuatro tipos", 11, """
<p>Seguimos el marco de Wardle y Derakhshan (2017) para el Consejo de Europa, completado con la información veraz como referencia. Basta con dos preguntas: <b>¿es verdad?</b> y <b>¿quien lo difunde quiere hacer daño?</b></p>
<table class="t">
<tr><th>Tipo</th><th>¿Es verdad?</th><th>¿Intención de dañar?</th></tr>
<tr><td><span class="tag" style="background:#647f52">Información veraz</span></td><td>Sí</td><td>No</td></tr>
<tr><td><span class="tag" style="background:#a97f3f">Información errónea</span></td><td>No</td><td>No</td></tr>
<tr><td><span class="tag" style="background:#b65c72">Desinformación</span></td><td>No</td><td>Sí</td></tr>
<tr><td><span class="tag" style="background:#7f6ea3">Malinformación</span></td><td>Sí</td><td>Sí</td></tr>
</table>
<p class="small">Para practicar con casos reales: <b>maldita.es/tag/desinformacion</b> y <b>newtral.es</b>.</p>
""", fig_tree(),
["Dos preguntas bastan: ¿es verdad? y ¿quiere dañar?",
 "La malinformación es la más difícil de detectar porque lo que dice es cierto."],
"Un árbol de decisión: dos preguntas, cuatro hojas de colores."))

# 9
add(page(9, C["ocre"], B1, "Relevancia: la noción clave", 12, """
<ul class="dots">
<li>Proporcionar <b>información relevante</b> es la tarea central de todo servicio de información, y la cantidad de información relevante que ofrece es una métrica importante de su éxito.</li>
<li>Saracevic (2007) sostiene que la relevancia es una de las nociones clave, si no la principal, de la ciencia de la información y, en especial, de la recuperación de información.</li>
<li>La relevancia no basta por sí sola. Si un documento es relevante, otros diez muy parecidos, igual de relevantes, aportan cada vez menos interés y utilidad.</li>
<li>Un documento puede tratar justo del tema buscado y, aun así, servir de poco si es antiguo, está en un idioma que el usuario no lee o está dirigido a especialistas cuando el usuario es lego.</li>
</ul>
<p>Por eso se han propuesto conceptos cercanos: <b>utilidad, uso, pertinencia temática</b> y <b>pertinencia</b>.</p>
""", fig_relevance(),
["Relevante ≠ útil: el tema no lo es todo.",
 "La novedad, el idioma, el nivel y la actualidad deciden si un documento sirve."],
"Una lupa que destaca un documento entre varios iguales, con cuatro filtros debajo."))

# 10
add(page(10, C["morado"], B1, "Información encarnada", 13, """
<p>Los cuerpos humanos pueden ser <b>fuentes y depósitos</b> de información, y eso condiciona cómo entendemos el comportamiento y las prácticas informacionales. En lo social, informar implica significado y comunicación entre personas.</p>
<p>La información encarnada amplía la noción de información <b>más allá del documento</b>: reconoce que el cuerpo percibe, recuerda y comunica.</p>
<ul class="dots">
<li>Tiene sólidas bases filosóficas y un desarrollo consolidado en Ciencias de la Información (Bates, Lloyd, Cox).</li>
<li>Sirve para visibilizar saberes subestimados y proteger derechos culturales, lingüísticos y de accesibilidad.</li>
</ul>
<p>La <b>epistemología feminista</b> ha sido clave para legitimar el conocimiento encarnado. Donna Haraway, en «Situated Knowledges» (<i>Feminist Studies</i>, 14(3), 1988), criticó la pretensión de un conocimiento «desde ninguna parte» y defendió que todo saber es situado y corporal.</p>
""", fig_body(C["morado"], ["Percibe", "Recuerda", "Comunica", "Saber situado"]),
["El cuerpo también es fuente y depósito de información, no solo el documento.",
 "Haraway (1988): todo conocimiento es situado y corporal."],
"Una silueta rodeada de lo que hace el cuerpo con la información: percibir, recordar, comunicar."))

# 11
add(page(11, C["verde"], B1, "El cuerpo, fuente y depósito", 14, """
<div class="cards2">
<div><h3>El cuerpo como fuente</h3>Percibimos con los sentidos y guardamos en el cuerpo saberes que no están en ningún documento.<p class="ex">Ejemplo: un bombero «lee» el humo; una cirujana sabe cuánta presión aplicar.</p></div>
<div><h3>La dimensión social</h3>Informar es compartir significado entre personas: los gestos, las miradas y las distancias también comunican.<p class="ex">Ejemplo: en un laboratorio se aprende observando e imitando a quien tiene experiencia.</p></div>
</div>
<p>No todos los cuerpos perciben igual: la <b>diversidad corporal y sensorial</b> también forma parte de las prácticas informacionales (Bates, 2006; Lloyd, 2010; Cox, 2018).</p>
""", fig_body(C["verde"], ["Sentidos:\nperciben", "Manos:\nsaber hacer", "Gestos y\npostura", "Comunicación\ncon otros"]),
["Sentidos y manos: el cuerpo como fuente. Gestos y relación con otros: la dimensión social.",
 "La diversidad de cuerpos implica diversidad de prácticas informacionales."],
"La silueta con cuatro etiquetas: dos para lo que el cuerpo sabe y dos para lo que comparte."))

# 12
add(page(12, C["terra"], B1, "Implicaciones de la información encarnada", 15, """
<p>Cuatro implicaciones para el comportamiento y las prácticas informacionales:</p>
<div class="cards2 tight">
<div><h3>1 · Conocimiento tácito y procedimental</h3>Mucho de lo que sabemos no se verbaliza ni se registra con facilidad. Polanyi (1966): «sabemos más de lo que podemos decir». El saber del artesano (Sennett, 2008), la destreza de una cirujana o la ejecución automatizada de un músico se activan y transmiten sobre todo con la práctica física.</div>
<div><h3>2 · La experiencia sensorial como búsqueda</h3>El cuerpo no es un receptor pasivo. Vista, oído, tacto, olfato y propiocepción buscan y verifican información. Muchas decisiones profesionales se basan en cómo «se siente», «se ve» o «huele» una situación. Lloyd (2007): los bomberos desarrollan un «sentido del fuego». Los sentidos se educan cultural y profesionalmente.</div>
<div><h3>3 · Transmisión cultural y socialización</h3>Gestos, posturas, expresiones faciales y uso del espacio son depósitos de información culturalmente heredada. Mauss (1936) mostró que cada sociedad moldea sus «técnicas del cuerpo». La interpretación de las señales corporales varía mucho entre culturas.</div>
<div><h3>4 · Aprendizaje situado</h3>Aprender no ocurre solo en la mente individual: se produce participando en <b>comunidades de práctica</b> (Lave y Wenger, 1991), donde la presencia física es central. En talleres, laboratorios u ocio especializado, la información circula entre cuerpos (Cox et al., 2017).</div>
</div>
""", None,
["Tácito (Polanyi) · sensorial (Lloyd) · cultural (Mauss) · situado (Lave y Wenger).",
 "Las cuatro muestran que hay información que solo se transmite con el cuerpo y la práctica."],
"Cuatro tarjetas, un autor por tarjeta: Polanyi, Lloyd, Mauss, Lave y Wenger."))

# 13
add(page(13, C["rosa"], B1, "Tres usos de «información»", 16, """
<dl class="defs big">
<dt>Información como cosa</dt><dd>Asociada a un documento o a una entidad física o digital. Es objetiva y está «contenida» en los documentos; en la práctica equivale a ellos.</dd>
<dt>Información como proceso</dt><dd>Lo que cambia el estado de conocimiento de una persona cuando se informa. Subyace a las teorías del comportamiento informacional.</dd>
<dt>Información como conocimiento</dt><dd>Se equipara con el conocimiento que transmite. Expresa su estrecha relación sin precisar cuál es.</dd>
</dl>
<p>Buckland (1991) defiende la <b>información como cosa</b>: la ciencia de la información trata sobre todo con información en forma de documentos.</p>
""", fig_three_uses(),
["Cosa (el documento), proceso (informarse) y conocimiento (lo que se sabe).",
 "Para Buckland, la ciencia de la información trabaja sobre todo con la información como cosa."],
"Tres franjas: un documento, una flecha que gira y una diana."))

# 14
add(page(14, C["teal"], B1, "De los datos a la sabiduría: DIKUW", 17, """
<p>La jerarquía <b>DIKUW</b> (<i>Data, Information, Knowledge, Understanding, Wisdom</i>) ordena cinco niveles, de abajo arriba:</p>
<dl class="defs">
<dt>Datos</dt><dd>hechos y observaciones sin procesar, sin contexto ni significado propio.</dd>
<dt>Información</dt><dd>datos procesados a los que se da significado y contexto; sirven para responder preguntas y decidir.</dd>
<dt>Conocimiento</dt><dd>comprensión y aplicación de la información, adquiridas con la experiencia y el aprendizaje.</dd>
<dt>Comprensión</dt><dd>integrar y sintetizar conocimiento, identificando patrones y relaciones.</dd>
<dt>Sabiduría</dt><dd>aplicar el conocimiento de forma ética y reflexiva, atendiendo a valores y contexto.</dd>
</dl>
<p class="small">La formulación clásica se atribuye a Ackoff (1989). Rowley (2007) revisó cómo la definen los manuales.</p>
""", fig_pyramid(["#7a3e2c", C["terra"], C["ocre"], "#a08c6a", "#2b3a55"],
                 ["Sabiduría", "Comprensión", "Conocimiento", "Información", "Datos"], w=300),
["Cada nivel añade significado y contexto al anterior.",
 "Ackoff (1989) la formuló; Rowley (2007) revisó sus definiciones."],
"Una pirámide de cinco pisos: cuanto más arriba, menos cantidad y más sentido."))

# 15
add(page(15, C["ocre"], B1, "DIKUW con un ejemplo", 18, """
<p class="small">Los datos son hipotéticos y solo ilustran el modelo.</p>
<table class="t dikuw">
<tr><th>Nivel</th><th>Qué hace</th><th>En el ejemplo</th></tr>
<tr><td><b>Datos</b></td><td>Cifras aisladas, sin contexto.</td><td>«38» y «22» no significan nada por sí solas.</td></tr>
<tr><td><b>Información</b></td><td>Contextualiza: qué se mide, dónde, cuándo y para quién.</td><td>Abandono en 1.º de Ingeniería Informática (2025-26): 38 % mujeres, 22 % hombres.</td></tr>
<tr><td><b>Conocimiento</b></td><td>Relaciona con la experiencia y la literatura previas.</td><td>La diferencia de 16 puntos supera el umbral de alerta del sistema de calidad.</td></tr>
<tr><td><b>Comprensión</b></td><td>Explica el porqué: busca causas y las relaciona.</td><td>La brecha se asocia a la falta de referentes y al sentimiento de no pertenencia en entornos masculinizados.</td></tr>
<tr><td><b>Sabiduría</b></td><td>Juzga qué conviene hacer y por qué.</td><td>Implantar mentoría y acogida con perspectiva de género, con seguimiento del indicador en el sistema de garantía de calidad.</td></tr>
</table>
""", None,
["Datos: cifras. Información: cifras con contexto. Conocimiento: comparación con una referencia.",
 "Comprensión: causas. Sabiduría: decisión justificada y evaluable."],
"Sigue el «38 / 22» de abajo arriba: en cada nivel la cifra gana una capa de sentido."))

# 16
add(page(16, C["morado"], B1, "DIKUW: el camino hacia la comprensión", 19, """
<p>Otra forma de representar el modelo es como un recorrido en el tiempo y en la acción:</p>
<ul class="dots">
<li><b>Eje horizontal</b>: lo que hacemos (investigar, absorber, hacer, interactuar, reflexionar).</li>
<li><b>Eje vertical</b>: cómo se relacionan las partes (reunirlas, conectarlas, formar un todo, unir el todo).</li>
<li>Datos, información y conocimiento miran al <b>pasado</b>: describen lo que ya ocurrió. La sabiduría mira al <b>futuro</b>: orienta qué hacer.</li>
<li>La <b>comprensión</b> no es un escalón más, sino lo que permite pasar de un nivel al siguiente.</li>
</ul>
""", fig_bellinger(),
["Subir en la escala exige actuar (hacer, interactuar, reflexionar), no solo acumular.",
 "La comprensión es el motor que conecta los niveles."],
"Una escalera de cuatro cajas de colores atravesada por una flecha diagonal: la comprensión.",
layout="stacked", figcap="Adaptado del diagrama clásico datos-información-conocimiento-sabiduría."))

# 17
add(page(17, C["verde"], B1, "Hacia teorías unificadas: Stonier y Bates", 20, """
<p>Ha habido intentos de explicar la información en todos los dominios. Los más relevantes para las CID son los de Stonier, Bates y Floridi (este último, en la página siguiente).</p>
<div class="cards2 tight">
<div><h3>Tom Stonier (1927-1999)</h3><ul class="dots">
<li>La información es una <b>entidad física</b>, como la materia y la energía: la capacidad de crear y mantener organización.</li>
<li>Se expresa en la vida, en la inteligencia humana y, por último, en el significado (información registrada).</li>
<li>Su propuesta ha tenido poco desarrollo explícito posterior.</li></ul></div>
<div><h3>Marcia Bates (2005; 2006)</h3><ul class="dots">
<li>Integra la información en los ámbitos físico, biológico y mental.</li>
<li>Distingue una cadena de cinco conceptos: información 1, datos 1, información 2, datos 2 y conocimiento (ver diagrama).</li></ul></div>
</div>
""", fig_bates(),
["Stonier: la información es física, como la materia y la energía.",
 "Bates: el patrón existe → un organismo lo percibe → le da significado → la sociedad lo registra → se integra en lo que sabemos."],
"Una escalera de cinco peldaños que baja de la naturaleza (información 1) al conocimiento."))

# 18
add(page(18, C["terra"], B1, "Floridi: datos bien formados, significativos y verídicos", 21, """
<p><b>Punto de partida. ¿Qué es un dato?</b> Una diferencia que se puede percibir: luz encendida / apagada, un 0 / un 1, tinta negra sobre papel blanco.</p>
<table class="t">
<tr><th>Condición</th><th>Sí</th><th>No</th></tr>
<tr><td><b>Bien formados</b><br><span class="small">siguen las reglas de la sintaxis</span></td><td>«La biblioteca abre a las 8:00»</td><td>«abre biblioteca 8:00 las a la»</td></tr>
<tr><td><b>Significativos</b><br><span class="small">tienen sentido en un código compartido</span></td><td>«La biblioteca abre a las 8:00»</td><td>«Las ideas verdes incoloras duermen furiosamente» (Chomsky, 1957)</td></tr>
<tr><td><b>Verídicos</b><br><span class="small">se corresponden con la realidad</span></td><td>«La Universidad de Murcia está en Murcia»</td><td>«La Universidad de Murcia está en Sevilla»</td></tr>
</table>
<p>Solo cuando se cumplen <b>las tres condiciones</b> hablamos de información (Floridi, 2010, 2011).</p>
""", fig_floridi(),
["Información = datos + sintaxis + significado + verdad.",
 "Si falla una sola condición, no hay información en sentido estricto."],
"Un embudo con tres filtros: forma, sentido y verdad."))

# 19
add(page(19, C["rosa"], B1, "Contenido semántico = datos bien formados y significativos", 22, """
<p>Todo lo que está bien formado y tiene significado es <b>contenido semántico</b>. Según sea verdadero o falso, y según la intención de quien lo difunde, hay tres tipos:</p>
<table class="t">
<tr><th>Tipo</th><th>¿Verdadera?</th><th>¿Intención de engañar?</th><th>Ejemplo</th></tr>
<tr><td><b>Información</b></td><td>Sí</td><td>No</td><td>«Los exámenes empiezan el 7 de enero», en la web oficial.</td></tr>
<tr><td><b>Información errónea</b></td><td>No</td><td>No</td><td>Una compañera escribe en el grupo que empiezan el 17 porque lo leyó mal.</td></tr>
<tr><td><b>Desinformación</b></td><td>No</td><td>Sí</td><td>Una cuenta falsa anuncia que «se suspenden los exámenes» para crear caos.</td></tr>
</table>
<p class="q"><b>Para debatir:</b> para Floridi, la información errónea y la desinformación no son información, aunque lo parezcan. Bates, en cambio, no exige que la información sea verdadera. ¿Dónde encajaría la malinformación, que es verdadera pero se usa para dañar?</p>
""", fig_semantic(),
["Contenido semántico = bien formado + significativo. Información = además, verdadero.",
 "Floridi exige verdad; Bates no."],
"Un tronco (contenido semántico) con tres ramas y una cuarta, la malinformación, en duda.",
layout="below"))

# 20
add(page(20, C["teal"], B1, "Otras teorías unificadas de la información", 23, """
<p>Intentan explicar con un solo concepto qué es la información en todos los ámbitos: la física, la biología, la mente y la sociedad.</p>
<table class="t">
<tr><th>Teoría</th><th>Autoría</th><th>Enfoque</th></tr>
<tr><td>Teoría General de la Información</td><td>Burgin (2010)</td><td>matemático y lógico</td></tr>
<tr><td>Metafilosofía centrada en la información</td><td>Brenner y Wu</td><td>filosófico</td></tr>
<tr><td>Teoría Unificada de la Información</td><td>Hofkirchner (2009, 2010)</td><td>sistemas complejos</td></tr>
<tr><td>Cibersemiótica</td><td>Brier (2008, 2017)</td><td>signos y significado</td></tr>
</table>
<p class="q"><b>¿Por qué las estudiamos?</b> Son marcos ambiciosos que buscan unificar el concepto de información, pero todavía no se han aplicado en las CID. Conocerlas nos ayuda a situar nuestra disciplina en un debate más amplio.</p>
""", fig_theories(),
["Cuatro intentos de unificar el concepto: Burgin, Brenner y Wu, Hofkirchner y Brier.",
 "Aún no se aplican en las CID, pero sitúan la disciplina en el debate."],
"Cuatro cajas alrededor de un mismo círculo: cuatro caminos hacia la misma meta."))

# 21
add(page(21, C["ocre"], B1, "Cuatro teorías, cuatro ideas clave", 24, """
<div class="cards2 tight">
<div><h3>Burgin (2010) · Teoría General de la Información</h3>La información es la capacidad de cambiar un sistema, igual que la energía es la capacidad de cambiar la materia.<p class="ex">Ejemplo: una noticia solo es información para ti si cambia lo que sabes.</p></div>
<div><h3>Brenner y Wu · Metafilosofía centrada en la información</h3>La información forma parte del mundo físico y biológico, junto a la materia y la energía.<p class="ex">Ejemplo: unas huellas en la arena informan de que alguien pasó, aunque nadie las mire.</p></div>
<div><h3>Hofkirchner (2009, 2010) · Teoría Unificada</h3>Un «superconcepto» de información que surge (emerge) en sistemas complejos que se autoorganizan.<p class="ex">Ejemplo: en una colonia de hormigas ninguna manda, pero el grupo «sabe» dónde está la comida.</p></div>
<div><h3>Brier (2008, 2017) · Cibersemiótica</h3>La información solo tiene sentido cuando un ser vivo interpreta un signo. Une biología, mente y sociedad.<p class="ex">Ejemplo: un semáforo en rojo significa «para» para quien conduce, pero nada para un perro.</p></div>
</div>
""", None,
["Burgin: cambio · Brenner y Wu: parte del mundo · Hofkirchner: emergencia · Brier: interpretación de signos.",
 "Asocia cada teoría a su ejemplo: noticia, huellas, hormigas, semáforo."],
"Cuatro tarjetas, cuatro escenas: una noticia, unas huellas, un hormiguero y un semáforo."))

# 22
add(page(22, C["morado"], B1, "Conclusiones sobre la información", 25, """
<ol class="steps">
<li><b>Concepto central.</b> La información es un concepto fundamental, si no el central, de las ciencias de la información y la documentación.</li>
<li><b>Complejo y multifacético.</b> Ninguna comprensión única de la idea funciona en todos los contextos.</li>
<li><b>Base necesaria.</b> La teoría de Shannon se acepta como fundamento de toda teoría general de la información.</li>
<li><b>Enfoque más apropiado.</b> La filosofía de la información de Floridi parece la más adecuada para las CID.</li>
</ol>
""", fig_conclusions(),
["Central y multifacético.", "Shannon es la base; Floridi, el enfoque para las CID."],
"Cuatro casillas numeradas: dos describen el concepto y dos nombran a sus autores clave."))

# 23
add(page(23, C["verde"], B2, "¿Qué es un documento?", 27, """
<blockquote><cite>Suzanne Briet (1951, p. 10)</cite>¿Es una estrella un documento? ¿Es una piedra rodada por un torrente un documento? ¿Es un animal vivo un documento? No. Pero las fotografías y los catálogos de estrellas, las piedras en un museo de mineralogía y los animales que están registrados y se exhiben en un zoológico son documentos.</blockquote>
<blockquote><cite>Michael Buckland (2017)</cite>Un objeto se considera documento cuando existe una afirmación o una percepción de que es evidencia de alguna creencia.</blockquote>
""", fig_briet(),
["Un objeto es documento cuando se trata como evidencia, no por lo que es.",
 "Briet (1951) y Buckland (2017) coinciden en esta idea."],
"Tres parejas: el mismo objeto antes y después de convertirse en evidencia."))

# 24
add(page(24, C["terra"], B2, "Preguntas sobre los límites", 28, """
<ul class="dots">
<li>Los documentos, como portadores de información, son centrales en las disciplinas y profesiones de la información. El movimiento de la documentación de la primera mitad del siglo XX fue uno de los precursores de la ciencia de la información.</li>
<li>Aunque los documentos contienen información y datos, <b>no son sinónimos</b> de ninguno de los dos.</li>
<li><b>Etimología:</b> del latín <i>docere</i> (enseñar, informar) y el sufijo <i>-mentum</i> (medio). El diccionario lo define como algo escrito o inscrito que aporta evidencia o información sobre cualquier tema.</li>
</ul>
<p class="lead">¿Dónde está el límite?</p>
<ul class="dots">
<li>¿Una pintura o una escultura? ¿Una muestra geológica etiquetada?</li>
<li>¿Un antílope en un zoo, en un entorno que indica su hábitat?</li>
<li>Si la fotografía de la Luna es un documento, ¿lo es la Luna vista con un telescopio?</li>
</ul>
<p>Estas cuestiones las abordaron los documentalistas europeos de la primera mitad del siglo XX: Paul Otlet, Henri La Fontaine, Frits Donker Duyvis y Suzanne Briet, cuyo texto de 1951 resume las ideas de la época.</p>
""", fig_spectrum(),
["Documento ≠ información ≠ datos.",
 "Docere + -mentum: «medio para enseñar». El límite de qué es documento es discutible."],
"Una línea de grises: del libro, que es claramente documento, a la Luna en el telescopio."))

# 25
add(page(25, C["rosa"], B2, "Los pioneros de la documentación", 29, """
<h3 class="sub">Controlar el saber publicado</h3>
<ul class="dots">
<li>Desde mediados del siglo XIX crece el volumen de información académica publicada, sobre todo en ciencia y tecnología.</li>
<li>La documentación amplía el estudio de la bibliografía (que existe desde el siglo XVIII) a la autoría, la impresión, la publicación y los servicios bibliotecarios.</li>
<li>Los pioneros plantearon por primera vez las preguntas sobre los límites de lo que es un documento y sobre los procesos de documentación.</li>
<li>Su conclusión: <b>cualquier objeto</b> debería considerarse documento si proporciona información y evidencia.</li>
</ul>
""", fig_pioneers(),
["Problema: demasiada información publicada. Respuesta: la documentación.",
 "Conclusión de los pioneros: cualquier objeto que aporte evidencia puede ser documento."],
"Cuatro iniciales: PO, HL, FD y SB, los fundadores de la documentación."))

# 26
add(page(26, C["teal"], B2, "Una conclusión: evidencia", 30, """
<ul class="dots">
<li>Los pioneros ampliaron la idea de documento más allá de los textos impresos, e incluso más allá de los objetos creados con la intención de comunicar.</li>
<li>El énfasis pasó de la <b>comunicación</b> a la <b>evidencia</b>: un documento es un elemento físico que aporta evidencia y, por eso, es informativo.</li>
<li>Buckland desarrolla esta línea en «Information as thing» (1991), donde opone la información como cosa a la información como conocimiento o como proceso, y en «What is a "document"?» (1997).</li>
<li>Esta visión amplia tiene consecuencias prácticas: subdisciplinas enteras, como la <b>documentación de museos</b>, solo tienen sentido si se acepta.</li>
</ul>
""", fig_shift(),
["De la comunicación a la evidencia: el documento como entidad física.",
 "Sin esta idea no existiría la documentación de museos."],
"Una flecha que lleva de «comunicación» a «evidencia»."))

# 27
add(page(27, C["ocre"], B2, "La teoría moderna del documento", 31, """
<ul class="dots">
<li>La teoría moderna del documento, a veces llamada <b>teoría neodocumental</b>, examina el concepto de documento y cómo combinarlo con otros conceptos para entender la comunicación de información y conocimiento en una infosfera donde muchos documentos son digitales.</li>
<li>Además de la naturaleza y los atributos de los documentos, estudia los <b>procesos de documentación</b>, mediante los cuales se crean, organizan y usan.</li>
<li>Los documentos adoptan formas muy diversas, pero hay una distinción común entre dos tipos principales: <b>intencionales</b> y <b>atributivos</b>.</li>
</ul>
""", fig_neodoc(),
["La teoría neodocumental estudia qué son los documentos y qué procesos los crean, organizan y usan.",
 "Primera distinción: documentos intencionales y atributivos."],
"Un árbol con dos ramas: lo que es el documento y lo que se hace con él."))

# 28
add(page(28, C["morado"], B2, "Documentos intencionales y atributivos", 32, """
<table class="t">
<tr><th></th><th>Intencionales</th><th>Atributivos</th></tr>
<tr><td><b>Origen</b></td><td>Se crean deliberadamente como documentos.</td><td>Objetos no creados como documentos que después pasan a serlo.</td></tr>
<tr><td><b>Ejemplos</b></td><td>Libros, fotografías.</td><td>Especímenes de un herbario; objetos de museo tratados como evidencia.</td></tr>
<tr><td><b>Reconocimiento</b></td><td>Casi universal.</td><td>Depende del uso y del contexto.</td></tr>
</table>
<ul class="dots">
<li>Un objeto puede ser documento para una persona, en un momento y con un propósito concretos. Importa más <b>si funciona como documento</b> que su forma física.</li>
<li>Como muchas cosas pueden ser documentos, la teoría se centra en un conjunto de <b>atributos</b> que todos los documentos poseen, al menos en cierta medida.</li>
</ul>
""", fig_intent(),
["Intencional: nace documento. Atributivo: se convierte en documento.",
 "Lo que cuenta es la función, no la forma."],
"Un libro y una hoja de herbario: uno nació documento; la otra llegó a serlo."))

# 29
add(page(29, C["verde"], B2, "Cinco atributos de los documentos", 33, """
<ol class="steps">
<li><b>Indizabilidad.</b> Un documento trata sobre algo o señala algo, como un dedo índice: tiene «sobreidad» y puede actuar como símbolo.</li>
<li><b>Documentalidad.</b> Su poder especial: cumple una función social en un contexto, un momento y un lugar determinados.</li>
<li><b>Complementariedad.</b> Tiene tres dimensiones: material (composición física o técnica), informativa (actividad cognitiva) y social (significado económico, político o cultural).</li>
<li><b>Fijeza.</b> Es lo bastante estable en el tiempo para cumplir su función. Un libro puede durar siglos; los documentos digitales cambian más, y la teoría neodocumental reconoce esa fluidez.</li>
<li><b>Productividad.</b> De un original surgen nuevos documentos, de forma <b>jerárquica</b> (primarios, secundarios, terciarios) o <b>rizomática</b>, sin un documento primario ni prioridades absolutas entre ellos.</li>
</ol>
""", fig_pentagon(),
["Indizabilidad, documentalidad, complementariedad, fijeza y productividad.",
 "Regla mnemotécnica: «I-Do-Co-Fi-Pro»."],
"Un pentágono con el documento en el centro y un atributo en cada vértice."))

# 30
add(page(30, C["terra"], B2, "Los procesos de documentación", 34, """
<table class="t">
<tr><th>Proceso</th><th>Qué incluye</th></tr>
<tr><td><b>1. Creación</b></td><td>Autoría u otra forma de creación.</td></tr>
<tr><td><b>2. Selección</b></td><td>Elección y recolección.</td></tr>
<tr><td><b>3. Organización</b></td><td>Disposición, clasificación e indización.</td></tr>
<tr><td><b>4. Difusión</b></td><td>Copia, reproducción y difusión.</td></tr>
<tr><td><b>5. Preservación</b></td><td>Conservación y digitalización.</td></tr>
<tr><td><b>6. Destrucción</b></td><td>Eliminación del documento (expurgo).</td></tr>
</table>
<div class="cards2 tight">
<div><h3>Más allá de las instituciones</h3>Son los procesos de la cadena de la información registrada, base de bibliotecas y archivos. También importan en la vida cotidiana, para registrar el pasado y planificar el futuro.</div>
<div><h3>Otras entidades como documentos</h3>Tratar los paisajes como documentos permite usarlos como evidencia en juicios sobre derechos de tierras y agua. Tratar los objetos de museo como documentos mejora la experiencia de los visitantes.</div>
</div>
""", fig_cycle(),
["Crear, seleccionar, organizar, difundir, preservar y destruir.",
 "Se aplican a bibliotecas y archivos, a la vida cotidiana y a paisajes u objetos."],
"Un ciclo de seis colores: del nacimiento del documento a su expurgo."))

# 31
add(page(31, C["rosa"], B2, "Categorización y organización de documentos", 35, """
<div class="cards2 tight">
<div><h3>Bibliografía</h3>Desde el siglo XVIII estudia las obras impresas. Se ocupa de su <b>descripción</b>, su <b>selección</b> para fines concretos, su <b>organización</b> y su <b>difusión</b>.</div>
<div><h3>Documentación</h3>Se desarrolla a partir de la bibliografía y crea sistemas de descripción y clasificación: herramientas para organizar los recursos.</div>
</div>
<p>Una forma sencilla y útil de categorizar los documentos es por <b>nivel de recurso</b>: del nivel 0 (información en bruto) al nivel 5 (listas de listas de listas). Los niveles se detallan en la página siguiente.</p>
""", fig_biblio(),
["Bibliografía: describir, seleccionar, organizar, difundir.",
 "La documentación nace de la bibliografía y clasifica los recursos por niveles (0-5)."],
"Cuatro círculos encadenados: las cuatro tareas de la bibliografía."))

# 32
add(page(32, C["teal"], B2, "Niveles de recurso documental", 36, """
<table class="t">
<tr><th>Nivel</th><th>Qué es</th><th>Ejemplos</th></tr>
<tr><td><b>0 · Cero</b></td><td>Información en bruto, antes de entrar en la cadena de comunicación.</td><td>Salida de instrumentos de laboratorio, de una interfaz de búsqueda o de una API.</td></tr>
<tr><td><b>1 · Primario</b></td><td>La «información original».</td><td>Artículos de revista, entradas de blog, tuits.</td></tr>
<tr><td><b>2 · Secundario</b></td><td>Información de valor añadido, que organiza material primario.</td><td>Libros de texto, reseñas, resúmenes.</td></tr>
<tr><td><b>3 · Terciario</b></td><td>Apunta a los primarios y secundarios y facilita su uso.</td><td>Bibliografías, enciclopedias, directorios.</td></tr>
<tr><td><b>4 · Cuaternario</b></td><td>Listas de listas: acceso a recursos de nivel superior.</td><td>Bibliografías de bibliografías.</td></tr>
<tr><td><b>5 · Quinario</b></td><td>Listas de listas de listas.</td><td>Proliferan en la web, igual que los cuaternarios.</td></tr>
</table>
<p class="q"><b>La categorización es subjetiva.</b> Una bibliografía médica es terciaria, pero para un futuro historiador de la sanidad sería primaria. También varía según la disciplina: un historiador considera primarios los documentos de archivo originales, y secundarios los artículos basados en ellos.</p>
""", None,
["0 bruto · 1 original · 2 valor añadido · 3 apunta · 4 listas de listas · 5 listas de listas de listas.",
 "El nivel depende de quién usa el documento y para qué."],
"Una pila que se estrecha hacia arriba: cada nivel apunta al de abajo."))

# 33
add(page(33, C["ocre"], B2, "Colecciones: de la posesión al acceso", 37, """
<ul class="dots">
<li>El diccionario define colección como «un número de objetos recolectados o reunidos, vistos como un todo; un grupo de cosas recolectadas y organizadas».</li>
<li>En las CID, una <b>colección</b> es un conjunto organizado de elementos con información, seleccionados para un propósito en un contexto particular y, por lo general, únicos para esa situación. Las hay en bibliotecas, archivos, museos, galerías y todo tipo de centros de información.</li>
<li>Pasar de colecciones físicas a digitales supone pasar de la <b>propiedad y la ubicación</b> al <b>acceso</b>, algo reconocido desde hace años.</li>
<li>La colección digital es dinámica e impermanente, con ciclos de vida diversos e impredecibles, y en parte ya no está bajo control local.</li>
<li>Como sus recursos se enlazan con otros, cuesta trazar un límite claro sobre lo que está dentro. Un mismo documento digital puede estar a la vez en varias colecciones, algo imposible en el mundo predigital.</li>
</ul>
""", fig_collections(),
["Colección física: poseer y ubicar. Colección digital: dar acceso.",
 "Lo digital difumina los límites: un documento puede estar en varias colecciones a la vez."],
"Dos círculos que se solapan: la zona común son los documentos que viven en ambos mundos."))

# 34
add(page(34, C["morado"], B2, "Colección física frente a colección digital", 38, """
<table class="t">
<tr><th>Dimensión</th><th>Colección física</th><th>Colección digital</th></tr>
<tr><td><b>Base</b></td><td>Propiedad y ubicación.</td><td>Acceso.</td></tr>
<tr><td><b>Límites</b></td><td>Definidos por contención: lo que hay dentro.</td><td>Difusos por los vínculos entre recursos; se definen por criterios de selección.</td></tr>
<tr><td><b>Control</b></td><td>Local.</td><td>En parte, ya no es local.</td></tr>
<tr><td><b>Ciclo de vida</b></td><td>Más estable.</td><td>Dinámico, impermanente, con ciclos diversos e impredecibles.</td></tr>
<tr><td><b>Pertenencia</b></td><td>Cada ítem está en una colección.</td><td>Un mismo documento puede estar en varias colecciones.</td></tr>
</table>
<p class="small">Imagen de la diapositiva original: el Archivo Apostólico Vaticano, ejemplo de colección física, definida por lo que contienen sus estanterías.</p>
""", None,
["Cinco diferencias: base, límites, control, ciclo de vida y pertenencia.",
 "En lo digital, la colección se define por criterios, no por paredes."],
"Las estanterías del Archivo Vaticano frente a una red de enlaces."))

# 35
add(page(35, C["verde"], B3, "Dominios de información", 40, """
<p>Los contextos de uso de la información pueden describirse por área geográfica, tipo de institución o perfil de las personas usuarias. La distinción más útil es el <b>dominio</b>, que suele coincidir con:</p>
<ul class="dots">
<li>una disciplina académica (matemáticas, historia);</li>
<li>una actividad profesional (atención sanitaria, finanzas);</li>
<li>un interés recreativo (coleccionar libros);</li>
<li>la información cotidiana o una comunidad de discurso.</li>
</ul>
<p class="lead">Tres dimensiones definen y explican un dominio:</p>
<dl class="defs">
<dt>Ontológica</dt><dd>su principal objeto de interés: la botánica, las plantas; la historia, el pasado; la teología, lo divino.</dd>
<dt>Epistemológica</dt><dd>el tipo de conocimiento del dominio, o los distintos tipos asociados a paradigmas o formas de comprensión.</dd>
<dt>Sociológica</dt><dd>las personas y grupos que intervienen en el dominio.</dd>
</dl>
""", fig_domain(),
["Dominio = disciplina, profesión, afición o comunidad de discurso.",
 "Se analiza en tres dimensiones: qué estudia, cómo conoce y quién participa."],
"Un triángulo con el dominio en el centro y una dimensión en cada vértice."))

# 36
add(page(36, C["terra"], B3, "Terminología de dominio", 41, """
<p>La <b>denominación estructurada de las cosas</b> es una de las herramientas más básicas para organizar y comunicar información de forma precisa y sin ambigüedad. Todos los dominios tienen la suya; en la información cotidiana, es el diccionario.</p>
<table class="t">
<tr><th>Herramienta</th><th>Descripción</th></tr>
<tr><td><b>1 · Diccionarios generales</b></td><td>Pueden ser multilingües.</td></tr>
<tr><td><b>2 · Diccionarios y glosarios temáticos</b></td><td>Para temas específicos.</td></tr>
<tr><td><b>3 · Diccionarios de uso especial</b></td><td>Rimas, citas, pistas de crucigramas.</td></tr>
<tr><td><b>4 · Nombres propios</b></td><td>Diccionarios biográficos y de lugares.</td></tr>
<tr><td><b>5 · Listas de nombres específicos</b></td><td>Productos, medicamentos, sustancias químicas.</td></tr>
<tr><td><b>6 · Herramientas de recuperación</b></td><td>Clasificaciones, taxonomías, ontologías, encabezamientos de materia y tesauros.</td></tr>
</table>
""", fig_terms(),
["Cada dominio tiene su terminología: nombrar bien es organizar bien.",
 "Seis tipos, del diccionario general al tesauro."],
"Seis bloques numerados que van del diccionario general a las ontologías."))

# 37
add(page(37, C["rosa"], B3, "Análisis de dominio: once enfoques (Hjørland)", 42, """
<p>Birger Hjørland propuso, dentro del paradigma <b>sociocognitivo</b>, once enfoques con los que la ciencia de la información puede abordar un dominio. Es un puente entre investigación y práctica.</p>
<ol class="cols2">
<li>Guías de literatura y portales temáticos</li>
<li>Clasificaciones especiales y tesauros</li>
<li>Indización y recuperación en temas especializados</li>
<li>Estudios empíricos de usuarios</li>
<li>Estudios bibliométricos</li>
<li>Estudios históricos</li>
<li>Estudios de documentos y «géneros»</li>
<li>Estudios epistemológicos y críticos</li>
<li>Terminología, lenguajes especiales y análisis del discurso</li>
<li>Estructuras e instituciones en la comunicación de la información</li>
<li>Cognición, conocimiento experto e inteligencia artificial</li>
</ol>
<p>Quien trabaja en un ámbito no tiene por qué hacer estos estudios, pero sí conocer sus resultados; por ejemplo, la Clasificación Internacional de Enfermedades en información sanitaria. Comprender la terminología de un dominio es imprescindible para ofrecer información de forma eficaz.</p>
""", None,
["Once enfoques que van de la práctica (guías, tesauros) a la investigación (epistemología, IA).",
 "No hace falta aplicarlos todos, pero sí conocer sus resultados."],
"Una lista de once casillas en dos columnas: la caja de herramientas de Hjørland."))

# 38
add(page(38, C["teal"], B3, "Ejemplo 1: la química", 43, """
<h3 class="sub">Disciplina científica</h3>
<ul class="dots">
<li>Estudia las sustancias, sus propiedades y sus reacciones; es la base de las industrias química y farmacéutica.</li>
<li>Tiene una base de información muy amplia y fue pionera en servicios de información.</li>
<li>Recursos: libros, revistas, bases de datos bibliográficas y bancos de datos de propiedades.</li>
<li>Entidades clave: <b>sustancias y reacciones</b>, con múltiples representaciones (nombres, números de registro, diagramas 2D y 3D).</li>
</ul>
<h3 class="sub">Hitos</h3>
<ul class="dots">
<li><b>1881</b>: primera edición del <i>Handbuch</i> de Beilstein, gran compilación de datos de compuestos orgánicos.</li>
<li><b>1907</b>: nace <i>Chemical Abstracts</i>, hoy Chemical Abstracts Service (CAS), de la American Chemical Society.</li>
</ul>
""", fig_chem(),
["En química, la entidad clave es la sustancia, y cada una tiene muchas representaciones.",
 "Beilstein (1881) y Chemical Abstracts (1907): pioneros de los servicios de información."],
"La molécula de dapsona con su fórmula, su masa y sus códigos SMILES e InChIKey."))

# 39
add(page(39, C["ocre"], B3, "Ejemplo 2: la historia", 44, """
<div class="cards2 tight">
<div><h3>Si es ciencia social…</h3>Busca tendencias generales y explicaciones a partir de datos sociales, para establecer «leyes» históricas.</div>
<div><h3>Si es humanidad…</h3>Interpreta acontecimientos únicos y se centra en los relatos individuales.</div>
</div>
<ul class="dots">
<li><b>Fuentes primarias:</b> documentos de archivo, artefactos de museo y prensa de época. <b>Secundarias:</b> artículos e informes de investigación. La digitalización los abre a más público.</li>
<li><b>Herramientas de organización:</b> Historic England mantiene tesauros de lugares marítimos, cargamentos, materiales de construcción y tipos de aviones; el Museo Británico, de objetos y materiales.</li>
<li><b>Instituciones muy diversas:</b> universidades, sociedades científicas, editoriales, radiotelevisiones y gobiernos; bibliotecas, archivos y centros de documentación de museos.</li>
</ul>
""", fig_history(),
["La historia puede ser ciencia social (tendencias) o humanidad (relatos).",
 "Sus fuentes y herramientas cambian según esa elección epistemológica."],
"Un gráfico de tendencias frente a un documento único con su relato."))

# 40
add(page(40, C["morado"], B3, "El trabajo de información en un dominio", 45, """
<p>Actividades más habituales del profesional especializado en la información de un dominio:</p>
<ul class="grid2">
<li>Búsquedas y consultas de referencia «difíciles»</li>
<li>Asistir o liderar revisiones sistemáticas</li>
<li>Evaluar e interpretar información</li>
<li>Proporcionar conocimiento actualizado</li>
<li>Sugerir recursos y desarrollar colecciones</li>
<li>Promover recursos especializados</li>
<li>Crear guías para usuarios</li>
<li>Crear terminologías y taxonomías</li>
<li>Catalogar y describir recursos</li>
<li>Gestionar datos de investigación</li>
<li>Coordinar conocimientos y comunidades</li>
<li>Formación, consultoría y asesoramiento</li>
</ul>
<p class="q"><b>¿Cuánto hay que saber de la materia?</b> No tanto como las personas usuarias: quien gestiona información médica no tiene por qué ser médico. Sí hay que entender la lógica y el lenguaje del área y conocer sus fuentes y necesidades. Por ejemplo, saber que <i>Phyllostachys aurea</i> es una planta (un bambú), no un filósofo griego.</p>
""", None,
["Doce tareas típicas: buscar, evaluar, organizar, crear herramientas y formar.",
 "Basta con dominar la lógica y el lenguaje del área, no ser especialista en ella."],
"Un birrete: hay que saber lo suficiente del área, sin necesidad de ser experto en ella."))

# 41
add(page(41, C["verde"], "SÍNTESIS", "Síntesis de la lección", 46, """
<dl class="defs big">
<dt>1 · Información</dt><dd>Concepto central y multifacético. Shannon es su base necesaria; Floridi, el enfoque más apropiado para las CID.</dd>
<dt>2 · Documentos</dt><dd>Es documento lo que funciona como evidencia e información y se relaciona con otros en una colección. En lo digital, las colecciones se definen por criterios.</dd>
<dt>3 · Dominios</dt><dd>El dominio (ontológico, epistemológico, sociológico) condiciona el uso de la información. Hjørland ofrece un puente entre investigación y práctica.</dd>
</dl>
""", fig_synthesis(),
["Información → documentos → dominios: del concepto al objeto y del objeto al contexto."],
"Tres bandas de color, una por bloque del tema."))

CSS = open(os.path.join(os.path.dirname(__file__), "style.css"), encoding="utf-8").read()
doc = f'''<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>Tema 2 · Apuntes visuales</title><style>{CSS}</style></head><body>
{"".join(P)}
</body></html>'''
out = os.path.join(os.path.dirname(__file__), "tema2_apuntes_visuales.html")
open(out, "w", encoding="utf-8").write(doc)
print("pages:", len(P), "->", out)
