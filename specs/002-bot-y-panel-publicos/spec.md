# Especificación 002: Bot y panel de lectura pública

**Estado:** implementado en código (`d04b7d9`, `e3d114b`). **Bloqueado en ejecución:** Actions no arranca
jobs por facturación (ver `plan.md`). Pendiente de verificación en vivo.
**Depende de:** [001 · núcleo](../001-radar-nucleo/spec.md).

## Problema

Quien quiere entender el semáforo no tiene por qué instalar Python ni leer el repo. Necesita consultar
desde Telegram o desde un panel, con cifras y su explicación.

## Historias de usuario

**US1 · Consultar por Telegram (P1).** Como lector, escribo un comando y recibo una respuesta con datos
y su explicación, sin registrarme.
- *Dado* `/estado`, *entonces* recibo el semáforo con sus señales.
- *Dado* `/prediccion`, *entonces* recibo un rango histórico con su probabilidad de subida, nunca un
  número puntual.
- *Dado* un comando desconocido, *entonces* recibo la sugerencia de `/ayuda`.
- *Dado* un error interno, *entonces* recibo "No pude calcular eso ahora", sin detalles técnicos.

**US2 · Descargar datos (P2).** Como lector, pido `/datos usdclp` y recibo el CSV.
- *Dado* una serie fuera de la lista, *entonces* recibo las opciones válidas, sin leer ningún archivo.

**US3 · Gráfico (P2).** Como lector, pido `/grafico` y recibo una imagen del último año con el semáforo.

**US4 · Límites justos (P1).** Como dueño, quiero que nadie sature el bot ni consuma la cuota de Actions.
- *Dado* más de 5 consultas de un mismo chat en 10 minutos, *entonces* el bot avisa una vez y deja de
  responder hasta que pase la ventana.
- *Dado* una corrida con 100 mensajes atendidos, *entonces* el resto queda para la siguiente.

**US5 · Panel público (P2).** Como lector, abro un panel y exploro calibración, radar frente a DCA,
estacionalidad, correlación y salud de datos.

## Requisitos funcionales

- **FR-101** Ningún comando exige identificar al usuario. No se guarda el chat ni el nombre de quien escribe.
- **FR-102** Lo único persistente del bot es el offset en `data/bot.json`.
- **FR-103** Mensajes de bots y sin texto se ignoran.
- **FR-104** El contenido de los usuarios se envía sin formato.
- **FR-105** Límite por chat: 5 consultas en 10 minutos, solo en memoria.
- **FR-106** Límite por corrida: 100 mensajes.
- **FR-107** El workflow corre cada 30 minutos y versiona el offset solo si cambió.
- **FR-108** `/ayuda` muestra la URL del panel solo si `DASHBOARD_URL` está definida.

## Criterios de éxito

- **SC-101** Cada comando responde sin excepciones con los datos actuales (verificado localmente).
- **SC-102** Una consulta se responde en la siguiente corrida: latencia máxima ~30 minutos.
- **SC-103** El consumo mensual de minutos de Actions (bot + diario) se mantiene dentro de 2.000 minutos
  con margen. Estimado: ~1.500 min/mes.
- **SC-104** El panel carga sin excepciones desde la raíz del repo (verificado con `AppTest`).

## Aclaraciones pendientes

- **[NECESITA ACLARACIÓN] Latencia.** ¿30 minutos bastan? Si no, la opción es un Cloudflare Worker que dispare
  el workflow al recibir el mensaje (requiere cuenta y token de GitHub).
- **[NECESITA ACLARACIÓN] Repo público.** Para que el código sea leíble, el repo tendría que ser público.
  El bot y el panel funcionan sin eso.
