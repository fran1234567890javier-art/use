# -*- coding: utf-8 -*-
"""Ampliaciones de cada capítulo del libro (se añaden al final de cada uno)."""
from build_base import chart, C

d_gap = chart(C([(101, .3, .2), (102.2, .3, .2), (103.0, .3, .2), (103.4, .2, .3)]) +
              [(104.6, 105.1, 104.3, 104.9), (104.9, 105.3, 104.2, 104.4), (104.4, 104.6, 103.6, 103.7), (103.7, 104.0, 103.3, 103.5),
               (103.5, 104.6, 103.3, 104.4), (104.4, 105.4, 104.2, 105.2)],
              boxes=[(3, 9, 103.4, 104.6, "#3b6fd8", "GAP diario")], lines=[(3, 9, 104.0, "#7a3fd1", "CE50% del gap", True)],
              arrows=[(7, 103.0, "up", "#1f9d74")], labels=[(3, 102.6, "cierre 17:00 NY", "#555"), (4, 105.7, "apertura 18:00", "#555")],
              title="Gap diario: hueco entre el cierre y la reapertura; el precio suele volver a él")

d_break = chart(C([(101, .3, .2), (102.4, .3, .2), (101.6, .2, .3), (101.0, .2, .3), (101.9, .3, .2), (102.3, .3, .2), (101.8, .2, .3),
                   (102.2, .7, .2), (103.4, .3, .2), (104.1, .3, .2), (103.6, .2, .3), (104.6, .3, .2)]),
                lines=[(1, 11, 102.7, "#3b6fd8", "máximo anterior", True)],
                labels=[(7, 103.1, "mecha: NO es Break", "#d9483b"), (8, 104.1, "cuerpo: SÍ es Break", "#1f9d74")],
                title="Break válido = CIERRE con cuerpo más allá del nivel; una mecha no cuenta")

d_qm_buy = chart(C([(104, .2, .3), (102.5, .2, .3), (101.0, .2, .4), (102.2, .3, .2), (103.2, .3, .2), (101.6, .2, .3), (100.0, .2, .4),
                    (101.2, .3, .2), (102.6, .3, .2), (103.9, .4, .2), (102.6, .2, .3), (101.4, .2, .3), (102.5, .3, .2), (103.8, .3, .2)], start=104.2),
                 labels=[(2, 100.3, "L", "#333"), (4, 103.9, "H", "#333"), (6, 99.3, "LL", "#333"), (9, 104.7, "HH (rompe H)", "#333")],
                 lines=[(2, 13, 101.0, "#1f9d74", "QM = nivel de L: compra al volver", True)], arrows=[(11, 100.9, "up", "#1f9d74")],
                 title="Quasimodo de compra: L, H, LL, HH... y se compra el retorno al L")

d_news = chart(C([(101, .2, .2), (101.2, .2, .2), (100.9, .2, .2), (101.1, .2, .2), (100.8, .2, .2)]) +
               [(100.8, 101.0, 98.85, 99.3), (99.3, 101.6, 99.1, 101.4), (101.4, 102.3, 101.1, 102.0), (102.0, 102.6, 101.7, 102.4)],
               boxes=[(0, 8, 99.0, 99.4, "#1f9d74", "Key [Buy] (orden puesta antes)")],
               lines=[(0, 8, 99.2, "#7a3fd1", "BUY LIMIT", True), (0, 8, 98.6, "#d9483b", "SL", False)],
               labels=[(5, 101.4, "dato 8:30 NY", "#555")],
               title="Noticia: la mecha barre el Key en segundos; la orden ya estaba puesta")

d_range = chart(C([(101, .3, .2), (102.6, .3, .2), (101.4, .2, .3), (102.5, .3, .2), (101.3, .2, .3), (102.4, .3, .2), (101.5, .2, .3),
                   (102.6, .3, .2), (101.4, .2, .3), (102.5, .3, .2)]),
                boxes=[(0, 9, 101.1, 102.9, "#999", "rango: sin dirección")],
                title="Rango (lateral): muchos toques al mismo nivel = nivel USADO; mejor no operar en medio")

EXTRA = {}

