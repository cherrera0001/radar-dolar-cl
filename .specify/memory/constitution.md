# Constitución del radar del dólar

Principios que todo cambio debe respetar. Si una decisión los contradice, se registra en
`councils/decisions/` antes de implementarse, no después.

## I. Describir antes que ordenar

El radar describe si el dólar está barato o caro frente a lo que lo mueve. No emite órdenes de compra
o venta mientras ninguna regla de timing le gane a DCA fuera de muestra (`docs/INVESTIGACION.md`).
Cualquier cambio que convierta una descripción en recomendación requiere evidencia de backtest
walk-forward y una decisión registrada.

## II. Honestidad medible

Toda cifra publicada lleva su fecha de datos, su número de días, su número aproximado de episodios
independientes y su línea base. Un rango histórico no es una predicción puntual. Si la evidencia es
poca, se dice. Ninguna respuesta presenta un pasado como garantía del futuro.

## III. Causalidad

Ninguna señal usa datos posteriores a la fecha que describe. La decisión del día *d* usa la señal de
*d−1* (`docs/METODOLOGIA.md`, principio 1). Hay pruebas que alteran el futuro y verifican que el
pasado no cambie. Los cambios que toquen la alineación de fechas requieren esa prueba.

## IV. Fuentes validadas en el cuerpo

Cada fuente valida la estructura, las fechas y los rangos de su respuesta, no solo el código HTTP.
Un dato fuera de contrato falla ruidosamente. Un dato futuro se descarta, nunca se guarda. Las series
se alinean con antigüedad máxima explícita; no se imputan valores en silencio.

## V. Lectura pública, sin datos personales

El panel y el bot son de acceso libre. Quien consulta no inicia sesión y su identidad no se guarda.
Lo único persistente del bot es el offset de Telegram (`data/bot.json`). Las alertas automáticas de
cambio de semáforo van solo al chat del dueño. No se guardan posiciones, montos ni patrimonio
personal en el repositorio.

## VI. Sin secretos en el código ni en los logs

Tokens y credenciales viven en secretos de GitHub Actions o en variables de entorno. Los mensajes de
error no muestran el token. El contenido de los usuarios se envía a Telegram sin formato, para que no
se interprete como Markdown o HTML.

## VII. Sin servidor propio y con costo acotado

Todo corre en GitHub Actions y en el propio repositorio. Los datos son CSV versionados en git, sin
base de datos. El consumo de minutos debe mantenerse dentro de la cuota gratuita, con margen.
Cualquier integración que requiera un servicio nuevo se justifica en el plan.

## VIII. Textos en español

Los mensajes al usuario, la documentación y los nombres de dominio están en español, con las mismas
convenciones del código existente.

## IX. Cambios con evidencia

Una señal nueva se evalúa con `radar investigar` antes de cambiar la recomendación publicada.
El backtest se reporta en cada resumen, incluso cuando el resultado es desfavorable.

## Gobernanza

- Las decisiones de producto que afectan lo que el radar dice o recomienda se registran en
  `councils/decisions/` con el protocolo de `councils/README.md`.
- Las especificaciones viven en `specs/<NNN-nombre>/` con `spec.md`, `plan.md` y `tasks.md`.
- Un cambio que no cumple un principio se bloquea hasta que la constitución se enmiende explícitamente.
