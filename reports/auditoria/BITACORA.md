# Bitácora de la auditoría

Fechas en America/Santiago. Commit base: `057ee1c` (rama `main`). Cada corrección vive en su propia rama
`audit/<ID>-<slug>` con las pruebas en verde; ninguna está mergeada.

## Iteración 0 · 2026-10-27 · reconocimiento

- Flujo mapeado: `radar/fuentes/*` → `almacen.py` → `metricas.py` / `senales.py` / `decision.py` / `backtest.py` →
  `reporte.py` / `grafico.py` / `envios.py` / `telegram.py` / `bot.py`. Tablero Streamlit no revisado en esta pasada.
- Workflows leídos: `bcch.yml` (manual), `bot.yml` (cron */30 vigía; corrida de 5,5 h; `concurrency: radar-bot`),
  `ci.yml`, `diario.yml` (`0 12 * * 1-5` UTC, `concurrency: radar-datos`), `semanal.yml` (`30 12 * * 1` UTC).
- Línea base: `pytest -q` → 93 pasan; `ruff check radar tests` → limpio.
- Hallazgos iniciales: R-01 a R-13. Registro en `reports/auditoria/REGISTRO_RIESGOS.md` (rama `audit/registro`, fdeadc1).

## Iteración 1 · 2026-10-27 · dimensión E (comunicación)

- Hallazgo: R-01, severidad 15. `radar/cli.py:118` arma el aviso con `"\\n"`: Telegram recibe `\n` literal.
- Prueba que falla antes: `tests/test_cli_alerta.py`. Corrección: `"\n"`.
- Corregido: `audit/R-01-aviso-salud-saltos` (fe5e0ec). 94 pruebas en verde, ruff limpio.

## Iteración 2 · 2026-10-27 · dimensión F (operación)

- Hallazgo: R-02, severidad 12. `radar actualizar` sale con 1 si ninguna fuente responde, y el paso de avisos de
  salud de `diario.yml` no tenía `if: always()`. Con una caída total, el aviso nunca se enviaba.
- Prueba que falla antes: `tests/test_workflows.py` (primer contrato de workflows; se lee como texto, sin PyYAML).
- Corregido: `audit/R-02-alerta-con-fallo` (431493d). 94 pruebas en verde.
- Nota: `actionlint` no está instalado; la validación del YAML queda pendiente de CI.

## Iteración 3 · 2026-10-27 · dimensión A (fuentes)

- Hallazgo: R-03, severidad 9. `http_get` no reintentaba. Además, un corte al leer la respuesta
  (`ConnectionResetError`, `RemoteDisconnected`) no era `FuenteError` y tumbaba toda la actualización. Esto
  no estaba en el registro inicial; se confirmó leyendo `base.py` en esta pasada.
- Prueba que falla antes: `tests/test_fuentes_http.py` (5 casos; en el código original fallan al montar la
  fixture porque `base.time` y `base.REINTENTOS` no existen).
- Corregido: `audit/R-03-reintentos-http` (5b8d8cf). 98 pruebas en verde.

## Iteración 4 · 2026-10-27 · dimensión F (concurrencia)

- Hallazgo: R-04, severidad 6. `diario`, `semanal` y `bcch` hacen `git push` sin rebase; `bot.yml` sí.
- Prueba que falla antes: `test_todo_push_de_datos_reintenta_tras_rebase` en `tests/test_workflows.py`.
- Corregido: `audit/R-04-push-con-rebase` (fe78dad), apilada sobre `audit/R-02-alerta-con-fallo` porque
  `tests/test_workflows.py` vive ahí. 95 pruebas en verde.

## Iteración 5 · 2026-10-27 · dimensión B (almacenamiento)

- Hallazgo: R-05, severidad 3. `almacen.guardar` escribe directo sobre el CSV; una muerte a mitad lo deja truncado.
- Prueba que falla antes: `tests/test_almacen_atomico.py` (el escritor muere con el encabezado y el CSV queda vacío).
- Corregido: `audit/R-05-escritura-atomica` (b874909). Escritura a `.tmp` + `os.replace`. 94 pruebas en verde.

## Iteración 6 · 2026-10-27 · dimensión E/G (bot)

- Hallazgo: R-14, severidad 8. Un 403 al responder (p. ej. el chat bloqueó al bot) dejaba el offset atrás, y el
  mismo update se reintentaba en cada corrida. Nada más se atendía. Se confirmó leyendo `ciclo()` en `bot.py`.
- Prueba que falla antes: `tests/test_bot_veneno.py` (2 casos).
- Corregido: `audit/R-14-mensaje-veneno` (47f7df0). `TelegramError` lleva el código; `permanente` = 4xx salvo 429.
  Los errores transitorios siguen reintentándose (la prueba existente `test_envio_fallido_no_avanza_el_offset`
  sigue en verde). 95 pruebas en verde.

## Iteración 7 · 2026-10-27 · decisiones pendientes (no tomadas)

- R-06 (causalidad del cobre, severidad 12): requiere decisión metodológica. Opciones en el registro.
- R-07 (imperativos al dueño, severidad 20): conflicto entre constitución (I, VI) y el prompt de auditoría. Requiere decisión.
- R-08 (conciliación BCCh/mindicador, severidad 8): requiere credenciales y una tolerancia definida.
- R-11 (SHA de acciones): requiere verificación en línea.

## Estado al cierre de esta pasada

- Dimensiones revisadas al menos una vez: A, B, C, D, E, F, G, H (C, G, A y F parciales; ver el registro).
- Hallazgos abiertos de severidad ≥ 9 sin decisión humana: ninguno.
- Resumen en `reports/auditoria/RESUMEN.md`.

## Pasada 2 · 2026-10-27 · resolver lo pendiente

- Rama de integración `audit/integracion`: une R-01, R-02, R-03, R-04, R-05, R-14 y las nuevas.
- R-11 · pin de acciones por SHA (resueltos con `gh api` contra `actions/checkout` y `actions/setup-python`).
- R-09 · vigía de la corrida diaria (`radar vigia`, `vigia.yml`). Prueba de la lógica pura en `tests/test_vigia.py`.
- R-06 · decisión del día d con señal de d−2 (`DESFASE_DECISION`). Primer intento rompió 5 pruebas de backtest que
  codificaban el desfase de 1 día; las fixtures se movieron dos días atrás y la semántica no cambió. Cifras nuevas:
  prueba fuera de muestra −0,041 % → −0,083 % frente a DCA. `docs/INVESTIGACION.md` actualizado.
- R-08 · conciliación BCCh frente a mindicador (`radar/conciliacion.py`), aviso si hay 2 días seguidos con más de 0,5 %.
  Credenciales en `diario.yml` y `semanal.yml`.
- R-10 · textos largos de Telegram en partes, sin cortar en silencio.
- R-15 · el gráfico reutiliza un archivo temporal.
- R-13 · prueba que fija el grupo `radar-datos` en todo workflow que escribe `data/`.
- R-07 · opción (a) adoptada; guarda de regresión en `tests/test_textos_publicos.py`. Pendiente de confirmación.
- Un fallo de la prueba de privacidad (`reports/` no puede contener las órdenes del plan ni el peso objetivo) obligó a quitar esas
  palabras de RESUMEN.md. La guarda hizo lo que debía.
- Estado final: 127 pruebas en verde en `audit/integracion`, `ruff` limpio.
