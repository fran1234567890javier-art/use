# -*- coding: utf-8 -*-
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