EXTRA["Antes de empezar"] = """
<h3>Qué es (y qué no es) este método</h3>
<p>Es un método de <b>niveles</b>. El trader no usa indicadores. Marca zonas donde el precio ya giró antes, espera a que el precio vuelva a ellas y entra con una orden ya colocada. Su ventaja, si la tiene, está en tres cosas:</p>
<ol><li><b>Elegir bien el nivel:</b> pocos, claros y con liquidez delante.</li>
<li><b>Entrar con un stop pequeño</b>, que permite ganar varias veces lo que arriesga.</li>
<li><b>Proteger rápido</b> (breakeven) y dejar correr lo que funciona.</li></ol>
<p>No es un sistema automático. Con reglas fijas, en nuestras pruebas con el oro de 2026, los modelos parecidos salieron casi siempre <b>negativos o neutros</b>. La diferencia la marca el criterio para descartar niveles malos, y ese criterio solo se gana <b>marcando y revisando cientos de niveles</b>. Por eso el plan de práctica es tan importante.</p>
<h3>Qué necesitas</h3>
<ul><li>Una cuenta gratuita de <b>TradingView</b> (sirve en el móvil, pero es mejor en el ordenador).</li>
<li><b>MetaTrader 5</b> con una cuenta <b>demo</b> de un bróker regulado. Comprueba que el lote mínimo sea 0,01 y que el spread del oro no pase de unos 0,30 $.</li>
<li>Un cuaderno o una hoja de cálculo para el <b>diario</b>.</li>
<li>Unas <b>2 horas al día</b>, durante una de las dos killzones.</li></ul>
"""

EXTRA["1. El oro (XAUUSD) en 10 minutos"] = """
<h3>Cómo se mueve el oro en 2026</h3>
<ul><li><b>Movimiento diario medio: 117 $.</b> En enero, febrero y marzo fue de 150–180 $ al día. En octubre y noviembre, de 70–95 $.</li>
<li><b>Una vela de M5</b> en la sesión de Londres o Nueva York mide una mediana de <b>5,2 $</b>. Un stop de 1 $ es muy pequeño, menos de una vela, así que solo funciona si la entrada está justo en el nivel.</li>
<li><b>Días extremos:</b> +6,2 % el 3 de febrero y −9,0 % el 30 de enero. En días así, cualquier método sufre.</li></ul>
<h3>Ejemplo de cálculo, paso a paso</h3>
<p>Vendes 0,01 lotes en 4.137,70 con el stop en 4.140,10 y el TP1 en 4.130,50.</p>
<ul><li><b>Riesgo:</b> 4.140,10 − 4.137,70 = 2,40 $. Con 0,01 lotes, pierdes <b>2,40 $</b> si salta el stop.</li>
<li><b>Objetivo:</b> 4.137,70 − 4.130,50 = 7,20 $. Ganas <b>7,20 $</b>, es decir, <b>3R</b> (7,20 ÷ 2,40).</li>
<li><b>Spread:</b> al vender entras al precio Bid y sales comprando al Ask, unos 0,24 $ más caro. En la práctica, el stop salta cuando el Ask toca 4.140,10. Por eso los stops muy pequeños se tocan más de lo que parece en el gráfico.</li></ul>
<h3>Bid, Ask y por qué te salta el stop "sin tocarlo"</h3>
<p>El gráfico muestra normalmente el <b>Bid</b>. Las compras se abren al <b>Ask</b>, que es Bid + spread, y las ventas se cierran también al Ask. Si vendes con el stop a 0,20 $ de una mecha, puede saltar aunque el gráfico no llegue, porque el Ask sí llega. Para evitarlo:</p>
<ul><li>En las <b>ventas</b>, pon el stop al menos el spread (≈0,30 $) por encima de la mecha.</li>
<li>En MT5, activa <i>Mostrar línea Ask</i> en las propiedades del gráfico.</li></ul>
"""

EXTRA["2. Las herramientas"] = """
<h3>Configuración recomendada en TradingView</h3>
<ol><li>Símbolo: <b>OANDA:XAUUSD</b> o el de tu bróker. Así los precios son casi iguales a los del MT5.</li>
<li>Zona horaria: <b>(UTC-5) Nueva York</b>. Así las horas de las killzones son siempre las mismas.</li>
<li>Velas: alcistas en verde y bajistas en rojo, <b>sin mechas de otro color</b>, para distinguir bien los cuerpos.</li>
<li>Guarda una <b>plantilla de dibujo</b> para el Key: rectángulo gris al 25 % de opacidad, texto "Key • [Sell]" a la derecha y la opción de extender a la derecha activada.</li>
<li>Pon en la barra de favoritos: línea horizontal, rectángulo, texto, regla y posición larga y corta.</li></ol>
<h3>Configuración recomendada en MT5 (móvil)</h3>
<ol><li>Activa <i>Mostrar niveles de trading</i>, para ver la entrada, el SL y el TP en el gráfico.</li>
<li>Activa el <i>trading con un clic</i> solo cuando ya tengas práctica. Al principio usa la ventana de orden normal, para revisar el precio y el volumen antes de enviar.</li>
<li>Para poner una orden límite: pulsa <i>Nueva orden</i>, cambia el tipo a <i>Buy Limit</i> o <i>Sell Limit</i>, y escribe el precio (el CE50%), el SL y, si quieres, el TP.</li>
<li>Para mover el SL a breakeven: mantén pulsada la posición, elige <i>Modificar</i> y pon el SL igual al precio de entrada, o arrastra la línea del SL en el gráfico.</li>
<li>Para cerrar una parte: mantén pulsada la posición, elige <i>Cerrar</i>, cambia el volumen (por ejemplo, de 0,02 a 0,01) y confirma.</li></ol>
<div class="tip">El trader marca en TradingView y ejecuta en MT5. Cuando pases un nivel de una aplicación a otra, <b>comprueba la diferencia de precio</b> entre las dos (normalmente 0,10–0,50 $) y ajusta la orden.</div>
"""

