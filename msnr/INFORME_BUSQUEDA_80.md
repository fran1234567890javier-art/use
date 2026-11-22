# Búsqueda de una estrategia MSNR/SNT a 1:5 con un 80 % de acierto (XAUUSD 2026)

> Material educativo. No es asesoramiento financiero.

## Método
- **Base:** 114 setups del modelo SNT/MSNR (Key level Classic A/V de H1/H4, barrido, MSS, entrada en el 0,764, solo killzones), con entradas en M1, M5 y M15.
- **Salida:** objetivo de 5R y stop de 1R. También se probó una variante que mueve el stop a la entrada (BE) al llegar a +2R.
- **Filtros combinados:** temporalidad, lado, tipo de nivel, killzone, día de la semana y tamaño del stop. Salen 350 combinaciones con al menos 5 operaciones.
- **Validación:** la búsqueda solo usa **enero a mediados de junio**. La mejor combinación se comprueba después en **junio a noviembre**, datos que la búsqueda no ha visto.

## Resultado
| | Aprendizaje (ene–jun) | Prueba (jun–nov) |
|---|---|---|
| Sin filtros, a 5R | 16,4 % de acierto, −0,02R | 8,5 % de acierto, −0,49R |
| **Mejor combinación encontrada** (cortos en nivel A-H1, solo viernes, stop medio) | **60 % (3 de 5)**, +2,6R | **0 % (0 de 2)**, −1R |
| Combinaciones con un 80 % o más | **0 de 350** | — |

- Ninguna combinación llega al 80 % ni siquiera en los datos usados para buscarla.
- Lo mejor que aparece es un 60 % con solo 5 operaciones, que es casualidad: fuera de muestra cae al 0 %.
- Esto es sobreajuste. Si se prueban suficientes filtros sobre pocas operaciones, siempre sale alguno bonito en el pasado que luego no funciona.

## Conclusión
No existe en estos datos una estrategia MSNR a 1:5 con un 80 % de acierto, ni siquiera haciendo trampa con los filtros. Lo realista a 1:5 es un acierto del 15–25 %.
