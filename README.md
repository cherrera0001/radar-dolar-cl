# Radar Dólar Chile

Señales para **ahorrar en dólares a largo plazo desde Chile**: cada día hábil revisa el dólar
observado, el cobre, el dólar global, las tasas y la aversión al riesgo; los lunes envía un
resumen a Telegram y avisa cuando cambia el semáforo (🟢 COMPRAR · 🟡 NEUTRAL · 🔴 ESPERAR).

Corre sin servidores en **GitHub Actions**; los datos se versionan como CSV en `data/series/`.

> Herramienta personal y educativa. **No es asesoría financiera.** Si se ofreciera a terceros como
> recomendación de inversión, revisar la Ley Fintec (21.521) y el registro de asesores ante la CMF.

## Cómo se usa la señal

Regla para tu cuota mensual de ahorro:

1. **50%** el primer día hábil del mes, siempre.
2. **50%** el primer día del mes en que el radar marque **COMPRAR**; si no ocurre, el último día hábil.

El backtest compara exactamente esta regla contra comprar el 100% el primer día (DCA).

## Estado de la evidencia (v0.1, 2026-10-23)

Backtest 2012-11 a 2026-09, 167 meses, mismo presupuesto mensual:

| Estrategia | CLP por dólar | vs DCA |
|---|---|---|
| DCA (todo el día 1) | $711,28 | — |
| Radar v0.1 | $711,89 | **−0,09%** |

**Hoy las señales no le ganan a DCA.** Ninguna señal por sí sola lo hace de forma significativa
(`radar backtest` muestra el detalle). El radar sí describe bien *dónde* está el dólar (caro o barato
frente a cobre y dólar global), pero mover media cuota dentro del mismo mes no captura valor.
Ver [docs/METODOLOGIA.md](docs/METODOLOGIA.md) y la hoja de ruta.

## Uso local

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
radar actualizar        # descarga series (la primera vez rellena desde 2012, ~3 min)
radar senales           # estado actual con explicación de cada señal
radar backtest          # radar vs DCA y cada señal por separado
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