EXTRA["3. Estructura: hacia dónde va el mercado"] = d_break + d_range + """
<h3>Cómo leer la estructura en 3 pasos</h3>
<ol><li><b>D1, las últimas 20 velas:</b> ¿los máximos y los mínimos suben, bajan o están en un rango? Anota "D1 alcista", "D1 bajista" o "D1 rango".</li>
<li><b>H4, las últimas 30 velas:</b> lo mismo. Si H4 coincide con D1, la dirección es clara. Si no, H4 está corrigiendo y conviene esperar.</li>
<li><b>H1:</b> busca el <b>último Break</b>. Si el último Break de H1 fue hacia abajo, el mercado de hoy "quiere" bajar hasta que haya un Break al alza.</li></ol>
<h3>El Break, bien medido</h3>
<ul><li>Solo cuenta el <b>cierre del cuerpo</b>. Una mecha que pasa el nivel y vuelve es un barrido (Ts), no un Break.</li>
<li>Cuanto más alta la temporalidad, más importa: un Break de D1 vale más que diez de M5.</li>
<li>El <b>Weekly break</b> (ruptura del máximo o mínimo de la semana anterior) aparece en sus capturas antes de movimientos largos.</li></ul>
<h3>Cuándo no operar</h3>
<p>En un <b>rango</b>, el precio rebota varias veces entre dos niveles. Cada toque gasta el nivel (deja de estar fresco) y los barridos son poco fiables. Si D1 y H4 están en rango, opera solo los <b>extremos</b> del rango, nunca el medio, o no operes.</p>
<div class="warn"><b>Error típico:</b> comprar porque "ya ha bajado mucho". El trader vendía en una tendencia bajista larga y solo compraba en suelos muy claros, con objetivos cortos.</div>
"""

EXTRA["4. Niveles MSNR: A, V y Gap (Classic A)"] = d_gap + """
<h3>Marcar un nivel A, paso a paso</h3>
<ol><li>En H1, busca un pico donde una vela <b>verde</b> va seguida de una vela <b>roja</b>.</li>
<li>Mira el <b>cierre</b> de la verde y la <b>apertura</b> de la roja. Suelen ser casi el mismo precio.</li>
<li>Traza una línea o una caja estrecha entre esos dos precios. Ese es el nivel A.</li>
<li>Comprueba que el precio <b>no ha vuelto</b> a ese nivel desde entonces. Si es así, está <b>fresco</b>.</li>
<li>Para un V, haz lo mismo en un valle: vela roja seguida de vela verde.</li></ol>
<h3>Por qué con cuerpos y no con mechas</h3>
<p>La mecha es un movimiento rápido que muchas veces barre stops. El <b>cuerpo</b> marca dónde el mercado aceptó el precio al cierre. MSNR parte de la idea de que las zonas de cuerpos se respetan más y de que las mechas son liquidez que se barrerá.</p>
<h3>El gap diario</h3>
<ul><li>El oro cierra a las 17:00 NY y reabre a las 18:00 NY. Si reabre en otro precio, queda un <b>hueco</b> (gap).</li>
<li>El precio suele volver a rellenar ese hueco en los días siguientes. Por eso es un buen <b>Key</b>, y su CE50% (la mitad del gap) es un buen punto de entrada.</li>
<li>En las capturas, la compra del <b>13 de noviembre en 3.880,18</b> estaba dentro de un gap diario (3.875,7–3.885,2). La venta del <b>7 de octubre en 4.137,71</b>, también (4.135,1–4.140,3).</li></ul>
<h3>Cuántos niveles marcar</h3>
<p>Pocos. Si marcas todos los A y V de H1 tendrás decenas y el gráfico no servirá. Quédate con:</p>
<ul><li>Los <b>2 más cercanos</b> por encima y por debajo del precio.</li>
<li>Los que coinciden con un máximo o mínimo del día, de Asia o de la semana.</li>
<li>Los que tienen liquidez (máximos o mínimos iguales) justo antes de llegar.</li></ul>
"""

