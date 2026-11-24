# -*- coding: utf-8 -*-
"""Genera libro.html: manual paso a paso del método Key + MSNR + liquidez observado en las capturas."""
import html

# ------------------------------------------------------------------ diagramas SVG
def chart(candles, w=620, h=260, boxes=(), lines=(), labels=(), arrows=(), pad=28, title=None):
    """candles: lista de (o,h,l,c). boxes: (i0,i1,lo,hi,color,texto). lines: (i0,i1,precio,color,texto,dash).
    labels: (i,precio,texto,color). arrows: (i,precio,'up'|'down',color)."""
    lo = min(c[2] for c in candles); hi = max(c[1] for c in candles)
    for b in boxes: lo, hi = min(lo, b[2]), max(hi, b[3])
    for l in lines: lo, hi = min(lo, l[2]), max(hi, l[2])
    span = hi - lo or 1; lo -= span * 0.10; hi += span * 0.18; span = hi - lo
    n = len(candles); cw = (w - 2 * pad) / n
    X = lambda i: pad + cw * i + cw / 2
    Y = lambda p: pad + (h - pad * 1.4) * (1 - (p - lo) / span)
    s = [f'<svg viewBox="0 0 {w} {h}" class="chart" xmlns="http://www.w3.org/2000/svg">',
         f'<rect x="0" y="0" width="{w}" height="{h}" fill="#fbfbfd" rx="8"/>']
    for i0, i1, blo, bhi, col, txt in boxes:
        x0 = pad + cw * i0; x1 = pad + cw * (i1 + 1)
        s.append(f'<rect x="{x0:.1f}" y="{Y(bhi):.1f}" width="{x1 - x0:.1f}" height="{Y(blo) - Y(bhi):.1f}" fill="{col}" opacity="0.28"/>')
        if txt: s.append(f'<text x="{x0 + 4:.1f}" y="{Y(bhi) - 4:.1f}" text-anchor="start" class="bt">{html.escape(txt)}</text>')
    for i0, i1, p, col, txt, dash in lines:
        x0 = pad + cw * i0; x1 = pad + cw * (i1 + 1)
        da = 'stroke-dasharray="5 4"' if dash else ""
        s.append(f'<line x1="{x0:.1f}" x2="{x1:.1f}" y1="{Y(p):.1f}" y2="{Y(p):.1f}" stroke="{col}" stroke-width="1.6" {da}/>')
        if txt: s.append(f'<text x="{x1 - 2:.1f}" y="{Y(p) - 4:.1f}" text-anchor="end" class="lt" fill="{col}">{html.escape(txt)}</text>')
    for i, (o, hh, ll, c) in enumerate(candles):
        col = "#1f9d74" if c >= o else "#d9483b"
        s.append(f'<line x1="{X(i):.1f}" x2="{X(i):.1f}" y1="{Y(hh):.1f}" y2="{Y(ll):.1f}" stroke="{col}" stroke-width="1.4"/>')
        top, bot = Y(max(o, c)), Y(min(o, c))
        s.append(f'<rect x="{X(i) - cw * 0.32:.1f}" y="{top:.1f}" width="{cw * 0.64:.1f}" height="{max(bot - top, 1.2):.1f}" fill="{col}"/>')
    for i, p, d, col in arrows:
        y = Y(p); x = X(i)
        if d == "up":
            s.append(f'<path d="M{x:.1f},{y + 4:.1f} l-7,14 h14 z" fill="{col}"/>')
        else:
            s.append(f'<path d="M{x:.1f},{y - 4:.1f} l-7,-14 h14 z" fill="{col}"/>')
    for i, p, txt, col in labels:
        s.append(f'<text x="{X(i):.1f}" y="{Y(p):.1f}" text-anchor="middle" class="lb" fill="{col}">{html.escape(txt)}</text>')
    if title: s.append(f'<text x="{pad}" y="16" class="ct">{html.escape(title)}</text>')
    s.append("</svg>")
    return "".join(s)

def C(seq, start=100.0):
    """Construye velas a partir de una lista de (cierre, mecha_arriba, mecha_abajo)."""
    out, o = [], start
    for c, up, dn in seq:
        out.append((o, max(o, c) + up, min(o, c) - dn, c)); o = c
    return out

# ---------- diagramas concretos
d_trend = chart(C([(101, .3, .2), (103, .4, .3), (102, .3, .3), (101.2, .2, .3), (104, .4, .2), (105.5, .3, .3), (104.2, .3, .4),
                   (103.6, .2, .3), (106.5, .3, .2), (107.8, .4, .3), (106.6, .2, .4), (106, .3, .2), (109, .4, .3)]),
                labels=[(1, 103.9, "H", "#333"), (3, 100.6, "HL", "#333"), (5, 106.3, "HH", "#333"), (7, 103.0, "HL", "#333"),
                        (9, 108.7, "HH", "#333"), (11, 105.4, "HL", "#333")],
                lines=[(1, 4, 103.4, "#3b6fd8", "Break", True), (5, 8, 105.8, "#3b6fd8", "Break", True)],
                title="Tendencia alcista: máximos y mínimos cada vez más altos")

d_av = chart(C([(101, .2, .2), (102.5, .3, .2), (103.8, .3, .2), (102.6, .3, .3), (101.4, .2, .3), (100.2, .3, .2), (99.4, .2, .3),
                (100.8, .3, .2), (101.9, .3, .3), (103.2, .3, .2), (103.9, .2, .2)]),
             boxes=[(2, 10, 103.8, 103.8 + 0.001, "#d9483b", "")], lines=[(2, 10, 103.8, "#d9483b", "A (resistencia): cierre alcista + apertura bajista", False),
                                                               (6, 10, 99.4, "#1f9d74", "V (soporte): cierre bajista + apertura alcista", False)],
             title="Niveles MSNR: se marcan con los CUERPOS, nunca con las mechas")

