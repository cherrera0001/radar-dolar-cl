# Análisis empírico del histórico 2012–2026

> Issue #14, 2026-10-23. Datos: `data/series/` (sin modificar). Scripts reproducibles en
> `research/historico/` (`main.py`, `q6.py`, `q6b.py`); se ejecutan con el venv del repo:
> `.venv/bin/python research/historico/main.py`. Retornos logarítmicos; siempre se separa
> 2012–2019 (diseño) de 2020–2026 (prueba). No se afirma causalidad.

## 0. Hallazgo previo: las fechas no son del mismo día de mercado (→ issue #19)

| Serie | La fecha t del CSV corresponde al mercado de | Evidencia |
|---|---|---|
| usdclp | **t−1** | corr(u_t, DXY_{t−1}) = 0,53 vs 0,03 en t |
| cobre_lb | **t−2** | corr(cobre_t, DXY_{t−2}) = −0,33; corr(u_t, cobre_{t+1}) = −0,34 |
| dxy, vix | t | — |

Para las preguntas 1, 2 y 5 se reubicó usdclp en t−1 y cobre en t−2 (días hábiles). Tras alinear,
la correlación contemporánea queda en k=0 (cobre −0,37; DXY +0,50), N = 3.147 días comunes
(oct-2012 a oct-2026). **Sin alinear aparece un Granger falso** "el dólar adelanta al cobre"
(p ≈ 1e−25 y 1e−40) y R² de 0,28–0,30 para "el DXY adelanta al dólar": es solo desfase de fechas.

## 1. Relación USDCLP–cobre

| Frecuencia | Muestra | N | corr(u, cobre) [IC95] | corr(u, DXY) | β cobre | β cobre \| DXY | β DXY \| cobre | R² |
|---|---|---|---|---|---|---|---|---|
| 1 día | 2012-19 | 1592 | −0,36 [−0,40; −0,32] | 0,51 | −0,17 | −0,11 | 0,88 | 0,31 |
| 1 día | 2020-26 | 1555 | −0,38 [−0,42; −0,33] | 0,51 | −0,23 | −0,11 | 1,07 | 0,28 |
| 1 semana | 2012-19 | 373 | −0,42 [−0,50; −0,34] | 0,53 | −0,22 | −0,15 | 0,90 | 0,36 |
| 1 semana | 2020-26 | 355 | −0,47 [−0,55; −0,39] | 0,57 | −0,31 | −0,17 | 1,12 | 0,37 |
| 1 mes | 2012-19 | 86 | −0,49 [−0,63; −0,31] | 0,61 | −0,31 | −0,20 | 1,06 | 0,46 |
| 1 mes | 2020-26 | 82 | −0,57 [−0,70; −0,40] | 0,69 | −0,39 | −0,17 | 1,30 | 0,52 |

Correlación/beta móviles de 252 días: 2012-19 corr −0,55/−0,37/−0,15 (mín/mediana/máx), β −0,25/−0,17/−0,10 (p10/mediana/p90); 2020-26 corr −0,61/−0,39/−0,19, β −0,32/−0,25/−0,12.

Beta semanal por régimen (error robusto HC): A oct-2012–sep-2019 −0,22 (0,03); B oct-2019–2021 −0,18 (0,06); C 2022–2026 −0,40 (0,04). C−A = −0,18 (z = −3,65); B−A sin diferencia (z = 0,5). Por año, la correlación diaria toca mínimos en 2017 (−0,19) y 2021 (−0,22) y máximos en 2018 (−0,51) y 2024 (−0,52).

**Lectura:** el signo es estable (negativo en todas las ventanas de un año desde 2013); la magnitud cambia por régimen. Lo estable es la beta del cobre **controlando por DXY** (≈−0,11 diaria, −0,15 a −0,17 semanal); el aumento de la beta simple viene de la beta al DXY (0,9 → 1,1–1,3) y de la covarianza cobre–DXY. La correlación crece con el horizonte.

## 2. ¿El cobre o el DXY adelantan al USDCLP?

Correlaciones cruzadas corr(u_t, z_{t−k}), k = 1–20; banda 95% ±0,05.

| Muestra | Cobre k=1 | Cobre máx \|k=6..20\| | DXY k=1 | DXY máx \|k=6..20\| | Rezagos significativos |
|---|---|---|---|---|---|
| 2012-19 | −0,11 | 0,07 | +0,16 | 0,04 | cobre k=1 y k=15; DXY k=1 |
| 2020-26 | −0,14 | 0,04 | +0,10 | 0,05 | cobre k=1; DXY k=1 |

Granger (u_t sobre 5 o 10 rezagos propios y de z; Wald robusto HC0):

| Muestra | u ← cobre (p=5) | u ← cobre (p=10) | u ← DXY (p=5) | u ← DXY (p=10) | ΔR² (p=5) |
|---|---|---|---|---|---|
| 2012-19 | 0,27 | 0,70 | **0,004** | **0,009** | cobre +0,005; DXY +0,011 |
| 2020-26 | **0,025** | 0,10 | 0,79 | 0,98 | cobre +0,009; DXY +0,002 |