EXTRA["5. El Key [Buy] / Key [Sell]"] = """
<h3>Ejemplo completo de cómo nace un Key [Sell]</h3>
<ol><li>El precio sube a 4.185,9 en la sesión de Londres y cae. Ese máximo queda como <b>techo 1</b>.</li>
<li>Por la tarde vuelve a subir y se gira otra vez en 4.185,4: es el <b>techo 2</b>, un doble techo.</li>
<li>Justo ahí hay un <b>nivel A de H1</b> (4.184,6–4.185,4). Ya hay dos razones en el mismo precio.</li>
<li>Por encima de los dos techos se acumulan los stops de quienes vendieron allí. Es la <b>liquidez</b> (X).</li>
<li><b>Key • [Sell]</b> = caja de 4.184,6 a 4.186,0. El CE50% queda en ≈4.185,3.</li>
<li>Al día siguiente, a las 08:47 NY y tras el dato de las 8:30, el precio barre hasta 4.187,9 y cae 35 $. Es lo que se ve en la captura del 1 de octubre.</li></ol>
<h3>Cómo puntuar un Key (de 0 a 5)</h3>
<table><tr><th>Criterio</th><th>Punto</th></tr>
<tr><td>A favor de la dirección de D1 y H4</td><td>+1</td></tr>
<tr><td>Es un doble techo o suelo, o un máximo o mínimo de día, Asia o semana</td><td>+1</td></tr>
<tr><td>Coincide con un A, V o Gap fresco de H1 o H4</td><td>+1</td></tr>
<tr><td>Tiene liquidez delante (máximos o mínimos iguales que barrer)</td><td>+1</td></tr>
<tr><td>El precio llegará en una killzone</td><td>+1</td></tr></table>
<p><b>Opera solo los Key de 4 o 5 puntos.</b> Los de 3 puntos, en demo, para aprender. Esta puntuación es mía: el trader no la publica, pero resume lo que se repite en sus mejores capturas.</p>
<h3>Cuándo el Key deja de valer</h3>
<ul><li>Si el precio ya lo <b>tocó</b> y reaccionó una vez: está usado.</li>
<li>Si una vela de M15 o H1 <b>cierra con cuerpo</b> al otro lado (Fts o Break).</li>
<li>Si han pasado más de 3–5 días sin que el precio llegue: el mercado ha cambiado.</li></ul>
"""

EXTRA["6. Liquidez: X, Ts, Fts y Break"] = """
<h3>Dónde está la liquidez</h3>
<ul><li><b>Máximos y mínimos iguales</b> (equal highs y equal lows): son la liquidez más evidente.</li>
<li><b>Máximo y mínimo de Asia</b> (20:00–00:00 NY). Londres y Nueva York suelen barrer uno de los dos.</li>
<li><b>Máximo y mínimo del día anterior</b> (PDH y PDL) y de la semana anterior.</li>
<li><b>Líneas de tendencia</b> muy tocadas: debajo de cada toque hay stops.</li></ul>
<h3>Ts frente a Fts, en la vela de M5 o M15</h3>
<table><tr><th></th><th>Ts (giro probable)</th><th>Fts (no hay giro)</th></tr>
<tr><td>Mecha</td><td>Larga, más allá del nivel</td><td>Puede ser corta</td></tr>
<tr><td>Cierre del cuerpo</td><td><b>Dentro</b>, de vuelta al lado del Key</td><td><b>Fuera</b>, al otro lado del nivel</td></tr>
<tr><td>Vela siguiente</td><td>Va en contra del barrido</td><td>Sigue en la misma dirección</td></tr>
<tr><td>Qué haces</td><td>Mantienes la orden o entras</td><td>Cancelas o sales en el stop</td></tr></table>
<h3>Por qué funciona el barrido</h3>
<p>Para mover mucho dinero, los grandes necesitan contrapartida. Los stops de los demás (compras que se cierran vendiendo, o ventas que se cierran comprando) les dan esa contrapartida justo en el nivel. Por eso el precio "busca" los máximos y mínimos y muchas veces gira justo después. No siempre es así: cuando no gira, es un <b>Fts</b>, y tu stop pequeño limita la pérdida.</p>
<div class="ex"><b>Ejercicio 6b.</b> Durante una semana, apunta cada día si Londres barrió el máximo o el mínimo de Asia, y qué hizo el precio después. Verás cuántas veces el barrido marcó el giro del día.</div>
"""