d_key = chart(C([(101, .3, .2), (102.4, .4, .2), (103.6, .5, .2), (102.0, .3, .3), (101.0, .2, .4), (102.2, .3, .2), (103.3, .45, .2),
                 (101.8, .3, .2), (100.9, .3, .3), (101.5, .2, .3), (102.6, .3, .2), (103.75, .2, .3), (102.4, .3, .2), (101.1, .2, .3)]),
              boxes=[(2, 13, 103.4, 104.1, "#d9483b", "Key • [Sell]")], lines=[(2, 13, 103.75, "#7a3fd1", "CE50%", True)],
              arrows=[(11, 104.3, "down", "#d9483b")], labels=[(2, 104.75, "techo 1", "#555"), (6, 104.75, "techo 2", "#555")],
              title="Key [Sell] en un doble techo; la orden va en el CE50% de la zona")

d_ts = chart(C([(101, .3, .3), (102, .3, .2), (101.2, .2, .3), (100.4, .3, .2), (101.3, .3, .3), (102.1, .3, .2), (101.5, .2, .3),
                (100.9, .2, .3), (100.6, .2, 1.1), (101.8, .3, .2), (102.9, .3, .2), (104.0, .3, .2)]),
             lines=[(3, 11, 100.2, "#1f9d74", "mínimo anterior (liquidez)", True)], labels=[(8, 99.2, "Ts: barre y vuelve", "#1f9d74")],
             arrows=[(9, 100.4, "up", "#1f9d74")], title="Turtle soup (Ts): la mecha barre el mínimo y el cuerpo cierra dentro")

d_fts = chart(C([(101, .3, .3), (102, .3, .2), (101.2, .2, .3), (100.4, .3, .2), (101.3, .3, .3), (101.0, .2, .3), (100.6, .2, .4),
                 (99.5, .2, .3), (99.0, .2, .3), (98.4, .3, .2), (98.9, .3, .3), (97.8, .2, .3)]),
              lines=[(3, 11, 100.2, "#d9483b", "mínimo anterior", True)], labels=[(8, 98.3, "Fts: el cuerpo cierra fuera = ruptura real", "#d9483b")],
              title="Fts / Fake break: si el CUERPO cierra más allá, no hay giro: no compres")

d_qm = chart(C([(101, .3, .2), (102.6, .3, .2), (104.0, .4, .2), (102.8, .3, .2), (101.8, .2, .3), (103.2, .3, .2), (105.0, .4, .2),
                (103.6, .3, .2), (102.2, .2, .3), (101.0, .2, .3), (102.0, .3, .2), (103.5, .3, .2), (104.1, .2, .2), (102.9, .2, .3)]),
             labels=[(2, 104.7, "H", "#333"), (4, 101.2, "L", "#333"), (6, 105.7, "HH", "#333"), (9, 100.4, "LL (rompe L)", "#333")],
             lines=[(2, 13, 104.0, "#d9483b", "QM = nivel de H: venta al volver", True)], arrows=[(12, 104.4, "down", "#d9483b")],
             title="Quasimodo de venta: H, L, HH, LL... y se vende el retorno al H")

d_entry = chart(C([(101, .3, .2), (102.2, .3, .2), (103.1, .3, .2), (102.4, .3, .2), (101.6, .2, .3), (100.8, .2, .3), (100.3, .2, .6),
                   (101.4, .2, .2), (102.6, .3, .2), (103.8, .3, .2), (105.0, .3, .2), (106.1, .3, .2)]),
                boxes=[(4, 11, 99.9, 100.6, "#1f9d74", "Key • [Buy]")],
                lines=[(4, 11, 100.25, "#7a3fd1", "orden BUY LIMIT (CE50%)", True), (4, 11, 99.55, "#d9483b", "SL 1-3 $ bajo la zona", False),
                       (7, 11, 103.1, "#3b6fd8", "TP1: máximo anterior", True)],
                title="Plan completo: límite en el CE50%, stop detrás de la zona, TP1 en la liquidez")

d_mgmt = chart(C([(100.3, .1, .1), (101.0, .2, .1), (101.6, .2, .2), (102.3, .2, .2), (103.2, .2, .2), (102.7, .2, .2), (103.6, .2, .2),
                  (104.6, .2, .2), (105.3, .3, .2), (104.8, .2, .2), (106.2, .3, .2)]),
               lines=[(0, 10, 100.3, "#7a3fd1", "entrada", True), (0, 3, 99.55, "#d9483b", "SL inicial", False),
                      (3, 10, 100.35, "#d9483b", "SL a breakeven al +1R", False), (4, 10, 103.1, "#3b6fd8", "TP1: cierra 50 %", True),
                      (7, 10, 105.3, "#3b6fd8", "TP2 / dejar correr", True)],
               title="Gestión: breakeven, parcial en TP1 y el resto corre")

# ------------------------------------------------------------------ contenido
CH = []
def ch(t, body): CH.append((t, body))

ch("Antes de empezar", """
<p>Este libro reconstruye, paso a paso, la forma de operar que se ve en las <b>499 capturas</b> del canal DOVA
(1 de octubre a 24 de noviembre de 2026). Cada regla viene de algo que el trader dibuja o hace en sus gráficos. Las operaciones de ejemplo están <b>comprobadas con datos reales del oro</b> minuto a minuto.</p>
<div class="warn"><b>Lo que este libro no puede prometer.</b> Nadie puede garantizar que ganes dinero, "sí o sí". El canal no publica su historial completo ni sus pérdidas. El número grande del MT5 (2M, 5M, 8M) es <b>beneficio flotante, no el saldo</b>, y el saldo que se ve ronda los 450.000–677.000 $. El método se puede aprender, pero <b>solo tus propias estadísticas en demo</b> dirán si te funciona. Por eso el libro termina con un plan de 12 semanas y un diario de operaciones.</div>
<h3>Cómo usar el libro</h3>
<ol><li>Lee los capítulos 1 a 4 (lo básico) con TradingView abierto en XAUUSD.</li>
<li>Haz los <b>ejercicios</b> de cada capítulo antes de seguir.</li>
<li>Imprime el <b>checklist</b> (capítulo 13) y la <b>plantilla del diario</b> (capítulo 16).</li>
<li>Sigue el <b>plan de 12 semanas</b> en una cuenta demo. Solo pasa a real si cumples los requisitos de la semana 12.</li></ol>
<p class="small">Material educativo. No es asesoramiento financiero.</p>
""")

