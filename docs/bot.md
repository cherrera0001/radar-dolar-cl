# Bot y panel público del radar del dólar

Cualquiera puede consultar el bot en Telegram y ver el panel. Todo el contenido describe datos públicos
(mindicador.cl y FRED). **No es asesoría financiera** ni predice con certeza.

## Comandos

| Comando | Qué responde |
|---|---|
| `/ayuda` | Lista de comandos |
| `/estado` | Semáforo de hoy, puntaje y señales, con la explicación de cada una |
| `/historia` | Qué hizo el dólar 3, 6 y 12 meses después de días con cada estado, frente a cualquier día |
| `/prediccion` | Escenarios históricos desde hoy: mediana y rango del 80%. **Rango, no predicción** |
| `/grafico` | Imagen del último año con el semáforo |
| `/backtest` | Radar frente a DCA en toda la historia |
| `/salud` | Frescura, huecos y fallas de cada fuente |
| `/datos <serie>` | CSV de una serie (`usdclp`, `cobre_lb`, `dxy`, `tpm`, `fed_funds`, `vix`) |

## Cuándo llega la respuesta

El bot revisa mensajes cada 30 minutos (GitHub Actions). Una consulta se responde en la siguiente
revisión: hasta unos 30 minutos después. Cada corrida atiende hasta 100 mensajes.

## Límites

- Hasta **5 consultas cada 10 minutos por chat**. Al pasar el límite, el bot avisa una vez.
- El bot no responde a otros bots ni a mensajes sin texto.

## Privacidad

- El bot **no guarda quién escribe**. Lo único persistente es el número de mensaje que sigue (`data/bot.json`).
- Los límites por chat viven solo en memoria durante la corrida.
- Las alertas automáticas de cambio de semáforo van solo al dueño del radar.

## Panel público

El panel de Streamlit (`streamlit_app.py`) muestra calibración, radar frente a DCA, estacionalidad,
correlación y salud de datos. Para publicarlo en Streamlit Community Cloud:

1. Entrar a `share.streamlit.io` y elegir **New app**.
2. Repo `cherrera0001/radar-dolar-cl`, rama `main`, archivo `streamlit_app.py`.
3. En **Sharing**, elegir **Public**.
4. Copiar la URL en la variable de repo `DASHBOARD_URL` (Settings → Variables → Actions) para que `/ayuda` la muestre.

## Cómo se ejecuta

- `radar bot` atiende en forma continua (uso local).
- `radar bot --una-vez` atiende lo pendiente y termina (lo que usa GitHub Actions).
- Requiere el secreto `TELEGRAM_BOT_TOKEN`.
