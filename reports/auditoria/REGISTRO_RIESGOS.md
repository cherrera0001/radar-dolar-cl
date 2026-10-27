# Registro de riesgos · auditoría autónoma

Escala: Impacto (1–5) × Probabilidad (1–5) = Severidad. El impacto es 5 cuando el usuario recibe un número o una
fecha incorrectos, o una señal basada en datos rancios o incompletos. Las evidencias son `archivo:línea` del
commit base `057ee1c` (rama `main`).

Estados: **Abierto** · **Corregido** (rama con tests en verde) · **Requiere decisión** (opciones en la columna
de descripción) · **Hipótesis** (sin prueba reproducible todavía).

| ID | Área | Descripción | Evidencia (archivo:línea) | Impacto | Probabilidad | Severidad | Estado |
|---|---|---|---|---|---|---|---|
| R-01 | E · Comunicación | El aviso de salud de fuentes se arma con `"\\n"` (barra invertida + n), así que Telegram recibe `\n` literal en vez de saltos de línea. | `radar/cli.py:118` | 3 | 5 | 15 | Corregido · rama `audit/R-01-aviso-salud-saltos` |
| R-02 | F · Operación | Si `radar actualizar` falla en todas las fuentes sale con código 1 y el paso "Avisos de salud" de `diario.yml` no tiene `if: always()`, así que el aviso de caída total nunca se envía. | `.github/workflows/diario.yml:33-37`, `radar/cli.py:54` | 4 | 3 | 12 | Corregido · rama `audit/R-02-alerta-con-fallo` |
| R-03 | A · Fuentes | `http_get` no reintenta: un fallo de red transitorio cuenta como día fallido para la salud de la fuente (3 días hábiles seguidos disparan aviso). | `radar/fuentes/base.py:219-226` | 3 | 3 | 9 | Corregido · rama `audit/R-03-reintentos-http` |
| R-04 | F · Concurrencia | `diario`, `semanal` y `bcch` hacen `git push` sin reintento con rebase. `bot.yml` sí lo hace, y corre con otro grupo de `concurrency`, así que un push de `bot` entre medio hace fallar el push de datos (el commit del día se pierde hasta la corrida siguiente). | `.github/workflows/diario.yml:52-53`, `semanal.yml:44-45`, `bcch.yml:50-51`, `bot.yml:51` | 2 | 3 | 6 | Corregido · rama `audit/R-04-push-con-rebase` |
| R-05 | B · Almacenamiento | `almacen.guardar` escribe directo sobre el CSV. Si el job muere a mitad de la escritura, el CSV queda truncado y la siguiente lectura ve una historia incompleta. | `radar/almacen.py:80-85` | 3 | 1 | 3 | Corregido · rama `audit/R-05-escritura-atomica` |
| R-06 | C · Causalidad | La alineación a día de mercado de `cobre_lb` (−2 días hábiles) hace que la fila del día t−1 use un dato etiquetado t+1. El backtest y la decisión desplazan la señal solo 1 día (`compuesto.shift(1)`). Si la fecha de etiqueta es la fecha en que el dato está disponible, hay un adelanto de un día. Es una decisión metodológica: la alineación se midió con correlaciones y no con fechas de disponibilidad. Opciones: (a) desplazar la señal según el mayor desfase de sus insumos (2 días) y repetir `radar investigar`; (b) documentar que el desfase es por fecha de vigencia y no de disponibilidad. **Recomendación: (a).** | `radar/almacen.py:35-44`, `radar/backtest.py:45`, `docs/METODOLOGIA.md:6`, `docs/HISTORICO.md:8-12` | 4 | 3 | 12 | Requiere decisión |
| R-07 | E · Texto al dueño | Las instrucciones usan imperativos ("Vende solo ese monto…", "Compra tu cuota completa…"). La constitución (I, VI) los permite solo para el chat del dueño. El prompt de auditoría prohíbe "compre/venda/mantenga" en cualquier texto al usuario. Conflicto entre dos reglas. Opciones: (a) mantener imperativos solo para el dueño y dejar la regla del prompt para contexto público; (b) pasar a formas descriptivas ("Venta de necesidad: US$ X en tramos…") también para el dueño. **Recomendación: (a), y el prompt de auditoría se ajusta.** | `radar/decision.py:229-236`, `.specify/memory/constitution.md` (I, VI) | 4 | 5 | 20 | Requiere decisión |
| R-08 | A · Fuentes | Sin conciliación cruzada: el dólar de mindicador no se contrasta con BCCh (fase 2 inactiva en `actualizar`). Una divergencia silenciosa de una fuente no se detecta. | `radar/actualizar.py:147-169`, `radar/fuentes/bcentral.py:252-254`, `radar/cli.py:180-194` | 4 | 2 | 8 | Requiere decisión (activar BCCh en `actualizar` con tolerancia definida; requiere credenciales y decidir la tolerancia) |
| R-09 | F · Observabilidad | Nada avisa si el cron no corre (GitHub retrasa o salta crones). Un `diario` que no corre durante días deja el tablero con datos viejos sin aviso. El vigía solo existe para `bot`. | `.github/workflows/diario.yml`, `.github/workflows/semanal.yml` | 4 | 2 | 8 | Abierto (recomendación en RESUMEN: workflow de salud que alerte por `data/estado.json` vencido) |
| R-10 | E · Telegram | `telegram.mensaje` corta el texto a 4000 caracteres sin aviso; un resumen largo pierde en silencio el pie y el aviso de fuente. | `radar/telegram.py:14`, `radar/telegram.py:406` | 2 | 1 | 2 | Abierto (bajo) |
| R-11 | G · Supply chain | Las acciones están fijadas por etiqueta de versión (`@v4`, `@v5`), no por SHA. Fijar SHA requiere verificarlos contra el repositorio oficial y no se pudo hacer offline. | `.github/workflows/*.yml` (`actions/checkout@v4`, `actions/setup-python@v5`) | 2 | 2 | 4 | Requiere decisión (fijar SHA con verificación en línea) |
| R-12 | H · Pruebas | No hay pruebas de los workflows: un cambio en `if:`, en `permissions:` o en el orden de pasos no falla en CI. | `tests/` (ausente), `.github/workflows/ci.yml:24-25` | 3 | 3 | 9 | Corregido en las ramas R-02 y R-04 (`tests/test_workflows.py`) |
| R-13 | B · Escrituras concurrentes | `data/envios.json` y `data/estado.json` se leen y escriben sin bloqueo; sólo la concurrencia de Actions los protege. Riesgo bajo mientras el grupo `radar-datos` cubra `diario`, `semanal`. | `radar/envios.py:336-346`, `radar/reporte.py:191-193` | 2 | 1 | 2 | Abierto (bajo) |

## Dimensiones revisadas

| Dimensión | Estado | Nota |
|---|---|---|
| A. Fuentes de datos | Parcial | R-03, R-08. Falta revisar feriados chilenos y de EE. UU. y la divergencia entre fuentes. |
| B. Integridad y almacenamiento | Parcial | R-05, R-13. Duplicados y orden se cubren en `almacen.guardar`; faltan pruebas de huecos. |
| C. Estadística y modelos | Parcial | R-06. No se revisaron sesgos del `valor_justo` ni costos de canal (`docs/estado-del-arte/03-costos-canales.md`). |
| D. Señales y decisión | Revisada | Precedencia y frescura correctas (`decision.py`). Sin histéresis: anotado en R-07 como decisión, no como defecto. |
| E. Comunicación | Parcial | R-01, R-07, R-10. Falta revisar `bot.py`. |
| F. Operación serverless | Parcial | R-02, R-04, R-09, R-11. |
| G. Seguridad | Parcial | Token no aparece en errores (`telegram.py:391`). Falta `pip-audit` (no ejecutado: sin red). R-11. |
| H. Pruebas | Parcial | R-12. Se agregan pruebas de workflows y de alerta. |