ch("1. El oro (XAUUSD) en 10 minutos", """
<table><tr><th>Concepto</th><th>Valor</th><th>Para qué te sirve</th></tr>
<tr><td>Precio</td><td>~3.600–5.600 $ en 2026</td><td>Se mueve una media de <b>117 $ al día</b> (1.173 pips)</td></tr>
<tr><td>1 pip</td><td>0,10 $</td><td>Un stop de 10 pips = 1 $ de distancia</td></tr>
<tr><td>1 punto (MT5)</td><td>0,01 $</td><td>La regla del MT5 mide en puntos: 300 puntos = 3 $</td></tr>
<tr><td>1 lote</td><td>100 onzas</td><td>Gana o pierde <b>100 $ por cada 1 $</b> que se mueve el precio</td></tr>
<tr><td>0,01 lotes</td><td>1 onza</td><td><b>1 $ por cada 1 $</b>. Es el tamaño para una cuenta de 100 $</td></tr>
<tr><td>100 lotes (los del canal)</td><td>10.000 onzas</td><td><b>10.000 $ por cada 1 $</b> de movimiento</td></tr>
<tr><td>Spread</td><td>~0,24 $ (2,4 pips)</td><td>Con stops de 1 $, el spread ya es una cuarta parte del riesgo</td></tr></table>
<h3>Sesiones (hora de España)</h3>
<p>El trader opera las <b>killzones</b> de Londres y Nueva York y casi nunca la de Asia. Las horas cambian cuando EE. UU. y Europa cambian la hora en fechas distintas. La regla fija es la hora de Nueva York:</p>
<table><tr><th>Sesión</th><th>Hora de Nueva York</th><th>España en invierno (NY + 6 h)</th><th>España en verano (NY + 6 h)</th></tr>
<tr><td>Asia (no operar)</td><td>20:00 – 00:00</td><td>02:00 – 06:00</td><td>02:00 – 06:00</td></tr>
<tr><td><b>Killzone Londres</b></td><td>02:00 – 05:00</td><td>08:00 – 11:00</td><td>08:00 – 11:00</td></tr>
<tr><td><b>Killzone NY AM</b></td><td>07:00 – 11:00</td><td>13:00 – 17:00</td><td>13:00 – 17:00</td></tr>
<tr><td>Datos de EE. UU. (IPC, PPI, NFP)</td><td>08:30</td><td>14:30</td><td>14:30</td></tr>
<tr><td>FOMC (tipos de interés)</td><td>14:00</td><td>20:00</td><td>20:00</td></tr></table>
<p class="small">Durante unas semanas de marzo y de finales de octubre la diferencia es de 5 horas, porque EE. UU. y Europa no cambian la hora el mismo día. Comprueba siempre la hora de Nueva York.</p>
<div class="ex"><b>Ejercicio 1.</b> Con 0,01 lotes y un stop de 2,5 $, ¿cuánto pierdes si salta el stop? ¿Y con 0,03 lotes?</div>
""")

ch("2. Las herramientas", """
<p>El trader usa <b>dos aplicaciones</b>: TradingView para dibujar el mapa y MetaTrader 5 (MT5) para ejecutar.</p>
<h3>TradingView: el mapa</h3>
<ul><li><b>Temporalidades:</b> M30 y M15 para marcar los Key; H1, H4, D1 y W1 para el contexto.</li>
<li><b>Herramientas:</b> <i>Rectángulo</i> gris para la zona Key, <i>Línea horizontal</i> para máximos y mínimos y <i>Texto</i> para las etiquetas (Key • [Sell], Classic A, Ts, Break, CE50%, X).</li>
<li>Activa las líneas verticales de separación de días o sesiones. El trader las tiene en casi todas sus capturas.</li></ul>
<h3>MT5: la ejecución</h3>
<ul><li><b>Temporalidades:</b> M1, M3 y M5 para ver la entrada.</li>
<li><b>Órdenes:</b> <b>Buy Limit / Sell Limit</b>, la orden pendiente que queda colocada en el nivel (aparece en 57 capturas).</li>
<li><b>Stop loss y breakeven:</b> arrastra la línea del SL en el gráfico.</li>
<li><b>Regla:</b> mide la distancia en puntos para saber el riesgo y el recorrido (aparece en 66 capturas).</li>
<li><b>Cierre parcial:</b> en la posición, <i>Cerrar</i> y elige un volumen menor.</li></ul>
<div class="tip"><b>Consejo.</b> Pon en MT5 una cuenta <b>demo</b> del mismo bróker que vayas a usar en real. Así el spread y los precios serán los mismos.</div>
""")

