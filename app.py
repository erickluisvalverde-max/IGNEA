import os
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

st.set_page_config(page_title="Análisis Geoquímico de Galápagos", layout="wide")

st.title("Análisis geoquímico de Galápagos")

archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx", "xls"])

if archivo is None:
    st.info("Primero sube tu archivo Excel para ver los gráficos y resultados.")
    st.stop()

df = pd.read_excel(archivo)

df.columns = df.columns.str.strip()

if "Sr" in df.columns:
    df["Sr"] = pd.to_numeric(
        df["Sr"].astype(str).str.replace("*", "", regex=False),
        errors="coerce"
    )

if "Rb" in df.columns:
    df["Rb"] = pd.to_numeric(
        df["Rb"].astype(str).str.replace("*", "", regex=False),
        errors="coerce"
    )

st.success("¡Excel cargado, limpio y listo para hacer ciencia!")
st.dataframe(df.head(), use_container_width=True)

# -------------------------
# 1. Diagrama Sr vs Nd (Seaborn)
# -------------------------
st.subheader("Diagrama Sr vs Nd")

sns.set_theme(style="whitegrid")
fig, ax = plt.subplots(figsize=(10, 6))

sns.scatterplot(
    data=df,
    x="Sr87_Sr86",
    y="Nd143_Nd144",
    hue="Location",
    palette="tab10",
    s=100,
    edgecolor="black",
    ax=ax
)

ax.set_title("Sr vs Nd", fontsize=14, fontweight="bold")
ax.set_xlabel("87Sr / 86Sr", fontsize=12)
ax.set_ylabel("143Nd / 144Nd", fontsize=12)
ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

fig.tight_layout()
st.pyplot(fig)

# -------------------------
# 2. Sr vs Nd interactivo (Plotly)
# -------------------------
st.subheader("Evolución geoquímica: Isótopos de Sr vs Nd por isla")

fig = px.scatter(
    df,
    x="Sr87_Sr86",
    y="Nd143_Nd144",
    color="Location",
    hover_name="Sample",
    hover_data=["SiO2", "MgO", "La", "Yb"],
    title="Evolución Geoquímica: Isótopos de Sr vs Nd por Isla",
    labels={
        "Sr87_Sr86": "87Sr / 86Sr",
        "Nd143_Nd144": "143Nd / 144Nd",
        "Location": "Isla / Localidad"
    },
    template="plotly_white"
)

