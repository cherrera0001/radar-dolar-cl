"""Dashboard del radar del dólar. Solo lee data/ y describe el pasado; no predice.

Ejecutar desde la raíz del repo:  streamlit run streamlit_app.py
"""

from __future__ import annotations

from datetime import date

import altair as alt
import numpy as np
import streamlit as st

from radar import investigacion, metricas, reporte
from radar.almacen import tabla
from radar.senales import SERIES, calcular

st.set_page_config(page_title="Radar del dólar", layout="wide")


@st.cache_data(ttl=3600)
def cargar():
    df = tabla(SERIES)
    senales = calcular(df)
    preparado = investigacion.preparar(df["usdclp"], senales)
    walk = investigacion.walk_forward(preparado)
    return df, senales, preparado, walk


df, senales, preparado, walk = cargar()
actual = reporte.actual(senales, df["usdclp"])

st.title("Radar del dólar en Chile")
st.caption(f"Datos al {actual['fecha']} · Descriptivo: muestra lo que pasó, no lo que va a pasar.")

c1, c2, c3 = st.columns(3)
c1.metric("Dólar observado", f"${reporte.num(actual['precio'])}")
c2.metric("Estado del semáforo", actual["estado"])
c3.metric("Puntaje compuesto", reporte.num(actual["compuesto"]) if np.isfinite(actual["compuesto"]) else "sin datos")

t1, t2, t3, t4, t5 = st.tabs(["Calibración", "Radar vs DCA", "Estacionalidad", "Correlación", "Salud de datos"])

with t1:
    st.subheader("¿Qué hizo el dólar después de cada estado?")
    st.caption("Porcentaje de días en que el dólar estaba más alto N meses después. "
               "La línea base es cualquier día. Si el estado no se separa de la línea base, no aporta información.")
    cal = metricas.calibracion(df["usdclp"], senales["compuesto"])
    base = cal[cal["estado"] == "TODOS"][["horizonte", "sube"]].rename(columns={"sube": "base"})
    datos = cal[cal["estado"] != "TODOS"].merge(base, on="horizonte")
    barras = alt.Chart().mark_bar().encode(
        x=alt.X("estado:N", sort=metricas.ESTADOS, title=None),
        y=alt.Y("sube:Q", axis=alt.Axis(format="%"), title="% de días con dólar más alto"),
        color=alt.Color("estado:N", legend=None,
                        scale=alt.Scale(domain=metricas.ESTADOS, range=["#2e7d32", "#f9a825", "#c62828"])),
        tooltip=["horizonte", "estado", "dias", "episodios", alt.Tooltip("sube:Q", format=".0%")],
    )
    linea_base = alt.Chart().mark_rule(strokeDash=[4, 4]).encode(
        x=alt.X("estado:N", sort=metricas.ESTADOS), y="base:Q")
    # Una sola fuente por capa: Altair exige datos comunes al facetar capas.
    grafico = alt.layer(barras, linea_base, data=datos).facet(
        column=alt.Column("horizonte:N", sort=list(metricas.HORIZONTES), title="Horizonte"))
    st.altair_chart(grafico, width="content")
    st.dataframe(
        cal.assign(sube=lambda d: (d["sube"] * 100).round(1), mediana=lambda d: (d["mediana"] * 100).round(2),
                   p10=lambda d: (d["p10"] * 100).round(2), p90=lambda d: (d["p90"] * 100).round(2))
        .rename(columns={"sube": "subió %", "mediana": "mediana %", "p10": "p10 %", "p90": "p90 %"}),
        hide_index=True,
    )
    st.info("Pocos episodios = poca evidencia. Mira la columna `episodios` antes de sacar conclusiones.")

with t2:
    st.subheader("Precio medio pagado: DCA vs radar (fuera de muestra, desde 2020)")
    st.caption("CLP por USD. Para quien compra, menor es mejor. Diseño hasta 2019, prueba desde 2020.")
    comp = metricas.comparacion_acumulada(preparado, walk["elegida"])
    st.line_chart(comp)
    prueba = walk["prueba"]
    base_dca = prueba[investigacion.DCA.nombre]
    cols = st.columns(len(prueba))
    for col, (nombre, r) in zip(cols, prueba.items(), strict=True):
        if r is None:
            continue
        mejora = investigacion.mejora_pct(r, base_dca)
        col.metric(nombre, f"{r.precio_medio:,.2f} CLP/USD", f"{mejora:+.2f}% USD vs DCA")

with t3:
    st.subheader("Variación mensual del dólar por año")
    st.caption("Cierre a cierre de cada mes. Rojo = el dólar subió; azul = bajó.")
    piv = metricas.estacional(df["usdclp"]).reset_index().melt("anio", var_name="mes", value_name="var")
    nombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    piv["mes"] = piv["mes"].map(lambda m: nombres[int(m) - 1])
    mapa = alt.Chart(piv).mark_rect().encode(
        x=alt.X("mes:N", sort=nombres, title=None),
        y=alt.Y("anio:O", title=None),
        color=alt.Color("var:Q", scale=alt.Scale(scheme="redblue", domainMid=0, reverse=True),
                        title="% mensual"),
        tooltip=["anio", "mes", alt.Tooltip("var:Q", format=".2f")],
    ).properties(height=40 * piv["anio"].nunique())
    st.altair_chart(mapa, width="stretch")

with t4:
    st.subheader("Correlación móvil de 1 año con el dólar")
    st.caption("Correlación de retornos diarios. Cobre negativa = cuando sube el cobre, el peso se aprecia. "
               "Si la correlación se acerca a cero, la relación se rompió.")
    st.line_chart(metricas.correlacion(df))

with t5:
    st.subheader("Estado de las fuentes")
    st.caption("Días desde el último dato, huecos de más de 4 días y fallas consecutivas del último run.")
    st.dataframe(metricas.salud(date.today()), hide_index=True)
