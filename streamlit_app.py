"""Tablero del radar del dólar. Solo lee data/ y describe el pasado; no predice.

Ejecutar desde la raíz del repo:  streamlit run streamlit_app.py

Cada pestaña tiene tres partes: qué muestra, una lectura calculada con los datos actuales y los límites.
Las frases de lectura se generan con las cifras vigentes; no son texto fijo.
"""

from __future__ import annotations

from datetime import date

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from radar import almacen, investigacion, metricas, reporte
from radar.almacen import tabla
from radar.senales import DIAS_ANIO, SERIES, calcular, estado

st.set_page_config(page_title="Radar del dólar", layout="wide")

ESTADOS = metricas.ESTADOS
COLOR_ESTADO = ["#2e7d32", "#f9a825", "#c62828"]  # BARATO, NORMAL, CARO
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
UMBRAL_SEPARACION_PP = 5  # diferencia en puntos porcentuales para decir que los estados se separan
EPISODIOS_MINIMOS = 10  # por debajo, la conclusión es débil


def pct(x: float, dec: int = 1) -> str:
    return f"{reporte.num(100 * x, dec)}%"


def pp(x: float) -> str:
    return f"{x:+.0f} pp".replace(".", ",")


@st.cache_data(ttl=3600)
def cargar():
    df = tabla(SERIES)
    senales = calcular(df)
    preparado = investigacion.preparar(df["usdclp"], senales)
    walk = investigacion.walk_forward(preparado)
    return df, senales, preparado, walk


@st.cache_data(ttl=3600)
def cierre_observado() -> tuple[date, float]:
    """Último dólar observado con su fecha real. El semáforo usa un día de rezago, por eso se muestra aparte."""
    s = almacen.leer("usdclp")
    return s.index.max().date(), float(s.iloc[-1])


df, senales, preparado, walk = cargar()
actual = reporte.actual(senales, df["usdclp"])
fecha_obs, precio_obs = cierre_observado()
nombre_dca = investigacion.DCA.nombre
nombre_radar = walk["elegida"].nombre

st.title("Radar del dólar en Chile")
st.caption(f"Cierre del {fecha_obs:%d-%m-%Y}. Describe lo que pasó; no predice.")

c1, c2, c3 = st.columns(3)
c1.metric("Dólar", f"${reporte.num(precio_obs)}")
c2.metric("Semáforo", actual["estado"], help="BARATO, NORMAL o CARO según cobre, dólar global y tasas.")
c3.metric("Puntaje", reporte.num(actual["compuesto"]) if np.isfinite(actual["compuesto"]) else "sin datos",
          help="Entre −1 (caro) y +1 (barato). Entre −0,25 y +0,25 es NORMAL.")
st.warning(
    "**Este tablero no dice si comprar, vender o mantener.** Esa decisión depende de tu plan personal "
    "(colchón, necesidades, peso del dólar en tu patrimonio), no del precio."
)

t1, t2, t3, t4, t5 = st.tabs(["Calibración", "Radar vs DCA", "Estacionalidad", "Correlación", "Salud de datos"])


