# Implementation Plan: Motor de acciones v1

**Branch**: `main` | **Date**: 2026-10-24 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/003-motor-acciones/spec.md`

## Summary

Motor de instrucciones con precedencia SIN SEÑAL > VENDER > MANTENER > COMPRAR, según la decisión del concilio
2026-10-23_220000. Envío solo al dueño, una vez por mes y por contenido. Contexto público sin colores ni
instrucciones.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: numpy, pandas (existentes); matplotlib (existente, gráfico); ninguna nueva

**Storage**: `data/envios.json` (huellas de envío); perfil fuera del repo (secreto `PERFIL_DUENO` o `perfil.local.json`)

**Testing**: pytest; `tests/test_decision.py`, `tests/test_privacidad.py`, `tests/test_bot.py`

**Target Platform**: GitHub Actions (ubuntu-latest) y uso local en WSL

**Project Type**: CLI + bot de Telegram (`radar`)

**Performance Goals**: el motor corre en menos de 1 s con la historia completa

**Constraints**: sin servidor propio; sin datos personales en el repo; minutos de Actions dentro de la cuota

**Scale/Scope**: un perfil (dueño); lectores públicos solo con contexto

## Constitution Check

- I. Describir y ordenar, con compuertas: PASA. Precedencia del concilio; COMPRAR solo días 1 a 5; VENDER por banda en sombra (pendiente de implementar la bitácora).
- V. Perfil fuera del repo: PASA. Lectura desde secreto o archivo ignorado; `test_privacidad` vigila `data/` y `reports/`.
- VI. Destinatarios: PASA. `radar accion` envía con `telegram.enviar`, que va solo a `TELEGRAM_CHAT_ID`.
- VIII. Idempotencia: PASA. `envios.enviar_una_vez` con clave por mes y huella de la instrucción.
- IX. Costo acotado: PASA. Una corrida diaria más un paso; sin servicios nuevos.

## Project Structure

### Documentation

```text
specs/003-motor-acciones/
├── spec.md
├── plan.md
└── tasks.md
```

### Source Code

```text
radar/
├── decision.py      # Perfil, Instruccion, decidir(), frescura_ok(), texto()
├── envios.py        # registro de envíos (huella, reintento)
├── reporte.py       # contexto_publico() (sin colores ni instrucciones)
└── cli.py           # cmd_accion, cmd_alerta (solo salud)
tests/
├── test_decision.py
└── test_privacidad.py
```

**Structure Decision**: módulos nuevos en `radar/`; sin subpaquetes, igual que el resto del proyecto.

## Complexity Tracking

| Violación | Por qué es necesaria | Alternativa más simple descartada |
|---|---|---|
| Dos formatos de salida (dueño y público) | El concilio exige contexto genérico para lectores | Un solo formato con instrucciones: rechazado por la trampa de fragilidad del concilio |