EXTRA["7. El Quasimodo de H1 (QM)"] = d_qm_buy + """
<h3>Cómo encontrarlo</h3>
<ol><li>En H1, busca un movimiento que haga un <b>nuevo extremo</b> (HH en una venta), barriendo un máximo anterior.</li>
<li>Después, el precio <b>rompe con cuerpo</b> el último mínimo (L). Ese es el cambio de estructura.</li>
<li>El nivel del QM es el <b>máximo anterior al HH</b> (H). El precio suele volver ahí antes de seguir bajando.</li>
<li>Si ese H coincide con un Key o un A/V fresco, pon la orden en él.</li></ol>
<h3>Errores frecuentes con el QM</h3>
<ul><li>Llamar QM a cualquier giro. Si el precio <b>no rompe con cuerpo</b> el L, no hay QM.</li>
<li>Entrar antes de que vuelva al nivel. El QM se opera en el <b>retroceso</b>, no en la ruptura.</li>
<li>Usarlo contra la tendencia de D1 sin nada más que lo apoye.</li></ul>
"""

EXTRA["8. La entrada: orden límite en el Key"] = """
<h3>Ejemplo numérico completo (cuenta de 100 $)</h3>
<ol><li><b>Contexto:</b> D1 y H4 bajistas. Key [Sell] de 4 puntos en 4.126,0–4.128,4 (doble techo y nivel A de H1).</li>
<li><b>CE50%:</b> (4.126,0 + 4.128,4) ÷ 2 = <b>4.127,2</b>. Sell Limit en 4.127,2.</li>
<li><b>Stop:</b> 4.128,4 (extremo) + 0,30 $ (spread) + 0,50 $ (margen) = <b>4.129,2</b>. Riesgo: 2,0 $.</li>
<li><b>Tamaño:</b> 100 $ × 2 % ÷ (2,0 × 100) = <b>0,01 lotes</b>, un riesgo de 2 $.</li>
<li><b>TP1:</b> el mínimo anterior en 4.119,2, es decir, 8 $ = <b>4R</b>.</li>
<li>Si a las 11:00 NY no se ha llenado, la cancelas.</li></ol>
<h3>¿Orden límite o entrada con confirmación?</h3>
<table><tr><th></th><th>Orden límite (lo que hace él)</th><th>Confirmación en M1/M5</th></tr>
<tr><td>Precio de entrada</td><td>El mejor, en la mecha</td><td>Peor, unos dólares después</td></tr>
<tr><td>Stop</td><td>Muy pequeño</td><td>Un poco mayor</td></tr>
<tr><td>Riesgo de entrar en un Fts</td><td>Alto: entras aunque el nivel se rompa</td><td>Bajo: esperas a ver el giro</td></tr>
<tr><td>Operaciones perdidas</td><td>Pocas</td><td>Más: a veces se va sin ti</td></tr>
<tr><td>Recomendado para</td><td>Cuando ya tengas 100 operaciones en demo</td><td><b>Al empezar</b></td></tr></table>
<h3>Confirmación en M1/M5, paso a paso</h3>
<ol><li>El precio entra en la caja del Key.</li>
<li>En M1 o M5, espera a que haga un <b>Ts</b>: mecha fuera y cierre dentro.</li>
<li>Espera un <b>Break</b> en contra: una vela que cierre más allá del último mínimo (para vender) o máximo (para comprar) de M1/M5.</li>
<li>Entra en el <b>retroceso</b>, al CE50% de la vela del Break, con el stop detrás de la mecha del Ts.</li></ol>
"""

EXTRA["9. La gestión de la operación"] = """
<h3>Plan de gestión por escrito (antes de entrar)</h3>
<table><tr><th>Momento</th><th>Acción</th><th>Por qué</th></tr>
<tr><td>Entras</td><td>El stop ya está puesto. No lo tocas en contra</td><td>Limita la pérdida a 1R</td></tr>
<tr><td>+1R a favor</td><td>SL a la entrada (breakeven)</td><td>La operación ya no puede perder</td></tr>
<tr><td>TP1 (siguiente máximo o mínimo)</td><td>Cierras el 50 %</td><td>Aseguras ganancia aunque luego vuelva</td></tr>
<tr><td>Nuevo máximo o mínimo a favor</td><td>Subes o bajas el SL detrás del último swing</td><td>Proteges lo ganado sin cortar la tendencia</td></tr>
<tr><td>TP2 (nivel grande o Key contrario)</td><td>Cierras el resto</td><td>Ahí suele girar el precio</td></tr>
<tr><td>Break en contra en M15</td><td>Cierras el resto</td><td>La estructura cambió</td></tr></table>
<h3>Ojo con el breakeven demasiado pronto</h3>
<p>Si mueves el SL a la entrada con +0,3R, una vuelta normal del precio te sacará "a cero" muchas veces y el mercado seguirá sin ti. Hazlo a <b>+1R</b> o tras el primer Break a favor. En las capturas, el trader lo hace muy rápido, pero con 100 lotes cada dólar son 10.000 $ y su prioridad es no devolver dinero.</p>
<h3>Con 0,01 lotes no puedes cerrar la mitad</h3>
<p>Con el lote mínimo no hay "medio lote". Tienes dos opciones:</p>
<ol><li>Abrir <b>0,02 lotes</b> con un stop la mitad de grande (por ejemplo 1 $ en lugar de 2 $): el riesgo es el mismo y puedes cerrar 0,01 en TP1.</li>
<li>Mantener 0,01 y cerrar todo en TP1, o todo en TP2 con breakeven. Elige una y úsala siempre igual, para que tus estadísticas sean comparables.</li></ol>
"""

