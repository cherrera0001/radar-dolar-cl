# Resumen de la auditoría · 2026-10-27

Commit base: `057ee1c` (`main`). Registro completo: `REGISTRO_RIESGOS.md`. Bitácora: `BITACORA.md`.
Ninguna rama está mergeada. Todas pasan `pytest -q` (93 base + las pruebas de cada rama) y `ruff check radar tests`.

## Top 10 riesgos por severidad

| # | ID | Severidad | Riesgo | Estado |
|---|---|---|---|---|
| 1 | R-07 | 20 | Instrucciones con imperativos ("Vende", "Compra") frente a la regla de "ningún texto de compre/venda/mantenga" del prompt | Requiere decisión |
| 2 | R-01 | 15 | Aviso de salud de fuentes con `\n` literal en Telegram | Corregido · `audit/R-01-aviso-salud-saltos` |
| 3 | R-02 | 12 | Sin aviso de caída total: el paso de alerta no corre si `radar actualizar` falla | Corregido · `audit/R-02-alerta-con-fallo` |
| 4 | R-06 | 12 | Adelanto de un día en la señal de cobre (backtest y decisión) | Requiere decisión |
| 5 | R-03 | 9 | Sin reintentos; un corte de conexión al leer tumbaba la actualización entera | Corregido · `audit/R-03-reintentos-http` |
| 6 | R-12 | 9 | Workflows sin pruebas | Corregido · dentro de las ramas R-02 y R-04 |
| 7 | R-08 | 8 | Sin conciliación entre mindicador y BCCh | Requiere decisión |
| 8 | R-09 | 8 | Nada avisa si el cron deja de correr | Abierto (recomendación abajo) |
| 9 | R-14 | 8 | Un update con error permanente frenaba la cola del bot | Corregido · `audit/R-14-mensaje-veneno` |
| 10 | R-04 | 6 | Push de datos sin rebase: un push del bot entre medio pierde el commit del día | Corregido · `audit/R-04-push-con-rebase` (apilada sobre R-02) |

## Lo corregido (ramas listas para PR)

| ID | Rama | Commit | Pruebas |
|---|---|---|---|
| R-01 | `audit/R-01-aviso-salud-saltos` | fe5e0ec | `tests/test_cli_alerta.py` |
| R-02 | `audit/R-02-alerta-con-fallo` | 431493d | `tests/test_workflows.py` |
| R-03 | `audit/R-03-reintentos-http` | 5b8d8cf | `tests/test_fuentes_http.py` |
| R-04 | `audit/R-04-push-con-rebase` (sobre R-02) | fe78dad | `tests/test_workflows.py` |
| R-05 | `audit/R-05-escritura-atomica` | b874909 | `tests/test_almacen_atomico.py` |
| R-14 | `audit/R-14-mensaje-veneno` | 47f7df0 | `tests/test_bot_veneno.py` |
| registro | `audit/registro` | fdeadc1 | documentos |

Orden sugerido para mergear: R-01, R-02, R-04 (después de R-02), R-03, R-05, R-14. Ninguno toca la misma línea que otro,
excepto R-02 y R-04 (ambos editan `diario.yml`, en pasos distintos).

## Requiere decisión (no tomada)

1. **R-07 · imperativos al dueño.** Recomiendo (a): mantener "COMPRAR / VENDER / MANTENER" solo en el chat del dueño,
   como permite la constitución (I y VI), y aplicar la prohibición del prompt a todo texto público. Eso exige ajustar
   el prompt de auditoría, no el código.
2. **R-06 · desfase del cobre.** Recomiendo (a): desplazar la señal según el mayor desfase de sus insumos (2 días
   hábiles) en el backtest y en la decisión, y repetir `radar investigar`. Cambia los números publicados, así que
   necesita aprobación.
3. **R-08 · conciliación BCCh.** Activar `bcentral` en `actualizar` con una tolerancia. Hace falta fijar la tolerancia
   (sugerencia: divergencia mayor a 0,5 % en el dólar observado durante 2 días → aviso de salud) y confirmar que
   `BCCH_USER` y `BCCH_PASS` estén en los secretos.
4. **R-11 · SHA de acciones.** Fijar `actions/checkout` y `actions/setup-python` por SHA. Requiere verificar los
   SHA contra el repositorio oficial con acceso a red.

## Recomendaciones de arquitectura serverless

- **Workflow de salud (R-09).** Un workflow aparte, con cron de varias corridas al día (por ejemplo 14:00 y 20:00 UTC,
  días hábiles), que lea `data/estado.json` y avise si `ultima_actualizacion.fecha` no es el último día hábil.
  Así un cron saltado por GitHub se detecta el mismo día. Mismo grupo de `concurrency` que `diario`.
- **Fuente de respaldo.** BCCh sirve de contraste y, si mindicador cae, de respaldo para el dólar observado (con
  credenciales ya disponibles). Ver R-08.
- **Concurrencia.** Se dejó `radar-bot` separado de `radar-datos` a propósito: si el bot entrara al grupo de datos,
  bloquearía `diario` durante 5,5 h. La solución correcta es la de R-04 (rebase con reintento), no unir grupos.
- **Salida parcial de `radar actualizar`.** Hoy un error parcial sale con 0 y solo queda en la salud de fuentes.
  Está bien para el job, pero conviene que el workflow muestre el error en el resumen de Actions (`::warning::`).

## Próximos pasos

1. Revisar y mergear las ramas en el orden sugerido, con la CI en verde (ci.yml corre `ruff` y `pytest`).
2. Decidir R-06, R-07 y R-08. Yo empezaría por R-07, que bloquea el texto público.
3. Completar las dimensiones parciales: A (feriados chilenos y de EE. UU.), C (`investigacion.py` a fondo, costos
   de canal), F (tiempos reales de los jobs en Actions) y G (`pip-audit` con red).
4. Validar `actionlint` en CI: no estaba instalado en este entorno, así que los workflows se verificaron solo con
   las pruebas de texto de `tests/test_workflows.py`.
