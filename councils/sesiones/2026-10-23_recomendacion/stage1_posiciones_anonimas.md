# Stage 1 · Posiciones anonimizadas (orden aleatorio)

Concilio 2026-10-23 sobre `councils/agenda/2026-10-23_recomendacion_comprar_vender_mantener.md`.
Las posiciones se anonimizaron como A–F para la revisión cruzada (Stage 2). La correspondencia
con los roles se revela en el JSON de decisión después de la síntesis. Contenido condensado
fielmente de cada entrega (se omiten listas de fuentes repetidas; cada consejero citó el material).

---

## Consejero A · confianza 85%

**Posición.** Con los datos actuales no se puede emitir COMPRAR/VENDER como señales de timing. Defendible hoy: COMPRAR = cuota completa cada mes por un canal barato; VENDER = solo cuando el usuario necesita pesos, nunca por lectura de mercado.

**Propuesta.** Única regla táctica admisible a prueba (R-MOD): modular el monto mensual 0,75x–1,25x, caja máx. 2 cuotas, presupuesto igual a DCA, señal pre-registrada (p. ej. NDF neto de no residentes con rezago real), costos 0,5–0,75%/compra, caja en CLP rinde TPM y USD rinde Fed − 1%. **Defecto detectado:** `simular()` supone tasa 0% para la caja, sesga contra la acumulación.

**Potencia (Monte Carlo propio, USDCLP 2020-01 a 2026-09, 20.000 señales aleatorias; vol mensual 3,67%, AC −0,09):** desvío nulo de la mejora vs DCA 0,26% (modular ±25%) → mejora mínima detectable ≈0,74% (α 5%, potencia 80%) y ≈1,05% con Bonferroni ~30; modular ±50% → ≈1,5% / 2,1%; postergar 2 meses ≈0,72% / 1,0%. Los efectos observados (−0,04% a −0,21%) son ruido (0,2–0,8σ). Detectar ≈1% exige capturar 40–55% del techo de oráculo: implausible. El desvío nulo con trayectoria fija subestima la incertidumbre.

**Multiplicidad.** >130 pruebas ya hechas (v0.1 7 configuraciones evaluadas con la muestra completa que incluye la prueba; H1 15 combinaciones con la prueba mirada dos veces; HISTORICO ~80 correlaciones cruzadas, 8 Granger, ~16 pendientes, 3 eventos). **El período 2020–26 está quemado**; la H1 "desvío >5% sobre media 252d" nació de mirar 2020–26 y no puede validarse con él. Corrección: registro de hipótesis acumulado; Reality Check de White (2000) / SPA de Hansen (2005) con bootstrap estacionario; Romano-Wolf; Deflated Sharpe y PBO (Bailey–López de Prado); t ≥ 3 (Harvey-Liu-Zhu 2016).

**Protocolo mínimo.** (1) Pre-registro con hash de commit. (2) Holdouts limpios: USDCLP 1999–2011 (nunca mirado), réplica en AUD/PEN/COP/BRL, paper trading desde hoy. (3) Aprobación conjunta: SPA p<0,05 sobre la familia, mejora neta ≥0,75%, signo positivo en ambos subperíodos y ≥3 de 4 pares, nunca >2 meses sin comprar, peor año ≤1% bajo DCA. (4) VENDER: además mejora > costo ida y vuelta (0,9–5%): hoy inalcanzable.

**Riesgos.** Falso positivo por multiplicidad → posterga compras en tendencia alcista; asimetría de VENDER; "CARO" z=2,7 leído como orden.

**Cambiaría de opinión si** una regla pre-registrada pasa SPA en 1999/2003–2019, ≥0,75% neto en 2020–26 y ≥3 de 4 pares, y ≥12 meses de paper trading no negativos.

