# Literatura académica: predictibilidad del USD/CLP para un ahorrista con compra mensual

> Investigación del 2026-10-23 (issue #13). Cada referencia fue verificada en la web; lo no
> verificado está marcado. Contexto de partida: el backtest 2012–2026 del radar v0.1 no le ganó a
> DCA (−0,07% a −0,21% fuera de muestra).

**Resumen:** la literatura es consistente con el backtest. A 1–12 meses, los modelos de
fundamentales (cobre, DXY, tasas, volatilidad) no le ganan de forma estable al paseo aleatorio.
La predictibilidad que existe es de largo plazo y frágil, contemporánea (no sirve para anticipar)
o de microestructura, con datos que un particular no tiene. El margen controlable está en el
costo de ejecución y en dónde se dejan los dólares comprados, no en el momento de compra.

## 1. Predictibilidad del tipo de cambio: Meese-Rogoff y lo que vino después

- **Fuente:** Meese & Rogoff (1983). El paseo aleatorio pronostica tan bien como los modelos monetarios de precios flexibles, de precios rígidos y con cuenta corriente, a 1–12 meses, para USD/GBP, USD/DEM, USD/JPY y el dólar ponderado por comercio, incluso usando fundamentales efectivamente realizados.
- **Fuente:** Rossi (2013, JEL). La respuesta depende del predictor, el horizonte, la muestra, el modelo y el método de evaluación. Los casos más favorables son reglas de Taylor y activos externos netos, con modelos lineales y pocos parámetros. El paseo aleatorio sin deriva sigue siendo el estándar más difícil de superar.
- **Largo plazo, fuente:** Mark (1995, AER) encontró predictibilidad creciente con el horizonte usando la brecha entre el tipo de cambio y sus fundamentales monetarios. Según la literatura que lo cita, Kilian (1999) no la encuentra al actualizar los datos y Faust, Rogers & Wright (2001) la ven solo en una ventana estrecha de versiones de datos (**NO VERIFICADO directamente**: citadas por terceros).
- **PPP, fuente:** Rogoff (1996, JEL): consenso de vida media de 3–5 años para los desvíos del tipo de cambio real; revisiones posteriores, citadas por terceros, muestran intervalos de confianza muy amplios.
- **Por qué ocurre, fuente:** Engel & West (2005, JPE). Si los fundamentales son I(1) y el factor de descuento está cerca de 1, el tipo de cambio se comporta casi como un paseo aleatorio aunque el modelo sea correcto.
- **Interpretación:** un valor justo cobre+DXY puede describir bien el nivel y no servir para elegir cuándo comprar en horizonte mensual, como en el backtest.

## 2. Monedas commodity y el peso chileno

- **Fuente:** Chen & Rogoff (2003, JIE). En Australia y Nueva Zelandia el precio en dólares de las materias primas tiene un efecto fuerte y estable sobre el tipo de cambio real; queda un puzzle de PPP en los residuos.
- **Fuente:** Chen, Rogoff & Rossi (2010, QJE). La dirección robusta es la inversa a la intuitiva: las monedas commodity predicen los precios de las materias primas, dentro y fuera de muestra; lo contrario es mucho más débil, porque el tipo de cambio mira hacia adelante.
- **Fuente:** Ferraro, Rogoff & Rossi (2015, JIMF), petróleo y CAD: sin relación sistemática mensual o trimestral; sí diaria, sobre todo contemporánea. Con rezagos, la capacidad predictiva es "efímera".
- **Chile, fuente:** Pincheira & Hardy (2019, Resources Policy). El peso chileno predice los retornos del índice LME y de metales básicos (dirección peso → metales).
- **Chile, fuente:** De Gregorio & Labbé (2011, DT BCCh 640): efecto estructural del cobre sobre el tipo de cambio real y el ciclo; no es un trabajo de pronóstico.
- **Interpretación:** usar la tendencia de 3 meses del cobre para predecir el USD/CLP va contra la dirección causal útil; el cobre ya está en el CLP el mismo día.

## 3. Flujo de órdenes y microestructura

- **Fuente:** Evans & Lyons (2002, JPE). El flujo de órdenes entre dealers explica >60% de la variación diaria del DEM/USD, frente a <10% de los modelos macro.
- **Fuente:** Evans & Lyons (2005, AER P&P). Fuera de muestra (3 años), un modelo de flujo de clientes supera al paseo aleatorio y al modelo macro, de 1 día a 1 mes; explica ~16% de la varianza mensual.
- **Chile, fuente:** Aldunate, Da, Larrain & Sialm (2025, JFE). Las recomendaciones de cambio de fondo de una asesora (82 entre 2011 y 2020) generaron flujos de AFP que mueven el peso (elasticidad ~0,8 en el working paper). Los bancos locales proveen liquidez spot y se cubren en forwards, con desviaciones de la paridad cubierta.
- **Interpretación:** los flujos importan, pero el efecto es sobre todo contemporáneo y requiere datos de muy poco rezago. Que las series públicas de forwards de AFP y no residentes sirvan para pronosticar desde la posición de un particular está **NO VERIFICADO**.

## 4. Factores carry, momentum y value

- **Fuente:** Menkhoff et al. (2012a, JF). El carry compensa riesgo de volatilidad global del FX; el factor explica >90% del corte transversal de 5 portafolios.
- **Fuente:** Menkhoff et al. (2012b, JFE). Momentum cruzado de hasta ~10% anual; costos y límites al arbitraje lo reducen.
- **Fuente:** Asness, Moskowitz & Pedersen (2013, JF). Value y momentum en 8 mercados, incluidas monedas, correlacionados negativamente.
- **Fuente:** Lustig, Roussanov & Verdelhan (2011, RFS). Un factor de pendiente explica el corte transversal.
- **Fuente:** Burnside et al. (2011, RFS). Retornos del carry atribuidos a un "peso problem".
- **Fuente:** Moskowitz, Ooi & Pedersen (2012, JFE). Momentum de serie de tiempo (1–12 meses, con reversión parcial) en 58 instrumentos, incluidos forwards de monedas.
- **Interpretación:** son cortes transversales sobre muchas monedas; no se trasladan a una sola decisión de comprar USD con CLP. Solo el momentum de serie de tiempo aplica a un par, medido sobre el retorno del forward (carry incluido).

## 5. Paridad descubierta y forward premium puzzle

- **Fuente:** Fama (1984, JME). La variación de los forwards es sobre todo prima de riesgo; pendiente negativa en desarrolladas.
- **Fuente:** Bansal & Dahlquist (2000, JIE). La anomalía se limita a desarrolladas y a cuando la tasa de EE.UU. supera a la extranjera; en emergentes los forwards están menos sesgados.
- **Fuente:** Zigraiova et al. (2021, EER), meta-análisis de 3.643 estimaciones: pendiente 0,23–0,45 en desarrolladas y 0,95–1,16 en emergentes (consistente con la paridad).
- **Interpretación:** para el CLP, el diferencial TPM–Fed tiende a compensarse con depreciación; en valor esperado el momento de compra es casi neutro.

## 6. DCA versus suma única

- **Fuente:** Vanguard (Shtekhman, Tasopoulos & Wimmer, 2012). En EE.UU., Reino Unido y Australia, la suma única le ganó a la compra periódica ~2/3 de las veces (cifras exactas por plazo y región **NO VERIFICADO**).
- **Interpretación:** depende de una prima esperada positiva (acciones); USD contra CLP no la tiene clara si la paridad descubierta se cumple. Quien ahorra de su sueldo no tiene suma única: comprar cada mes es comprar cuando llega el ingreso.

## Referencias

| Cita | URL | Verif. | Hallazgo |
|---|---|---|---|
| Meese & Rogoff (1983). *J. Int. Econ.* 14:3-24 | https://rogoff.scholars.harvard.edu/publications/empirical-exchange-rate-models-seventies-do-they-fit-out-sample | Sí | Paseo aleatorio iguala a modelos estructurales a 1-12 meses |
| Rossi (2013). *JEL* 51(4):1063-1119 | https://doi.org/10.1257/jel.51.4.1063 | Sí | Predictibilidad depende de predictor, horizonte y muestra |
| Mark (1995). *AER* 85(1):201-218 | https://ideas.repec.org/a/aea/aecrev/v85y1995i1p201-18.html | Sí | Predictibilidad a horizontes largos, luego cuestionada |
| Rogoff (1996). *JEL* 34:647-668 | https://web.williams.edu/Economics/macro/rogoff.pdf | Sí | Vida media de 3-5 años para desvíos de PPP |
| Engel & West (2005). *JPE* 113:485-517 | https://doi.org/10.1086/429137 | Sí | Tipo de cambio ≈ paseo aleatorio con descuento cercano a 1 |
| Chen & Rogoff (2003). *JIE* 60(1):133-160 | https://doi.org/10.1016/S0022-1996(02)00072-7 | Sí | Materias primas explican el TCR de AUD y NZD |
| Chen, Rogoff & Rossi (2010). *QJE* 125(3):1145-1194 | https://www.nber.org/papers/w13901 | Sí | El tipo de cambio predice las materias primas |
| Ferraro, Rogoff & Rossi (2015). *JIMF* 54:116-141 | https://www.nber.org/papers/w17998 | Sí | Solo relación diaria; con rezagos, efímera |
| Pincheira & Hardy (2019). *Resources Policy* 62:256-281 | https://ideas.repec.org/a/eee/jrpoli/v62y2019icp256-281.html | Sí (abstract WP) | El CLP predice los metales |
| De Gregorio & Labbé (2011). DT BCCh 640 | https://ideas.repec.org/p/chb/bcchwp/640.html | Sí (título y tema) | Cobre, TCR y fluctuaciones en Chile |
| Evans & Lyons (2002). *JPE* 110(1):170-180 | https://doi.org/10.1086/324391 | Sí | Flujo explica >60% de la variación diaria |
| Evans & Lyons (2005). *AER* 95(2):405-414 | https://doi.org/10.1257/000282805774669934 | Sí | Modelo de flujos supera al paseo aleatorio fuera de muestra |
| Aldunate, Da, Larrain & Sialm (2025). *JFE* 170 | https://www.nber.org/papers/w30753 | Sí | Flujos de AFP mueven el CLP (elasticidad ~0,8) |
| Menkhoff et al. (2012a). *JF* 67(2):681-718 | https://doi.org/10.1111/j.1540-6261.2012.01728.x | Sí | Carry compensa riesgo de volatilidad global |
| Menkhoff et al. (2012b). *JFE* 106(3):660-684 | https://doi.org/10.1016/j.jfineco.2012.06.009 | Sí | Momentum cruzado ~10% anual |
| Asness, Moskowitz & Pedersen (2013). *JF* 68(3) | https://pages.stern.nyu.edu/~lpederse/papers/ValMomEverywhere.pdf | Sí | Value y momentum en monedas |
| Lustig, Roussanov & Verdelhan (2011). *RFS* 24(11):3731-3777 | https://www.nber.org/papers/w14082 | Sí | Factor de pendiente explica el carry |
| Burnside et al. (2011). *RFS* 24(3):853-891 | https://doi.org/10.1093/rfs/hhq138 | Sí | Carry y "peso problem" |
| Moskowitz, Ooi & Pedersen (2012). *JFE* 104(2):228-250 | https://doi.org/10.1016/j.jfineco.2011.11.003 | Sí | Momentum de serie de tiempo 1-12 meses |
| Fama (1984). *JME* 14(3):319-338 | https://eml.berkeley.edu/~craine/EconH195/Fall_14/webpage/Fama_Forward%20Discount.pdf | Sí | Prima de riesgo domina; pendiente negativa |
| Bansal & Dahlquist (2000). *JIE* 51(1):115-144 | https://doi.org/10.1016/S0022-1996(99)00039-2 | Sí | Puzzle limitado a desarrolladas |
| Zigraiova et al. (2021). *EER* 134 | https://ideas.repec.org/p/cpr/ceprdp/15817.html | Sí (CEPR) | Pendiente 0,95-1,16 en emergentes |
| Shtekhman, Tasopoulos & Wimmer (2012). Vanguard | https://corporate.vanguard.com/content/dam/corp/research/pdf/cost_averaging_invest_now_or_temporarily_hold_your_cash.pdf | Parcial | Suma única gana ~2/3 en acciones y bonos |

## Conclusiones accionables

1. Mantener la compra fija mensual y no condicionarla a señales de precio (Meese-Rogoff; Rossi; Engel-West).
2. No usar cobre ni DXY rezagados para el timing: la causalidad útil va del CLP al cobre (Chen-Rogoff-Rossi; Pincheira-Hardy; Ferraro et al.).
3. No demorar la compra para ganar la tasa en pesos: la paridad descubierta se cumple aproximadamente en emergentes.
4. Optimizar el costo de compra: ahorro cierto frente a un beneficio de timing nulo en promedio (interpretación; medir con datos).
5. Poner los USD a rendir apenas se compran (depósitos o T-bills en USD).
6. Esperar caídas fuertes del CLP en episodios de volatilidad global sin intentar anticiparlas (Menkhoff 2012a: dato de riesgo, no señal).
7. Usar el valor justo solo como alerta de extremos y con horizonte de años (Rogoff 1996; Mark 1995 y críticas).

## Hipótesis que vale la pena testear

- Costo y momento de ejecución (spread por canal, día de la semana o del mes).
- Momentum de serie de tiempo 1-12 meses (con carry) para modular el monto 0,75x–1,25x, fuera de muestra y neto de costos.
- Desvíos extremos del valor justo (>2 desviaciones) con horizonte 12-36 meses, con datos desde la flotación de 1999 (riesgo de sobreajuste alto).
- Expectativas de encuestas del BCCh (EOF, EEE) frente al paseo aleatorio (indicio **NO VERIFICADO**).
- Flujos publicados de AFP y no residentes con su rezago real de publicación.

## Hipótesis descartadas o muy improbables

- Fundamentales macro como predictores a 1-12 meses.
- Diferencial de tasas como señal de timing en una moneda emergente.
- Trasladar primas cruzadas de carry, value y momentum a un solo par.
- VIX o volatilidad como señal anticipada (relación contemporánea).
- Aplicar a USD/CLP el "la suma única gana dos tercios de las veces".
