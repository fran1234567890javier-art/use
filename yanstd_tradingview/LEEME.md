# YANSTD SMC Scalper para TradingView (port en Pine Script v5)

Port simplificado del EA de MT5 **YANSTD** ([yanstd888/institutional-smc-scalper-mt5](https://github.com/yanstd888/institutional-smc-scalper-mt5), licencia MIT). Un EA de MT5 no funciona en TradingView, así que la lógica de señales está reescrita en Pine.

> Material educativo, no asesoramiento financiero.

## Archivos

| Archivo | Para qué |
|---|---|
| `YANSTD_indicador.pine` | Dibuja POIs, órdenes límite, SL/TP, sesgo M15, panel y alertas |
| `YANSTD_estrategia.pine` | Lo mismo, y además ejecuta las órdenes en el Probador de estrategias |
| `plantilla.pine` + `build_pine.py` | Fuente común de los dos scripts |
| `simular.py` | Réplica en Python para comprobar que salen señales |

## Cómo ponerlo

1. Abre el archivo `.pine` en GitHub y pulsa **"Copy raw file"** (el icono de copiar). No selecciones el texto a mano: si se cuela "ine Script®" al principio sale el error CE10005.
2. En TradingView: **Editor de Pine** → borra todo → pega → **Guardar** → **Añadir al gráfico**.
3. Gráfico **XAUUSD en 3 minutos** (sirve de 1 a 5 minutos). En 15 minutos o más el panel avisa en rojo y no funciona bien.
4. Si tarda en aparecer algo, baja hasta el principio del historial cargado: necesita unas 100 velas M15 para fijar el sesgo.

## Qué hace (igual que el EA, salvo lo indicado)

- **Sesgo M15:** máquina de estados BOS / CHoCH con pivotes de 6 velas, ruptura por cierre con desplazamiento (cuerpo ≥ 55%). El CHoCH deja un "giro pendiente" que caduca a las 12 velas M15.
- **King SNR H4 y H1:** par de velas que barre un mínimo (o máximo) y cierra de vuelta. Si va en contra, la operación cuenta como contra tendencia (−10 puntos y mínimo 75).
- **POI M5:** vela de desplazamiento (cuerpo ≥ 70%) que rompe el máximo/mínimo de las 12 velas previas, deja un FVG > 0,30·ATR y un OB ≤ 1,5·ATR. Debe haber barrido liquidez o contener un nivel de $5.
- **Entrada:** orden límite en el 50% del FVG o en el Fib 0,786. Se descarta si está a más de 2,25·ATR M5, si el RR estructural es < 1,10 o si no está en OTE 0,618–0,786. Gana el candidato con más puntuación (mínimo 50).
- **SL:** fondo del POI − 2·ATR M15 − spread, limitado entre 0,35 y 2,5 ATR M15.
- **Salidas:** TP1 a 1,5R (cierra 50% y SL a breakeven), TP2 a 1,6R (cierra 25%), el 25% restante corre sin TP. Si llega a 1,2R a favor, SL a +0,3R. Si tras 16 velas M5 no ha ido ni 0,7R a favor, cierra.
- **Caducidad:** 60 velas M5 (preset L5) o 30 (preset G27B). Máximo 3 órdenes a la vez.
- **Horario UTC:** no opera fin de semana ni de 20:00 a 22:59; cierra todo el viernes a las 20:00.
- **Modo "Gatillo M3"** (opcional): en vez de límite, entra a mercado cuando el precio toca el POI y en M3 hay barrido + CHoCH. Los triángulos verdes/fucsia marcan esos gatillos en los dos modos.

## Qué NO tiene (diferencias con el EA)

- Sin ticks: un toque se aproxima con el máximo/mínimo de la vela. Si una vela toca SL y TP, se cuenta SL.
- Spread fijo (input, 0,30 $ por defecto). Sin comisiones.
- Sin SmartBrain, sin filtro de noticias, sin panel gráfico del EA.
- El mapa MSNR (OCL/A/V/QML) está muy reducido: solo da bonus si el POI coincide con el swing M15 y está en OTE.
- King SNR guarda solo la última zona de cada lado.
- TradingView es "netting": no puede tener compra y venta abiertas a la vez, así que no abre órdenes en contra de las que ya hay.
- **No he podido compilarlo aquí** (el servidor de TradingView está bloqueado desde este entorno). Lo he revisado a mano y replicado en Python. Si sale un error rojo, pásame captura del mensaje y la línea.

## Comprobación en Python (oro M1 de 2026, enero a noviembre)

`simular.py` replica la lógica del indicador sobre datos M1 reales (bid) convertidos a M3/M5/M15/H1/H4:

| Ajuste | Órdenes | Ejecutadas | Ganadas / perdidas / BE | Suma R | Media por operación |
|---|---|---|---|---|---|
| Por defecto (L5, OTE exigido) | 119 | 94 | 39 / 52 / 2 | +6,5R | +0,07R |
| Sin exigir OTE | 260 | 191 | 75 / 111 / 4 | +8,2R | +0,04R |
| Preset G27B (expira 30) | 123 | 86 | 32 / 51 / 2 | −4,0R | −0,05R |

Unas 8–10 operaciones al mes. La media está muy cerca de 0R, con meses de −7,5R y otros de +8,8R: con estos números no hay una ventaja demostrada. La réplica no es idéntica al EA (ver diferencias arriba).

En el panel, "POIs sin orden por" explica por qué no entra: la mayoría se descartan por **RR estructural** y **distancia**. Si no ves órdenes, desactiva "Exigir OTE" o "Exigir RR estructural" para ver más (a costa de peor calidad).