# ---------------------------------------------------------------- 1. Calibración
with t1:
    st.subheader("Cuando el semáforo estuvo en cada estado, ¿el dólar subió después?")
    horizonte = st.radio("Plazo", list(metricas.HORIZONTES), horizontal=True, index=1, key="hz_cal")
    cal = metricas.calibracion(df["usdclp"], senales["compuesto"])
    fila_h = cal[cal["horizonte"] == horizonte]
    base = fila_h[fila_h["estado"] == "TODOS"].iloc[0]
    por_estado = fila_h[fila_h["estado"] != "TODOS"]

    caro = por_estado[por_estado["estado"] == "CARO"]
    if not caro.empty:
        st.markdown(
            f"**En {horizonte}:** tras un día CARO, el dólar subió en {pct(caro.iloc[0]['sube'], 0)} de los casos. "
            f"Cualquier día: {pct(base['sube'], 0)}."
        )
    rango = (por_estado["sube"].max() - por_estado["sube"].min()) * 100
    if rango < UMBRAL_SEPARACION_PP:
        st.info("Los tres estados dan resultados casi iguales. El semáforo no cambia la probabilidad de subida.")
    else:
        st.info(f"Los estados se separan {reporte.num(rango, 0)} puntos. Revisa cuántos casos hay abajo.")
    episodios_bajos = int(por_estado["episodios"].min())
    if episodios_bajos < EPISODIOS_MINIMOS:
        st.warning(f"Pocos casos: el estado con menos tiene {episodios_bajos} episodios. Puede ser azar.")

    # Una sola fuente por capa: Altair no admite capas con datos distintos dentro de un facet.
    barras = alt.Chart().transform_filter(alt.datum.estado != "TODOS").mark_bar().encode(
        x=alt.X("estado:N", sort=ESTADOS, title=None),
        y=alt.Y("sube:Q", axis=alt.Axis(format="%"), title="% de días con dólar más alto"),
        color=alt.Color("estado:N", legend=None, scale=alt.Scale(domain=ESTADOS, range=COLOR_ESTADO)),
        tooltip=["horizonte", "estado", "dias", "episodios", alt.Tooltip("sube:Q", format=".1%", title="subió")],
    )
    linea_base = alt.Chart().transform_filter(alt.datum.estado == "TODOS").mark_rule(
        strokeDash=[4, 4], color="#555").encode(y="sube:Q")
    grafico = alt.layer(barras, linea_base, data=cal).properties(width=160, height=260).facet(
        column=alt.Column("horizonte:N", sort=list(metricas.HORIZONTES), title=None))
    st.altair_chart(grafico, width="content")

    # Histograma de retornos futuros por estado: la forma completa, no solo el porcentaje
    st.caption("Histograma: cada barra cuenta los días en que el dólar se movió en ese rango en el plazo elegido.")
    dias_h = metricas.HORIZONTES[horizonte]
    j = pd.DataFrame({
        "estado": senales["compuesto"].dropna().map(estado),
        "retorno": metricas.retornos_futuros(df["usdclp"], dias_h),
    }).dropna()
    j = j[j["estado"].isin(ESTADOS)]
    hist = alt.Chart(j).mark_bar(opacity=0.5).encode(
        x=alt.X("retorno:Q", bin=alt.Bin(step=0.02), axis=alt.Axis(format="%", title="retorno del dólar en el horizonte")),
        y=alt.Y("count():Q", stack=None, title="días"),
        color=alt.Color("estado:N", scale=alt.Scale(domain=ESTADOS, range=COLOR_ESTADO), title="estado"),
        tooltip=["estado:N", alt.Tooltip("count():Q", title="días")],
    )
    cero = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color="#000").encode(x="x:Q")
    st.altair_chart((hist + cero).properties(height=280), width="stretch")
    with st.expander("Tabla completa"):
        st.dataframe(
            cal.assign(sube=lambda d: (d["sube"] * 100).round(1), mediana=lambda d: (d["mediana"] * 100).round(2),
                       p10=lambda d: (d["p10"] * 100).round(2), p90=lambda d: (d["p90"] * 100).round(2))
            .rename(columns={"sube": "subió %", "mediana": "mediana %", "p10": "p10 %", "p90": "p90 %"}),
            hide_index=True,
        )


# ---------------------------------------------------------------- 2. Radar vs DCA
with t2:
    st.subheader("¿Comprar según el radar fue mejor que comprar una cuota fija cada mes?")
    st.caption("Precio medio pagado por dólar desde 2020 (prueba fuera de muestra). Menor = mejor.")
    comp = metricas.comparacion_acumulada(preparado, walk["elegida"]).dropna(how="all")
    if comp.empty:
        st.info("Todavía no hay meses de prueba con compras.")
    else:
        largo = comp.rename_axis("mes").reset_index().melt("mes", var_name="estrategia", value_name="clp_usd")
        linea = alt.Chart(largo.dropna()).mark_line(point=True).encode(
            x=alt.X("mes:T", title=None),
            y=alt.Y("clp_usd:Q", scale=alt.Scale(zero=False), title="CLP por USD"),
            color=alt.Color("estrategia:N", title=None, legend=alt.Legend(orient="bottom")),
            tooltip=[alt.Tooltip("mes:T", format="%m-%Y"), "estrategia:N", alt.Tooltip("clp_usd:Q", format=",.2f")],
        ).properties(height=320)
        st.altair_chart(linea, width="stretch")

        # Diferencia mensual del radar contra DCA (positiva = el radar pagó más)
        dif = ((comp[nombre_radar] / comp[nombre_dca] - 1) * 100).dropna()
        ultimo_mes = dif.index[-1]
        ganados = int((dif < 0).sum())
        st.markdown(
            f"**Hasta {ultimo_mes:%m-%Y}:** el radar pagó {reporte.num(abs(dif.iloc[-1]), 2)}% "
            f"{'más' if dif.iloc[-1] > 0 else 'menos'} por dólar que DCA. "
            f"Fue mejor en {ganados} de {len(dif)} meses."
        )
        barras_dif = alt.Chart(dif.rename("dif").rename_axis("mes").reset_index()).mark_bar().encode(
            x=alt.X("mes:T", title=None),
            y=alt.Y("dif:Q", title="% vs DCA (negativo = pagó menos)"),
            color=alt.condition(alt.datum.dif < 0, alt.value("#2e7d32"), alt.value("#c62828")),
            tooltip=[alt.Tooltip("mes:T", format="%m-%Y"), alt.Tooltip("dif:Q", format="+.2f", title="% vs DCA")],
        ).properties(height=200)
        st.altair_chart(barras_dif, width="stretch")
        st.caption("Verde: el radar pagó menos que DCA ese mes. Rojo: pagó más.")

    st.warning("No incluye costos de cambio ni comisiones. Una diferencia de décimas de punto es menor que esos costos.")


