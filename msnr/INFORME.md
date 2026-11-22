# MSNR «Alchemist» en TSLA: backtest y prueba del flujo completo

Datos: 60 sesiones de velas de 5 minutos de TSLA, del 27-07-2026 al 19-10-2026 (4.619 velas, solo horario regular). Son los datos de ejemplo que trae el paquete `day-trader-skill`: desde este entorno no se puede descargar cotizaciones nuevas (Yahoo devuelve 403).

## 1. Las reglas que he probado

MSNR (Malaysian Support and Resistance) es un método discrecional. Para poder medirlo lo he convertido en reglas fijas:

| Paso | Regla |
|---|---|
| Niveles (1 h) | Solo cuerpos, nunca mechas. **A** (resistencia): vela alcista seguida de bajista. **V** (soporte): bajista seguida de alcista. **GAP**: hueco entre el cierre de un día y la apertura del siguiente. |
| Frescura | Solo se opera el **primer toque** de un nivel; después deja de ser válido. |
| Storyline (sesgo, 1 h) | Alcista si la última ruptura de cuerpo fue por encima de un A; bajista si fue por debajo de un V. Solo se opera a favor. |
| Confirmación (5 min) | Tras tocar el nivel, en ≤ 30 min una vela cierra más allá del extremo de la vela de toque sin haber cerrado al otro lado del nivel. Entrada en la apertura siguiente. |
| Stop / objetivo | Stop detrás del extremo de la reacción (± 0,05 %). Objetivo 2R. Cierre obligatorio a las 15:55. Entradas entre 9:45 y 15:00. |
| Costes | 0,02 % por lado. Si una vela toca stop y objetivo, cuenta como stop. |

## 2. Resultados

R = múltiplos del riesgo de cada operación (−1R = salta el stop).

| Variante | Operaciones | % ganadoras | R medio | R total | Factor de beneficio | Peor racha (R) | IC 90 % del R medio |
|---|---|---|---|---|---|---|---|
| **MSNR completa (2R, largos y cortos)** | 26 | 38,5 % | **−0,13** | −3,3 | 0,79 | −8,6 | −0,50 a +0,26 |
| Objetivo 3R | 26 | 38,5 % | −0,19 | −5,0 | 0,68 | −8,6 | −0,54 a +0,17 |
| Sin storyline | 42 | 33,3 % | −0,17 | −6,9 | 0,74 | −12,5 | −0,47 a +0,15 |
| Solo largos | 15 | 40,0 % | **+0,14** | +2,1 | 1,26 | −6,8 | −0,41 a +0,74 |
| Solo cortos | 10 | 40,0 % | −0,44 | −4,4 | 0,31 | −4,4 | −0,83 a −0,02 |

En el mismo periodo, TSLA subió un 16,9 %.

## 3. Conclusiones

1. **La versión completa pierde dinero**: −0,13R por operación. Con una regla de riesgo de 50 $ por operación, serían unos −165 $ en 60 días.
2. **El filtro de storyline sí ayuda**: sin él, más operaciones y peor resultado (−0,17R).
3. **Los largos salen positivos y los cortos muy negativos**, pero esto refleja sobre todo que TSLA subió con fuerza en estos meses: comprar soportes en una acción alcista funciona casi con cualquier regla.
4. **Subir el objetivo a 3R empeora**: el precio casi nunca llega tan lejos antes del cierre.
5. **La muestra es demasiado pequeña** para sacar conclusiones firmes: con 26 operaciones, el intervalo de confianza va de −0,50R a +0,26R. No se puede afirmar ni que funcione ni que no funcione. Harían falta varios cientos de operaciones, en varios valores y en mercados bajistas y laterales.

**Veredicto:** con estos datos, MSNR tal y como la he mecanizado **no tiene ventaja demostrada**. No la operaría con dinero real.

## 4. Prueba del flujo completo con las skills (simulación, sin dinero)

Última señal de compra de la estrategia: **TSLA, 15-10-2026 a las 14:50**, entrada 360,79, stop 359,62, objetivo 363,12.

| Skill | Resultado |
|---|---|
| `trader-exit` | Riesgo 1,17 $ por acción (0,32 %), relación 1,99R, cierre obligatorio 15:55. |
| `trader-timemachine` | 10.000 simulaciones: objetivo primero 26 %, stop primero 50 %, ni uno ni otro 24 %. R medio esperado +0,15. «Cerca del punto de equilibrio». |
| `trader-budget` | Con 5.000 $ y máximo 50 $ de pérdida: **10 acciones** (3.608 $). Pérdida máxima 11,70 $. |
| `trader-risk` | **PASS**: dentro de todos los límites. |
| `trader-broker` | Ficha de orden preparada (bracket con stop y objetivo). **No se envió**: no hay bróker conectado y siempre exige tu «sí». |

Lo que pasó de verdad aquel día: el precio llegó al objetivo, **+1,88R** (unos +22 $ con 10 acciones).

## Archivos

- `msnr_backtest.py`: el backtest (reproducible).
- `msnr_results.json`: resumen y lista de todas las operaciones.
- `trader/`: plan, simulación, orden propuesta y verificación de riesgo.

*Material educativo, no asesoramiento financiero.*
