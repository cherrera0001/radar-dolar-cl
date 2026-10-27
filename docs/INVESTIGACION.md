# Investigación

Registro de hipótesis evaluadas con el marco walk-forward (`radar investigar`, issue #9).
Regla: los parámetros se eligen **solo** con el período de diseño (< 2020-01); cada
estrategia se mide **una vez** en el período de prueba (≥ 2020-01). Solo pasa a
producción lo que gana en prueba. El detalle generado está en `reports/investigacion.md`.

## H1 · Acumular la cuota cuando el dólar está caro frente a su valor justo (#10)

**Hipótesis.** Si el dólar está sobre su valor justo (modelo cobre + DXY), guardar la cuota en
pesos (hasta N meses) y convertir la caja cuando vuelve a su valor justo consigue más dólares
que DCA.

**Diseño.** Grilla N ∈ {2, 3, 6}, entrada ∈ {2%, 5%, 8%}, salida ∈ {0%, 2%} (salida < entrada).
Tope de riesgo: nunca más de N meses sin comprar. Al cierre del período la caja se convierte
entera, para que todas las estrategias gasten lo mismo.

**Resultado (2026-10-23, datos 2012-11 a 2026-09):**

| Período | DCA | Radar v0.1 | Acumulación elegida (N=2, entra >2%, sale ≤0%) |
|---|---|---|---|
| Diseño 2012-11 a 2019-12 (86 meses) | $613,27 | −0,096% | **+0,276%** |
| Prueba 2020-01 a 2026-09 (81 meses) | $856,65 | −0,068% | **−0,207%** |

**Re-ejecución con fechas de mercado alineadas (#19, 2026-10-23).** El histórico mostró que
`usdclp` estaba fechado 1 día hábil después del mercado y `cobre_lb` 2 días. Con el desfase de
la decisión de 1 día, la señal de cobre de la fila *t−1* usaba un dato que el mercado conoce
recién en *t+1*. Corregido el 2026-10-27 (R-06): la decisión del día *d* usa la señal de *d−2*
(`DESFASE_DECISION`). Resultado con ese desfase:

| Período | Radar v0.1 | Acumulación elegida (misma combinación) |
|---|---|---|
| Diseño 2012-11 a 2019-12 | −0,117% | +0,171% |
| Prueba 2020-01 a 2026-09 | −0,124% | **−0,083%** |

(La versión anterior, con desfase de 1 día, daba −0,129% y −0,041% en la prueba.)

La conclusión no cambia: ninguna regla le gana a DCA fuera de muestra.

**Conclusión: rechazada.** La mejor combinación del diseño pierde en la prueba: es
sobreajuste. El valor justo cobre + DXY describe bien cuándo el dólar está caro, pero esa
"caridad" no se corrige en uno o dos meses de forma aprovechable: entre 2020 y 2026 el dólar
pasó largos períodos caro respecto del modelo y siguió subiendo (pandemia, estallido, ciclo de
tasas), así que esperar costó dólares.

**Qué queda abierto.** Señales de flujo, en vez de precio (exportaciones de cobre y flujos
cambiarios del Banco Central, issue #8), evaluadas con este mismo marco.

## Lectura general para un ahorrista de largo plazo

Con las señales disponibles hoy, ninguna regla de *timing* evaluada le gana a DCA fuera de
muestra, y las diferencias (±0,3%) son pequeñas frente al costo de equivocarse esperando. La
recomendación operativa del radar es **comprar la cuota completa cada mes (DCA)**, y usar el
semáforo como contexto (cuán caro o barato está el dólar), no como orden de compra.
