# Radar Dólar Chile

Señales para **ahorrar en dólares a largo plazo desde Chile**: cada día hábil revisa el dólar
observado, el cobre, el dólar global, las tasas y la aversión al riesgo; los lunes envía un
resumen a Telegram y avisa cuando cambia el semáforo (🟢 BARATO · 🟡 NORMAL · 🔴 CARO).

Corre sin servidores en **GitHub Actions**; los datos se versionan como CSV en `data/series/`.

> Herramienta personal y educativa. **No es asesoría financiera.** Si se ofreciera a terceros como
> recomendación de inversión, revisar la Ley Fintec (21.521) y el registro de asesores ante la CMF.

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

Detalle en [docs/INVESTIGACION.md](docs/INVESTIGACION.md) y [docs/METODOLOGIA.md](docs/METODOLOGIA.md).
Nuevas señales (p. ej. flujos del Banco Central) se evalúan con `radar investigar` antes de cambiar
esta recomendación.

## Uso local

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
radar actualizar        # descarga series (la primera vez rellena desde 2012, ~3 min)
radar senales           # estado actual con explicación de cada señal
radar backtest          # radar vs DCA y cada señal por separado
radar investigar        # walk-forward: parámetros con 2012-2019, resultado en 2020-2026
radar resumen           # texto del resumen semanal (--enviar para Telegram)
radar alerta            # aviso solo si cambió el semáforo (--enviar)
radar prueba-telegram   # verifica el bot
pytest -q && ruff check radar tests
```

## Automatización (GitHub Actions)

| Workflow | Cuándo | Qué hace |
|---|---|---|
| `diario.yml` | Lun–vie 12:00 UTC | Actualiza series, avisa si cambia el semáforo, versiona `data/` |
| `semanal.yml` | Lunes 12:30 UTC | Resumen + backtest a Telegram, versiona `data/` y `reports/` |
| `ci.yml` | Push/PR | ruff + pytest |

Secretos del repo: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` y, en la fase 2, `BCCH_USER` / `BCCH_PASS`.

## Fuentes

| Serie | Fuente | Notas |
|---|---|---|
| Dólar observado (`usdclp`) | mindicador.cl | El Banco Central publica el valor de mañana el día hábil anterior |
| Libra de cobre (`cobre_lb`) | mindicador.cl | USD/lb |
| TPM | mindicador.cl | % |
| Dólar global (`dxy`) | FRED `DTWEXBGS` | Semanal, ~10 días de rezago (tolerancia 14 días) |
| Fed funds | FRED `DFF` | % |
| VIX | FRED `VIXCLS` | |
| Series oficiales BCCh | API BDE (fase 2) | Responde HTTP 200 con `{"Codigo": -5}` ante credenciales inválidas: se valida el cuerpo |

Cada fuente valida **el cuerpo** de la respuesta (estructura, fechas, rangos de cordura), no el
código HTTP: un `200` con un error dentro es la forma más común en que una integración miente.