ch("3. Estructura: hacia dónde va el mercado", d_trend + """
<p><b>Tendencia alcista:</b> máximos (H) y mínimos (HL) cada vez más altos. <b>Bajista:</b> al revés.
Un <b>Break</b> es una vela que <b>cierra con el cuerpo</b> más allá del último máximo o mínimo. El trader también marca el <b>Weekly break</b>, la ruptura del máximo o mínimo de la semana.</p>
<h3>Cómo lo usa el trader</h3>
<ul><li>En <b>H4, D1 y W1</b> decide la dirección grande. En octubre y noviembre de 2026 el oro bajaba desde ~4.690, y él mantenía <b>ventas de varios días</b> (desde 4.629, 4.198 y 4.077).</li>
<li>Sobre esa dirección grande hace operaciones cortas: <b>vende en los techos</b> y, en los suelos fuertes, <b>compra rebotes</b>.</li></ul>
<h3>Regla para ti</h3>
<ol><li>Mira D1 y H4. Si los dos son bajistas, busca sobre todo <b>Key [Sell]</b>.</li>
<li>Compra solo en un <b>Key [Buy]</b> muy claro (doble suelo, mínimo semanal o gap) y con un objetivo corto.</li>
<li>Si D1 y H4 no coinciden, opera menos o con la mitad de riesgo.</li></ol>
<div class="ex"><b>Ejercicio 3.</b> Abre XAUUSD en H4 y marca los 3 últimos máximos y mínimos. ¿La tendencia es alcista, bajista o lateral?</div>
""")

ch("4. Niveles MSNR: A, V y Gap (Classic A)", d_av + """
<p>Malaysian SnR marca soportes y resistencias con los <b>cuerpos</b> de las velas: el cierre de una y la apertura de la siguiente.</p>
<table><tr><th>Nivel</th><th>Se forma con</th><th>Es</th></tr>
<tr><td><b>A</b> (Classic A)</td><td>Una vela alcista y después una bajista: del cierre de la 1.ª a la apertura de la 2.ª</td><td>Resistencia (zona de venta)</td></tr>
<tr><td><b>V</b></td><td>Una vela bajista y después una alcista</td><td>Soporte (zona de compra)</td></tr>
<tr><td><b>Gap</b></td><td>El hueco entre el cierre de un día y la apertura del siguiente</td><td>Soporte o resistencia</td></tr></table>
<ul><li><b>Fresco:</b> el precio aún no ha vuelto a tocarlo. Es el que vale.</li>
<li><b>Usado:</b> ya lo ha tocado una vez. Pierde fuerza.</li></ul>
<p>El trader escribe <b>"Classic A"</b> en sus gráficos (15 capturas) y suele combinarlo con el <b>CE50%</b>: "CE50% + A level".
En los datos reales, la compra del 26 de octubre en <b>4.011,2</b> cayó dentro de un <b>V de H1</b> (4.011,1–4.011,9).</p>
<div class="ex"><b>Ejercicio 4.</b> En H1, pon el gráfico en <i>línea</i>, que solo usa los cierres. Busca 3 picos y 3 valles y conviértelos en niveles A y V.</div>
""")

ch("5. El Key [Buy] / Key [Sell]", d_key + """
<p>Es la herramienta principal del trader: aparece en <b>90 capturas</b>. Es una <b>caja gris horizontal</b> donde piensa vender (Key • [Sell]) o comprar (Key • [Buy]).</p>
<h3>Dónde se pone un Key (por orden de fuerza)</h3>
<ol><li><b>Doble techo o doble suelo:</b> dos giros en el mismo precio.</li>
<li><b>Máximo o mínimo del día anterior, de Asia o de la semana.</b></li>
<li><b>Base del impulso:</b> la zona desde donde salió un movimiento fuerte.</li>
<li><b>Nivel A, V o Gap fresco de MSNR</b> en H1 o H4.</li>
<li><b>Quasimodo de H1</b> (capítulo 7).</li></ol>
<h3>Cómo dibujarlo</h3>
<ol><li>En M30 o M15, traza la caja desde el <b>cuerpo</b> hasta la <b>mecha</b> de la vela o velas que forman el nivel.</li>
<li>Calcula el <b>CE50%</b>: el punto medio de la caja, o de la mecha si la mecha es muy larga. <b>Ahí va la orden.</b></li>
<li>Escribe "Key • [Sell]" o "Key • [Buy]" y la temporalidad.</li>
<li>Extiende la caja hacia la derecha hasta que el precio la toque.</li></ol>
<div class="tip"><b>Regla de calidad.</b> Un buen Key tiene <b>liquidez delante</b>, es decir, máximos o mínimos que el precio barrerá antes de llegar (capítulo 6). Si no la hay, el nivel suele romperse.</div>
<div class="ex"><b>Ejercicio 5.</b> Marca hoy 2 Key [Sell] y 2 Key [Buy] en M30. Haz captura. Mañana comprueba cuáles reaccionaron.</div>
""")

ch("6. Liquidez: X, Ts, Fts y Break", d_ts + d_fts + """
<p>La <b>liquidez</b> son los stops de otros traders, acumulados justo detrás de los máximos y mínimos. El precio suele ir a buscarlos antes de girar.</p>
<table><tr><th>Etiqueta</th><th>Significado</th><th>Qué haces</th></tr>
<tr><td><b>X</b></td><td>El punto de liquidez que debe barrerse: un mínimo o máximo evidente</td><td>Esperar a que lo barra</td></tr>
<tr><td><b>Ts</b> (turtle soup)</td><td>La mecha barre el nivel y el <b>cuerpo cierra dentro</b></td><td>Señal de giro: tu orden límite entra ahí</td></tr>
<tr><td><b>Fts / Fake break</b></td><td>Barrido fallido: el cuerpo <b>cierra fuera</b> y sigue</td><td>No operar ese Key. Si estabas dentro, sales en el stop</td></tr>
<tr><td><b>Break</b></td><td>Ruptura real con cierre de cuerpo</td><td>Cambia la dirección. El nivel roto suele servir para el lado contrario</td></tr></table>
<p>Ejemplo real del <b>13 de noviembre</b> (dato PPI, 8:30 NY): el oro barrió el mínimo de Asia (3.884) y el de las 4 horas anteriores, y llegó a <b>3.879,19</b> dentro de un gap diario. La compra del trader en <b>3.880,18</b> subió 26 $ en minutos.</p>
<div class="ex"><b>Ejercicio 6.</b> Busca en M15 tres barridos de este mes. ¿Cuántos fueron Ts (giro) y cuántos Fts (siguió)? Apunta la hora: ¿estaban en una killzone?</div>
""")

