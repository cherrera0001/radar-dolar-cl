# Bot y panel público del radar del dólar

Cualquiera puede consultar el bot en Telegram y ver el panel. Todo el contenido describe datos públicos
(mindicador.cl y FRED). **No es asesoría financiera** ni predice con certeza.

## Comandos

| Comando | Qué responde |
|---|---|
| `/ayuda` | Lista de comandos |
| `/estado` | Semáforo de hoy, puntaje y señales, con la explicación de cada una |
| `/porque` | Por qué el semáforo dice eso: las tres señales que más pesan y cuántas van en la misma dirección. Avisa si el dato está atrasado (en días hábiles) |
| `/cambios` | Qué señales se movieron desde la última lectura guardada, con la fecha de esa lectura |
| `/glosario` | Qué significan puntaje, semáforo, señal sin datos, percentil, valor justo, DCA y fecha del dato |
| `/historia` | Qué hizo el dólar 3, 6 y 12 meses después de días con cada estado, frente a cualquier día |
| `/prediccion` | Escenarios históricos desde hoy: mediana y rango del 80%. **Rango, no predicción** |
| `/grafico` | Imagen del último año con el semáforo |
| `/backtest` | Radar frente a DCA en toda la historia |
| `/salud` | Frescura, huecos y fallas de cada fuente |
| `/datos <serie>` | CSV de una serie (`usdclp`, `cobre_lb`, `dxy`, `tpm`, `fed_funds`, `vix`) |

## Cuándo llega la respuesta

El bot escucha mensajes de forma continua: cada corrida de GitHub Actions dura unas 5,5 horas y, al
terminar, dispara la siguiente. Una consulta normalmente se responde en segundos. El cron cada 30 minutos
solo sirve de vigía: si la cadena se corta, la reinicia. Cada corrida atiende hasta 1000 mensajes.

Si Telegram tiene un outage (p. ej. `getUpdates` 502), la corrida no muere de inmediato: espera con
backoff (30 s, 60 s, 120 s…) y reintenta hasta 5 veces seguidas. Solo si el outage se prolonga, la
corrida termina en rojo, el workflow avisa al dueño (un mensaje al día) y encola la siguiente corrida
esperando 4 minutos, para no amplificar la caída en una ráfaga de reintentos.

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
- `radar bot --una-vez` atiende lo pendiente y termina.
- GitHub Actions (`bot.yml`) usa `radar bot --durante 19800 --publicar`: escucha 5,5 horas y guarda el offset en `data/bot.json`.
- Requiere el secreto `TELEGRAM_BOT_TOKEN`.
- Los textos de lectura (`/porque`, `/cambios`, `/glosario`) salen de `radar/lectura.py`, la misma función que usa el tablero.
