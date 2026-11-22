# Método Alchemist SnR (MSNR) paso a paso, aplicado al XAUUSD

> Material educativo. No es asesoramiento financiero. Esta guía resume con mis palabras las reglas públicas del método y cómo las he comprobado con datos. Practica primero en una cuenta demo.

## 0. La idea en una frase
Se espera a que el precio llegue a una zona importante de temporalidad alta **a favor de la dirección del mercado**, se deja que barra la liquidez (que salte los stops de otros) y se entra cuando el precio confirma el giro con un **Quasimodo**.

## 1. Marcar los niveles (solo cuerpos, nunca mechas)
Usa el **gráfico de líneas** o fíjate solo en la apertura y el cierre de cada vela.

| Nivel | Cómo se forma | Qué es |
|---|---|---|
| **A** (Classic A) | Una vela alcista seguida de una bajista. La zona va del cierre de la primera a la apertura de la segunda. | Resistencia |
| **V** (Classic V) | Una vela bajista seguida de una alcista. | Soporte |
| **GAP** | El hueco entre el cierre de un día (17:00 NY) y la apertura del siguiente (18:00 NY). | Soporte si el gap es alcista, resistencia si es bajista |

- **Dónde:** en **D1, H4 y H1**. Son los **POI**, los puntos de interés.
- **Frescura:** un nivel solo vale **la primera vez** que el precio vuelve a él. Después de tocarlo ya está "usado" y no se opera.

## 2. El storyline (la dirección)
- **Alcista:** la última vela de H4 que rompió con cuerpo un nivel lo hizo **hacia arriba**, rompiendo un nivel A.
- **Bajista:** la última ruptura con cuerpo fue **hacia abajo**, rompiendo un nivel V.
- **Regla:** solo se compra con storyline alcista en H4 y en H1, y solo se vende con storyline bajista en ambos. **Es la regla que más ha ayudado en todas las pruebas.**

## 3. Esperar al POI y a la liquidez
- **Para comprar:** el precio baja hasta un soporte (V o GAP alcista) fresco de H1, H4 o D1. Antes de llegar, conviene que haya hecho al menos 2 máximos cada vez más bajos. Esa es la **línea de tendencia** que el mercado barrerá; el curso habla de un ángulo de 45–60°.
- **Para vender:** al revés, el precio sube hasta una resistencia (A o GAP bajista) fresca.

## 4. El gatillo: el Quasimodo (QM) en M15
Para comprar, en M15:
1. Hay un mínimo **L** y después un máximo **H**.
2. El precio baja más allá de **L** y forma un **LL**, tocando el POI. Ahí se barre la liquidez.
3. Una vela **cierra con cuerpo por encima de H** y forma un **HH**. Ese es el cambio de estructura.
4. El **nivel QM es L**. Se pone una **orden límite en L** y se espera a que el precio vuelva a él.

Para vender es lo mismo, pero al revés: H, L, HH y LL, con la orden límite en H.

**Horario:** solo en las sesiones de Londres (02:00–05:00 NY) y Nueva York (07:00–11:00 y 13:00–15:00 NY). No se opera en Asia.

## 5. Stop y take profit adaptados al mercado
- **Stop:** detrás del LL (o del HH en ventas), con un pequeño margen. Si el stop es enorme, más grande que el ATR de H1, no se opera.
- **TP1:** el HH del Quasimodo (o el LL en ventas). Ahí se cierra el **50 %** y el stop se mueve a la entrada, para no perder.
- **TP2:** la **siguiente liquidez** que aún no se ha barrido: un máximo o mínimo de H1, o el máximo o mínimo del día anterior. Ahí se cierra el otro 50 %.

## 6. Gestión del dinero
- **Riesgo:** un **1 % de la cuenta** por operación (como mucho un 2 %). Con un 5 % se gana más rápido cuando sale bien, pero una mala racha te deja sin cuenta.
- **Tamaño:** lotes = (saldo × riesgo) ÷ (distancia al stop en $ × 100). Ejemplo: con 100 $, un 1 % de riesgo y un stop de 4,47 $, salen 0,002 lotes. Es **menos que el lote mínimo** (0,01), así que con 100 $ hace falta un bróker que permita **micro lotes o cuentas cent**.
- **Límite diario:** después de 2 pérdidas en un día, no se opera más ese día.

## 7. Checklist antes de entrar
- [ ] Storyline de H4 y H1 a favor
- [ ] POI fresco de H1, H4 o D1 (primer toque)
- [ ] Barrido de liquidez (LL o HH) dentro del POI
- [ ] Quasimodo confirmado con cierre de cuerpo en M15
- [ ] Orden límite en el nivel QM y dentro de la sesión de Londres o Nueva York
- [ ] Stop detrás del barrido y más pequeño que 1 ATR de H1
- [ ] TP1 a 1R como mínimo, y TP2 en la siguiente liquidez
- [ ] Riesgo del 1 % y menos de 2 pérdidas hoy

## 8. Ejemplo real: venta del 29 de octubre de 2026
- **Contexto:** storyline bajista en H4 y en H1. El precio sube hasta una resistencia **A de H1** fresca.
- **Quasimodo:** en M15, barre el último máximo y cierra con cuerpo por debajo del mínimo anterior.
- **Entrada:** orden límite en el nivel QM, a **4.034,11** (10:44 NY).
- **Stop:** 44,7 pips (unos 4,47 $) por encima.
- **Salidas:** TP1 en 3,9R y TP2 en 4,1R.
- **Resultado: +4,0R.** Con un 1 % de riesgo, la cuenta sube un 4 %.

## 9. Qué esperar (comprobado con XAUUSD de enero a noviembre de 2026)
| Versión | Operaciones/año | Acierto | Resultado medio | 100 $ al 1 % | 100 $ al 5 % |
|---|---|---|---|---|---|
| **Entrada en M15, POI de H1/H4/D1** | 11–12 | 36 % | +0,52R | 105,67 $ | 126,03 $ |
| Entrada en M5 (la misma idea) | 18–20 | 17 % | −0,42R | 92,51 $ | 65,48 $ |
| Solo POI de H4/D1 en M15 (más estricto) | 3 | 33 % | +0,52R | 101,50 $ | 106,32 $ |

Este método da **pocas operaciones**: alrededor de una al mes. Además, solo la versión en M15 sale positiva en 2026, y 11 operaciones son muy pocas para estar seguros. Practícalo en demo y apunta cada operación para tener tus propias estadísticas.