ch("7. El Quasimodo de H1 (QM)", d_qm + """
<p>Lo usa como <b>confirmación</b> de algunos Key ("1H [QM]").</p>
<ol><li><b>Venta:</b> el precio hace un máximo <b>H</b>, un mínimo <b>L</b>, un máximo más alto <b>HH</b> (barre la liquidez) y después <b>rompe L</b> con cuerpo y forma un <b>LL</b>.</li>
<li>El <b>nivel QM es H</b>. Pon la Sell Limit ahí, o en el CE50% entre H y HH.</li>
<li><b>Compra:</b> exactamente al revés (L, H, LL, HH y compra en L).</li></ol>
<div class="tip">Un Key que coincide con un QM de H1 y además con un nivel A o V fresco es la <b>mejor zona</b>: tres razones en el mismo precio.</div>
""")

ch("8. La entrada: orden límite en el Key", d_entry + """
<p>El trader <b>no persigue el precio</b>: deja una <b>orden límite</b> esperando en el Key, a veces horas antes. Las entradas se llenan en la mecha del barrido, como 4.011,2, 3.989, 4.059,18 o 3.880,18.</p>
<h3>Reglas de entrada</h3>
<ol><li><b>Dirección:</b> a favor de H4 y D1 (capítulo 3).</li>
<li><b>Zona:</b> un Key fresco con liquidez delante (capítulos 5 y 6).</li>
<li><b>Precio de la orden:</b> el CE50% de la zona.</li>
<li><b>Stop:</b> entre 1 y 3 $ (10–30 pips) <b>detrás del extremo de la zona</b>. En las capturas, la mediana es de 1,01 $ y tres de cada cuatro stops están a 3 $ o menos.</li>
<li><b>Horario:</b> la orden debe poder ejecutarse en Londres o en Nueva York AM. Si no se llena antes de las 11:00 NY, <b>cancélala</b>.</li>
<li><b>Anulación:</b> si una vela de M15 <b>cierra con el cuerpo</b> al otro lado del Key antes de que entres (Fts), cancela la orden.</li></ol>
<h3>Si prefieres confirmación (más lento y más seguro)</h3>
<p>En lugar de la orden límite, espera en M1 o M5 a que el precio toque el Key, barra (Ts) y haga un <b>Break</b> en contra del movimiento. Entra en el retroceso con el stop detrás de la mecha. Entrarás menos veces, pero con más motivo.</p>
<div class="ex"><b>Ejercicio 8.</b> Para tus Key del ejercicio 5, escribe la orden completa: tipo (Buy o Sell Limit), precio, SL y TP1. Calcula el riesgo en $ con 0,01 lotes.</div>
""")

ch("9. La gestión de la operación", d_mgmt + """
<p>Es lo que más se repite en las capturas:</p>
<ol><li><b>Breakeven rápido:</b> cuando la operación va +1R a favor (la misma distancia que el stop), mueve el SL a la entrada. La cuarta parte de los stops que se ven ya están a 0,19 $ o menos de la entrada.</li>
<li><b>Cierres parciales:</b> cierra el <b>50 % en TP1</b>, el máximo o mínimo anterior más cercano. El trader va reduciendo, por ejemplo 100 → 95 → 84 → 68 lotes.</li>
<li><b>Deja correr el resto</b> hasta el siguiente nivel grande (el máximo o mínimo del día o de la semana), o hasta que haya un Break en contra. El trader <b>casi nunca pone TP</b> y aguanta ganadoras días enteros.</li>
<li><b>Escalonar:</b> pone 2 o 3 órdenes en el mismo techo (por ejemplo 4.125, 4.127 y 4.128). <b>Tú no:</b> pon una sola orden, o reparte tu riesgo del 1 % entre ellas.</li></ol>
<div class="warn"><b>Cobertura (compra y venta a la vez).</b> El trader la usa a menudo. Para aprender, <b>no la uses</b>: complica la gestión y oculta las pérdidas.</div>
""")

ch("10. Las noticias", """
<p>El trader publica el calendario económico antes de los datos y varias de sus mejores operaciones son del minuto del dato:</p>
<table><tr><th>Dato</th><th>Fecha del ejemplo</th><th>Qué pasó</th></tr>
<tr><td>IPC (inflación)</td><td>14 de octubre y 10 de noviembre</td><td>Ventas de 100 lotes y caída de ~40–70 $</td></tr>
<tr><td>PPI</td><td>13 de noviembre, 8:30 NY</td><td>Compra en 3.880,18 tras barrer Asia, +26 $ en minutos</td></tr>
<tr><td>FOMC</td><td>28 de octubre</td><td>Entradas en M1 en el pico de volatilidad</td></tr></table>
<h3>Reglas para ti</h3>
<ol><li>Cada domingo mira el calendario de la semana (Forex Factory o Investing). Filtra USD y alto impacto.</li>
<li><b>No abras operaciones nuevas</b> entre 5 minutos antes y 5 minutos después del dato, salvo que tu orden límite <b>ya estuviera puesta</b> en un Key con su stop.</li>
<li>En las noticias el precio puede <b>saltarse tu stop</b> (slippage). Con 0,01 lotes lo notarás poco; con lotes grandes es peligroso.</li></ol>
""")

