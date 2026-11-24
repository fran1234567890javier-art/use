# Análisis de las 499 capturas del canal DOVA (1 de octubre a 24 de noviembre de 2026)

> Material educativo. No es asesoramiento financiero. Todo se ha sacado de las imágenes publicadas: no hay historial del bróker, así que **lo que no se publicó no se puede ver**.
> El catálogo imagen por imagen está en `capturas_analisis/resultado_00.jsonl` … `resultado_07.jsonl` (499 líneas).

## 1. Qué hay en las capturas

| Tipo de imagen | Nº |
|---|---|
| MT5 con posiciones u órdenes abiertas | 327 |
| Análisis en TradingView (niveles dibujados) | 79 |
| Otros: calendarios, marketing, chats, suscriptores, imágenes motivacionales | 52 |
| Historial u operaciones cerradas | 22 |
| Posición dibujada con la herramienta de RR de TradingView | 13 |
| Saldo o resultados | 6 |

**Activos:** casi todo es oro (XAUUSD.ecn). Hay 14 capturas de BTCUSD, una de GBPUSD y una de EURUSD.

**Temporalidades:**

| Temporalidad | Capturas | Uso |
|---|---|---|
| M15 | 95 | Marcar niveles |
| M1 | 91 | Ejecución |
| M30 | 66 | Marcar niveles |
| M5 | 41 | Ejecución |
| H1 | 40 | Contexto |
| D1 | 24 | Contexto |
| H4 | 18 | Contexto |
| W1 | 9 | Contexto |

**Dirección:** unas 185 capturas son ventas y unas 94 son compras. Opera sobre todo a favor de la bajada del oro desde agosto.

## 2. Corrección importante: el número grande no es el saldo
El número del botón central de la barra inferior del MT5 (2,02M, 5,10M, 8,63M…) es **el beneficio flotante de las posiciones abiertas, no el saldo de la cuenta**. Se comprueba en las capturas de la pestaña *Trade*:

| Captura | Balance (dinero cerrado) | Equity (con lo abierto) | Botón central |
|---|---|---|---|
| 8 de octubre (photo_86) | **450.042 $** | 634.259 $ | — |
| 29 de octubre (photo_310) | **676.685 $** | 6.963.046 $ | 6.286.361 $ (suma de 8 posiciones abiertas) |
| 7 de noviembre (photo_388) | **474.658 $** | 1.130.658 $ | 656.000 $ |

Por tanto, **mi cálculo anterior de "×4,27 en 43 días" estaba mal**: comparaba beneficios flotantes, no el crecimiento de la cuenta. El saldo cerrado que se ve pasa de unos 450.000 $ a unos 475.000 $ en un mes, con un pico de 677.000 $ entre medias. No sé si hubo retiradas.

Además, los números alternan entre **al menos dos o tres cuentas**: la grande (`.ecn`), otras de entre 15.000 y 500.000 $ y una pequeña (`.raw`).

## 3. El método, paso a paso (lo que analiza)

### Paso 1: el mapa de niveles en TradingView (M15, M30 y H1)
Marca zonas horizontales con una caja gris y una etiqueta:

| Etiqueta | Veces | Qué significa |
|---|---|---|
| **Key • [Sell]** / **Key • [Buy]** | 50 / 40 | El nivel clave donde piensa vender o comprar. Suele estar en un **máximo o mínimo anterior**, en un **doble techo o doble suelo**, o en la **base del impulso** que lo creó. |
| **[ + ] //** | 28 | Una marca propia que acompaña al Key. Por cómo la usa, parece indicar que el nivel está **confirmado** o que la orden **ya está puesta**. No está explicada en ninguna parte. |
| **Classic A** | 15 | El nivel **A de MSNR**: una vela alcista seguida de una bajista, marcado con los cuerpos. Es una resistencia. |
| **Break** / **Weekly break** | 15 / 3 | Una **ruptura de estructura**: el precio cierra más allá del último máximo o mínimo, o del de la semana. |
| **CE50%** | 9 | El **50 % de la vela o de la mecha** que forma el nivel. Es el punto exacto de la entrada dentro de la zona. |
| **Ts** / **Fts / Fake break** | 9 / 3 | **Turtle soup**: un barrido falso de un máximo o mínimo. **Fts** es un turtle soup fallido o una ruptura falsa. |
| **X** | 10 | El punto de liquidez o de invalidación que el precio tiene que barrer. |
| **1H QM** | 4 | Un **Quasimodo de H1** como confirmación del giro. |

**No usa** BOS, CHOCH, MSS, FVG, Order Blocks ni Fibonacci. Su método es casi puro **MSNR + liquidez**: niveles con cuerpos y barridos.

### Paso 2: el contexto (H1, H4, D1 y W1)
- Mantiene **ventas grandes de varios días** abiertas desde arriba (37 lotes en 4.629, 100 en 4.198 y 100 en 4.077). Son la mayor parte del beneficio flotante.
- Sobre esa tendencia bajista abre operaciones **tácticas en los dos sentidos**: compras en los suelos y ventas en los techos.

