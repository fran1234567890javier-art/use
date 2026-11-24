# KimiBot v3 en TradingView (Pine Script v5)

Versión en Pine Script del bot [ilham191026-projek/KimiBot](https://github.com/ilham191026-projek/KimiBot). El original está escrito en Python y envía señales por Telegram, así que **no se puede cargar en TradingView tal cual**. Lo que hay aquí es su lógica reescrita.

| Archivo | Para qué sirve |
|---|---|
| `KimiBot_v3_indicador.pine` | Señales BUY y SELL, niveles (entrada, SL, TP1, TP2), panel de capas y alertas |
| `KimiBot_v3_estrategia.pine` | La misma lógica como estrategia, para ver el backtest en el *Probador de estrategias* (50 % en TP1 y 50 % en TP2) |

## Cómo instalarlo
1. Abre TradingView en el **ordenador**, pon XAUUSD y elige el gráfico de **1 minuto**.
2. Abajo, abre **Pine Editor**. Borra lo que haya y pega el contenido de `KimiBot_v3_indicador.pine`.
3. Pulsa **Guardar** y luego **Añadir al gráfico**.
4. Para recibir avisos: botón **Alerta** → Condición "KimiBot v3" → "Cualquier llamada a la función alert()".

## Qué hace cada capa (igual que el bot)
| Capa | Temporalidad | Regla |
|---|---|---|
| 1 | H4 | Sesgo por swings: más de un 60 % de HH/HL es alcista y más de un 60 % de LH/LL es bajista. **Obligatoria** |
| 2 | H1 | Hay un Order Block en la dirección y el precio está dentro de él, o hay un FVG sin mitigar |
| 3 | M30 | Una vela barre el máximo o mínimo de Asia con una mecha de más de 1,5 veces el cuerpo |
| 4 | M15 | CRT: la vela barre la anterior, cierra de vuelta a favor y su cuerpo es ≥ 40 % del rango. Antigüedad máxima: 4 h |
| 5 | M5 | MSS: cierre más allá del último swing (fractal de 3 velas a cada lado) |
| 6 | M1 | Al menos 2 de estas 4: momento, envolvente, pin bar y volumen |

La señal sale con **5 de 6** capas, ADX(H1) > 25, ATR(H1) dentro del rango permitido, en sesión de Londres o Nueva York y respetando 30 minutos de cooldown.
- **SL:** el barrido CRT de M15 ± 2 pips. Si queda a menos de 15 pips, usa el swing de M30. Si pasa de 20 pips, no hay señal.
- **TP1** = 1,5R y **TP2** = 2,5R.

## Problemas que tiene el bot original (y el preset "Ajustado")
1. **La capa 3 nunca se cumple.** El "rango de Asia" se calcula con las últimas 48 velas de M30, que incluyen las propias velas que se comprueban. Así, ninguna vela puede quedar por debajo de ese mínimo. El preset *Ajustado* usa el rango real de Asia (20:00–00:00 GMT), que es lo que describe el propio código.
2. **En el oro, el filtro de ATR lo bloquea casi todo.** Exige un ATR de H1 de entre 8 y 35 pips (0,8–3,5 $), y en 2026 el ATR del oro en H1 ronda los 120–170 pips.
3. **El filtro de "spread" mide el rango de la vela de M5** (≤ 2 pips). En el oro y en la mayoría de pares casi nunca se cumple.
4. **El SL máximo de 20 pips** (2 $ en el oro) es menor que una vela normal de M5.
5. **El margen del CRT es 0,0001 en todos los símbolos**, también en el oro y en los pares con JPY.

Con el preset **Original**, la señal se comporta igual que el bot en Python, es decir, casi nunca aparece en el oro. El preset **Ajustado** corrige la capa 3 y te deja poner el rango de ATR y el SL máximo para el oro (por defecto, 40–300 pips y 60 pips).

## Lo que no se ha podido portar
- La narrativa con IA (Groq).
- El calendario económico.
- El envío por Telegram. Las alertas de TradingView lo sustituyen y se pueden mandar a Telegram con un webhook.
- El spread real del bróker.

Material educativo. No es asesoramiento financiero. Prueba primero la estrategia en el Probador de estrategias y en una cuenta demo.
