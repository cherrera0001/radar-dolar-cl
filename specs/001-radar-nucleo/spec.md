# Especificación 001: Radar del dólar (núcleo)

**Estado:** vigente. Describe lo que el código hace hoy (commit `e3d114b`), no lo deseado.
**Constitución:** `.specify/memory/constitution.md`

## Problema

Quien ahorra en dólares desde Chile compra en cuotas y no sabe si el precio de hoy es alto o bajo
frente a lo que lo mueve. Las fuentes que consulta muestran el precio, pero no explican la
comparación, ni cuánto le ha costado a alguien esperar o comprar antes.

## Quién lo usa

- **Dueño del radar:** recibe alertas de cambio de semáforo y el resumen semanal.
- **Lectores públicos:** consultan el bot de Telegram y el panel.

## Historias de usuario

**US1 · Estado de hoy (P1).** Como lector, quiero ver si el dólar está barato, normal o caro hoy,
con la explicación de cada señal, para entender de dónde sale el resultado.
- *Dado* datos al día, *cuando* pido `/estado` o `radar senales`, *entonces* veo el semáforo, el
  puntaje, cuántas señales coinciden, y una línea por señal con su valor.
- *Dado* una señal sin datos, *entonces* aparece como "sin datos", nunca como neutra.

**US2 · Aviso de cambio (P1).** Como dueño, quiero un aviso solo cuando el semáforo cambia, con qué
señales lo movieron, para no revisar a diario.
- *Dado* que el estado cambió respecto a la última corrida, *cuando* corre `diario.yml`, *entonces*
  llega un mensaje con el estado anterior, el nuevo y las señales que cambiaron 0,1 o más.
- *Dado* que no cambió, *entonces* no llega nada.

**US3 · Resumen semanal (P2).** Como dueño, quiero un resumen semanal con el backtest y el resultado
fuera de muestra, para contrastar la recomendación con la evidencia.

**US4 · Historial del semáforo (P2).** Como lector, quiero saber qué hizo el dólar después de días
con cada estado, frente a cualquier día, para juzgar si el estado aporta información.
- *Dado* un horizonte de 3, 6 o 12 meses, *entonces* veo el porcentaje de días en que el dólar subió,
  con cantidad de días y episodios aproximados.

**US5 · Panel (P3).** Como lector, quiero un panel con calibración, comparación con DCA, estacionalidad,
correlación con cobre y DXY, y salud de datos, para explorar sin escribir código.

**US6 · Salud de fuentes (P2).** Como dueño, quiero aviso cuando una fuente falla tres días hábiles
seguidos, se atrasa, o vuelve a responder, para no usar datos viejos sin saberlo.

## Requisitos funcionales

- **FR-001** El semáforo se calcula con 6 señales ponderadas (valor justo 0,30; posición en el año 0,25;
  cobre 0,15; dólar global 0,10; tasas 0,10; riesgo 0,10). Estado BARATO si el compuesto ≥ 0,25,
  CARO si ≤ −0,25, NORMAL en medio. Mínimo 3 señales disponibles.
- **FR-002** Las series se indexan por día de mercado y se alinean sin imputar más allá de su
  antigüedad máxima (7 días; 14 para el DXY).
- **FR-003** Un valor futuro respecto a la fecha de corrida se descarta antes de guardarse.
- **FR-004** Cada fuente valida el cuerpo de la respuesta y falla ruidosamente si es inválido.
- **FR-005** Las alertas de cambio se envían solo cuando el estado difiere del último guardado; el
  estado se guarda después de enviar, para reintentar si falla Telegram.
- **FR-006** El backtest compara cada estrategia con DCA y reporta la diferencia en cada resumen.
- **FR-007** La recomendación publicada es DCA mientras ninguna regla gane fuera de muestra.
- **FR-008** Las series se publican como CSV en `data/series/`; no hay base de datos.

## Criterios de éxito

- **SC-001** Con datos al día, `radar senales` termina en menos de 10 segundos.
- **SC-002** Ninguna cifra publicada llega sin fecha ni sin línea base cuando corresponde.
- **SC-003** Un dato futuro nunca aparece en `data/series/` (verificado por prueba).
- **SC-004** Las alertas no se repiten sin cambio de estado.

## Supuestos

- Mindicador.cl y FRED siguen publicando con la estructura validada hoy.
- El dueño mantiene habilitado Actions con cuota disponible.
- Los datos son públicos; el repo puede seguir privado mientras el bot y el panel sean públicos.

## Aclaraciones pendientes

- **[NECESITA ACLARACIÓN] Recomendación frente a órdenes.** La constitución (I) y el README dicen que el
  radar describe y no ordena. El concilio del 2026-10-23 (`councils/decisions/2026-10-23_220000`)
  autorizó emitir COMPRAR / VENDER / MANTENER con reglas de prioridad. Son incompatibles: hay que
  decidir cuál es el producto antes de implementar el concilio. Mientras tanto, no se implementa.
- **[NECESITA ACLARACIÓN] Repo público.** ¿El código y los datos pasan a ser públicos? Cambia la
  privacidad (principio V) y la exposición de la historia de git.
- **[NECESITA ACLARACIÓN] Frecuencia del bot.** ¿Basta con ~30 min de latencia, o hace falta respuesta
  inmediata (Cloudflare Worker)?
- **[NECESITA ACLARACIÓN] Marco legal.** El README cita la Ley Fintec (21.521). Ofrecer el radar como
  servicio público puede acercarse a asesoría. ¿Se consulta antes de publicar?