ch("11. Riesgo y tamaño: lo que más importa", """
<p>El trader opera <b>100 lotes</b>, es decir, 10.000 $ por cada dólar que se mueve el oro. Con un stop de 1 $, arriesga unos 10.000 $, un ~2 % de un saldo de 475.000 $. <b>Sin stop</b>, 47 $ en contra con una sola posición se llevan todo el saldo. Tú vas a empezar pequeño.</p>
<h3>Fórmula del tamaño</h3>
<p class="formula">Lotes = (Saldo × % de riesgo) ÷ (distancia al stop en $ × 100)</p>
<table><tr><th>Saldo</th><th>Riesgo 1 %</th><th>Stop 1 $</th><th>Stop 2 $</th><th>Stop 3 $</th></tr>
<tr><td>100 $</td><td>1 $</td><td>0,01</td><td>0,01 (= 2 %)</td><td>0,01 (= 3 %)</td></tr>
<tr><td>500 $</td><td>5 $</td><td>0,05</td><td>0,02–0,03</td><td>0,01–0,02</td></tr>
<tr><td>1.000 $</td><td>10 $</td><td>0,10</td><td>0,05</td><td>0,03</td></tr>
<tr><td>5.000 $</td><td>50 $</td><td>0,50</td><td>0,25</td><td>0,16</td></tr></table>
<p class="small">Con 100 $, el lote mínimo (0,01) ya supone un 1–3 % con estos stops. Si tu bróker ofrece cuenta <b>cent</b>, podrás ajustar mejor.</p>
<h3>Reglas fijas</h3>
<ul><li>Riesgo por operación: <b>1 %</b>, como máximo un 2 %.</li>
<li>Como mucho <b>2 pérdidas al día</b>. A la segunda, se acabó el día.</li>
<li>Pérdida máxima semanal: <b>5 %</b>. Si la alcanzas, para y revisa tu diario.</li>
<li><b>Siempre con stop.</b> Nunca lo muevas en contra.</li></ul>
<h3>Por qué no copiar sus 100 lotes ni arriesgar un 7–10 %</h3>
<p>En nuestras simulaciones, sin una ventaja demostrada, arriesgar un 10 % por operación quema la cuenta en el <b>80 % de los casos</b> en 240 operaciones. Con una ventaja real, el 1–2 % también hace crecer la cuenta, más despacio pero sin quemarla.</p>
<div class="ex"><b>Ejercicio 11.</b> Tienes 300 $, el stop está a 2,4 $ y quieres arriesgar un 1 %. ¿Cuántos lotes pones? Con el lote mínimo de 0,01, ¿qué porcentaje arriesgas de verdad?</div>
""")

ch("12. Tu rutina diaria (hora de España)", """
<table><tr><th>Hora (España)</th><th>Qué haces</th></tr>
<tr><td><b>07:30 – 08:00</b></td><td>D1 y H4: dirección. M30: marca 2–3 Key (máximo y mínimo de ayer, rango de Asia, dobles techos o suelos, A/V frescos). Calendario del día.</td></tr>
<tr><td>08:00 – 11:00</td><td><b>Killzone Londres:</b> pon las órdenes límite en los Key a favor de la dirección y vigila los Ts y los Fts.</td></tr>
<tr><td>11:00 – 13:00</td><td>Gestiona lo abierto: breakeven y parciales. <b>No abras operaciones nuevas.</b></td></tr>
<tr><td>13:00 – 17:00</td><td><b>Killzone NY AM:</b> actualiza los Key con lo que ha hecho Londres. A las 14:30 hay datos: aplica las reglas del capítulo 10.</td></tr>
<tr><td>17:00</td><td>Cancela las órdenes que no se hayan llenado. Apunta en el diario cada operación con su foto antes y después.</td></tr></table>
<p class="small">Si no puedes estar a esas horas, elige <b>una sola killzone</b> y opera solo esa.</p>
""")

ch("13. Checklist (imprímelo)", """
<div class="check">
<h3>Antes de poner la orden</h3>
<p>☐ La dirección de D1 y H4 está clara y la orden va a favor (o es un Key [Buy] de rebote muy claro)<br>
☐ El Key está en un doble techo o suelo, en un máximo o mínimo de día, Asia o semana, o en un A/V fresco<br>
☐ Tiene <b>liquidez delante</b> (X): máximos o mínimos que el precio barrerá antes de llegar<br>
☐ Mejor si coincide con un QM de H1 o con un Classic A<br>
☐ La orden está en el <b>CE50%</b> de la zona<br>
☐ El stop está 1–3 $ detrás del extremo de la zona<br>
☐ TP1 (el siguiente máximo o mínimo) está a <b>1,5R o más</b><br>
☐ La orden se puede llenar en Londres o en NY AM, y no se abre dentro de los 5 minutos de un dato<br>
☐ Riesgo ≤ 1 % (lotes calculados con la fórmula)<br>
☐ Hoy llevo menos de 2 pérdidas</p>
<h3>Con la operación abierta</h3>
<p>☐ A +1R, el stop pasa a la entrada<br>
☐ En TP1, cierro el 50 %<br>
☐ El resto corre hasta el siguiente nivel grande, o salgo si hay un Break en contra<br>
☐ Si una vela de M15 cierra con cuerpo al otro lado del Key (Fts) antes de entrar, cancelo la orden</p>
<h3>Después</h3>
<p>☐ Captura antes y después, y apunto el resultado en R en el diario</p>
</div>
""")