**Exige.** `docs/REGISTRO.md`; en `investigacion.py`: costos, rendimiento de caja, nula de estrategias aleatorias con igual rotación, SPA/RC, DSR, PBO-CSCV; datos USDCLP 1999–2011 (API BDE), AUD/PEN/COP/BRL, NDF con fecha de publicación; paper trading con bitácora inmutable; corregir cobre (#20).

---

## Consejero B · confianza 80%

**Posición.** El radar no debe emitir COMPRAR/VENDER como orden de timing. Por defecto: "COMPRA TU CUOTA DEL MES en el canal más barato" hasta que una regla pase salvaguardas duras. VENDER solo con necesidad de pesos declarada con fecha.

**Propuesta.** COMPRAR = cuota fija hoy (una regla validada solo modula 0,75x–1,25x, nunca deja de comprar). MANTENER = no vender y poner los USD a rendir en un instrumento con garantía o regulado. VENDER = solo necesidad declarada a ≤12 meses, mostrando el costo ida y vuelta del canal.

**Salvaguardas para pasar de "contexto" a "instrucción":** (1) prerregistro; (2) gana neta de costos ≥0,5% anual fuera de muestra con 0,5–0,75%/compra; (3) IC bootstrap por bloques que excluya 0 tras corregir por todas las hipótesis ya probadas, ambas submuestras, ≥30 eventos independientes; (4) datos con fecha de publicación (vintages BCCh); (5) 12 meses en vivo sin plata con degradación automática a "contexto" si pierde; (6) bloqueo "SIN SEÑAL" si un insumo supera su antigüedad, mindicador y BCCh difieren >0,3% o falta el precio ejecutable del canal; timestamp y fuente en todo mensaje; (7) sin push por cambio de señal: un recordatorio mensual, sin "urgente"/"oportunidad"; (8) canales neutrales: sin referidos ni comisiones, ranking por costo medido con metodología publicada.

**Marco legal (verificado vía BCN, CMF Educa, Carey, DF; no es asesoría legal):** Ley 21.521 art. 3 n°2 define asesoría de inversión como recomendaciones a terceros sobre conveniencia de inversiones en valores de oferta pública, instrumentos financieros o proyectos. Art. 3 n°8 excluiría dinero y divisas de "instrumento financiero" (redacción literal NO VERIFICADA): comprar USD al contado quedaría probablemente fuera; recomendar money market USD, USDC/USDT o saldos fintech podría quedar dentro. Art. 5: inscripción solo si es "profesional". FAQ CMF NCG 502 (jul-2024): asesoría = capacidad/intención de influir + habitual y sostenida hacia público o grupo; los programas de referidos son ejemplo; contenido "objetivo y neutral" excluido; disclaimers no mencionados.

**Riesgos.** Falsa precisión (z=2,7 hoy tienta a "ESPERAR"); sesgo de confirmación con la hipótesis de flujos del dueño; notificaciones que inducen a operar (alerta en la RPM 26-27 oct); datos erróneos/atrasados (observado ≠ precio ejecutable, DXY con rezago, huecos del cobre, divergencia #7, revisiones NDF); conflicto de interés por referidos y sesgo a stablecoins sin garantía; lectores externos hacen al bot "habitual, sostenido y con capacidad de influir".

**Cambiaría de opinión si** H2/H3 con vintages cumple las salvaguardas 1–5 (≥0,5% neto, IC sin 0 tras multiplicidad, 12 meses en vivo); en lo legal, opinión escrita de abogado o consulta formal a la CMF.

**Exige.** Vintages BCCh; serie diaria propia de costo ejecutable por canal con hora; registro de hipótesis y prerregistro; libro en vivo de cada mensaje vs DCA con degradación; monitor de frescura/divergencia → "SIN SEÑAL"; política de notificaciones; ficha de metodología, riesgos y conflictos estilo art. 8 n°5; issue de revisión legal antes de ampliar lectores.

---

## Consejero C · confianza 80%

**Posición.** El radar no debe opinar sobre el precio del dólar; debe decir si esta semana el usuario debe actuar según su propio plan. Con la evidencia actual un COMPRAR/VENDER basado en precio sería ruido con apariencia de consejo.

**Propuesta.** Perfil declarado una vez: cuota Q y día de compra (día de sueldo), canal, colchón en pesos C meses (defecto 6), necesidades en pesos con fecha, W* objetivo de USD sobre patrimonio líquido con banda ±10 pp. **Regla semanal** (viernes, datos de d−1, prioridad descendente): (1) VENDER solo si hay necesidad en pesos a ≤90 días no cubierta por el colchón (vender el déficit en 1–3 tramos semanales) o si USD > W*+10 pp (vender hasta W*); nunca por "dólar caro". (2) COMPRAR si esta semana es el día de compra y el colchón está completo: Q completo en el canal más barato medido ese día; si el colchón está incompleto, la cuota va a pesos. (3) MANTENER en otro caso. Backtest con costos 0,46% / 2,51% y tres brazos: (a) DCA banco, (b) DCA canal barato, (c) (b) + modulación 0,75x–1,25x con H2/H3/H4 en modo sombra. Métricas: USD por peso neto de costos, costo de ventas forzadas, VENDER emitidos por año.

**Ejemplo de mensaje (datos del 23-oct-2026 del material):** "Tu plan: US$500/mes, compra el primer día hábil de noviembre, colchón completo, sin necesidades en pesos, USD dentro de tu banda. Precio hoy (17:03): Fintual $1.000,00 · Buda USDC $997,45 + 0,5% · BancoEstado $1.019,00. Observado $986,58 / $984,96: referencia, no precio ejecutable. Lo que sí controlas: comprar en Fintual en vez de BancoEstado ahorra ~$9.500 este mes (~US$120/año). Contexto (no es señal): al 16-oct el dólar estaba 7,9% sobre su promedio de 12 meses; esa señal no ha predicho nada fuera de muestra. El BCCh decide la tasa el 27-oct a las 18:00. **Decisión: MANTENER.**"

**Riesgos.** Vender en el peor momento (−15,4% en 20 sesiones tras el 14-jul-2022) → colchón obligatorio y aviso de necesidades a 90 días; un semáforo caro/barato semanal entrena sesgos (contexto abajo, rotulado "no es señal"; destacar el ahorro por canal); custodia sin garantía (Fintual, Global66, stablecoins); mantención de cuentas USD; impuestos al vender (NO VERIFICADO): registrar costo de cada compra.

**Cambiaría de opinión si** H2/H3 con vintages superan "canal barato + DCA" por ≥0,5% anual neto en ≥2020, con el mismo signo en 2020–22 y 2023–26 y t>2 → acepta modulación 0,75x–1,25x dentro de COMPRAR, sin VENDER por precio. Cambiaría la banda si la simulación muestra que rebalancear a ±10 pp destruye más valor que no vender nunca.

**Exige.** Perfil y registro de compras (fecha, precio, monto, canal); precios por canal diarios (dolaronline, Buda, observado BCCh conciliado #7); backtest con costos y tres brazos; H2/H3 en sombra con vintages; verificar impuestos SII, rentabilidad de money market USD, tarifarios de mantención; calendario BCCh solo como contexto.

---

## Consejero D · confianza 75%

**Posición.** La recomendación no puede apoyarse en una predicción del precio; tiene que salir de una regla de asignación: qué porcentaje del patrimonio financiero va en USD, con bandas de rebalanceo y mirando cuándo se necesitarán pesos. COMPRAR/VENDER/MANTENER describen dónde está el usuario respecto de su porcentaje objetivo.

**Fundamento.** Para este usuario el USD es un seguro: el CLP se deprecia en las crisis (2019 +16,7% en 27 días, 2020, 2022) cuando cae el ingreso local; con paridad descubierta aproximada en emergentes (pendiente 0,95–1,16) el USD no rinde exceso esperado. La decisión es cuánto seguro tener.

**Propuesta.** w = USD / patrimonio financiero en CLP (incluye pesos líquidos; excluye vivienda y AFP); w* lo elige el usuario (defecto 40%). COMPRAR: w < w*+10 pp → cuota completa el día de cobro en canal ≤0,5%. MANTENER: w*+10 ≤ w < w*+20 → cuota del mes en pesos (UF o depósito), sin tocar lo comprado. VENDER: w ≥ w*+20 (vender hasta w*+10) o necesidad conocida de pesos a <12 meses no cubierta (vender solo ese monto en tramos mensuales durante 6–12 meses). Walk-forward mensual con dato de m−1; costos 0,46% / 0,93% (estrés 2,5% / 5%); USD rinde Fed − 1%, pesos TPM − 0,5%; grilla fija a priori w* ∈ {30, 50, 70}%, bandas {10/20, 15/30}; métricas: patrimonio final en CLP real (UF) y USD, peor caída en CLP real a 12 meses, CLP disponibles en la fecha de la necesidad; comparar contra 100% USD DCA y 100% pesos UF; diseño 2012–19, prueba ≥2020, prueba externa AUD/NZD/PEN. El indicador de contexto debe ser el **tipo de cambio real**, no el nominal (el nominal sube por diferencial de inflación y sesga el percentil hacia "caro").

**En contra.** En 2012–19 la reversión fue nula y dominó la tendencia alcista: un rebalanceo que vende USD caros pudo perder; no se sabe si el rebalanceo gana neto de 0,93% ida y vuelta.

**Riesgos.** Vender el seguro antes de necesitarlo (2019–22: 700 → 1.040; bandas anchas, VENDER lo menos frecuente); elegir mal w* (es preferencia y pasivos, el radar debe pedirlo); falsa precisión ("superaste tu banda", no "el dólar va a bajar"); custodia; contexto actual (+7,9%, z=2,7, RPM 26-27 oct) no debe convertirse en VENDER.

**Cambiaría de opinión si** H2/H3 con vintages mejoran ≥0,93%/año neto fuera de muestra en ambas submuestras (acepta modulador 0,75x–1,25x); si el rebalanceo pierde contra DCA neto de costos en ambas submuestras y en AUD/NZD/PEN (COMPRAR = DCA siempre; VENDER solo por necesidad); si las encuestas BCCh (EOF/EEE) le ganan al paseo aleatorio a 12 meses (H6).

**Exige.** Tipo de cambio real BCCh; observado desde 1999; TPM, IPC, UF; códigos F099 con vintages; CPI EE.UU.; AUD/NZD/PEN; issue "backtest de asignación con bandas" con estado de cartera, costos por canal, rendimiento de saldos y necesidad de pesos simulada; #19 y #20 previos; interfaz que pide w*, horizonte y necesidades.

---

## Consejero E · confianza 80%

**Posición.** La pregunta no es cuándo comprar sino cuánta exposición en USD mantener y cuándo rebalancear contra esa meta. El estado sale de la distancia a la meta y de la necesidad de pesos con fecha, no del precio. VENDER solo con necesidad no cubierta o exposición sobre el techo de la banda.

**Propuesta.** Entradas: G gasto mensual, necesidades con fecha <24 meses, w* sobre patrimonio financiero sin colchón. **Colchón en CLP** fuera del cálculo: 6 meses de G + 100% de necesidades a <24 meses; no se dolariza (si ya está en USD, se cubre primero). Regla mensual (primer día hábil): COMPRAR si colchón completo y w ≤ w*+5 pp (cuota completa, canal más barato verificado); MANTENER si w*+5 < w ≤ w*+10 (cuota en CLP; rebalanceo con flujo nuevo, sin costo de venta); VENDER si w > w*+10 durante 2 meses seguidos (vender hasta w*+5) o faltan pesos para una necesidad a ≤6 meses; venta en tramos de 2–3 meses, solo por canal con ida y vuelta ≤1%. Test walk-forward con parámetros fijos, costos 0,5–0,75% compra y 0,5–1% venta (banco 2,5%/lado); métricas: patrimonio CLP, CVaR 5% a 12 meses, máxima caída, **pérdida realizada en ventas forzadas** simulando una necesidad de pesos en cada mes (incluidos feb-2023 y feb-2026). Gana si reduce pérdida realizada o CVaR sin costar >0,2%/año vs DCA.

**Colas (cálculo propio sobre data/series/usdclp.csv):** volatilidad anual 11,0% (13,1% desde 2020); peor retorno a 12 meses −22,2% (p1 −15,7%); máxima caída −25,1% (1.042,97 el 15-jul-2022 → 781,49 el 3-feb-2023); pandemia −18,2%; ene-2025 → feb-2026 −15,7%. El riesgo real es necesitar pesos tras una apreciación del peso. Peor pérdida latente de una cartera DCA: −9,7% (desde 2020), −7,4% (2022), −8,2% (2024).

**Custodia.** Saldos USD en fintech sin garantía; depósitos a plazo con tope UF 200/banco y UF 400 en el sistema; cuentas vista 100%. USDC cayó a ~0,87 el 11-mar-2023 (SVB) y los exchanges suspendieron conversiones (CNBC, Decrypt, Fed FEDS Notes 2025). Límites: ≤20% de los USD en stablecoins o fintech sin garantía y solo como canal de paso; saldo por banco dentro del tope de garantía.

**Riesgos.** Venta forzada en la cola (control: colchón); liquidez del canal en estrés; VENDER mal entendido como señal reintroduce timing y genera ganancias tributables.

**Cambiaría de opinión si** una señal de flujos con fecha de publicación gana neta de 0,75%/lado en ambas submuestras sin empeorar CVaR (modula 0,75x–1,25x dentro de la banda, nunca la meta); si la banda no reduce pérdida realizada ni CVaR frente a "DCA + colchón", la banda sobra.

**Exige.** Perfil (w*, G, necesidades, saldos por custodio); backtest de rebalanceo con ventas, necesidades inyectadas, CVaR, máxima caída y pérdida realizada, escenarios oct-2019, mar-2020, jul-2022→feb-2023, ene-2025→feb-2026; spread diario por canal con histórico; mapa de custodia (garantía, regulador, tope); #19, #20, #7.

---

## Consejero F · confianza 80%

**Posición.** Ninguna señal de dirección merece COMPRAR/VENDER/MANTENER para este usuario. Lo defendible es una regla de ejecución y de liquidez. Cuando el BCCh publica NDF o derivados de AFP (T+1/T+2), los dealers ya lo vieron en su libro: el minorista no tiene ventaja informativa. Pierde dinero con certeza en el spread y vendiendo en el peor momento operativo.

**Propuesta.** COMPRAR (defecto mensual) = cuota completa por el canal más barato verificado, nunca la pizarra; MANTENER = no deshacer, USD rindiendo o con garantía; VENDER = solo necesidad declarada con fecha y monto, escalonada, nunca apuesta de dirección. **R-EJEC:** ventana días hábiles 1–5 en horario de mayor liquidez; orden límite al precio medio en Buda (maker 0,2%); si no se ejecuta al día 5, a mercado en el canal más barato (Fintual ~0,46% o Buda taker ~0,74%); no operar entre el comunicado de la RPM (18:00) y la apertura siguiente; métrica: costo efectivo vs precio medio del instante + deslizamiento vs precio medio del día 1; sin historia de libro → forward-test en papel 6 meses; pasa si el costo total queda ≥0,15 pp bajo "DCA día 1 en Fintual" y el deslizamiento promedio ±0,1%. **R-SAL:** necesidad de N pesos en T → vender N/k cada mes en los k = 3–6 meses previos por el canal de menor spread de venta (opcional, solo si pasa walk-forward: adelantar un tramo si USDCLP >5% sobre su media de 252d, frágil). **R-COLCHÓN:** 3–6 meses de necesidad en CLP para no vender nunca forzado; testear con 2019, 2020 y 2022 (venta forzada vs escalonada).

**En contra.** Evans-Lyons (2005) sí predicen, pero con datos propios del dealer; la reversión +5% fuerte en 2020–26 es frágil; el supuesto de que los spreads de apps se ensanchan fuera de horario y en estrés **no está verificado**: hay que medirlo.

**Corrección clave.** El dólar observado se calcula con operaciones del día anterior: no es un precio ejecutable; usarlo como referencia de costo es un error (metodología BCCh). El spot se negocia sobre todo en DATATEC y liquida T+1 (horario de DATATEC no verificado).

**Riesgos.** Venta forzada con spreads abiertos en estrés; contraparte (stablecoins, saldos fintech); órdenes límite no ejecutadas (tope de 5 días); VENDER como señal de dirección induce ida y vuelta (0,9–5%); mantención de cuentas USD (BCI ≈21 UF/año).

**Cambiaría de opinión si** H2/H3 con fecha de publicación real y vintages ganan >0,5% neto en ≥2020 con la ganancia en >10 episodios independientes (modula 0,75x–1,25x, nunca saltarse meses); si la orden límite no ahorra >0,1 pp vs Fintual a mercado, R-EJEC se reduce a "compra el día 1 en el canal más barato".

**Exige.** Logger del libro de Buda (order_book y ticker cada 5–15 min en horario hábil: precio medio, spread, profundidad hasta US$2.000); panel de spreads por canal con hora (dolaronline 1–2 veces/día); series BCCh con vintages y fecha de captura; costos en el backtest (0,5% compra, 0,5–2,5% venta) y módulo venta forzada vs escalonada con 2019, 2020 y 2022; confirmar horario de DATATEC.
