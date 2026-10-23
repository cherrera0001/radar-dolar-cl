# Concilio 2026-10-23 · ¿Cómo emite el Radar Dólar una recomendación COMPRAR / VENDER / MANTENER?

Protocolo: v1 de sg-engagement-2026 (`councils/README.md` de ese repo): Stage 0 verificación ·
Stage 1 consejeros en paralelo · Stage 2 revisión cruzada anónima · Stage 3 síntesis del
presidente · Stage 5 disidencias con condición de reactivación · Stage 6 trampa de fragilidad.
Issue: #15.

## Pregunta

El dueño quiere que el mensaje final sea una **recomendación simple: COMPRAR, VENDER o MANTENER
dólares**, respaldada por datos, estadística y operación real. Usuario objetivo: una persona en
Chile que ahorra en USD todos los meses (p. ej. US$200–2.000/mes), horizonte de años, y que puede
tener una necesidad de pesos en algún momento.

**¿Qué regla de decisión, horizonte, datos y gestión de riesgo permiten emitir esa recomendación
con evidencia fuera de muestra y neta de costos? ¿O la evidencia obliga a redefinir qué significa
"COMPRAR / VENDER / MANTENER" para este usuario?**

## Stage 0 · Supuestos críticos verificados con datos (no se discuten, se usan)

| Supuesto | Verificación | Resultado |
|---|---|---|
| Las señales de precio/fundamentales (valor justo cobre+DXY, percentil anual, tendencias de cobre y DXY, diferencial TPM–Fed, VIX) no le ganan a comprar fijo cada mes | Backtest 2012–2026 y walk-forward diseño ≤2019 / prueba ≥2020, fechas de mercado alineadas, decisión con señal de d−1 | v0.1 −0,13% y acumulación −0,04% fuera de muestra (`docs/INVESTIGACION.md`) |
| El cobre o el DXY no anticipan al CLP más allá de 1 día | Correlaciones cruzadas y Granger por submuestra con series alineadas | Sin adelanto robusto (`docs/HISTORICO.md` §2) |
| El techo del timing dentro del mes es pequeño | Cota con oráculo | 1,8–2,5% (solo un oráculo); día 1 ≡ promedio del mes (`docs/HISTORICO.md` §3) |
| El costo del canal de compra es grande respecto del timing | Precios publicados el 23-oct-2026 | Pizarra banco ~2,5% vs Fintual ~0,46% vs Buda ~0,2–0,74%; ida y vuelta 0,9%–5% (`docs/estado-del-arte/03-costos-canales.md`) |
| Existen datos diarios de flujos | Códigos BDE verificados en archivos oficiales SIID | NDF neto de no residentes y derivados USD/CLP por sector (fondos de pensiones, empresas…), diarios (`docs/estado-del-arte/02-chile-bcch.md` §4) |
| Los flujos mueven el CLP | Literatura | Sí, contemporáneamente (Evans-Lyons 2002; Aldunate et al. JFE 2025). Poder predictivo con rezago de publicación: **no demostrado** |

## Material obligatorio

- `docs/ESTADO_DEL_ARTE.md` (síntesis) y `docs/estado-del-arte/*.md` (informes completos)
- `docs/HISTORICO.md` (análisis empírico 2012–2026)
- `docs/INVESTIGACION.md` y `docs/METODOLOGIA.md` (marco walk-forward, resultados)

## Qué debe entregar cada consejero

1. **Posición** en una frase y **confianza** (0–100%).
2. **Propuesta concreta**: qué significa COMPRAR / VENDER / MANTENER para este usuario; la regla
   de decisión especificada para poder testearla con el marco walk-forward (datos, umbrales,
   horizonte, frecuencia, tamaño, costos supuestos).
3. **Evidencia** que la respalda (citando el material) y **la que la contradice**.
4. **Riesgos** y cómo puede dañar al usuario.
5. **Qué dato o resultado te haría cambiar de opinión** (condición observable).
6. **Datos y desarrollo que exige** (fuentes, frecuencia, issues).
