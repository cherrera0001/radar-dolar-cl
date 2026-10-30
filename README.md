# Radar Dólar Chile

Describe si el **dólar observado está barato, normal o caro** frente a lo que lo mueve (cobre, dólar global,
tasas y aversión al riesgo), para quien ahorra en dólares a largo plazo desde Chile.

Lo consultas en **Telegram** (`/estado`, `/historia`, `/prediccion`, `/grafico`…) o en el **panel** de
Streamlit. Todo corre en **GitHub Actions**, sin servidor propio; los datos son CSV versionados en
`data/series/`.

> **No es asesoría financiera.** Describe el pasado y no garantiza el futuro. Las instrucciones de acción
> son del plan personal del dueño. Ofrecerlas a terceros requiere revisión legal (Ley Fintec 21.521, CMF),
> pendiente por decisión del dueño.

## Qué recomienda (y por qué)

**Compra tu cuota completa cada mes (DCA).** El semáforo describe si el dólar está barato o caro
frente a lo que lo mueve; no es una orden de compra, porque ninguna regla de *timing* probada le ha
ganado a DCA fuera de muestra:

| Estrategia | Historia 2012–2026 | Fuera de muestra 2020–2026 |
|---|---|---|
| Timing dentro del mes (v0.1) | −0,12% | −0,13% |
| Acumular pesos si el dólar está caro (#10) | — | −0,04% (en diseño parecía +0,19%: sobreajuste) |

Cifras con fechas de mercado alineadas y decisión con la señal del día anterior (#19).
Lo que sí ahorra con certeza es el **canal de compra**: ~2,5% en la pizarra de un banco vs ~0,5%
en canales de bajo spread ([estado del arte](docs/ESTADO_DEL_ARTE.md)).

**Describir y ordenar.** El radar describe el semáforo y, además, emite una instrucción mensual según el plan
del dueño: SIN SEÑAL, VENDER, MANTENER o COMPRAR (decisión del concilio
`councils/decisions/2026-10-23_220000_*.json`). La instrucción depende del perfil, del calendario y de datos
vigentes; no depende de adivinar el precio. Ver [especificación 003](specs/003-motor-acciones/spec.md).

Detalle en [docs/INVESTIGACION.md](docs/INVESTIGACION.md) y [docs/METODOLOGIA.md](docs/METODOLOGIA.md).
Nuevas señales se evalúan con `radar investigar` antes de cambiar esta recomendación.

## Consultar (público)

| Dónde | Cómo |
|---|---|
| **Telegram** | Escribe `/ayuda` al bot. Responde en hasta ~30 minutos. Detalle en [docs/bot.md](docs/bot.md). |
| **Panel** | Streamlit: calibración, radar frente a DCA, estacionalidad, correlación y salud de datos. URL en `DASHBOARD_URL`. |
| **Datos** | `data/series/*.csv`, o `/datos <serie>` en Telegram. |

No hace falta cuenta ni identificarse. El bot no guarda quién escribe.

## Uso local

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev,dashboard]"
radar actualizar        # descarga series (la primera vez rellena desde 2012, ~3 min)
radar senales           # estado actual con explicación de cada señal
radar backtest          # radar vs DCA y cada señal por separado
radar investigar        # walk-forward: parámetros con 2012-2019, resultado en 2020-2026
radar resumen           # texto del resumen semanal (--enviar para Telegram)
radar alerta            # avisos de salud de fuentes (--enviar los manda al dueño)
radar vigia             # avisa si la corrida diaria no dejó registro de hoy
radar accion           # instrucción del mes (días 1 a 5); --enviar la manda al dueño, una vez
radar prueba-telegram   # verifica el bot de alertas
radar bot               # atiende comandos de Telegram en continuo (Ctrl+C para salir)
radar bot --una-vez     # atiende lo pendiente y termina (lo que usa Actions)
streamlit run streamlit_app.py   # panel en http://localhost:8501
pytest -q && ruff check radar tests
```

## Automatización (GitHub Actions)

| Workflow | Cuándo | Qué hace |
|---|---|---|
| `diario.yml` | Lun–vie 12:00 UTC | Actualiza series, avisa de salud de fuentes (con los errores de la corrida y el enlace al run), instrucción mensual al dueño (días 1 a 5), avisa si el job falló, versiona `data/` |
| `semanal.yml` | Lunes 12:30 UTC | Resumen + backtest a Telegram, avisa si falló, versiona `data/` y `reports/` |
| `vigia.yml` | Lun–vie 15:00 y 21:00 UTC | Avisa si el job diario no corrió o quedó viejo (lo único que detecta un cron saltado) |
| `bot.yml` | En cadena continua | Atiende consultas de Telegram (cada corrida dispara la siguiente; el cron cada 30 min solo reinicia la cadena si se corta), avisa si el bot lleva un rato caído, versiona `data/bot.json` |
| `ci.yml` | Push/PR | ruff + pytest |

Cada corrida deja una línea en `data/ejecuciones.jsonl`: comando, fecha, duración, código de salida y
detalles (errores, avisos, consultas atendidas). Es el historial de ejecución del radar: los logs de
Actions caducan a los 90 días y solo se ven con `gh`; la bitácora queda en el repo y se versiona sola.

Cuando un workflow falla, el paso `radar caida` avisa al dueño por Telegram una vez al día por
componente, con el enlace a la corrida. Sin él, un job en rojo solo se ve entrando a Actions.

**Requisito:** Actions debe estar habilitado y con cuota de minutos disponible en la cuenta
(*Settings → Billing & plans*). Si la facturación falla, GitHub no arranca ningún job; el radar deja de
actualizar datos y de responder.

Secretos del repo: `TELEGRAM_BOT_TOKEN` (bot y alertas) y `TELEGRAM_CHAT_ID` (alertas al dueño) son
obligatorios. Pendientes de crear en *Settings → Secrets and variables → Actions* (valores del dueño,
el bot no puede crearlos):

- `BCCH_USER` / `BCCH_PASS`: credenciales de la API BDE del Banco Central (solicitud en
  [si3.bcentral.cl/Siete](https://si3.bcentral.cl/Siete)). Habilitan la conciliación del dólar
  observado contra la serie oficial (fase 2); sin ellas, cada corrida lo registra como error.
- `PERFIL_DUENO`: perfil personal en JSON para la instrucción mensual; sin él la instrucción es
  SIN SEÑAL ("perfil_ausente"). También puede vivir en `perfil.local.json` (ignorado por git).

Variables del repo (opcional): `DASHBOARD_URL`, la URL pública del panel que muestra `/ayuda`.

## Documentación de diseño

- [Especificación 003 · motor de acciones](specs/003-motor-acciones/spec.md), con [plan](specs/003-motor-acciones/plan.md) y [tareas](specs/003-motor-acciones/tasks.md).
- [Constitución](.specify/memory/constitution.md): principios que todo cambio respeta.
- [Especificación 001 · núcleo](specs/001-radar-nucleo/spec.md): qué hace el radar, historias de usuario y criterios.
- [Especificación 002 · bot y panel públicos](specs/002-bot-y-panel-publicos/spec.md), con
  [plan y tareas](specs/002-bot-y-panel-publicos/tasks.md).
- [Concilios](councils/README.md): decisiones de producto y su registro.

## Licencia

Código bajo [MIT](LICENSE). Los datos conservan las condiciones de sus fuentes.

## Fuentes

| Serie | Fuente | Notas |
|---|---|---|
| Dólar observado (`usdclp`) | mindicador.cl | El Banco Central publica el valor de mañana el día hábil anterior |
| Dólar observado (`usdclp`), respaldo | ExchangeRate-API (`er-api.com`) | Solo si mindicador.cl no responde: aproxima el último valor para no congelar la serie. Capa gratuita sin clave; se desactiva con `RADAR_USDCLP_RESPALDO=0` |
| Libra de cobre (`cobre_lb`) | mindicador.cl | USD/lb |
| TPM | mindicador.cl | % |
| Dólar global (`dxy`) | FRED `DTWEXBGS` | Semanal, ~10 días de rezago (tolerancia 14 días) |
| Fed funds | FRED `DFF` | % |
| VIX | FRED `VIXCLS` | |
| Series oficiales BCCh | API BDE (fase 2) | Responde HTTP 200 con `{"Codigo": -5}` ante credenciales inválidas: se valida el cuerpo |

Todas las descargas usan cabeceras de navegador y reintentos con backoff y jitter: mindicador.cl
corta conexiones con cara de bot, y un outage de minutos no debe tumbar la serie del día.

Cada fuente valida **el cuerpo** de la respuesta (estructura, fechas, rangos de cordura), no el
código HTTP: un `200` con un error dentro es la forma más común en que una integración miente.

## Hoja de ruta

1. **Fase 2 — Banco Central (API BDE):** exportaciones de cobre, flujos cambiarios y series oficiales;
   contraste del dólar observado mindicador vs BCCh.
2. **Investigación con validación walk-forward** (#9, hecho): `radar investigar`. La hipótesis de acumular
   pesos cuando el dólar está caro (#10) fue **rechazada** fuera de muestra; ver
   [INVESTIGACION.md](docs/INVESTIGACION.md).
3. **Respuesta inmediata en Telegram:** hoy el bot responde en hasta ~30 minutos (cron en Actions).
   Opción: un Cloudflare Worker gratuito que dispare el workflow al recibir el mensaje.
4. **Pendientes del concilio:** VENDER por banda en modo sombra, regla de 5 días en SIN SEÑAL y
   divergencia BCCh (fase 2). Ver [tareas 003](specs/003-motor-acciones/tasks.md).
