# Chile: qué mueve el USD/CLP y qué datos públicos sirven para seguirlo

> Investigación del 2026-10-23 (issue #13). Lo que no pudo verificarse en una fuente está
> marcado NO VERIFICADO. Los archivos de códigos del SIID (BCCh) usados para verificar los
> códigos de series están en `research/bcch-codigos/`.

**En resumen:** según el BCCh, el peso responde sobre todo al cobre, al dólar global y al
diferencial de tasas, y en algunos episodios a factores locales (2019). De los flujos, el que
tiene mejor evidencia y datos es la posición en derivados de no residentes y de fondos de
pensiones, publicada **a diario** en la BDE con códigos verificados. Quedan sin verificar los
códigos de cobre y de balanza de pagos, la cartera FX de la Superintendencia de Pensiones y las
ventas recientes de dólares de Hacienda.

## 1. Determinantes del CLP según el BCCh

- **Cobre y política macro.** DT 640 (De Gregorio y Labbé, 2011): la economía se volvió más resiliente a los shocks del cobre; el tipo de cambio real amortigua, gracias al tipo de cambio flexible, la regla fiscal y las metas de inflación.
- **Descomposición.** Recuadro del IPoM de marzo de 2018: dos shocks explican "casi el 90%" de las fluctuaciones del tipo de cambio nominal, uno emergente/idiosincrático y otro global (demanda mundial y valor del dólar); el shock externo principal tiene "alta correlación con el precio del cobre" (verificado solo por extracto; el PDF no se pudo leer).
- **2019.** IPoM dic-2019: depreciación "eminentemente idiosincrática", asociada al estallido social.
- **2021.** IPoM jun-2021: "desacople" del mercado chileno, con más peso de factores locales (retiros de pensiones, proceso constituyente).
- **2025.** IPoM dic-2025: los shocks geopolíticos *risk-off* deprecian a las monedas emergentes y "compensan el efecto positivo del mayor precio del cobre".
- **Diferencial de tasas.** Minuta BCCh (Broer y Dominichetti): tipo de cambio y sorpresas en el diferencial bajo paridad descubierta con prima de riesgo (solo ficha RePEc).
- **Carry trade.** DT 733 (Carreño y Cox, 2014): el carry de no residentes en forwards, con diferencial alto, se asocia a turbulencia (riesgo de *crash*), más aún con incertidumbre global alta.
- **Riesgo país y procesos constitucionales:** sin recuadro del BCCh que lo cuantifique; solo prensa (NO VERIFICADO como evidencia del BCCh).
- **Interpretación:** a largo plazo, cobre y DXY son las anclas; el diferencial de tasas y el posicionamiento de no residentes pesan en semanas o meses.

## 2. Flujos y su efecto

- **AFP:**
  - Aldunate, Da, Larrain y Sialm (JFE 2025; NBER w30753): los cambios de fondo inducidos por asesores mueven el CLP de forma significativa (elasticidad-precio ≈0,81); los bancos trasladan la presión al forward y aparecen desviaciones de la paridad cubierta.
  - DT 433 (Cowan, Rappoport y Selaive, 2007): los cambios en límites de inversión en el exterior tienen un efecto "significativo pero pequeño y transitorio".
  - Superintendencia de Pensiones (citada por la AAFP, 2022): la cobertura USD/CLP se hace casi toda con forwards locales.
  - IEF 2025-2026: las recomendaciones de asesores (~24 en 12 meses) reducen la capacidad de las AFP de amortiguar shocks externos.
  - Ago-2026: informe favorable del BCCh a una nueva definición de cobertura cambiaria para los fondos generacionales (Ley 21.735; Diario Oficial del 7-sep-2026). Puede cambiar la demanda estructural de forwards (interpretación).
- **Retiros de fondos (2020-2021):** el BCCh estimó que sin su intervención las AFP podrían haber liquidado hasta US$20.000 millones por retiro; respondió con compras de activos (≈US$10.000 millones, según prensa). Sin documento de trabajo que mida el efecto en el CLP.
- **No residentes:** tienen más del 50% de los montos vigentes de derivados de moneda (DF, citando al BCCh). Su posición neta NDF osciló de –US$15.000 millones a positiva por primera vez desde 2022 (mar-2025); en dic-2025 estaba en –US$6.340 millones.
- **Fisco/Hacienda:** desde abril de 2020 vende dólares por subasta en la Bolsa Electrónica, con topes anunciados (p. ej. hasta US$2.000 millones al mes y US$700 millones a la semana en 2020; US$80-160 millones diarios en nov-2021). Programas de 2025-2026: NO VERIFICADO.
- **Exportadores de cobre, Codelco, IED:** sin evidencia del BCCh que cuantifique su efecto (NO VERIFICADO).

## 3. Intervenciones y compras de reservas

| Episodio | Monto / diseño | Efecto según la fuente |
|---|---|---|
| Abr-2008 | Compra de US$8.000 millones, US$50 millones diarios | Solo prensa (DF) |
| Ene-2011 | Compra de US$12.000 millones en el año | Dólar +≈6,2% en 3 días (LyD) |
| Nov-2019 | Venta de hasta US$20.000 millones (10.000 spot + 10.000 cobertura) | Caída de ~$23 tras el anuncio; uso efectivo ≈US$2.550 millones. DT 962 (Jara y Piña, 2022): **redujo la volatilidad** |
| Ene-2021 | Compra de hasta US$12.000 millones en 15 meses | Dólar +~$17 ese día |
| Jul-2022 | Hasta US$25.000 millones (10.000 spot + 10.000 cobertura + 5.000 swaps) | ≈US$6.150 millones spot vendidos; el BCCh dice que "logró el objetivo" |
| Ago-2025 | Compra de ≈US$18.500 millones en 3 años, hasta US$25 millones diarios, esterilizada | Scotiabank estima impacto ≤$10 en total |

Evidencia general: DT 206 (Tapia y Tokman) y DT 433 concluyen que **los anuncios** tienen efecto; las operaciones diarias en sí no.

## 4. Series de la API del BCCh

Endpoint: `https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx` (función `GetSeries`; `SearchSeries` lista por frecuencia). Requiere cuenta gratuita.

| Serie | Código (verificado) | Frecuencia / rezago |
|---|---|---|
| Dólar observado | `F073.TCO.PRE.Z.D` | Diaria, T+1 |
| TPM | `F022.TPM.TIN.D001.NO.Z.D` | Diaria |
| Tipo de cambio multilateral (TCM) | `G073.TCMX.IND.199801.D` | Diaria (descripción inferida) |
| IMACEC base 2018 (original / desestacionalizado) | `F032.IMC.IND.Z.Z.EP18.Z.Z.0.M` / `.1.M` | Mensual, ~1 mes de rezago |
| **NDF neto vigente de no residentes vs bancos** (también por plazo) | `F099.DER.STO.Z.40.N.NR.NET.NDF.MMUSD.CLPUSD.C.Z.0.D` | **Diaria**; rezago ~1-2 días hábiles según DF; revisiones en ene-2026 |
| NDF neto transado de no residentes | `F099.DER.FLU.Z.40.N.NR.NET.NDF.MMUSD.CLPUSD.C.Z.0.D` | Diaria |
| **Derivados USD/CLP netos de bancos por sector** | `F099.DER.STO.Z.40.{SECTOR}.NET.Z.MMUSD.CLPUSD.Z.Z.0.D` con `R.42` fondos de pensiones, `R.55A` empresas, `R.44` seguros, `N.NR` no residentes, `R.63` residentes no bancos | **Diaria** |
| Fondos de pensiones: derivados USD/CLP vigentes por plazo | `F099.DER.STO.Z.42.R.40.NET.Z.MMUSD.CLPUSD.Z.Z.0.M` (y variantes) | Mensual |
| Posición neta de derivados del mercado formal | Cuadro `DER_MON_01` (códigos no visibles) | Diaria; rezago real aparente de semanas |
| Exportaciones FOB de cobre | Cuadro `BP6M_EXPORT`; **códigos NO VERIFICADOS** | Mensual, ~día 7 del mes siguiente |
| Balanza de pagos | `F061.1.FLU.S.USD.Z.T` (descripción NO VERIFICADA) | Trimestral, ~día 18 del segundo mes |
| Precio del cobre BML en la BDE | NO VERIFICADO | — |

Otras: Superintendencia de Pensiones (serie mensual de moneda extranjera sin cobertura: NO VERIFICADO); Cochilco (precio BML diario y producción mensual con ~1,5 meses de rezago; sin API confirmada).

## 5. Calendario 2026 (BCCh, extracto del sitio oficial)

- **RPM:** 26-27 ene, 24 mar, 27-28 abr, 16 jun, 27-28 jul, 8 sep, **26-27 oct**, 15 dic. Comunicado a las 18:00 del último día.
- **IPoM:** 25 mar, 17 jun, 9 sep, 16 dic.
- **Minutas:** 4 feb, 1 abr, 7 may, 24 jun, 5 ago, 16 sep, 4 nov, 23 dic.
- **IEF:** 19-may-2026; segundo semestre por verificar.
- **IPC (INE):** ~día 8 (calendario exacto no verificado). **IMACEC:** primer día hábil. **Comercio exterior:** ~día 7. **Derivados:** día 23.

## Cierre

**Series de flujo más prometedoras como señal:**
1. Posición NDF neta de no residentes (diaria, ~1-2 días de rezago; usar fecha de publicación y vintages porque se revisa). Base teórica: carry (DT 733).
2. Derivados netos de bancos con fondos de pensiones (diaria): captura los cambios de fondo inducidos por asesores (JFE 2025).
3. Exportaciones de cobre (mensual; la señal del mes m está disponible ~el 7 de m+1).
4. Compras de reservas del BCCh (anunciadas: sirven como control).

**Qué mostrar a un ahorrista:** RPM y comunicado de las 18:00, IPoM, IPC, IMACEC, anuncios de intervención o compra de reservas y eventos electorales. Con compras mensuales de largo plazo, como contexto de volatilidad y no como gatillo de compra.

## Fuentes

| Institución | Documento | Año | URL | Verificado |
|---|---|---|---|---|
| BCCh | DT 640 De Gregorio y Labbé | 2011 | https://econpapers.repec.org/paper/chbbcchwp/640.htm | Sí (resumen) |
| BCCh | DT 962 Jara y Piña | 2022 | https://econpapers.repec.org/paper/chbbcchwp/962.htm | Sí (resumen) |
| BCCh | DT 433 Cowan, Rappoport y Selaive | 2007 | https://econpapers.repec.org/paper/chbbcchwp/433.htm | Sí (resumen) |
| BCCh | DT 733 Carreño y Cox | 2014 | https://econpapers.repec.org/paper/chbbcchwp/733.htm | Sí (resumen) |
| BCCh | DT 206 Tapia y Tokman | 2003 | https://www.bcentral.cl/contenido/-/details/documento-de-trabajo-n-206 | Sí (extracto) |
| BCCh | IPoM mar-2018, recuadro | 2018 | https://www.bcentral.cl/documents/33528/3398177/ipom_marzo2018_Rec_traspaso_tipo_cambio.pdf | Parcial |
| BCCh | IPoM dic-2019 | 2019 | https://www.bcentral.cl/documents/33528/133297/ipm122019.pdf | Parcial |
| BCCh | IPoM jun-2021 | 2021 | https://www.bcentral.cl/documents/33528/3015467/IPoM_Junio_2021.pdf/61bb2ea4-44d4-f136-04bd-142514543552 | Parcial |
| BCCh | IPoM dic-2025 | 2025 | https://www.bcentral.cl/en/content/-/detalle/publicaciones/politica-monetaria/ipom-diciembre-2025 | Parcial |
| BCCh (minuta) | Broer y Dominichetti | — | https://ideas.repec.org/p/hal/journl/hal-04490108.html | Parcial |
| BCCh | Comunicado 14-jul-2022 | 2022 | https://www.bcentral.cl/contenido/-/details/comunicado-14072022 | Sí (vía prensa) |
| BCCh | Calendario de política monetaria 2026 | 2026 | https://www.bcentral.cl/web/banco-central/noticias-y-publicaciones/prensa/calendario-de-politica-monetaria-y-financiera | Parcial |
| BCCh | Documentación de la API | 2026 | https://si3.bcentral.cl/estadisticas/Principal1/Web_Services/documentacion.html | Sí |
| BCCh/SIID | Códigos de bancos y fondos de pensiones | 2025 | https://www.siid.cl/monitor-diario ; https://www.siid.cl/fondos-de-pensiones | Sí (descargados) |
| BCCh/SIID | Extensión serie NDF no residentes | 2025 | https://www.siid.cl/contenido/-/detalle/seminario-estadisticas-de-derivados-financieros-disponibles-en-el-siid-tr-del-bcch-duplicar-1 | Sí |
| BCCh | BDE exportaciones FOB | 2026 | https://si3.bcentral.cl/Siete/ES/Siete/Cuadro/CAP_BDP/MN_BDP42/BP6M_EXPORT/BP6M_EXPORT | Sí (sin códigos) |
| BCCh | BDE derivados `DER_MON_01` | 2026 | https://si3.bcentral.cl/Siete/ES/Siete/Cuadro/CAP_DERYSPOT/MN_DERYSPOT/DER_MON_01 | Sí |
| BCCh | IEF primer semestre 2026 | 2026 | https://www.bcentral.cl/contenido/-/detalle/prensa/nota-de-prensa/bcch-publica-ief-primer-semestre-2026 | Sí (extracto) |
| Diario Oficial | Informe BCCh cobertura fondos de pensiones | 2026 | https://www.diariooficial.interior.gob.cl/publicaciones/2026/09/07/44544/01/2866442.pdf | Parcial |
| Hacienda | Venta de dólares por Bolsa Electrónica | 2020 | https://www.hacienda.cl/areas-de-trabajo/finanzas-internacionales/oficina-de-la-deuda-publica/noticias/ministerio-de-hacienda-informa-inicio-del-nuevo-procedimiento-de-venta-de | Sí |
| JFE / NBER | Aldunate, Da, Larrain y Sialm | 2025 | https://www.nber.org/system/files/working_papers/w30753/w30753.pdf | Sí (resumen) |
| AAFP / SP | Cobertura vía forwards | 2022 | https://www.aafp.cl/noticiasafp/fondos-de-pensiones-sortean-con-exito-volatilidad-del-dolar-en-junio-alza-de-la-divisa-aporto-rentabilidad-positiva | Secundaria |
| Prensa (DF, La Tercera, Emol, Bloomberg Línea) | Montos de intervenciones y posiciones | 2008-2025 | df.cl; latercera.com; emol.com; bloomberglinea.com | Secundaria |
| Cochilco | Precio BML / producción | 2026 | https://www.reporteminero.cl/noticia/noticias/2026/09/produccion-cobre-chile-caida-julio-2026-codelco-escondida | Secundaria |
