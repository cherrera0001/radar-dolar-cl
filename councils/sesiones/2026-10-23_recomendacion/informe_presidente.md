# Concilio 2026-10-23 · Informe del presidente (evidence_auditor)

El JSON completo con todos los stages está en
`councils/decisions/2026-10-23_220000_recomendacion_comprar_vender_mantener.json` y las
disidencias en `councils/dissents/`. Este documento resume la lectura humana.

Roles (revelados después de la síntesis): **A** Cuantitativo · **B** Red team regulatorio ·
**C** Asesor financiero · **D** Economista macro · **E** Gestor de riesgo · **F** Operador de mesa FX.

## Stage 2 · Verificaciones contra código y datos

| Afirmación | Resultado |
|---|---|
| (a) `simular()` supone 0% para la caja (A) | **Verificado** (`investigacion.py:133-153`). Con caja a TPM y USD a Fed−1%, en la prueba 2020-01..2026-09: acumulación −0,041% → +0,020%; v0.1 −0,129% → −0,037%. Efecto 0,06–0,09 pp, dentro del ruido. En la grilla vista en prueba, una combinación (N=6, entrada 2%) "gana" +0,77%: ejemplo vivo de multiplicidad. Los costos proporcionales se cancelan entre reglas que solo compran con igual gasto. |
| (b) Colas (E) | **Verificado exacto**: −25,07% de 1.042,97 (15-jul-2022) a 781,49 (3-feb-2023); vol anual 11,0% (13,1% desde 2020); peor 12 meses −22,2%. La pérdida latente de una cartera DCA estaba **subestimada**: −11,6% (desde 2020), −9,2% (2022), −9,4% (2024). |
| (c) "2020–26 quemado" (A) | **Verificado para hipótesis de precio** (prueba ejecutada 2 veces; H1 nacida de mirar 2020–26; ≈144 pruebas). **Exagerado para flujos**: NDF y derivados nunca se cargaron; 2020–26 sirve para H2/H3 si el pre-registro va en git antes del primer commit de esos datos. |
| Potencia | MDE de modular ±25%: ≈0,48–0,64% en la muestra completa; ≈0,78% con 12 meses. Confirma el orden de magnitud de A. |

## Stage 3 · Decisión

**COMPRAR / VENDER / MANTENER se redefinen como instrucciones del plan del usuario, no como
pronósticos.** El motor evalúa a diario con datos de d−1 pero notifica una vez al mes.
Precedencia: **SIN SEÑAL > VENDER > MANTENER > COMPRAR**.

| Estado | Cuándo | Acción |
|---|---|---|
| SIN SEÑAL | Insumo vencido, mindicador vs BCCh >0,3%, sin precio ejecutable en 24 h o perfil sin confirmar >6 meses | Avisa y espera; **tras 5 días hábiles se emite COMPRAR** (un fallo de datos no puede ser un "esperar" encubierto) |
| VENDER | Solo necesidad declarada (fecha y monto) a ≤12 meses no cubierta por el colchón | Vender el déficit en tramos mensuales (≤6) por canal con ida y vuelta ≤1%. **Nunca por precio** |
| MANTENER | Colchón incompleto, o exposición w > w*+10 pp | La cuota del mes va a pesos, sin vender (rebalanceo con flujo nuevo, sin costo) |
| COMPRAR | Caso por defecto | Cuota completa en días hábiles 1–5, canal más barato verificado ese día dentro de los límites de custodia, nunca entre el comunicado de la RPM (18:00) y la apertura siguiente |

- **Colchón:** 6 meses de gasto + 100% de necesidades con fecha a ≤12 meses.
- **Custodia:** ≤20% de los USD sin garantía estatal (fintech, stablecoins), solo como canal de paso; depósitos ≤UF 200 por banco.
- **Notificaciones:** 1 mensaje mensual de acción + aviso cuando una necesidad entra a 90 días; sin push por cambios del semáforo. El semáforo va al pie, sin colores, como "Contexto (no es señal)", con tipo de cambio real.
- **Modo sombra:** H2 (NDF no residentes), H3 (derivados AFP), H4 (momentum) como moduladores 0,75x–1,25x; VENDER por banda; R-EJEC (orden límite en Buda); H1 y valor justo solo como contexto.
- **Lectores externos:** solo contenido genérico (compra tu cuota en el canal más barato + tabla de costos con metodología) hasta una revisión legal.

### Protocolo de validación para que algo salga de sombra

1. Pre-registro en `docs/REGISTRO.md` con hash de commit, anterior al primer commit de datos de la hipótesis; familia acumulada (≈144 pruebas hoy).
2. Holdouts: USDCLP 1999–2011 en sobre sellado; AUD/NZD/PEN/COP/BRL; 2020–26 solo para series de flujo nunca cargadas y con el signo mantenido al quitar los 2 mejores episodios.
3. Umbrales: mejora ≥ máx(0,5%; 2,8σ del nulo con igual rotación); SPA de Hansen p<0,05 sobre la familia; Deflated Sharpe >0; mismo signo en 2020–22 y 2023–26 y en ≥3 de 4 pares; ningún año >1% peor que DCA; nunca >2 meses sin comprar.
4. Paper trading de 12 meses como **control operativo**, no como prueba estadística.

## Stage 5 · Disidencias (con condición de reactivación)

D1 banda estrecha (E) · D2 orden límite en producción (F) · D3 VENDER por banda ya (D) ·
D4 cadencia semanal (C) · D5 umbral 0,5% sin SPA familiar (B, C, F) · D6 2020–26 usable para
flujos (presidente contra A) · D7 el paper trading no valida (presidente contra el consenso).
Detalle en `councils/dissents/2026-10-23_220000_recomendacion_comprar_vender_mantener.json`.

## Stage 6 · Trampa de fragilidad

**El consenso definió COMPRAR/VENDER/MANTENER relativos al perfil del dueño, pero el producto
es un broadcast.** Con un segundo lector, un MANTENER calculado con el w* del dueño se lee como
señal de mercado: reintroduce el timing rechazado y la habitualidad que la CMF considera asesoría.
Además, guardar el perfil en un repo donde "git es la base de datos" expone las finanzas del dueño.

Detección temprana: `getChatMemberCount > 1` bloquea estados no genéricos; test que falle si
MANTENER/VENDER se envía a un destino distinto del chat del dueño; CI que falle si aparece un
archivo de perfil bajo `data/` o `reports/`. Secundario: la única ganancia segura (canal barato)
descansa en una foto de precios de un solo día; #25 alerta si el p90 del costo de un canal supera
1% durante 5 días.

**Estado:** `decided_but_unauthorized`: requiere la autorización del dueño (`human_adversarial_pass`).
