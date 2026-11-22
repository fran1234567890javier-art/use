# MSNR Alchemist en XAUUSD con RR mínimo 1:5

> Material educativo. No es asesoramiento financiero. No se ha enviado ninguna orden.

## Datos

- **Activo:** XAUUSD (oro spot), velas de 1 minuto BID con spread real (Exness XAUUSDm, huecos rellenados con Dukascopy), del repositorio público [Best6626840/xauusd-m1-data](https://github.com/Best6626840/xauusd-m1-data).
- **Periodo:** 2 de enero a 19 de noviembre de 2026: 229 días de trading, 313.906 velas de 1 min y 62.902 de 5 min.
- **Comprobación de los datos:** comparé las velas con otra fuente independiente ([getdata-finance XAUUSD 5m](https://github.com/getdata-finance/xauusd-5m-ohlcv-metals-historical-data), marzo a septiembre). La correlación de los retornos horarios es **0,998**. Hay una diferencia de nivel de aproximadamente +0,45 %, compatible con que esa fuente sea el futuro (con prima sobre el spot). Las horas cuadran.
- **Comportamiento del precio en el periodo:** el oro bajó un 14,8 % (de 4.328 a 3.688 $).

## Reglas (las mismas que en TSLA, adaptadas a un mercado de casi 24 h)

| Regla | Detalle |
|---|---|
| Niveles (1 h, solo cuerpos) | A = vela alcista y después bajista (resistencia). V = bajista y después alcista (soporte). GAP = salto entre el cierre de las 17:00 y la reapertura de las 18:00 NY. Caducan a los 5 días. |
| Frescura | Solo se opera el primer toque de cada nivel. |
| Storyline | Última ruptura de cuerpo en 1 h: por encima de un A = alcista, por debajo de un V = bajista. Solo se opera a favor. |
| Confirmación (5 min) | En las 6 velas siguientes al toque, una vela cierra más allá del extremo de la vela de toque. Se entra en la apertura de la vela siguiente. |
| Stop | Extremo de la reacción ± 0,05 %, con un riesgo mínimo del 0,15 % (unos 6 $). |
| **Objetivo** | **5R, es decir, RR 1:5** |
| Horario | Entradas de 03:00 a 15:00 NY (Londres y Nueva York). Cierre forzado a las 16:50 NY, antes de la pausa diaria. |
| Costes | Spread real de cada vela: los largos compran al ask y venden al bid, y los cortos al revés. Si una vela toca el stop y el objetivo a la vez, cuenta como stop. Si el precio abre más allá del stop, se ejecuta a la apertura. |

Para ganar dinero con 1:5 basta un **16,7 % de aciertos** (1 de cada 6 operaciones).

## Resultados con RR 1:5

| Variante | Ops | Aciertos | R medio | R total | PF | Máx. DD | IC 90 % del R medio | Stop / Objetivo / Cierre |
|---|---|---|---|---|---|---|---|---|
| **A. MSNR completa** | 209 | 31,1 % | **+0,067** | +14,0 | 1,10 | −33,5R | −0,14 a +0,28 | 136 / **16** / 57 |
| B. Solo largos | 118 | 31,4 % | +0,060 | +7,1 | 1,09 | −22,3R | −0,22 a +0,34 | 76 / 9 / 33 |
| C. Solo cortos | 98 | 29,6 % | +0,080 | +7,8 | 1,12 | −16,7R | −0,21 a +0,39 | 63 / 8 / 27 |
| D. Sin storyline | 379 | 26,6 % | **−0,126** | −47,7 | 0,82 | −82,1R | −0,27 a +0,02 | 266 / 23 / 90 |
| E. Solo sesión NY | 138 | 35,5 % | +0,036 | +5,0 | 1,06 | −31,1R | −0,18 a +0,26 | 80 / 6 / 52 |
| F. Dejando correr hasta 3 días | 199 | 20,6 % | +0,142 | +28,4 | 1,18 | −45,9R | −0,12 a +0,43 | 158 / 36 / 5 |
| Ref. MSNR completa 1:2 | 219 | 40,2 % | +0,101 | +22,2 | 1,18 | **−8,4R** | −0,05 a +0,25 | 124 / 67 / 28 |

"Aciertos" incluye las operaciones cerradas en positivo a las 16:50 sin llegar al objetivo. **Solo el 7,7 % de las operaciones (16 de 209) llegó al objetivo de 5R.** El resto de la ganancia procede de cierres forzados en positivo.

### Barrido de RR (estrategia completa)

| RR | 1:1 | 1:2 | 1:3 | 1:4 | **1:5** | 1:6 | 1:8 |
|---|---|---|---|---|---|---|---|
| R medio | −0,044 | **+0,101** | +0,051 | +0,054 | +0,067 | +0,067 | +0,008 |
| Llegan al objetivo | 100 | 67 | 38 | 26 | 16 | 10 | 4 |
| Máx. DD | −12,8R | **−8,4R** | −18,4R | −23,9R | −33,5R | −33,5R | −33,5R |

## Comprobaciones

1. **Velas de 1 minuto:** rehice las 209 salidas minuto a minuto. No cambió ninguna (0 velas ambiguas) y el R medio sigue en +0,067.
2. **Auditoría manual:** recalculé desde los datos brutos el corto del 18 de noviembre a las 09:15. La salida a las 16:50 fue de 3.723,78, idéntica a la del backtest.
3. **Mitades del año:**
   - Enero a 12 de junio: +0,283R por operación, 105 operaciones.
   - 12 de junio a noviembre: **−0,151R** por operación, 104 operaciones, con una racha de 14 pérdidas seguidas.
   - Agosto (−13,3R) y septiembre (−10,9R) fueron los peores meses.
4. **Contra entradas al azar:** generé 300 carteras de 209 entradas con hora y lado aleatorios y el mismo riesgo y objetivo 5R. Su R medio mediano es −0,041. La estrategia (+0,067) supera al **82 %** de ellas, por debajo del 95 % que haría falta para descartar la suerte.
5. **Intervalo de confianza:** el IC 90 % del R medio incluye el cero, y hay un 30 % de probabilidad (bootstrap) de que el R medio real sea ≤ 0.

## Prueba con las skills (señal real del 6 de noviembre de 2026)

Señal: largo en un nivel V, entrada a 4.056,36 a las 10:15 NY, stop a 4.040,98 y objetivo a 4.133,26 (5R).

- **trader-exit:** plan válido, RR 5,0. Al redondear el objetivo a 4.133,25 el RR real quedaba en 4,9993 y el gestor de presupuesto lo rechazaba por estar por debajo del mínimo de 5. Hay que redondear el objetivo **hacia arriba**.
- **trader-timemachine** (10.000 simulaciones con 59 sesiones de oro, de 9:30 a 15:55): el objetivo sale primero en el **0,3 %** de las simulaciones, el stop primero en el 58,6 % y ninguno de los dos en el 41,1 %. R medio −0,066. En una sola sesión de NY, 5R casi nunca llega.
- **trader-budget** (configuración de 20.000 $, pérdida máxima de 50 $ y RR mínimo de 5): 3 onzas, con una pérdida máxima de 46,14 $. Con 5.000 $ no cabía ni una onza (1 oz ≈ 4.056 $).
- **trader-risk:** **BLOQUEADA**, porque XAUUSD no es una acción ni un ETF de EE. UU. y el paquete solo opera esos activos. Es el comportamiento correcto. Para operarlo habría que usar un bróker de CFD o futuros, o un ETF como GLD.
- **trader-broker:** muestra el ticket marcado como BLOQUEADO y no envía nada.
- **Resultado real de esa operación:** no tocó ni el stop ni el objetivo. Se cerró a las 16:50 en +0,66R.

## Conclusión

- Con RR 1:5 en XAUUSD, el MSNR mecanizado sale **ligeramente positivo (+0,067R por operación, +14R en 10,5 meses)**, pero **no es estadísticamente distinguible del azar**: el IC incluye el 0 y las entradas aleatorias lo igualan el 18 % de las veces.
- Además, toda la ganancia se concentra en la primera mitad del año. En la segunda mitad pierde.
- 1:5 es peor que 1:2 en este sistema. Rinde menos por operación (+0,067 frente a +0,101) y el drawdown es 4 veces mayor (−33,5R frente a −8,4R). Exige soportar rachas de 14 pérdidas seguidas. Con un objetivo tan lejano, el cierre intradía corta casi todas las operaciones antes del objetivo (solo 16 de 209 llegan).
- Dejar correr la operación 3 días mejora el R medio (+0,142), pero con un drawdown de −45,9R y una racha de 30 pérdidas seguidas.
- **Lo que sí aporta valor es la storyline.** Sin ella, el resultado es claramente negativo (−0,126R en 379 operaciones). Esto coincide con lo que vimos en TSLA.

### Advertencias

- Esta es una versión mecánica de una estrategia discrecional. Un trader de MSNR filtraría los niveles de otra forma.
- Solo hay un activo y 10,5 meses de datos, sin optimización de parámetros. Probar muchas variantes y quedarse con la mejor es sobreajuste.
- Los datos son de un bróker concreto (Exness Standard). Otros brókeres tienen spreads y precios ligeramente distintos.
- Se han ignorado el swap nocturno (variante F) y el deslizamiento en noticias.

## Archivos

- `msnr_xauusd.py`: el backtest. Uso: `python3 msnr_xauusd.py XAUUSD_M1_2026.csv.gz`.
- `msnr_xauusd_results.json`: todos los resultados y todas las operaciones.
- `XAUUSD_M1_2026.csv.gz`: los datos de 1 minuto.
- `XAUUSD-60d5m.json.gz`: las 61 sesiones en formato Yahoo usadas por trader-timemachine.
- `xau_pipeline/trader/`: el plan, la simulación, la orden propuesta y la configuración usada en la prueba con las skills.