EXTRA["10. Las noticias"] = d_news + """
<h3>Los datos que más mueven el oro</h3>
<table><tr><th>Dato</th><th>Cuándo</th><th>Movimiento típico</th></tr>
<tr><td>NFP (empleo de EE. UU.)</td><td>Primer viernes del mes, 8:30 NY</td><td>20–60 $ en minutos</td></tr>
<tr><td>IPC (inflación)</td><td>Hacia mediados de mes, 8:30 NY</td><td>20–70 $</td></tr>
<tr><td>PPI</td><td>Cerca del IPC, 8:30 NY</td><td>10–30 $</td></tr>
<tr><td>FOMC (tipos y discurso)</td><td>8 veces al año, 14:00 y 14:30 NY</td><td>20–80 $, en dos o tres latigazos</td></tr>
<tr><td>Ventas minoristas, peticiones de paro, ISM</td><td>Varias veces al mes</td><td>5–25 $</td></tr></table>
<h3>Cómo lo hace el trader</h3>
<ul><li>Publica el calendario <b>antes</b>, con los datos marcados en rojo.</li>
<li>Deja las <b>órdenes límite puestas</b> en un Key antes del dato. El latigazo barre el nivel y le llena en la mecha. Es lo que pasó el 13 de noviembre en 3.880,18.</li>
<li>Mantiene posiciones grandes durante el dato: es un riesgo alto que solo se ve cuando sale bien.</li></ul>
<h3>Reglas para ti (versión prudente)</h3>
<ol><li>Durante las semanas de práctica, <b>no operes</b> los datos. Solo mira cómo barren los Key que marcaste.</li>
<li>Cuando ya tengas experiencia: solo con una orden límite puesta antes, en un Key de 5 puntos, con el stop ya puesto y la mitad de tu riesgo normal.</li>
<li>Si ya tienes una operación abierta con ganancia, antes del dato <b>mueve el SL a breakeven</b> o cierra una parte.</li></ol>
"""

EXTRA["11. Riesgo y tamaño: lo que más importa"] = """
<h3>Cuánto se pierde en una mala racha</h3>
<table><tr><th>Pérdidas seguidas</th><th>Riesgo 1 %</th><th>Riesgo 2 %</th><th>Riesgo 5 %</th><th>Riesgo 7 %</th><th>Riesgo 10 %</th></tr>
<tr><td>5</td><td>−4,9 %</td><td>−9,6 %</td><td>−22,6 %</td><td>−30,4 %</td><td>−41,0 %</td></tr>
<tr><td>10</td><td>−9,6 %</td><td>−18,3 %</td><td>−40,1 %</td><td>−51,6 %</td><td>−65,1 %</td></tr>
<tr><td>15</td><td>−14,0 %</td><td>−26,1 %</td><td>−53,7 %</td><td>−66,3 %</td><td>−79,4 %</td></tr></table>
<p>Con un método que acierta un 30 % de las veces, <b>10 pérdidas seguidas</b> pasan al menos una vez en pocos cientos de operaciones. Con un 1 % de riesgo, la cuenta pierde menos del 10 % y puedes seguir. Con un 10 %, pierdes casi dos tercios.</p>
<h3>Cuánto hay que ganar para recuperar una pérdida</h3>
<table><tr><th>Si pierdes</th><th>10 %</th><th>25 %</th><th>50 %</th><th>75 %</th></tr>
<tr><td>Necesitas ganar</td><td>+11 %</td><td>+33 %</td><td>+100 %</td><td>+300 %</td></tr></table>
<h3>Cuándo subir el riesgo</h3>
<ol><li>Después de <b>100 operaciones</b> reales con un R medio positivo.</li>
<li>Sube de 0,5 en 0,5 puntos (del 1 % al 1,5 %) y espera otras 50 operaciones.</li>
<li>Nunca más del <b>2–3 %</b> mientras la cuenta sea tu propio dinero. Si quieres arriesgar más, hazlo en una cuenta fondeada (prop firm), donde el riesgo es la cuota.</li></ol>
"""