# ---------------------------------------------------------------- 3. Estacionalidad
with t3:
    st.subheader("¿Hay meses que el dólar suele subir o bajar?")
    st.caption("Rojo = el dólar subió ese mes. Azul = bajó.")
    piv = metricas.estacional(df["usdclp"])
    anio_min, anio_max = int(piv.index.min()), int(piv.index.max())
    rango_anios = st.slider("Años a mostrar", anio_min, anio_max, (anio_min, anio_max), key="anios")
    sub = piv.loc[rango_anios[0]:rango_anios[1]]
    largo = sub.reset_index().melt("anio", var_name="mes", value_name="var").dropna()
    largo["mes_nombre"] = largo["mes"].map(lambda m: MESES[int(m) - 1])
    mapa = alt.Chart(largo).mark_rect().encode(
        x=alt.X("mes_nombre:N", sort=MESES, title=None),
        y=alt.Y("anio:O", title=None),
        color=alt.Color("var:Q", scale=alt.Scale(scheme="redblue", domainMid=0, reverse=True), title="% mensual"),
        tooltip=["anio", "mes_nombre", alt.Tooltip("var:Q", format="+.2f", title="% mensual")],
    ).properties(height=max(200, 22 * sub.shape[0]))
    st.altair_chart(mapa, width="stretch")

    # Resumen por mes: promedio y proporción de años con alza (sobre todo el historial)
    resumen = pd.DataFrame({
        "mes": MESES,
        "promedio": [piv[m].mean() for m in range(1, 13)],
        "años_con_alza": [(piv[m] > 0).mean() * 100 for m in range(1, 13)],
        "años": [piv[m].count() for m in range(1, 13)],
    })
    mejor = resumen.loc[resumen["promedio"].idxmax()]
    peor = resumen.loc[resumen["promedio"].idxmin()]
    st.markdown(
        f"**Mes que más sube en promedio:** {mejor['mes']} ({reporte.num(mejor['promedio'], 1)}%). "
        f"**Mes que más baja:** {peor['mes']} ({reporte.num(peor['promedio'], 1)}%)."
    )
    barras_m = alt.Chart(resumen).mark_bar().encode(
        x=alt.X("mes:N", sort=MESES, title=None),
        y=alt.Y("promedio:Q", title="variación promedio mensual (%)"),
        color=alt.condition(alt.datum.promedio > 0, alt.value("#c62828"), alt.value("#1565c0")),
        tooltip=["mes", alt.Tooltip("promedio:Q", format="+.2f"),
                 alt.Tooltip("años_con_alza:Q", format=".0f", title="% años con alza"), "años"],
    ).properties(height=220)
    st.altair_chart(barras_m, width="stretch")
    st.warning("Son pocos años por mes. Un año extremo cambia el promedio. No es una regla para operar.")


