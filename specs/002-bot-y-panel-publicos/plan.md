# Plan 002: bot y panel públicos

## Plan

**Enfoque:** el bot no tiene servidor. GitHub Actions ejecuta `radar bot --una-vez` cada 30 minutos, lee
los mensajes pendientes con `getUpdates`, responde y guarda el offset. El panel es una app de Streamlit
que lee `data/series/` desde el repo.

**Módulos:**
- `radar/telegram.py`: cliente de la API. Envío de texto, documento y foto; lectura con offset.
- `radar/bot.py`: comandos, límites, offset y ciclo de atención.
- `radar/grafico.py`: PNG del último año (matplotlib, importación diferida).
- `radar/metricas.py` y `streamlit_app.py`: cinco métricas del panel.
- `.github/workflows/bot.yml`: cron de 30 minutos y versionado del offset.

**Riesgos:**
- *Facturación de Actions.* Hoy bloquea todos los jobs. Es el riesgo más alto y no está en el código.
- *Abuso.* Mitigado con límite por chat en memoria y tope por corrida. No es un límite duro entre
  corridas: un atacante con muchos chats puede consumir la cuota del tope por corrida.
- *Cambio de API de mindicador o FRED.* La validación del cuerpo falla ruidosamente.

**Estado de verificación:**
- Pruebas unitarias: 68/68 (`pytest`).
- Lint: `ruff check` limpio.
- Comandos contra datos reales: verificados localmente.
- Panel: `AppTest` sin excepciones.
- Workflow `bot.yml` en Actions: **no verificado**, bloqueado por facturación.
