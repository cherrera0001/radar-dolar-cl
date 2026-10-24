# Constitución del radar del dólar

## Core Principles

### I. Describir y ordenar, con compuertas

El radar describe siempre si el dólar está barato, normal o caro frente a lo que lo mueve. Además emite
instrucciones de acción (SIN SEÑAL, VENDER, MANTENER, COMPRAR) como instrucciones del plan del dueño, no
como pronósticos. Reglas no negociables:

- La precedencia es SIN SEÑAL > VENDER > MANTENER > COMPRAR. Una acción nunca depende de adivinar la
  dirección del precio.
- Ninguna regla de dirección de precio se publica como señal de mercado. Mientras no gane fuera de
  muestra con el protocolo de `councils/decisions/2026-10-23_220000_*.json`, sigue siendo contexto.
- La modulación por flujos y VENDER por banda corren en modo sombra (bitácora sin efecto en la
  instrucción) hasta pasar el protocolo de validación (#26 a #29).
- Cualquier cambio que endurezca o relaje una compuerta se decide en `councils/` antes de implementarse.

### II. Honestidad medible

Toda cifra publicada lleva su fecha de datos, su número de días, su número aproximado de episodios
independientes y su línea base. Un rango histórico no es una predicción puntual. Si la evidencia es poca,
se dice. Ninguna respuesta presenta el pasado como garantía del futuro.

### III. Causalidad

Ninguna señal usa datos posteriores a la fecha que describe. La decisión del día *d* usa la señal de *d−1*
(`docs/METODOLOGIA.md`, principio 1). Hay pruebas que alteran el futuro y verifican que el pasado no cambie.
Todo cambio que toque la alineación de fechas MUST incluir esa prueba.

### IV. Fuentes validadas en el cuerpo

Cada fuente valida estructura, fechas y rangos de su respuesta, no solo el código HTTP. Un dato fuera de
contrato falla ruidosamente. Un dato con fecha futura se descarta antes de guardarse. Las series se alinean
con antigüedad máxima explícita; no se imputan valores en silencio. Si una fuente está vencida o no puede
conciliarse, la instrucción es SIN SEÑAL, nunca una acción calculada sobre datos viejos.

### V. Lectura pública; perfil personal fuera del repo

El panel, el bot y el repositorio son de lectura pública. Quien consulta no inicia sesión y su identidad no
se guarda. Lo único persistente del bot es el offset de Telegram (`data/bot.json`). El perfil personal
(peso objetivo w\*, colchón, necesidades con fecha y monto, saldos por custodio) NUNCA se guarda en el
repositorio, en `data/` ni en `reports/`. Vive en un secreto de GitHub Actions o en un archivo local ignorado
por git. Un control de CI MUST fallar si aparece un archivo de perfil versionado.

### VI. Destinatarios: instrucciones personales solo al dueño

Las instrucciones con cifras o con VENDER / MANTENER / COMPRAR MUST enviarse únicamente al chat del dueño
(`TELEGRAM_CHAT_ID`). Cualquier otro destinatario recibe contexto genérico rotulado "Contexto (no es señal)",
sin colores ni instrucciones. Una prueba MUST fallar si un mensaje con una instrucción personal tiene como
destino un chat distinto del dueño.

La lectura pública de contexto genérico fue habilitada por decisión del dueño (2026-10-24). La revisión legal
(#31, opinión escrita o consulta CMF) queda pendiente y MUST completarse antes de ofrecer instrucciones de
acción a terceros.

### VII. Sin secretos en código ni en logs

Tokens y credenciales viven en secretos de GitHub Actions o en variables de entorno. Los mensajes de error no
muestran el token. El contenido de los usuarios se envía a Telegram sin formato, para que no se interprete
como Markdown o HTML.

### VIII. Mensajes idempotentes

Cada mensaje tiene una clave (tipo, período y contenido). Un mensaje con la misma clave y el mismo contenido
MUST NOT reenviarse. Un cambio de contenido sí se envía, porque cambió la información. El registro de envíos
vive en `data/envios.json`. Un envío fallido no se registra, para reintentarlo en la siguiente corrida.

### IX. Sin servidor propio y costo acotado

Todo corre en GitHub Actions y en el propio repositorio. Los datos son CSV versionados en git, sin base de
datos. El consumo de minutos debe mantenerse dentro de la cuota gratuita, con margen. Cualquier servicio nuevo
se justifica en el plan de la especificación correspondiente.

## Restricciones de datos y textos

- Los textos al usuario, la documentación y los nombres de dominio están en español, con las convenciones del
  código existente.
- Los datos de mercado son públicos (mindicador.cl, FRED, y BCCh en fase 2). Ninguna fuente de datos personales
  entra al repositorio.

## Flujo de trabajo y versionado

- Las especificaciones se escriben con spec-kit oficial (`/speckit-specify`, `/speckit-plan`, `/speckit-tasks`) en
  `specs/<NNN-nombre>/`.
- Cada cambio se versiona en git con un commit por unidad lógica. Los commits llevan la línea de coautoría
  indicada por la sesión.
- Un cambio que viola un principio se bloquea hasta enmendar esta constitución con un concilio registrado.

## Governance

Esta constitución prevalece sobre cualquier otra práctica del repositorio. Las enmiendas requieren un registro
en `councils/decisions/`, la versión actualizada aquí, y la revisión de las especificaciones afectadas.
La versión sigue el versionado semántico: MAJOR para redefiniciones de principios, MINOR para principios o
secciones nuevos, PATCH para aclaraciones de redacción. Todo cambio en la lógica de acciones MUST citar el
concilio que lo autoriza.

**Version**: 2.0.0 | **Ratified**: 2026-10-24 | **Last Amended**: 2026-10-24
