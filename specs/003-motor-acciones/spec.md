# Feature Specification: Motor de acciones v1 (SIN SEÑAL, VENDER, MANTENER, COMPRAR)

**Feature Branch**: `main` (sin rama de feature, por instrucción permanente del dueño)

**Created**: 2026-10-24

**Status**: Implemented (código y pruebas); pendiente de validación del dueño con su perfil real

**Input**: User description: "describir y ordenar: instrucciones de acción según el plan del dueño, con la
decisión del concilio 2026-10-23_220000 como referencia"

**Autoridad**: `councils/decisions/2026-10-23_220000_recomendacion_comprar_vender_mantener.json`
(estado `decided_authorized`, aprobado por el dueño el 2026-10-23).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Instrucción mensual al dueño (Priority: P1)

Como dueño, quiero recibir una sola instrucción por mes (SIN SEÑAL, VENDER, MANTENER o COMPRAR) según mi plan,
para no revisar el precio a diario ni decidir por intuición.

**Why this priority**: es el producto que el dueño pidió; sin esto el radar solo describe.

**Independent Test**: con un perfil de prueba en el entorno y datos vigentes, `radar accion` imprime una única
instrucción dentro de los días 1 a 5, y `radar accion --enviar` la envía una sola vez por mes.

**Acceptance Scenarios**:

1. **Given** un perfil con colchón completo, sin necesidades pendientes y peso dentro de w\*+10 pp, **When**
   corre el motor en días 1 a 5 con datos vigentes, **Then** la instrucción es COMPRAR.
2. **Given** una necesidad a ≤ 12 meses no cubierta por el colchón, **When** corre el motor, **Then** la
   instrucción es VENDER, con monto y sin mirar el precio.
3. **Given** un colchón incompleto o peso sobre w\*+10 pp, **When** corre el motor sin necesidad pendiente,
   **Then** la instrucción es MANTENER.
4. **Given** una instrucción ya enviada este mes con el mismo contenido, **When** corre de nuevo, **Then**
   no se envía nada.
5. **Given** la ventana de compra cerrada (día 6 o posterior), **When** corre el motor, **Then** no emite
   instrucción.

### User Story 2 - Sin señal cuando los datos o el perfil no son confiables (Priority: P1)

Como dueño, quiero que el sistema diga SIN SEÑAL cuando no puede actuar con confianza, en vez de inventar una
instrucción sobre datos viejos o un perfil desactualizado.

**Why this priority**: evita actuar sobre información falsa. Es la primera regla de precedencia del concilio.

**Independent Test**: con datos vencidos, o con un perfil sin confirmar hace más de 6 meses, o sin perfil, la
instrucción es SIN SEÑAL con su motivo.

**Acceptance Scenarios**:

1. **Given** cualquier serie fuera de su antigüedad máxima, **When** corre el motor, **Then** SIN SEÑAL con
   código `insumo_vencido`.
2. **Given** un perfil confirmado hace más de 180 días, **When** corre el motor, **Then** SIN SEÑAL con código
   `perfil_vencido`.
3. **Given** que no hay perfil configurado, **When** corre el motor, **Then** SIN SEÑAL con código
   `perfil_ausente`, sin que el repositorio contenga ningún dato personal.

### User Story 3 - Contexto público sin instrucciones (Priority: P2)

Como lector público, quiero ver el semáforo como contexto, rotulado "no es señal", sin colores ni instrucciones.

**Why this priority**: el repo es público; las instrucciones personales no pueden llegar a terceros.

**Independent Test**: `/estado` en el bot devuelve el texto de contexto y no contiene MANTENER, VENDER ni
COMPRAR.

**Acceptance Scenarios**:

1. **Given** un chat que no es el dueño, **When** pide `/estado`, **Then** recibe el semáforo sin iconos de
   color, rotulado "Contexto (no es señal)".

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001** El motor MUST aplicar la precedencia SIN SEÑAL > VENDER > MANTENER > COMPRAR.
- **FR-002** COMPRAR MUST emitirse solo en los días 1 a 5 del mes de cobro, en el canal más barato verificado.
- **FR-003** VENDER MUST limitarse al monto de necesidades declaradas a ≤ 12 meses no cubierto por el colchón,
  nunca por precio.
- **FR-004** MANTENER MUST aplicarse si el colchón está incompleto o el peso del dólar supera w\* + 10 pp.
- **FR-005** Con datos vencidos, el motor MUST devolver SIN SEÑAL y no una acción.
- **FR-006** El perfil MUST venir de un secreto (`PERFIL_DUENO`) o de `perfil.local.json` (ignorado por git).
  Nunca del repositorio (constitución V).
- **FR-007** Una instrucción MUST enviarse solo al chat del dueño, una vez por mes y por contenido
  (constitución VI y VIII).
- **FR-008** El semáforo MUST NOT generar avisos de cambio (concilio: sin push por cambios del semáforo).
- **FR-009** Los lectores públicos MUST recibir contexto genérico rotulado "no es señal".
- **FR-010** VENDER por banda (w > w\*+20 pp) MUST quedar en modo sombra: registrarse sin emitir instrucción.
  NEEDS CLARIFICATION: formato de la bitácora de sombra (#30) aún no definido.
- **FR-011** SIN SEÑAL por divergencia mindicador/BCCh > 0,3% MUST activarse cuando exista la fuente BCCh
  (fase 2). NEEDS CLARIFICATION: hoy esa comprobación no se ejecuta.
- **FR-012** Tras 5 días hábiles en SIN SEÑAL, el concilio prevé emitir COMPRAR. NEEDS CLARIFICATION: requiere
  estado persistente de cuántos días lleva en SIN SEÑAL; hoy no está implementado.

### Key Entities

- **Perfil**: w\* (peso objetivo), peso actual del dólar, colchón completo (sí/no), déficit de necesidades a
  ≤ 12 meses (USD) y fecha de última confirmación. Vive fuera del repositorio.
- **Instrucción**: acción (SIN SEÑAL, VENDER, MANTENER, COMPRAR), código estable y motivo en texto.
- **Registro de envíos**: clave (tipo y mes) con la huella del contenido. Vive en `data/envios.json`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** Un mismo contenido nunca se envía dos veces para la misma clave (verificado por prueba).
- **SC-002** Ninguna instrucción personal llega a un chat distinto del dueño (verificado por prueba y diseño).
- **SC-003** Con datos vencidos, el motor nunca devuelve COMPRAR, VENDER ni MANTENER (verificado por prueba).
- **SC-004** El repositorio no contiene archivos de perfil (CI falla si aparecen, verificado por
  `tests/test_privacidad.py`).
- **SC-005** El diario corre en verde en Actions con el paso de instrucción activo (verificado el 2026-10-24).

## Assumptions

- El dueño confirma su perfil cada 6 meses; el sistema lo verifica, no lo calcula.
- Los datos de mindicador y FRED siguen publicándose con la antigüedad validada hoy.
- El motor no pronostica el precio: su instrucción depende del perfil, del calendario y de la vigencia de los
  datos.
- La revisión legal (#31) queda pendiente. Las instrucciones no se ofrecen a terceros hasta completarla
  (constitución VI).
