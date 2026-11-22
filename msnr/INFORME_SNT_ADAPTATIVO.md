# XAUUSD 2026 con los apuntes White SNT, stop y take profit adaptados al mercado

> Material educativo. No es asesoramiento financiero. No se ha enviado ninguna orden.
> Periodo analizado: del 2 de enero al 19 de noviembre de 2026, con velas de 1 minuto y spread real. Cuenta inicial de 100 $.

## Qué cambia respecto a la prueba anterior

La entrada es la misma de antes: Key level Classic A o V de H1/H4 fresco, a favor de la storyline H1, barrido de liquidez, MSS con cuerpo, orden límite en el 0,764 (Hunter model), solo dentro de las killzones y un máximo de 2 pérdidas al día. Lo que cambia es la gestión de la salida:

| | Antes | Ahora (adaptado al mercado) |
|---|---|---|
| Stop | Detrás del barrido, con un máximo de 50 pips | Detrás del barrido más un colchón de 0,05 × ATR(H1). Se acepta si mide entre 0,15 y 1 ATR(H1), es decir, se ajusta a la volatilidad del momento. |
| TP1 | — | El extremo del impulso (nivel 0 del Fibonacci, liquidez interna). Tiene que dar al menos 1R. |
| TP2 | 14R a 20R fijos | La liquidez externa más cercana que aún no se ha barrido: un swing de H1 o el PDH/PDL. Si no hay ninguna, la extensión STD −2. |
| Gestión | Todo o nada | Se cierra el 50 % en TP1, el stop pasa a la entrada (BE) y el otro 50 % se deja correr hasta TP2, como recomiendan los apuntes. |
| Temporalidad de entrada | M5 | M1, M5 y M15, por separado y combinadas ("todas las temporalidades") |

Con estas reglas, el stop medio queda en 66 pips. El TP1 cae de media a 2,7R y el TP2 a 6,7R. Todos los niveles se calculan solo con datos anteriores a la entrada.

## Resultados (5 % de riesgo por operación)

| Entrada | Operaciones | Acierto* | R medio | R total | Factor de beneficio | Peor racha | 100 $ → |
|---|---|---|---|---|---|---|---|
| M1 | 50 | 30 % | −0,09 | −4,7 | 0,87 | 10 | **69,07 $** |
| M5 | 39 | 26 % | −0,13 | −5,1 | 0,82 | 15 | **69,03 $** |
| M15 | 19 | 21 % | −0,31 | −5,9 | 0,61 | 9 | **71,23 $** |
| **Todas (M1+M5+M15)** | 89 | 27 % | −0,14 | −12,6 | 0,81 | 18 | **41,55 $** (caída máxima −77 %) |

*Acierto = operaciones que llegaron al TP1. En las de la columna "Todas", 10 llegaron al TP2, 14 salieron en BE tras cobrar el TP1 (+1,4R de media) y 65 tocaron el stop.

Con un 1 % de riesgo en lugar del 5 %, las mismas operaciones dejan la cuenta en 87–95 $.

### Otras formas de salir (con todas las temporalidades)
| Salida | R medio | 100 $ → |
|---|---|---|
| **50 % en TP1 + BE + 50 % en TP2 (apuntes)** | −0,14 | 41,55 $ |
| 100 % en TP1 | −0,01 | 73,23 $ |
| 100 % a TP2, con BE tras tocar TP1 | −0,28 | 21,98 $ |

## Comprobaciones
- **Por mitades del año:** de enero a junio, +2,8R (casi todo en marzo, +10,4R). De junio a noviembre, −15,4R, con una racha de 18 pérdidas seguidas.
- **Por meses:** solo marzo (+10,4R) y noviembre (+5,5R) son claramente positivos.
- **Contra el azar:** generé 100 carteras de entradas al azar dentro de las killzones con el mismo stop, TP1 y TP2. Su R medio mediano es −0,06; la estrategia, −0,14. El azar empata o gana el 64 % de las veces.
- **Coherencia del cálculo:** revisé las 89 operaciones. Los R de las salidas en BE y en TP2 cuadran con sus TP1 y TP2.

## Conclusión
Adaptar el stop y el take profit al mercado mejora mucho el resultado frente al RR fijo de 1:14–1:20. Se pasa de 0 de 19 a un 27 % de operaciones que cobran TP1, y la pérdida media baja de −1R a −0,14R. Pero **sigue sin dar beneficio en 2026**. Con un 5 % de riesgo, los 100 $ acaban en **41,55 $**.

Un x9578 no sale de estas reglas. Exigiría acertar el TP1 en lugar del stop muchas más veces, algo que ninguna versión mecánica consigue en estos datos.

Lo que separa este resultado del de un trader discrecional es la elección de qué setups tomar y cuáles saltarse, y eso no se puede mecanizar sin ver el gráfico a posteriori. La única forma de comprobarlo es con su historial real de operaciones.

## Archivos
- `snt_adaptativo.py`: el backtest.
- `snt_adaptativo_results.json`: todas las operaciones, la curva de la cuenta, las variantes y las comprobaciones.