### Paso 3: la ejecución (M1, M3 y M5)
- Pone **órdenes límite de 100 lotes justo en el Key** (SELL LIMIT o BUY LIMIT, 57 capturas) antes de que llegue el precio.
- La entrada se llena en la **mecha del barrido**. En los datos reales del oro, varias entradas caen al céntimo en el nivel: 4.011,2 el 26 de octubre dentro de un V de H1 (4.011,1–4.011,9), y 3.989 y 4.059,18 en el giro exacto.
- Algunas órdenes no se llenan y aun así publica la regla de medición mostrando lo que habría ganado.

### Paso 4: el stop
En las 126 capturas de oro donde se ven la entrada y el stop:
- Distancia mediana: **1,01 $ (10 pips)**.
- La cuarta parte está a **0,19 $ o menos**, es decir, ya en la entrada (breakeven).
- Tres de cada cuatro están a **3 $ o menos**. El máximo visto es 11,8 $.
- En **muchas capturas no hay stop visible**.

### Paso 5: la gestión
1. **Breakeven muy rápido:** mueve el stop a la entrada en cuanto la operación va a favor.
2. **Cierres parciales:** por ejemplo, 100 → 95 → 84 → 68 lotes, o 10 → 2,92 → 2,39.
3. **Casi nunca pone take profit.** Deja correr las ganadoras durante horas o días.
4. **Escalonamiento:** 2 o 3 ventas de 100 lotes en el mismo techo (por ejemplo 4.125, 4.127 y 4.128).
5. **Cobertura:** a menudo tiene compras y ventas abiertas a la vez.

### Paso 6: las noticias
Publica antes el **calendario económico** y opera los datos de EE. UU.: IPC (14 de octubre y 10 de noviembre), PPI (13 de noviembre), FOMC (28 de octubre) y NFP. Varias de las mejores capturas son del minuto del dato. Por ejemplo, la compra del 13 de noviembre a las 8:30 NY en 3.880,18, en el PPI, que subió 26 $ en minutos.

### Paso 7: el tamaño
- **100 lotes** en la cuenta grande: en el oro, cada dólar de movimiento son **10.000 $**.
- Con un stop de 1 $, el riesgo es de unos 10.000 $, alrededor de un **2 % de un saldo de 475.000 $**.
- Sin stop, un movimiento en contra de 47 $ con una sola posición de 100 lotes se lleva el saldo entero.

## 4. Lo que no se ve (y cómo afecta)
- **Pérdidas:** solo 18 de las 499 capturas muestran un número negativo, casi todas pérdidas flotantes momentáneas. Las únicas **pérdidas cerradas** son de la **cuenta pequeña** (`.raw`): −153,70 $ el 24 de noviembre, en un informe con un **drawdown máximo del 251 %**.
- **Órdenes que desaparecen** cerca del stop, sin captura del cierre: photo_323, photo_536 y photo_544, entre otras.
- **El historial completo de la cuenta grande no aparece nunca.**
- **Marketing:** el canal mezcla las señales con el logo "DLT-9", un bot "IDOVA", listas de suscriptores, señales "premium", una semana gratis, pagos en USDT y capturas de seguidores. Esto no dice nada de si el método funciona, pero indica que **el canal también vende algo**.

## 5. Cómo practicarlo tú (versión prudente, en demo)
1. **Cada mañana**, en M30 y M15, marca 2 o 3 **Key**: los últimos máximos y mínimos del día anterior y de Asia, dobles techos y suelos, y niveles **A/V de MSNR** (con cuerpos). Apunta el **CE50%** de la vela que forma cada nivel.
2. **Decide la dirección** con H1 y H4: vende en Keys de arriba si el contexto es bajista y compra en Keys de abajo si es alcista.
3. **Pon una orden límite en el CE50% del Key**, con el stop **1–3 $ por detrás del extremo** del nivel. Si el precio barre el nivel y vuelve (Ts), es la situación que busca.
4. **Opera solo** en Londres (02:00–05:00 NY) y en Nueva York (07:00–11:00 NY). Con IPC, PPI, FOMC o NFP, entra solo si tu orden ya estaba puesta en un Key.
5. **Gestión:** mueve el stop a la entrada a +1R, cierra la mitad en el siguiente máximo o mínimo y deja correr el resto.
6. **Tamaño con 100 $:** 0,01 lotes = 1 $ por cada dólar de movimiento. Con un stop de 1–3 $, arriesgas **1–3 $, es decir, un 1–3 %**. No subas de ahí hasta tener 100 operaciones apuntadas.
7. **Apunta todo:** hora, Key, CE50%, stop, resultado en R y foto antes y después. Es justo lo que el canal no enseña.

## 6. Conclusión
- El trader usa **MSNR y liquidez**: niveles clave con cuerpos (Classic A, CE50%), barridos (Ts) y rupturas (Break). Ejecuta con **órdenes límite de 100 lotes**, **stops de unos 10 pips** que pasa enseguida a la entrada, **sin take profit** y aprovechando **las noticias**.
- **Los gráficos son reales:** los precios coinciden con los datos del oro. Pero **el éxito del canal no está demostrado.** Los números grandes son flotantes. El saldo real que se ve (unos 450.000–677.000 $) no muestra un crecimiento como el que sugieren las capturas. Y casi no se ven pérdidas.
- El método **sí se puede aprender y practicar**, pero solo tus propias estadísticas en demo te dirán si funciona.