**Lectura:** el único efecto que se repite es un arrastre de 1 día (|ρ| 0,10–0,16), compatible con horas de fijación distintas (observado = promedio del día en Chile; DXY al mediodía de Nueva York; cobre LME). El Granger no es robusto (DXY significativo solo en 2012-19, cobre solo en 2020-26; p anual del cobre entre 0,00 y 0,64) y el ΔR² no supera el 1%. Como el radar recibe el cobre con 1–2 días de desfase, ese arrastre probablemente no es aprovechable.

## 3. Timing dentro del mes (meses con ≥15 observaciones; %)

| Métrica | 2012-19 media / mediana / p90 | 2020-26 media / mediana / p90 |
|---|---|---|
| Rango del mes (máx/mín − 1) | 3,64 / 3,42 / 5,41 | 5,18 / 4,97 / 7,18 |
| Primer día vs promedio del mes | −0,04 / +0,15 / 1,72 (t = −0,22) | −0,09 / −0,08 / 2,51 (t = −0,40) |
| Promedio del mes vs mínimo (cota oráculo) | 1,79 / 1,68 / 2,79 | 2,52 / 2,47 / 3,91 |
| Primer día vs mínimo | 1,75 / 1,49 / 3,93 | 2,42 / 2,15 / 5,38 |
| Error absoluto medio, día 1 vs promedio | 1,37 | 1,67 |
| Meses | 96 | 82 |

Comprar el día 1 o al promedio es equivalente en esperanza (≈−0,05%, no significativo; el día 1 queda bajo el promedio el 47%/51% de los meses). **Techo teórico del timing intra-mes: ~1,8% (2012-19) a ~2,5% (2020-26)**, solo alcanzable por un oráculo. El mínimo cae más seguido en los extremos del mes (primera semana 33%/39%, última 26%/29%), lo esperable en un paseo aleatorio (ley del arcoseno), no un patrón de calendario.

## 4. Reversión a la media (señales causales, fin de mes)

Señales: desvío respecto de la media de 252 días (log); residuo z de una regresión móvil de 504 días de log USDCLP sobre log cobre y log DXY con solo datos pasados (existe desde sep-2014). Retornos futuros a 1, 3, 6 y 12 meses; pendiente con errores Newey-West. Ventanas solapadas: en 2020-26 hay ~6 años independientes.

**Desvío de la media de 252 días, umbral ±5%:**

| Muestra | h | N | Ret. promedio | > +5%: N / ret | < −5%: N / ret | Pendiente (t NW) | R² |
|---|---|---|---|---|---|---|---|
| 2012-19 | 1m | 85 | +0,58 | 35 / +0,37 | 4 / +0,27 | −0,09 (−1,3) | 0,02 |
| 2012-19 | 3m | 85 | +2,04 | 35 / +1,82 | 4 / +2,25 | −0,01 (−0,1) | 0,00 |
| 2012-19 | 6m | 85 | +3,89 | 35 / +4,44 | 4 / +4,86 | +0,04 (0,2) | 0,00 |
| 2012-19 | 12m | 85 | +6,75 | 35 / +7,02 | 4 / +9,57 | +0,07 (0,2) | 0,00 |
| 2020-26 | 1m | 80 | +0,21 | 26 / −0,61 | 12 / +1,56 | −0,10 (−2,0) | 0,03 |
| 2020-26 | 3m | 78 | +0,44 | 26 / −1,67 | 12 / +3,14 | −0,28 (−2,5) | 0,09 |
| 2020-26 | 6m | 75 | +0,93 | 26 / −2,86 | 12 / +8,51 | −0,59 (−3,6) | 0,21 |
| 2020-26 | 12m | 69 | +2,43 | 26 / −2,99 | 10 / +14,34 | −0,98 (−6,1) | 0,41 |

**Residuo del valor justo, umbral z ±1,5:**

| Muestra | h | N | z > +1,5: N / ret | z < −1,5: N / ret | Pendiente t (NW) |
|---|---|---|---|---|---|
| 2012-19 | 3m | 63 | 6 / +1,92 | 6 / +1,37 | −0,3 |
| 2012-19 | 12m | 63 | 6 / +2,59 | 6 / +5,62 | −0,5 |
| 2020-26 | 3m | 78 | 13 / −0,08 | 6 / +4,10 | −0,5 |
| 2020-26 | 12m | 69 | 13 / +1,66 | 6 / +11,73 | −0,7 |

**Lectura:** la reversión a la media de 1 año **no es robusta**: nula en 2012-19 (dominó la tendencia alcista del dólar) y fuerte en 2020-26 apoyada en pocos episodios (picos de 2020 y 2022, valle de 2021; 4–14 casos por grupo). El residuo del valor justo no predice en ninguna submuestra y sus coeficientes son inestables (β DXY de 0,33 a 2,19; β cobre cambia de signo en 2021). Lo más consistente: tras desvíos negativos grandes el dólar subió en 75–100% de los casos en ambas muestras, con N muy pequeño y en parte por la deriva alcista.

## 5. Eventos

