# Councils · Deliberación de expertos para decisiones del radar

Protocolo **v1 (`v1_verified_dissents_brittleness`)**, el mismo de `sg-engagement-2026/councils/`:
Stage 0 verificación de supuestos con datos · Stage 1 consejeros expertos en paralelo e
independientes · Stage 2 revisión cruzada anónima · Stage 3 síntesis del presidente
(evidence_auditor, puede disentir) · Stage 4 persistencia · Stage 5 disidencias con condición de
reactivación observable · Stage 6 trampa de fragilidad.

```
councils/
  agenda/      # briefs (pregunta + Stage 0 + qué entregar)
  sesiones/    # posiciones anonimizadas e informe del presidente
  decisions/   # JSON completo de cada decisión
  dissents/    # disidencias con reactivation_condition
```

## Decisiones

| Timestamp | Tema | Decisión | Estado |
|---|---|---|---|
| 2026-10-23_220000 | ¿Cómo emite el radar COMPRAR / VENDER / MANTENER? | Instrucciones del plan del usuario (SIN SEÑAL > VENDER por necesidad > MANTENER > COMPRAR cuota completa en canal barato); moduladores de flujo y VENDER por banda en sombra hasta pasar el protocolo de validación | `decided_but_unauthorized` |

Antes de cada concilio nuevo, revisar `dissents/` por si alguna `reactivation_condition` se cumplió.
