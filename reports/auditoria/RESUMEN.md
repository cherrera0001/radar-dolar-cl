# Resumen de la auditoría · 2026-10-27

Commit base: `057ee1c` (`main`). Registro completo: `REGISTRO_RIESGOS.md`. Bitácora: `BITACORA.md`.

## Dónde está todo

- **Rama de integración: `audit/integracion`.** Une todas las correcciones y tiene la suite completa en verde
  (127 pruebas) y `ruff check radar tests` limpio. Es local: no hay push ni merge a `main`.
- Una rama por hallazgo, cada una con su prueba: `audit/R-01-…` a `audit/R-15-…`, más `audit/R-07-…` y `audit/R-13-…`.
  Todas salen de la integración y ya están mergeadas en ella.

## Riesgos y estado

| ID | Severidad | Riesgo | Estado |
|---|---|---|---|
| R-07 | 20 | Órdenes de compra y venta en textos públicos | Resuelto: solo al dueño. Pendiente confirmar con el dueño |
| R-01 | 15 | Aviso de salud con `\n` literal | Corregido |
| R-02 | 12 | Sin aviso si falla toda la actualización | Corregido |
| R-06 | 12 | Señal de cobre con un día de adelanto en la decisión | Corregido (desfase de 2 días). Cifras cambiadas |
| R-03 | 9 | Sin reintentos; un corte de conexión tumbaba la actualización | Corregido |
| R-12 | 9 | Workflows sin pruebas | Corregido |
| R-08 | 8 | Sin conciliación entre mindicador y BCCh | Corregido (requiere secretos BCCH para activarse) |
| R-09 | 8 | Nada avisa si el cron no corre | Corregido: workflow `vigia.yml` |
| R-14 | 8 | Un update con error permanente frenaba la cola del bot | Corregido |
| R-04 | 6 | Push de datos sin rebase | Corregido |
| R-11 | 4 | Acciones fijadas por etiqueta, no por SHA | Corregido: SHA verificados contra GitHub |
| R-05, R-10, R-13, R-15 | 2 a 3 | Escritura no atómica, texto truncado, concurrencia, temporal | Corregidos |

## Cambios de comportamiento que debes conocer

1. **R-06 cambia las cifras publicadas.** Con el desfase de decisión de 2 días, la estrategia elegida en la prueba fuera
   de muestra pasa de −0,041 % a −0,083 % frente a DCA. El backtest completo va de −0,119 % a −0,120 %. La conclusión no
   cambia: ninguna regla le gana a DCA. `docs/INVESTIGACION.md` ya se actualizó.
2. **R-08 necesita los secretos `BCCH_USER` y `BCCH_PASS`** en el repositorio para activar la conciliación. Sin ellos, la
   actualización registra en errores que la conciliación no está disponible; no se inventa nada.
3. **R-09 es un workflow nuevo** (`vigia.yml`, días hábiles a las 15 y 21 UTC). Avisa si la última corrida registrada no
   es del último día hábil. Como el resto de los jobs, escribe `data/envios.json` y comparte el grupo `radar-datos`.

## Decisión tomada, pendiente de tu confirmación

- **R-07.** Adopté la opción (a): COMPRAR, VENDER y MANTENER solo se envían al chat del dueño, como permite la constitución
  (I y VI). Los textos públicos no tienen imperativos y una prueba lo garantiza. Esto contradice la regla de "ningún texto
  al usuario" del prompt de auditoría. Si prefieres la opción (b), hay que reescribir `decision.py`.

## Lo que sigue abierto

- **Sin verificar en este entorno:** los workflows nuevos y los cambios de `diario.yml` solo se validaron con pruebas de
  texto. `actionlint` no está instalado y no se pudo ejecutar un run real de Actions.
- **`pip-audit` no se ejecutó** (sin acceso a la base de vulnerabilidades desde aquí).
- **Dimensión C parcial:** `investigacion.py` no se revisó a fondo (sobreajuste de umbrales, costos de canal).
- **Dimensión F parcial:** no hay tiempos reales de los jobs de Actions.
- **R-13 y R-08** dependen de la configuración de Actions y de los secretos, que no se pueden comprobar desde el repo.

## Recomendaciones de arquitectura serverless (ya en curso o pendientes)

- Vigía de corridas (R-09): hecho. Revisar la primera semana de avisos para ajustar las horas.
- Conciliación con BCCh (R-08): hecha. Si la divergencia se vuelve frecuente, cambiar la tolerancia de 0,5 % exige un concilio.
- Concurrencia: el bot queda en su propio grupo (`radar-bot`) a propósito. Unirlo a `radar-datos` bloquearía el job diario
  durante 5,5 horas. Los pushes se coordinan con rebase (R-04).
