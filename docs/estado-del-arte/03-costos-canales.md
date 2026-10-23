# Costo real de comprar y mantener dólares en Chile (ahorro de US$200–2.000 al mes)

> Investigación del 2026-10-23 (issues #13 y #17). Los precios son **una sola foto del mercado**
> de ese día. Lo que no pudo confirmarse con una fuente está marcado NO VERIFICADO.

## 1. Resumen

- **El canal pesa mucho más que el momento.** Hoy, comprar en la pizarra de BancoEstado cuesta ~2,5% sobre el precio medio; Fintual ~0,46%; Buda (stablecoin) ~0,74% comprando de inmediato. Con US$500 al mes, la diferencia entre el más caro y el más barato es **~US$120 al año (~2 puntos porcentuales)**, entre 7 y 20 veces el ±0,1–0,3% que movían las reglas de timing.
- **Hay datos públicos automatizables:** API del BCCh (dólar observado), API pública de Buda (tiempo real) y, con baja frecuencia, el comparador dolaronline.cl. No hay API pública de bancos ni de Global66.

## 2. Precios publicados el 23-oct-2026

Fuente: [dolaronline.cl/comparador-dolar-chile](https://www.dolaronline.cl/comparador-dolar-chile/). "Tú compras" = lo que pagas por US$1; "Tú vendes" = lo que te pagan.

| Canal | Tú compras (CLP) | Tú vendes (CLP) | Diferencia | Hora del dato |
|---|---|---|---|---|
| BancoEstado (pizarra) | 1.019,00 | 969,00 | 50,00 (5,0%) | 17:03 |
| AFEX Agustinas | 998,00 | 982,00 | 16,00 (1,6%) | 05:44 (último válido) |
| Fintual (USD) | 1.000,00 | 990,77 | 9,23 (0,93%) | 17:03 |
| Buda USDC | 997,45 | 992,72 | 4,73 (0,48%) | 17:03 |
| Buda USDT | 996,43 | 991,53 | 4,90 (0,49%) | 17:03 |

Confirmado en la API de Buda ([ticker usdc-clp](https://www.buda.com/api/v2/markets/usdc-clp/ticker)): mejor venta 997,53, mejor compra 992,72. Comisión de Buda USDC-CLP: **0,5% taker y 0,2% maker**, mínimo 0,01 USDC ([mercado](https://www.buda.com/api/v2/markets/usdc-clp)); los precios del comparador no la incluyen.

**Dólar observado:** dolaronline muestra $984,96 para el 23-oct y [mindicador](https://mindicador.cl/api/dolar) $986,58 (y $976,82 el 22-oct): hay que conciliar. El observado se calcula con operaciones del día hábil anterior ([metodología BCCh](https://si3.bcentral.cl:443/estadisticas/Principal1/Metodologias/EC/PARIDADES/Dolar_observado.pdf)), no es un precio ejecutable; el mercado operaba cerca de $994–995. Por eso el costo se mide **contra el precio medio de cada canal**.

| Canal | Recargo sobre precio medio | Comisión | Costo al comprar | Ida y vuelta |
|---|---|---|---|---|
| BancoEstado | 25,0 CLP (2,51%) | — | **~2,5%** | ~5,0% |
| AFEX | 8,0 CLP (0,81%) | — | ~0,8% (sujeto a stock) | ~1,6% |
| Buda USDC inmediata | 2,4 CLP (0,24%) | 0,5% | ~0,74% | ~1,5% |
| Buda USDC orden límite | ~0 | 0,2% | ~0,2–0,45% (puede no ejecutarse) | ~0,5–0,9% |
| Fintual | 4,6 CLP (0,46%) | 0 | **~0,46%** | ~0,93% |

El recargo de Fintual coincide con el spread de $4 por dólar informado en 2024 ([Chócale](https://chocale.cl/2024/03/fintual-alza-comision-fondo-mutuo-very-conservative-streep-retornos-seguiran-muy-competitivos/)).

| Otros canales | Dato | Fuente | Estado |
|---|---|---|---|
| Bancos (Santander, Chile, BCI) | Spread $15–25 por dólar; brokers/apps (Global66, Racional, XTB) $2–8 | [Rankia 2026](https://www.rankia.cl/blog/como-invertir-forex/7188549-donde-comprar-dolares-chile-bancos-vs-brokers-online) | Rango de blog |
| Racional, Tenpo | Desde $1.000 CLP | ídem | Spread NO VERIFICADO |
| Global66 | "Tipo de cambio real, sin comisiones ocultas" | [global66.com](https://www.global66.com/cl/comprar/dolares/) (403) | NO VERIFICADO |
| Tenpo (tarjeta) | Spread promedio 3,8% sobre Mastercard en compras con tarjeta (2024) | [Chócale 2024](https://chocale.cl/2024/09/tarjetas-de-credito-comision-internacional-y-spread-tipo-de-cambio-costos-al-pagar-en-el-extranjero/) | Compra de USD: NO VERIFICADO |
| Mach, Itaú, Scotiabank, Security, BCI, Banco de Chile (pizarra) | — | — | NO VERIFICADO |

**Mantención de cuenta corriente en USD** ([Chócale, mar-2022](https://chocale.cl/2022/03/cuenta-corriente-en-dolares-moneda-extranjera-bancos-costos/); datos antiguos, revisar tarifarios): Santander 0,08 UF/mes; BCI 1,785 UF/mes si el saldo promedio es menor a 57 UF; Itaú $0 (otra nota menciona comisión); Scotiabank $0; Banco de Chile $0 con paquete. La mantención de BCI (≈21 UF/año) supera por mucho el spread en saldos pequeños.

## 3. Dónde mantener los dólares

| Opción | Rendimiento | Riesgo y regulación | Estado |
|---|---|---|---|
| Cuenta vista/corriente USD | ~0% | Banco CMF. **Garantía estatal 100% depósitos a la vista** (art. 132 LGB) | [CMF](https://www.cmfchile.cl/educa/600/w3-article-27460.html) |
| Depósito a plazo USD | NO VERIFICADO | Garantía estatal personas naturales: 100% con tope **UF 200 por banco y UF 400 en el sistema, por año** | [CMF](https://www.cmfchile.cl/educa/600/w3-article-27460.html) |
| Money market USD (p. ej. Principal Visión MM Dólar) | 3–4% anual histórico según Rankia (NO VERIFICADO); remuneración 0,95–1,4% | AGF fiscalizada por la CMF; sin garantía estatal | [Ficha](https://www.principal.cl/archivos/ficha-vision-money-market-dolar), [Rankia](https://www.rankia.cl/blog/fondos-mutuos-agf/5982242-como-invertir-fondos-mutuos-money-market) |
| ETF de Tesoros cortos (SGOV, BIL) vía corredora | NO VERIFICADO | Custodia del broker extranjero; sin garantía chilena | NO VERIFICADO |
| Saldo USD Fintual / Global66 | Global66: 6% en 2023 solo Colombia | No es depósito bancario: sin garantía estatal | [Forbes CO 2023](https://forbes.co/2023/10/08/negocios/cuenta-remunerada-en-dolares-sera-nuestra-palanca-de-crecimiento-dice-country-manager-de-global66/); Chile NO VERIFICADO |
| Stablecoins en Buda | 0% | Emisor, pérdida de paridad, custodia del exchange; sin garantía | Registro CMF de Buda NO VERIFICADO |

**Impuestos:** la compraventa de divisas no paga IVA y las ganancias se declaran en la Operación Renta ([Rankia](https://www.rankia.cl/blog/como-invertir-forex/7188549-donde-comprar-dolares-chile-bancos-vs-brokers-online)); para inversiones en USD el resultado en pesos se reconoce al liquidar ([AZ](https://www.az.cl/az-alert-tratamiento-tributario-de-las-inversiones-en-moneda-extranjera/); SII Oficio 3748/2021 vía [Transtecnia](https://transtecnia.cl/?p=72212)). Tratamiento de la ganancia cambiaria pura de una persona natural: NO VERIFICADO en fuente oficial del SII.

## 4. Estimación con US$500 al mes (US$6.000 al año)

| Canal | Costo de compra | Costo anual (US$) | Costo anual (CLP ~$994) |
|---|---|---|---|
| BancoEstado | 2,51% | **~151** | ~150.000 |
| AFEX | 0,81% | ~48 | ~48.000 |
| Buda inmediata | 0,74% | ~44 | ~44.000 |
| Fintual | 0,46% | **~28** | ~27.500 |

- Diferencia más caro vs más barato: **~US$123 al año (~2,05 pp)**; si después se venden, se duplica (~5,0% vs ~0,9% ida y vuelta).
- Las reglas de timing (±0,1–0,3% = US$6–18 al año) solo valen la pena con un canal ya barato, y su ventaja es menor que la diferencia compra-venta de cualquier canal (≥0,48%): si obligan a operar más seguido, pierden.

## 5. Fuentes automatizables

| Fuente | URL | Formato | Frecuencia | Uso |
|---|---|---|---|---|
| BCCh Siete REST (`F073.TCO.PRE.Z.D`) | https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx ([doc](https://si3.bcentral.cl/estadisticas/Principal1/Web_Services/documentacion_en.html)) | JSON | Diaria | **Sí**: oficial, registro gratuito (revisar términos) |
| Buda API pública | https://www.buda.com/api/v2/markets/usdc-clp/ticker ([doc](https://api.buda.com/en/)) | JSON sin autenticación | Tiempo real | **Sí**: documentada, 120 req/min por IP |
| mindicador.cl | https://mindicador.cl/api/dolar | JSON | Diaria | Respaldo del BCCh (términos NO VERIFICADOS) |
| dolaronline.cl | https://www.dolaronline.cl/comparador-dolar-chile/ | HTML | ~10 min | **Con cautela**: robots.txt lo permite; 1–2 lecturas al día, citando la fuente |
| Global66 | global66.com | HTML | — | **No** (403) |
| Bancos, Tenpo, Mach, Racional | — | — | — | Sin API ni página pública verificable |

## 6. Recomendaciones

1. No comprar en la pizarra del banco para ahorrar todos los meses.
2. Usar un canal de bajo spread: Fintual (~0,46%) o Buda con orden límite (~0,2–0,45%; en compra inmediata ~0,74% y riesgo de stablecoin y custodia). Comparar Global66, Racional o Tenpo en la app en el mismo minuto.
3. Evitar cuentas en USD con mantención si el saldo es bajo.
4. Para mantener los USD: con garantía estatal, cuenta vista o depósito a plazo en banco (tope UF 200 por banco); con rendimiento, money market en USD regulado por la CMF, comparando su comisión (0,5–1,4%) con lo que rinde.
5. Automatización mínima: observado del BCCh diario; ticker de Buda al comprar; dolaronline 1 vez al día para BancoEstado, Fintual y AFEX. Medir el costo contra el precio medio del momento, no contra el observado.
6. En el backtest, modelar un costo de 0,5–0,75% por compra en vez de 0%.
