# YANSTD (bot SMC + MSNR para MetaTrader 5): instalación paso a paso

Original: https://github.com/yanstd888/institutional-smc-scalper-mt5 (licencia MIT, se incluye `LICENSE`).
Es un **Expert Advisor de MetaTrader 5**: no funciona en TradingView ni en MT4.

## 1. Copiar los archivos
1. Abre MetaTrader 5 en el ordenador (Windows).
2. Menú **Archivo → Abrir carpeta de datos**.
3. Entra en `MQL5\Experts\` y copia ahí la carpeta **YANSTD** entera.
   Debe quedar así: `MQL5\Experts\YANSTD\YANSTD.mq5`, con las carpetas `Modules`, `GUI` y `Presets` al lado.

## 2. Compilar
1. Pulsa **F4** para abrir MetaEditor.
2. Abre `Experts\YANSTD\YANSTD.mq5` y pulsa **F7 (Compilar)**.
3. Abajo debe aparecer `0 errors`. Se crea `YANSTD.ex5`.

## 3. Probarlo primero en el Probador de estrategias (Ctrl + R)
- **Experto:** YANSTD. **Símbolo:** XAUUSD (el de tu bróker). **Periodo:** **M3**.
- **Modelado:** "Cada tick basado en ticks reales". **Depósito:** el que uses.
- En **Parámetros → Cargar**, elige `Presets\L5_SCALPING_M2.set` o `Presets\G27B_CHAMPION_XAUUSD.set`.

## 4. Ponerlo en una cuenta DEMO
1. Abre un gráfico de **XAUUSD en M3**.
2. Arrastra **YANSTD** desde el Navegador al gráfico.
3. En la pestaña **Común**, marca *Permitir trading algorítmico*.
4. En **Parámetros → Cargar**, elige el preset.
5. Activa el botón **Algo Trading** de la barra superior.
6. Déjalo funcionando al menos **100 operaciones** (2–3 meses) antes de decidir nada.

## Importante
- **Riesgo:** los presets usan **0,10 lotes fijos** (`InpFixedLot`), pensados para una cuenta de 10.000 $. Para cuentas pequeñas, baja `InpFixedLot` a 0,01 o cambia a riesgo en %.
- **Bróker:** necesita spread bajo en el oro (ECN o Raw) y, mejor, un VPS para que el ordenador esté siempre encendido.
- **Seguridad:** no hace llamadas a internet ni usa DLL. El filtro de noticias usa el calendario interno de MT5.
- **Resultados:** los del README son del propio autor y no están verificados por terceros.

Material educativo. No es asesoramiento financiero.