# ---------------------------------------------------------------- 4. Correlación
with t4:
    st.subheader("¿El dólar se mueve junto con el cobre y el dólar global?")
    st.caption("Va de −1 a +1. Cerca de 0 = no se mueven juntos. Medido en ventanas de un año.")
    corr = metricas.correlacion(df)
    if corr.empty:
        st.info("Faltan datos para calcular la correlación.")
    else:
        hoy_c = corr.iloc[-1]
        sentido = "en sentido contrario" if hoy_c["cobre"] < 0 else "en el mismo sentido"
        st.markdown(
            f"**Hoy:** el dólar y el cobre van {sentido} (correlación {reporte.num(hoy_c['cobre'], 2)}). "
            f"Con el dólar global: {reporte.num(hoy_c['dxy'], 2)}."
        )
        largo_c = corr.rename_axis("fecha").reset_index().melt("fecha", var_name="serie", value_name="correlación")
        lineas_c = alt.Chart(largo_c).mark_line().encode(
            x=alt.X("fecha:T", title=None),
            y=alt.Y("correlación:Q", scale=alt.Scale(domain=[-1, 1])),
            color=alt.Color("serie:N", title=None, scale=alt.Scale(
                domain=["cobre", "dxy"], range=["#b26a00", "#1565c0"]), legend=alt.Legend(orient="bottom")),
            tooltip=["fecha:T", "serie:N", alt.Tooltip("correlación:Q", format=".2f")],
        )
        cero_c = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color="#777", strokeDash=[3, 3]).encode(y="y:Q")
        st.altair_chart((lineas_c + cero_c).properties(height=280), width="stretch")

        st.markdown("**Relación diaria del último año** (retornos del dólar vs. retornos del cobre)")
        r = df[["usdclp", "cobre_lb"]].pct_change(fill_method=None).dropna().tail(DIAS_ANIO)
        puntos = alt.Chart(r.reset_index()).mark_circle(size=28, opacity=0.45, color="#555").encode(
            x=alt.X("cobre_lb:Q", axis=alt.Axis(format="%", title="retorno diario del cobre")),
            y=alt.Y("usdclp:Q", axis=alt.Axis(format="%", title="retorno diario del dólar")),
            tooltip=[alt.Tooltip("usdclp:Q", format=".2%", title="dólar"), alt.Tooltip("cobre_lb:Q", format=".2%", title="cobre")],
        )
        ajuste = puntos.transform_regression("cobre_lb", "usdclp").mark_line(color="#c62828", size=2)
        st.altair_chart((puntos + ajuste).properties(height=300), width="stretch")
    st.warning("Correlación no es causa. Mirar juntos no significa que uno explique al otro.")


# ---------------------------------------------------------------- 5. Salud de datos
with t5:
    st.subheader("¿Los datos están al día?")
    st.caption("Si una fuente está atrasada, el semáforo no es confiable ese día.")
    salud = metricas.salud(date.today()).copy()
    salud["límite días"] = salud["serie"].map(almacen.antiguedad_max)
    salud["estado"] = np.where(salud["dias_sin_dato"].isna(), "sin datos",
                               np.where(salud["dias_sin_dato"] <= salud["límite días"], "al día", "atrasada"))
    al_dia = int((salud["estado"] == "al día").sum())
    atrasadas = salud.loc[salud["estado"] != "al día", "serie"].tolist()
    if atrasadas:
        st.warning(f"**Lectura:** {al_dia} de {len(salud)} fuentes al día. Atrasadas o sin datos: {', '.join(atrasadas)}.")
    else:
        st.success(f"**Lectura:** las {len(salud)} fuentes están al día.")
    grafico_s = alt.Chart(salud.dropna(subset=["dias_sin_dato"])).mark_bar().encode(
        y=alt.Y("serie:N", sort="-x", title=None),
        x=alt.X("dias_sin_dato:Q", title="días desde el último dato"),
        color=alt.Color("estado:N", scale=alt.Scale(domain=["al día", "atrasada", "sin datos"],
                                                     range=["#2e7d32", "#c62828", "#777"]), title=None),
        tooltip=["serie", "ultimo_dato", "dias_sin_dato", "límite días", "huecos", "fallas_consecutivas"],
    )
    limite_s = alt.Chart(salud.dropna(subset=["dias_sin_dato"])).mark_tick(color="#000", thickness=2, size=22).encode(
        y=alt.Y("serie:N", sort="-x"), x="límite días:Q")
    st.altair_chart((grafico_s + limite_s).properties(height=220), width="stretch")
    st.caption("La marca negra es la antigüedad máxima tolerada para cada serie.")
    with st.expander("Detalle por serie"):
        st.dataframe(salud, hide_index=True)