fig.update_traces(
    marker=dict(size=12, line=dict(width=1, color="black")),
    selector=dict(mode="markers")
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------
# 3. Relaciones La/Sm vs Sm/Yb
# -------------------------
df["La_Sm"] = df["La"] / df["Sm"]
df["Sm_Yb"] = df["Sm"] / df["Yb"]
df.replace([np.inf, -np.inf], np.nan, inplace=True)

st.subheader("Fuentes mantélicas y profundidad")

fig = px.scatter(
    df,
    x="Sm_Yb",
    y="La_Sm",
    color="Location",
    hover_name="Sample",
    title="Fuentes Mantélicas y Profundidad: Relaciones de Tierras Raras (La/Sm vs Sm/Yb)",
    labels={
        "Sm_Yb": "Sm / Yb (A mayor valor, fusión más profunda)",
        "La_Sm": "La / Sm (A mayor valor, fuente más enriquecida)",
        "Location": "Isla"
    },
    template="plotly_white"
)

fig.update_traces(
    marker=dict(size=12, line=dict(width=1, color="black")),
    selector=dict(mode="markers")
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------
# 4. Fusión parcial - islas occidentales
# -------------------------
islas_occidentales = ["Fernandina", "Isabela"]
df_occ = df[df["Location"].isin(islas_occidentales)].copy()

C0_La = 0.687
D_La = 0.01

df_occ["F_fraccion"] = (C0_La / df_occ["La"] - D_La) / (1 - D_La)
df_occ["F_porcentaje"] = df_occ["F_fraccion"] * 100
df_occ["F_porcentaje"] = df_occ["F_porcentaje"].clip(lower=0.1)

st.subheader("Cálculo de fusión parcial para las islas occidentales")

tabla_resultados = df_occ[["Sample", "Location", "La", "F_porcentaje"]].round(2)
st.dataframe(tabla_resultados, use_container_width=True)

# -------------------------
# 5. Clasificación TAS
# -------------------------
st.subheader("Clasificación TAS")

from PIL import Image, ImageFile

df["Alkalis"] = df["Na2O"] + df["K2O"]

ruta_imagen = "Diagrama tas.png"

try:
    ImageFile.LOAD_TRUNCATED_IMAGES = True

    imagen_fondo = Image.open(ruta_imagen).convert("RGBA")
    imagen_fondo = np.array(imagen_fondo)

    fig, ax = plt.subplots(figsize=(10, 8), dpi=150)

    limites_imagen = [35, 75, 0, 16]
    ax.imshow(imagen_fondo, extent=limites_imagen, aspect="auto", zorder=1)

    sns.scatterplot(
        data=df,
        x="SiO2",
        y="Alkalis",
        hue="Location",
        ax=ax,
        s=100,
        edgecolor="black",
        linewidth=1,
        zorder=2
    )

    ax.set_title("Clasificación TAS", fontsize=14, pad=15)
    ax.set_xlabel("SiO2 (wt%)", fontsize=12)
    ax.set_ylabel("Na2O + K2O (wt%)", fontsize=12)
    ax.legend(title="Isla", bbox_to_anchor=(1.05, 1), loc="upper left")

    fig.tight_layout()
    st.pyplot(fig)

except Exception as e:
    st.error(f"No se pudo cargar la imagen TAS: {e}")

# -------------------------
# 6. K-means
# -------------------------
st.subheader("Clustering K-means: firmas geoquímicas")

columnas_ml = ["Sr87_Sr86", "Nd143_Nd144", "La", "Sm", "Yb"]
df_ml = df.dropna(subset=columnas_ml).copy()

X = df_ml[columnas_ml]

scaler = StandardScaler()
X_escalado = scaler.fit_transform(X)

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df_ml["Cluster_IA"] = kmeans.fit_predict(X_escalado)
df_ml["Cluster_IA"] = "Grupo Químico " + df_ml["Cluster_IA"].astype(str)

st.success(
    f"¡Modelo K-means entrenado con éxito! "
    f"El algoritmo analizó {len(df_ml)} muestras y encontró 3 firmas químicas distintas."
)

st.dataframe(
    df_ml[["Sample", "Location", "Sr87_Sr86", "Nd143_Nd144", "La", "Sm", "Yb", "Cluster_IA"]].round(3),
    use_container_width=True,
)

# -------------------------
# 7. Interpretación geológica final
# -------------------------
nombres_geologicos = {
    "Grupo Químico 0": "Firma de la Pluma (Enriquecido)",
    "Grupo Químico 1": "Manto Empobrecido (Tipo MORB)",
    "Grupo Químico 2": "Zona de Mezcla / Transición"
}

df_ml["Interpretacion_Geologica"] = df_ml["Cluster_IA"].map(nombres_geologicos)

st.subheader("Interpretación final de dominios mantélicos")

fig = px.scatter(
    df_ml,
    x="Sr87_Sr86",
    y="Nd143_Nd144",
    color="Interpretacion_Geologica",
    hover_name="Sample",
    hover_data=["Location"],
    title="Interpretación Final: Dominios Mantélicos de Galápagos (K-Means)",
    labels={
        "Sr87_Sr86": "Relación 87Sr / 86Sr",
        "Nd143_Nd144": "Relación 143Nd / 144Nd",
        "Interpretacion_Geologica": "Dominio del Manto"
    },
    template="plotly_white",
    color_discrete_map={
        "Firma de la Pluma (Enriquecido)": "red",
        "Manto Empobrecido (Tipo MORB)": "blue",
        "Zona de Mezcla / Transición": "orange"
    }
)

fig.update_traces(marker=dict(size=14, line=dict(width=1, color="black")))
st.plotly_chart(fig, use_container_width=True)

# -------------------------
# 8. Fusión parcial en todo el archipiélago
# -------------------------
C0_La = 0.687
D_La = 0.01

df["F_fraccion"] = (C0_La / df["La"] - D_La) / (1 - D_La)
df["F_porcentaje"] = df["F_fraccion"] * 100
df["F_porcentaje"] = df["F_porcentaje"].clip(lower=0.1, upper=30)

st.subheader("Fusión parcial en el archipiélago de Galápagos")

fig = px.scatter(
    df,
    x="F_porcentaje",
    y="La",
    color="Location",
    hover_name="Sample",
    title="Fusión Parcial en el Archipiélago de Galápagos",
    labels={
        "F_porcentaje": "Grado de Fusión Parcial Calculado (%)",
        "La": "Lantano (ppm)",
        "Location": "Isla / Localidad"
    },
    template="plotly_white"
)

F_linea_pct = np.linspace(0.1, 25, 100)
F_linea_fraccion = F_linea_pct / 100
La_linea = C0_La / (D_La + F_linea_fraccion * (1 - D_La))

fig.add_trace(
    go.Scatter(
        x=F_linea_pct,
        y=La_linea,
        mode="lines",
        name="Modelo Teórico (Batch Melting)",
        line=dict(color="black", width=2, dash="dash")
    )
)

fig.update_traces(marker=dict(size=10, line=dict(width=0.5, color="black")))
st.plotly_chart(fig, use_container_width=True)

resumen_fusion = (
    df.groupby("Location")["F_porcentaje"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

st.subheader("Promedio de fusión parcial por isla")
st.dataframe(resumen_fusion.round(2), use_container_width=True)