EXTRA["12. Tu rutina diaria (hora de España)"] = """
<h3>Domingo (30 minutos)</h3>
<ul><li>D1 y W1: dirección de la semana y máximo y mínimo de la semana anterior.</li>
<li>Calendario: apunta los datos de EE. UU. de la semana y su hora en España.</li>
<li>Marca en H4 los 2 Key principales de la semana, por encima y por debajo.</li></ul>
<h3>Antes de cada sesión (10–15 minutos)</h3>
<ol><li>¿Dónde están el máximo y el mínimo de Asia? ¿Y los del día anterior?</li>
<li>¿Qué nivel de la semana está más cerca?</li>
<li>Marca 2–3 Key en M30 y puntúalos de 0 a 5.</li>
<li>Pon las órdenes solo en los de 4–5 puntos y apunta el plan: entrada, SL, TP1 y lotes.</li></ol>
<h3>Durante la sesión</h3>
<ul><li>No cambies el plan con la operación abierta, salvo para mover el SL a favor.</li>
<li>Si saltan 2 stops, <b>se acabó el día</b>. Cancela las demás órdenes.</li></ul>
<h3>Después (10 minutos)</h3>
<ul><li>Captura de cada Key, con o sin operación.</li>
<li>Diario: resultado en R, si seguiste el checklist y una frase sobre lo aprendido.</li></ul>
"""

EXTRA["14. Siete operaciones reales explicadas"] = """
<h3>Qué tienen en común las que salieron mejor</h3>
<ol><li><b>Nivel con dos o tres razones:</b> un A o un gap junto a un máximo o mínimo anterior.</li>
<li><b>Barrido antes del giro:</b> los máximos de 4 h el 1 de octubre, y el mínimo de Asia y el de 4 h el 13 de noviembre.</li>
<li><b>Hora de killzone o de dato:</b> 08:47, 08:30 y 03:33 NY.</li>
<li><b>Recorrido grande frente al stop:</b> 25–48 $ de movimiento con stops de 1–3 $.</li></ol>
<h3>Qué enseña la del 26 de octubre</h3>
<p>Fue una compra de 120 lotes en un V de H1 perfecto. Subió 12 $ y el trader publicó la captura. <b>Después</b> el precio cayó 22 $ por debajo de la entrada. Sin stop, o con el stop ya en breakeven, el resultado final es muy distinto. Las capturas enseñan el mejor momento de cada operación, no el final.</p>
<h3>Ejercicio con estas operaciones</h3>
<div class="ex">En TradingView (XAUUSD, M15), ve a cada una de las fechas. Marca tú el Key <b>antes</b> de mirar qué pasó después, usando la reproducción de barras. Luego compara tu Key con la entrada del trader. ¿Lo habrías visto?</div>
"""

EXTRA["15. Lo que el canal no enseña"] = """
<h3>Cómo leer cualquier canal de señales</h3>
<table><tr><th>Lo que ves</th><th>Lo que significa</th></tr>
<tr><td>Un número enorme junto al botón central del MT5</td><td>Es el beneficio flotante de lo abierto, no el saldo</td></tr>
<tr><td>Capturas con la operación en ganancia</td><td>Son del mejor momento, no del cierre</td></tr>
<tr><td>Un RR dibujado en TradingView</td><td>Puede estar dibujado después del movimiento</td></tr>
<tr><td>Stop en la entrada</td><td>Ya lo movió: el riesgo original no se ve</td></tr>
<tr><td>Capturas de seguidores ganando</td><td>Los que perdieron no las envían</td></tr>
<tr><td>Solo ganadoras</td><td>No se puede calcular el acierto</td></tr></table>
<p>La única prueba seria es un <b>historial completo</b>: el informe del MT5 o un Myfxbook verificado, con todas las operaciones, también las perdedoras.</p>
"""

EXTRA["16. Plan de 12 semanas y diario"] = """
<h3>Qué mirar en la revisión de la semana 12</h3>
<ul><li><b>Por tipo de Key:</b> ¿funcionan mejor los dobles techos, los A/V o los gaps? Opera más los que mejor te salen.</li>
<li><b>Por sesión:</b> ¿Londres o Nueva York? Quédate con la mejor.</li>
<li><b>Por puntuación:</b> los Key de 5 puntos deberían ir mejor que los de 4. Si no es así, revisa cómo puntúas.</li>
<li><b>Errores:</b> cuenta las operaciones que no seguían el checklist. Si son más del 10 %, el problema es la disciplina, no el método.</li></ul>
<h3>Cuándo dejarlo o cambiar</h3>
<p>Si tras <b>100 operaciones</b> el R medio sigue por debajo de 0, el método, tal como lo aplicas, no te da ventaja. Cambia una sola cosa (por ejemplo, entrar solo con confirmación o solo en Key de 5 puntos) y prueba otras 50 en demo.</p>
"""

