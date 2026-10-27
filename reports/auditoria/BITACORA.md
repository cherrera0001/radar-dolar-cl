# Bitácora de la auditoría

Fechas en America/Santiago. Commit base de la auditoría: `057ee1c` (rama `main`).

## Iteración 0 · 2026-10-27 · reconocimiento

- Flujo mapeado: `radar/fuentes/*` → `almacen.py` → `metricas.py` / `senales.py` / `decision.py` / `backtest.py` →
  `reporte.py` / `grafico.py` / `envios.py` / `telegram.py` / `bot.py` → `streamlit_app.py`.
- Workflows leídos: `bcch.yml` (manual), `bot.yml` (cada 30 min como vigía, corrida de 5,5 h), `ci.yml`,
  `diario.yml` (12:00 UTC, días hábiles), `semanal.yml` (lunes 12:30 UTC). Los cron están en UTC.
- Línea base: `pytest -q` → 93 pasan; `ruff check radar tests` → limpio.
- Hallazgos nuevos: R-01 a R-13 (ver `REGISTRO_RIESGOS.md`).
- Pendiente: decidir R-06, R-07, R-08; las dimensiones A, B, C, E, F, G quedan parciales.

## Iteración 1 · 2026-10-27 · dimensión E (comunicación)

- Hallazgo: R-01 (severidad 15). `radar/cli.py:118` arma el aviso de salud con `"\\n"`.
- Corregido en `audit/R-01-aviso-salud-saltos`.
