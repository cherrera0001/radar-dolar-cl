# Estado del arte: predecir y comprar USD/CLP siendo ahorrista en Chile

Síntesis de cuatro investigaciones paralelas (2026-10-23, issue #13 y #14). Los informes
completos, con cada referencia y su URL, están en `docs/estado-del-arte/` y `docs/HISTORICO.md`.
Regla de lectura: **[F]** = hallazgo de la fuente; **[I]** = interpretación nuestra.

## 1. Las cinco conclusiones que ordenan el producto

1. **El momento de compra casi no importa; el canal sí.**
   - [F] A 1–12 meses ningún modelo de fundamentales le gana de forma estable al paseo aleatorio (Meese-Rogoff 1983; Rossi 2013; Engel-West 2005).
   - [F] En nuestro histórico, comprar el día 1 o al promedio del mes da lo mismo (diferencia ≈0, t<0,5), y el techo teórico del timing intra-mes (oráculo) es 1,8–2,5%.
   - [F] Hoy, comprar en la pizarra de BancoEstado cuesta ~2,5% sobre el precio medio y en Fintual ~0,46%: **~US$120/año** de diferencia con US$500/mes, 7–20 veces lo que movía cualquier regla de timing.
2. **El cobre no anticipa al peso; el peso anticipa al cobre.**
   - [F] Chen-Rogoff-Rossi 2010; Pincheira-Hardy 2019 (con el CLP).
   - [F] En el histórico no hay adelanto explotable más allá de 1 día, y ese día se explica por horarios de fijación distintos.
   - [I] Las señales de tendencia del cobre/DXY de la v0.1 iban contra la dirección causal útil.
3. **Los flujos sí mueven el peso y hay datos diarios.**
   - [F] Flujo de órdenes explica >60% de la variación diaria (Evans-Lyons 2002); los cambios de fondo de las AFP mueven el CLP (Aldunate-Da-Larrain-Sialm, JFE 2025); el carry de no residentes en forwards se asocia a turbulencia (BCCh DT 733).
   - [F] El BCCh publica **a diario** la posición NDF neta de no residentes y los derivados USD/CLP por sector (fondos de pensiones, empresas, seguros), con códigos verificados.
   - [I] Es la hipótesis original del dueño ("quién vende o compra dólares") y la única familia de señales con respaldo teórico y datos de alta frecuencia. **No hay evidencia publicada de que sean predictivas con el rezago de publicación**: hay que testearlo.
4. **Esperar para ganar la tasa en pesos no es gratis.**
   - [F] En emergentes la paridad descubierta se cumple aproximadamente (Bansal-Dahlquist 2000; meta-análisis Zigraiova et al. 2021, pendiente 0,95–1,16).
   - [I] El diferencial TPM–Fed se compensa en promedio con depreciación: es neutro como señal de timing. Lo que sí rinde es poner los USD a trabajar apenas se compran (depósito/money market en USD).
5. **Los extremos existen pero son pocos y no robustos.**
   - [F] La reversión a la media de 1 año aparece solo en 2020–2026 y descansa en 4–14 casos por grupo. El "valor justo" cobre+DXY tiene betas inestables y no predice en ninguna submuestra.
   - [F] Las intervenciones del BCCh (nov-2019, jul-2022) coincidieron con máximos locales (N=2); la evidencia del BCCh dice que **los anuncios** tienen efecto, no las operaciones diarias.

## 2. Qué implica para "COMPRAR / VENDER / MANTENER"

| Pregunta | Respuesta según la evidencia |
|---|---|
| ¿Puede el radar decir "compra hoy, no mañana" con ventaja? | No con señales de precio/fundamentales (literatura + backtest + histórico). |
| ¿Puede decir "compra este mes una cuota mayor/menor"? | Hipótesis abierta: momentum de serie de tiempo para modular el monto (0,75x–1,25x), flujos de no residentes/AFP, desvíos extremos con horizonte de años. Debe ganar fuera de muestra **neto de costos**. |
| ¿"VENDER" tiene sentido? | Solo para quien tiene USD y una necesidad en pesos; el costo ida y vuelta (0,9%–5%) exige una señal mucho más fuerte que la de compra. Hoy no existe. |
| ¿Dónde está la ganancia segura? | Canal de compra (spread), costo de mantención y rendimiento de los USD comprados. |

## 3. Hipótesis priorizadas para testear (marco walk-forward, #9)

| # | Hipótesis | Datos | Por qué | Riesgo |
|---|---|---|---|---|
| H2 | Posición NDF de no residentes (nivel/cambio) anticipa el USDCLP a 1–4 semanas | BCCh diario `F099.DER.STO.Z.40.N.NR.NET.NDF.MMUSD.CLPUSD.C.Z.0.D` | Carry/posicionamiento (DT 733), flujos (Evans-Lyons) | Revisiones de la serie: usar fecha de publicación |
| H3 | Derivados netos bancos–fondos de pensiones anticipan el USDCLP | BCCh diario `F099.DER.STO.Z.40.R.42.NET.Z.MMUSD.CLPUSD.Z.Z.0.D` | AFP mueven el CLP (JFE 2025) | Efecto quizá solo contemporáneo |
| H4 | Momentum de serie de tiempo 1–12m (con carry) modula el monto mensual | usdclp, tpm, fed_funds | Moskowitz-Ooi-Pedersen 2012 | Señal débil en un solo par |
| H5 | Depreciación anormal grande (no explicada por cobre/DXY) revierte en 20 sesiones | histórico | Eventos 2019 y 2022 | N muy pequeño |
| H6 | Expectativas de encuestas BCCh (EOF/EEE) vs paseo aleatorio | BCCh | Indicio no verificado | Fuente por confirmar |

Hipótesis **descartadas** por la literatura o el histórico: cobre/DXY/tasas como predictores a 1–12 meses; diferencial de tasas como timing en emergentes; trasladar carry/value/momentum cruzados a un par; VIX como señal anticipada; "suma única gana 2/3" aplicado a USD/CLP.

## 4. Requisitos de datos que surgieron (bloquean resultados confiables)

- **#19 Alinear fechas de mercado**: `usdclp` con fecha t es mercado de t−1; `cobre_lb` es t−2. Sin alinear aparecen adelantos falsos (p≈1e−25).
- **#20 Calidad**: el cobre no tiene dic-2017 ni 46 días hábiles más; el DXY es diario con ~1 semana de rezago.
- **Costos en el backtest**: modelar 0,5–0,75% por compra (canal barato) en vez de 0%.
- **Conciliar el dólar observado**: el 23-oct mindicador marca $986,58 y dolaronline $984,96 (#7).

## 5. Fuentes de datos

| Fuente | Qué | Frecuencia | Acceso |
|---|---|---|---|
| BCCh API BDE | Dólar observado, TPM, TCM, IMACEC, **derivados por sector, NDF no residentes**, exportaciones | Diaria / mensual | Registro gratuito (#5) |
| mindicador.cl | Dólar observado, cobre, TPM | Diaria | Abierta (tercero) |
| FRED | DXY amplio (diario, rezago ~1 semana), Fed funds, VIX | Diaria | Abierta |
| Buda API | USDC/USDT-CLP en tiempo real (bid/ask), comisiones | Tiempo real | Pública, 120 req/min |
| dolaronline.cl | Precios BancoEstado, Fintual, AFEX, Buda | ~10 min | HTML; 1–2 lecturas/día |
| Calendario BCCh | RPM 2026: 26-27 oct, 15 dic; IPoM 16 dic | — | Sitio BCCh |

## 6. Informes completos

- [Literatura académica](estado-del-arte/01-literatura-academica.md) — 23 referencias con URL y verificación
- [Chile: determinantes, flujos, intervenciones, series BCCh](estado-del-arte/02-chile-bcch.md)
- [Costos reales de comprar y mantener USD en Chile](estado-del-arte/03-costos-canales.md)
- [Análisis empírico del histórico 2012–2026](HISTORICO.md) — scripts en `research/historico/`