ch("14. Siete operaciones reales explicadas", """
<p>Operaciones del canal, comprobadas con los datos de 1 minuto del oro. Las horas son de Nueva York.</p>
<table class="tight"><tr><th>Fecha y hora</th><th>Operación</th><th>Por qué (la base)</th><th>Qué pasó</th><th>Lección</th></tr>
<tr><td>1 oct, 08:47 (tras el dato de las 8:30)</td><td>Venta de 100 lotes en 4.185,57</td><td>Barrido de los máximos de 4 h (4.185,9 → 4.187,9) en un A de H1 (4.184,6–4.185,4)</td><td>−35 $ de caída. Stop movido a la entrada</td><td>Ts en un A de H1 dentro de la killzone NY</td></tr>
<tr><td>2 oct, 20:05 (Asia)</td><td>Dibujo de venta con RR 74</td><td>Barrido de máximos (4.183,8) en un A de H1</td><td>−48 $. Pero se <b>dibujó después</b>, 38 minutos tras llegar al objetivo</td><td>Un RR dibujado a posteriori no demuestra nada</td></tr>
<tr><td>7 oct, 03:33 (Londres)</td><td>Venta de 2,39 lotes en 4.137,71</td><td>Storyline bajista en H1 y H4, en un gap diario, por debajo de la apertura de medianoche</td><td>Siguió bajando 29 $ y luego 60 $ más con el dato de las 8:00</td><td>A favor de la tendencia, en Londres, en un gap</td></tr>
<tr><td>13 oct, 09:50 (NY AM)</td><td>Venta de 10 lotes en ~4.174,8</td><td>Retroceso hacia un gap diario y un A de H1 tras caer desde 4.185</td><td>−25 $</td><td>Vender el retroceso a un nivel ya marcado</td></tr>
<tr><td>26 oct, 07:21 (NY AM)</td><td>3 compras, 120 lotes, en ~4.011</td><td>Toque exacto de un V de H1 (4.011,1–4.011,9) sobre la apertura de medianoche</td><td>+12 $ hasta las 08:30 y luego <b>−22 $</b> (3.988,8) a las 09:58</td><td>Sin stop, la ganancia de la captura pudo acabar en una gran pérdida</td></tr>
<tr><td>3–4 nov</td><td>Dibujo de un "Key" en 3.900</td><td>V de H1 fresco con storyline alcista</td><td>+150 $ hasta 4.047. Dibujado después</td><td>El Key correcto en D1 o H4 da los mayores recorridos</td></tr>
<tr><td>13 nov, 08:30 (PPI)</td><td>Compra de 100 lotes en 3.880,18</td><td>Barrido del mínimo de Asia y de 4 h dentro de un gap diario (3.875,7–3.885,2)</td><td>+26 $ en minutos</td><td>Ts y Key en una noticia. Muy rentable, pero muy arriesgado</td></tr></table>
""")

ch("15. Lo que el canal no enseña", """
<ul><li><b>Pérdidas:</b> solo 18 de las 499 capturas muestran algo en negativo, casi siempre pérdidas flotantes momentáneas. Las únicas pérdidas cerradas son de la cuenta pequeña, con un <b>drawdown máximo del 251 %</b> en su informe.</li>
<li><b>El saldo real:</b> 450.042 $ (8 de octubre), 676.685 $ (29 de octubre) y 474.658 $ (7 de noviembre). Los 2M–9M del botón son flotantes.</li>
<li><b>Órdenes que desaparecen</b> cerca del stop sin captura de su cierre.</li>
<li><b>Varias cuentas</b> mezcladas y capturas de seguidores.</li>
<li><b>Marketing:</b> "DLT-9", el bot IDOVA, señales premium y pagos en USDT.</li></ul>
<p>Nada de esto invalida las ideas técnicas, pero significa que <b>no conocemos su acierto real</b>. Tus estadísticas son las únicas que cuentan.</p>
""")

ch("16. Plan de 12 semanas y diario", """
<table><tr><th>Semanas</th><th>Objetivo</th><th>Para pasar a la siguiente fase</th></tr>
<tr><td>1–2</td><td><b>Solo marcar.</b> Cada día 2–3 Key en M30 con captura. Al día siguiente, anota si reaccionaron.</td><td>Más de 20 Key marcados y revisados</td></tr>
<tr><td>3–4</td><td><b>Backtest manual:</b> en TradingView, con la reproducción de barras, recorre 2 meses del pasado aplicando el checklist.</td><td>Más de 40 operaciones simuladas, con el resultado en R</td></tr>
<tr><td>5–10</td><td><b>Demo en directo</b> con un riesgo del 1 %. Todas las operaciones al diario.</td><td>Más de 60 operaciones en demo</td></tr>
<tr><td>11–12</td><td><b>Revisión:</b> calcula el acierto, el R medio, la peor racha y la peor caída. Mira qué Key funcionan mejor.</td><td>R medio ≥ +0,3 y peor caída &lt; 15 %</td></tr>
<tr><td>Después</td><td>Real con 100 $ y 0,01 lotes (1–3 %). Revisión cada 50 operaciones.</td><td>Si el R medio baja de 0, vuelve a la demo</td></tr></table>
<h3>Plantilla del diario</h3>
<table class="tight"><tr><th>#</th><th>Fecha y hora</th><th>Sesión</th><th>Dirección D1/H4</th><th>Tipo de Key</th><th>CE50%</th><th>Entrada</th><th>SL</th><th>TP1</th><th>Lotes</th><th>Resultado (R)</th><th>¿Seguí el checklist?</th><th>Nota</th></tr>
<tr><td>1</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>2</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>3</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table>
<h3>Cómo calcular tus números</h3>
<ul><li><b>R de una operación</b> = ganancia o pérdida ÷ lo que arriesgabas. Si salta el stop = −1R. Si ganas el doble del riesgo = +2R.</li>
<li><b>Acierto</b> = operaciones ganadoras ÷ total.</li>
<li><b>R medio</b> = suma de los R ÷ número de operaciones. Si sale positivo, tienes ventaja; si sale negativo, no.</li></ul>
""")

ch("17. Soluciones de los ejercicios", """
<ul><li><b>Ejercicio 1:</b> 0,01 lotes × 2,5 $ = <b>2,50 $</b>. Con 0,03 lotes, <b>7,50 $</b>.</li>
<li><b>Ejercicio 11:</b> 300 $ × 1 % = 3 $. 3 ÷ (2,4 × 100) = 0,0125, así que redondeas <b>hacia abajo</b> a <b>0,01 lotes</b>. Arriesgas 2,40 $, un <b>0,8 %</b>.</li>
<li><b>Ejercicios 3 a 8:</b> no tienen una respuesta única. Compara tu captura de un día con la del día siguiente y apunta qué falló. Esa es la forma de aprender este método.</li></ul>
""")