Fechas verificadas: anuncio de intervención del BCCh el [14-jul-2022](https://www.bcentral.cl/contenido/-/details/comunicado-14072022) (hasta US$25.000 millones, vigente desde el 18-jul; [DF](https://www.df.cl/consejo-del-banco-central-anuncia-programa-de-intervencion-cambiaria-y), [Forbes](https://forbes.cl/economia-y-finanzas/2022-07-14/banco-central-de-chile-interviene-para-tratar-de-frenar-depreciacion-del-peso/)) y el [28-nov-2019](https://www.emol.com/noticias/Economia/2019/11/28/968757/Banco-Central-interviene-US20-mil.html) (US$20.000 millones). t0 = último cierre antes del evento; CAR con modelo cobre+DXY estimado en [t−270, t−20].

| Evento (t0, nivel) | t−20 | t+1 | t+5 | t+20 | t+60 | Máximo post | CAR t+20 / t+60 | Volatilidad diaria antes → después |
|---|---|---|---|---|---|---|---|---|
| Estallido social (18-oct-2019, 709,7) | +0,8% | +2,0% | +2,3% | +10,3% | +8,7% | +16,7% en t+27 (28-nov-2019, 828,2) | +9,5 / +9,5 | 0,55% → 1,05% |
| Pandemia (11-mar-2020, 835,5) | −5,6% | +2,0% | +3,3% | +2,0% | −7,9% | +3,9% en t+6 | −5,8 / −11,9 | 0,66% → 0,97% |
| Intervención BCCh (14-jul-2022, 1043,0) | −16,9% | −5,3% | −11,1% | −15,4% | −10,5% | mínimo −16,9% en t+36 | −0,2 / −1,5 | 1,02% → 1,54% |

La columna t−20 indica dónde estaba el dólar 20 días antes respecto de t0. Estallido: depreciación de ~9–10% no explicada por cobre ni DXY; el máximo coincide con el anuncio de intervención del 28-nov-2019. Pandemia: pico breve (6 días) y luego caída mayor a la predicha. Julio 2022: depreciación anormal previa de +10,9% que se revirtió hacia t+20 junto con un rebote del cobre de +13%; no se separa el efecto del anuncio. Ambos anuncios coinciden con máximos locales (N = 2).

## 6. Calidad de datos (→ issue #20)

| Serie | N | Rango | Problemas |
|---|---|---|---|
| usdclp | 3686 | 2012-01-02 a 2026-10-26 | Sin duplicados ni huecos > 6 días; fecha futura por vigencia. Atípicos reales: 18–19-jul-2022 (−5,4% y −4,9%). |
| cobre_lb | 3450 | 2012-10-05 a 2026-10-26 | **Falta dic-2017** (7-dic a 2-ene; salto falso +10,9%). Faltan 46 días hábiles más (2014: 7, 2015: 25, 2017: 14). Huecos de 2 días con retorno −7,9% acumulado (2015-07-09). Solo 2 decimales (~0,2%). Mercado de t−2. |
| dxy | 3684 | hasta 2026-10-16 | **Diaria** (no semanal), publicada con ~1 semana de rezago; calendario de EE.UU. (149 días sin dato). |
| tpm | 3659 | — | 2 filas en fin de semana (2022-05-28, 2022-10-08). |
| fed_funds | 5409 | — | Calendario corrido; saltos de fin de mes reales. |
| vix | 3756 | hasta 2026-10-22 | Saltos reales (2018-02-05 +77%, 2024-08-05 +50%). |

## Hechos robustos (se cumplen en ambas submuestras)

1. El USDCLP se mueve contra el cobre (−0,36/−0,38 diario) y con el DXY (+0,51); la correlación crece con el horizonte (−0,49/−0,57 mensual con el cobre) y su signo nunca se invierte en ventanas de un año.
2. La beta del cobre condicionada al DXY es estable (≈−0,11 diaria; −0,15 a −0,17 semanal); la simple cambia de régimen: modelar ambos factores juntos.
3. No hay adelanto explotable más allá de 1 día.
4. El timing intra-mes vale como mucho 1,8–2,5% y solo con oráculo; día 1 y promedio son equivalentes. El rango mensual subió de 3,6% a 5,2%.
5. El desfase de fechas entre series es material y produce adelantos falsos si no se corrige.

## Hipótesis para probar fuera de muestra

- **H1:** con el USDCLP >5% sobre su media de 252 días, el retorno a 6–12 meses es menor que el incondicional (hoy solo en 2020-26; confirmar con datos posteriores o con AUD/PEN).
- **H2:** depreciaciones anormales grandes (CAR > +8% en 20–30 días) anteceden una reversión en 20 sesiones (regla mecánica, no eventos elegidos a mano).
- **H3:** betas variables en el tiempo (Kalman o cambio de régimen) dan un residuo con menos error a 1–3 meses que el valor justo de betas fijas.

Contexto al cierre de los datos (16-oct-2026, no es recomendación): USDCLP +7,9% sobre su media de 1 año y residuo del valor justo z = 2,7; ninguna de las dos señales ha demostrado ser robusta.
