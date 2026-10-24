# Tasks: Motor de acciones v1

**Input**: Design documents from `/specs/003-motor-acciones/`

**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Organization**: tareas agrupadas por historia de usuario.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: puede correr en paralelo (archivos distintos, sin dependencias)
- **[Story]**: historia a la que pertenece (US1, US2, US3)

## Phase 1: Fundaciones

- [x] T001 Registro de envíos con huella y reintento en `radar/envios.py` (`98aeb93`)
- [x] T002 [P] Guardas de privacidad en `tests/test_privacidad.py` (`907e159`)

## Phase 2: User Story 1 - Instrucción mensual (P1)

- [x] T010 [US1] Motor con precedencia en `radar/decision.py` (`decidir`) (`98aeb93`)
- [x] T011 [US1] Carga del perfil desde secreto o archivo local en `radar/decision.py` (`cargar_perfil`) (`98aeb93`)
- [x] T012 [US1] Comando `radar accion` con ventana y envío único en `radar/cli.py` (`98aeb93`)
- [x] T013 [US1] Paso mensual en `.github/workflows/diario.yml` (`98aeb93`)
- [x] T014 [US1] Pruebas de precedencia, banda estricta y deduplicación en `tests/test_decision.py` (`98aeb93`)

## Phase 3: User Story 2 - SIN SEÑAL (P1)

- [x] T020 [US2] Frescura de todas las series contra su antigüedad máxima (`frescura_ok`) (`98aeb93`)
- [x] T021 [US2] Perfil vencido (más de 180 días) y perfil ausente (`98aeb93`)
- [ ] T022 [US2] Divergencia mindicador/BCCh > 0,3% (**requiere fase 2: BCCh**)
- [ ] T023 [US2] Regla de 5 días hábiles en SIN SEÑAL antes de emitir COMPRAR (**requiere estado persistente**)

## Phase 4: User Story 3 - Contexto público (P2)

- [x] T030 [US3] `contexto_publico()` sin colores ni instrucciones; `/estado` lo usa (`98aeb93`)
- [x] T031 [US3] Prueba: el contexto público no contiene MANTENER, VENDER ni COMPRAR (`98aeb93`)

## Phase 5: Pendientes del concilio

- [ ] T040 VENDER por banda en modo sombra con bitácora inmutable (#29, #30)
- [ ] T041 Revisión legal antes de ofrecer instrucciones a terceros (#31, **decisión del dueño: diferida**)
- [ ] T042 Eliminar `reporte.alerta` y `que_movio` (sin uso desde el cambio al motor de acciones)
- [ ] T043 Validar con el perfil real del dueño: configurar `PERFIL_DUENO` como secreto (**acción del dueño**)
