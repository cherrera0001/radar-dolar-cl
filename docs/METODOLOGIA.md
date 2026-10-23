# Metodología

## Principios

1. **Causalidad.** Cada valor de una señal en la fecha *t* usa solo datos hasta *t*. El modelo de
   valor justo se ajusta con `[t-504, t-1]` y predice *t* (fuera de muestra). Hay un test que altera
   el futuro y verifica que el pasado no cambie.
2. **Sin sobreajuste.** Los pesos y umbrales son hipótesis a priori. No se eligen mirando el
   backtest, porque se evaluarían sobre la misma historia que los produjo.
3. **El backtest manda.** Si una señal no le gana a DCA, se reporta así en cada resumen.
4. **Datos honestos.** Una fuente que responde algo fuera de contrato o fuera de rango falla
   ruidosamente; las series se alinean con una antigüedad máxima (7 días; 14 para el DXY semanal).

## Señales (puntaje en [-1, 1]; + = dólar barato, − = dólar caro)

| Señal | Peso | Cálculo | Lógica |
|---|---|---|---|
| Valor justo | 0,30 | Regresión móvil de 2 años `log(USDCLP) ~ log(cobre) + log(DXY)`; puntaje `= −z/2` del residuo | Dólar bajo lo que explican sus fundamentos → comprar |
| Posición en el año | 0,25 | `1 − 2·percentil` del dólar en 252 días | Cerca del mínimo anual → comprar |
| Cobre (3 meses) | 0,15 | `−cambio_63d / 15%` | Cobre al alza trae dólares al país → esperar |
| Dólar global (3 meses) | 0,10 | `cambio_63d(DXY) / 5%` | Dólar fortaleciéndose afuera arrastra al CLP → comprar antes |
| Diferencial de tasas | 0,10 | `−Δ126d(TPM − Fed) / 1,5 pts` | Diferencial que se estrecha debilita al peso → comprar |
| Aversión al riesgo | 0,10 | `−z(VIX, 252d) / 2` | En pánicos el dólar se dispara y suele devolverse → esperar |

**Compuesto:** promedio ponderado de las señales disponibles (con al menos 3). BARATO si ≥ 0,25,
CARO si ≤ −0,25, NORMAL entre ambos. "Acuerdo" = cuántas señales tienen el mismo signo. Los estados
son descriptivos: la recomendación es DCA mientras ninguna regla gane fuera de muestra (#12).

## Backtest (v0.1)

Ambas estrategias gastan el mismo presupuesto mensual. DCA compra todo el primer día hábil; el radar
compra 50% ese día y 50% al primer BARATO del mes (o el último día hábil). Se excluyen el mes en curso
y los meses sin señal desde su primer día (calentamiento de las ventanas).

Resultado 2012-11 a 2026-09 (167 meses):

| Señal (sola) | vs DCA |
|---|---|
| Compuesto | −0,085% |
| Valor justo | −0,162% |
| Posición en el año | −0,165% |
| Cobre | −0,201% |
| Dólar global | −0,091% |
| Diferencial de tasas | −0,068% |
| VIX | +0,011% |

**Lectura:** dentro de un mes el dólar se mueve poco frente al ruido diario, así que reubicar
media cuota no captura valor y las señales de tendencia llegan tarde. El radar es útil como
*descripción* (caro/barato frente a fundamentos), aún no como regla que mejore el precio promedio.

## Hoja de ruta

1. **Fase 2 — Banco Central (API BDE):** exportaciones de cobre (volumen y valor), flujos
   cambiarios y series oficiales; contraste del dólar observado mindicador vs BCCh.
2. **Investigación con validación walk-forward** (#9, hecho): `radar investigar`. Primera
   hipótesis, acumular pesos cuando el dólar está caro (#10), **rechazada** fuera de muestra;
   ver [INVESTIGACION.md](INVESTIGACION.md).
3. **Comandos en Telegram** (`/dolar`, `/senales`): webhook en un Cloudflare Worker gratuito que
   dispara `repository_dispatch`, sin servidor propio.