APPENDIX = [
("Anexo A. Un día completo, de principio a fin", """
<p>Un ejemplo inventado pero realista, con precios redondos, para ver todo el proceso junto.</p>
<h3>07:30 (España): preparación</h3>
<ul><li>D1 bajista y H4 bajista: hoy buscamos <b>ventas</b>.</li>
<li>Máximo de ayer: 4.132. Asia: máximo 4.124 y mínimo 4.110. Precio actual: 4.116.</li>
<li>Key [Sell] A: 4.123–4.125, con el máximo de Asia y un nivel A de H1. Liquidez delante: dos máximos iguales en 4.121. <b>5 puntos.</b></li>
<li>Key [Sell] B: 4.131–4.133, el máximo de ayer. 4 puntos.</li>
<li>Datos: peticiones de paro a las 14:30. Anotado.</li></ul>
<h3>Plan escrito</h3>
<ul><li>Sell Limit en el CE50% de A: <b>4.124,0</b>. SL 4.125,8 (riesgo 1,8 $). TP1 4.110 (el mínimo de Asia), 14 $ = 7,8R. Lotes 0,01, riesgo 1,8 $ (1,8 % de 100 $).</li>
<li>Si A se rompe con un cierre de M15 por encima de 4.126, cancelo y paso a B.</li></ul>
<h3>09:20: llega el precio</h3>
<ul><li>El precio barre los dos máximos de 4.121 y llega a 4.124,6: se llena la Sell Limit.</li>
<li>La vela de M15 cierra en 4.122: es un <b>Ts</b>. Bien.</li></ul>
<h3>09:50: +1R</h3>
<p>El precio baja a 4.122,2 (+1R). Muevo el SL a 4.124,0 (breakeven). Ya no puedo perder.</p>
<h3>11:15: TP1</h3>
<p>El precio llega a 4.110. Con 0,01 lotes no puedo cerrar la mitad, así que cierro todo: <b>+14 $ (+7,8R, +14 % de la cuenta)</b>. Cancelo la orden de B.</p>
<h3>17:00: diario</h3>
<p>Apunto: Key A de 5 puntos, Londres, Ts claro, +7,8R, checklist cumplido. Nota: "el barrido de los máximos iguales fue la señal". Captura antes y después.</p>
<div class="warn">Este día sale perfecto para explicar el proceso. En la realidad, muchas órdenes no se llenan o saltan en el stop. Con un 30 % de acierto, de cada 10 días como este, unos 7 terminan en −1R o en 0.</div>
"""),
("Anexo B. Preguntas frecuentes", """
<p><b>¿Puedo hacerlo solo desde el móvil?</b><br>Sí, el trader opera con el MT5 del móvil. Pero marcar niveles es mucho más cómodo en el ordenador.</p>
<p><b>¿Cuánto tiempo hasta ser rentable?</b><br>No hay una fecha. Con este plan, en 12 semanas sabrás si tus números son positivos en demo. Muchos traders necesitan entre 6 meses y 2 años.</p>
<p><b>¿Y si mi bróker tiene otro precio que TradingView?</b><br>Marca los Key en el gráfico de tu bróker, o calcula la diferencia y súmala o réstala a cada nivel.</p>
<p><b>¿Puedo operar otros activos?</b><br>Los mismos conceptos sirven para índices y divisas, pero los tamaños de stop cambian. Empieza solo con el oro.</p>
<p><b>¿Por qué no copiar directamente sus señales?</b><br>Porque no se sabe su acierto real, entra con stops que tu bróker y tu spread pueden no respetar, y publica muchas operaciones cuando ya van ganando.</p>
<p><b>¿Qué hago si pierdo 3 o 4 operaciones seguidas?</b><br>Es normal. Revisa en el diario si seguiste el checklist. Si lo seguiste, sigue con el mismo riesgo. Si no, para un día y repasa los capítulos 5, 6 y 8.</p>
<p><b>¿Debo usar cobertura (comprar y vender a la vez)?</b><br>No mientras aprendes. Oculta las pérdidas y complica la gestión.</p>
<p><b>¿Vale la pena una cuenta fondeada (prop firm)?</b><br>Cuando tengas más de 100 operaciones en demo con R medio positivo, sí. Así arriesgas solo la cuota del examen. Lee bien sus reglas de pérdida diaria: con stops de 1–3 $ suelen ser fáciles de cumplir.</p>
"""),
]