ch("18. Glosario", """
<table><tr><th>Término</th><th>Significado</th></tr>
<tr><td>Key [Buy] / [Sell]</td><td>Zona marcada para comprar o vender</td></tr>
<tr><td>CE50%</td><td>El punto medio de la zona, la vela o la mecha: el precio exacto de la orden</td></tr>
<tr><td>Classic A / V</td><td>Resistencia y soporte de MSNR, marcados con los cuerpos</td></tr>
<tr><td>Gap</td><td>El hueco entre el cierre de un día y la apertura del siguiente</td></tr>
<tr><td>Ts (turtle soup)</td><td>Barrido de un máximo o mínimo con giro</td></tr>
<tr><td>Fts / Fake break</td><td>Barrido que no gira: la ruptura es real</td></tr>
<tr><td>Break / Weekly break</td><td>Ruptura con cierre de cuerpo del último máximo o mínimo, o del de la semana</td></tr>
<tr><td>X</td><td>Punto de liquidez que el precio va a buscar</td></tr>
<tr><td>QM (Quasimodo)</td><td>Patrón de giro: H, L, HH, LL (o al revés)</td></tr>
<tr><td>Killzone</td><td>Horas de más movimiento: Londres (02–05 NY) y NY AM (07–11 NY)</td></tr>
<tr><td>Breakeven (BE)</td><td>Stop movido al precio de entrada</td></tr>
<tr><td>Parcial</td><td>Cerrar solo una parte de la posición</td></tr>
<tr><td>Flotante</td><td>Ganancia o pérdida de lo que sigue abierto (no es dinero cobrado)</td></tr>
<tr><td>R</td><td>Unidad de riesgo: lo que pierdes si salta el stop</td></tr>
<tr><td>Lote</td><td>100 onzas de oro: 100 $ por cada 1 $ de movimiento</td></tr></table>
""")

# ------------------------------------------------------------------ HTML
toc = "".join(f'<li>{html.escape(t)}</li>' for t, _ in CH)
body = "".join(f'<section><h2>{html.escape(t)}</h2>{b}</section>' for t, b in CH)
HTML = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Método Key + MSNR en el oro</title>
<style>
@page {{ size: A4; margin: 16mm 15mm 16mm 15mm; }}
body {{ font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; color:#1d2433; font-size: 10.6pt; line-height: 1.45; }}
.cover {{ height: 255mm; display:flex; flex-direction:column; justify-content:center; text-align:center;
  background: linear-gradient(160deg,#0f1b33,#24365e); color:#fff; border-radius:12px; padding:20mm; page-break-after: always; }}
.cover h1 {{ font-size: 32pt; margin: 0 0 8mm; letter-spacing:.5px; }}
.cover .sub {{ font-size: 14pt; color:#f2c14e; margin-bottom: 14mm; }}
.cover .meta {{ font-size: 10pt; color:#c9d3ea; }}
.toc {{ page-break-after: always; }} .toc ol {{ columns: 2; font-size: 11pt; }}
section {{ page-break-before: always; }}
h2 {{ color:#24365e; border-bottom: 3px solid #f2c14e; padding-bottom: 3px; font-size: 17pt; margin-top: 0; }}
h3 {{ color:#24365e; font-size: 12pt; margin: 12px 0 4px; }}
table {{ border-collapse: collapse; width: 100%; margin: 6px 0 10px; font-size: 9.6pt; page-break-inside: avoid; }}
th {{ background:#24365e; color:#fff; text-align:left; padding:5px 6px; }}
td {{ border-bottom: 1px solid #dfe3ec; padding: 4px 6px; vertical-align: top; }}
table.tight {{ font-size: 8.4pt; }}
.chart {{ width: 100%; height: auto; margin: 4px 0 8px; border:1px solid #e3e7f0; border-radius: 8px; }}
.chart .ct {{ font-size: 12px; font-weight: 700; fill:#24365e; }} .chart .bt {{ font-size: 11px; font-weight:700; fill:#333; }}
.chart text {{ paint-order: stroke; stroke:#fbfbfd; stroke-width:4px; stroke-linejoin:round; }} .chart .lt {{ font-size: 10.5px; font-weight:600; }} .chart .lb {{ font-size: 11px; font-weight:700; }}
.warn {{ background:#fff3f0; border-left: 5px solid #d9483b; padding: 8px 10px; margin: 8px 0; border-radius: 4px; }}
.tip {{ background:#eef6f1; border-left: 5px solid #1f9d74; padding: 8px 10px; margin: 8px 0; border-radius: 4px; }}
.ex {{ background:#f3f0fb; border-left: 5px solid #7a3fd1; padding: 8px 10px; margin: 10px 0; border-radius: 4px; }}
.check {{ border: 2px solid #24365e; border-radius: 8px; padding: 6px 14px; font-size: 11pt; line-height: 1.8; }}
.formula {{ font-size: 13pt; text-align:center; background:#fbf6e6; padding: 8px; border-radius: 6px; font-weight:700; }}
.small {{ font-size: 8.8pt; color:#5a6275; }}
</style></head><body>
<div class="cover"><h1>Método Key + MSNR<br>en el oro (XAUUSD)</h1>
<div class="sub">Manual paso a paso para aprender a operar como el trader del canal DOVA</div>
<div class="meta">Reconstruido a partir de 499 capturas (1 de octubre a 24 de noviembre de 2026) y comprobado con datos reales de 1 minuto.<br><br>
Material educativo. No es asesoramiento financiero. Practica primero en una cuenta demo.</div></div>
<div class="toc"><h2>Índice</h2><ol>{toc}</ol></div>
{body}
</body></html>"""
open("/projects/sandbox/libro_dova/libro.html", "w", encoding="utf-8").write(HTML)
print("ok", len(HTML))
