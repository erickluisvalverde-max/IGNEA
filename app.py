# =========================================================
# IMPORTACIONES
# =========================================================

import os
import base64
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

from PIL import Image
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="Análisis Geoquímico de Galápagos",
    layout="wide"
)

# =========================================================
# TEMA VISUAL PROFESIONAL
# =========================================================

sns.set_theme(
    style="whitegrid",
    context="talk",
    palette="deep"
)

st.markdown("""
<style>

/* =========================================================
FUENTE
========================================================= */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* =========================================================
FONDO GENERAL
========================================================= */
.stApp {
    background:
        radial-gradient(circle at top left, rgba(37,99,235,0.08), transparent 30%),
        radial-gradient(circle at bottom right, rgba(14,165,233,0.08), transparent 30%),
        linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
    font-family: 'Inter', sans-serif;
}

/* =========================================================
CONTENEDOR
========================================================= */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    padding-left: 3rem;
    padding-right: 3rem;
    max-width: 1500px;
}

/* =========================================================
SIDEBAR
========================================================= */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
    border-right: 1px solid rgba(255,255,255,0.05);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* =========================================================
HERO
========================================================= */
.hero-box {

    background:
        linear-gradient(135deg, rgba(15,23,42,0.97), rgba(30,41,59,0.94)),
        url('https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?q=80&w=1600');

    background-size: cover;
    background-position: center;

    padding: 2.2rem;

    border-radius: 30px;

    box-shadow:
        0 12px 40px rgba(15,23,42,0.18),
        inset 0 1px 0 rgba(255,255,255,0.05);

    margin-bottom: 2rem;

    border: 1px solid rgba(255,255,255,0.06);

    position: relative;
    overflow: hidden;
}

.hero-box::before {
    content: "";
    position: absolute;
    inset: 0;
    background: rgba(15,23,42,0.55);
    backdrop-filter: blur(4px);
}

.hero-box * {
    position: relative;
    z-index: 2;
}

/* =========================================================
TÍTULOS
========================================================= */
.main-title {
    font-size: 3rem;
    font-weight: 800;
    color: white;
    margin-bottom: 0.5rem;
    letter-spacing: -1px;
}

.subtitle {
    color: #dbeafe;
    font-size: 1.05rem;
    line-height: 1.8;
    max-width: 900px;
}

.mini-tag {
    display: inline-block;
    background: rgba(59,130,246,0.18);
    color: #93c5fd;
    border: 1px solid rgba(147,197,253,0.25);
    padding: 0.45rem 0.9rem;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 700;
    margin-bottom: 1rem;
}

/* =========================================================
CARDS
========================================================= */
.section-card {

    background: rgba(255,255,255,0.74);

    backdrop-filter: blur(14px);

    border-radius: 24px;

    padding: 1.5rem;

    border: 1px solid rgba(255,255,255,0.5);

    box-shadow:
        0 8px 30px rgba(15,23,42,0.06);

    margin-bottom: 1.6rem;

    transition: all 0.25s ease;
}

.section-card:hover {
    transform: translateY(-2px);

    box-shadow:
        0 14px 40px rgba(15,23,42,0.10);
}

/* =========================================================
HEADERS
========================================================= */
h1, h2, h3 {
    color: #0f172a;
    font-weight: 700;
    letter-spacing: -0.5px;
}

/* =========================================================
DATAFRAME
========================================================= */
div[data-testid="stDataFrame"] {

    border-radius: 18px;

    overflow: hidden;

    border: 1px solid rgba(148,163,184,0.18);

    box-shadow:
        0 4px 20px rgba(15,23,42,0.05);
}

/* =========================================================
GRÁFICOS
========================================================= */
div[data-testid="stPlotlyChart"],
div[data-testid="stPyplot"] {

    background: rgba(255,255,255,0.86);

    border-radius: 22px;

    padding: 1rem;

    border: 1px solid rgba(255,255,255,0.5);

    box-shadow:
        0 8px 30px rgba(15,23,42,0.06);

    margin-top: 1rem;
    margin-bottom: 1rem;
}

/* =========================================================
UPLOAD
========================================================= */
div[data-testid="stFileUploader"] {

    background: rgba(255,255,255,0.82);

    border-radius: 24px;

    padding: 1.5rem;

    border: 2px dashed #94a3b8;

    box-shadow:
        0 8px 24px rgba(15,23,42,0.05);
}

/* =========================================================
BOTONES
========================================================= */
.stButton > button {

    background: linear-gradient(135deg, #2563eb, #1d4ed8);

    color: white;

    border: none;

    border-radius: 14px;

    padding: 0.7rem 1.3rem;

    font-weight: 600;

    transition: all 0.2s ease;

    box-shadow:
        0 6px 18px rgba(37,99,235,0.25);
}

.stButton > button:hover {

    transform: translateY(-2px);

    box-shadow:
        0 10px 25px rgba(37,99,235,0.35);
}

/* =========================================================
SCROLLBAR
========================================================= */
::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-thumb {
    background: rgba(100,116,139,0.4);
    border-radius: 999px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("Panel Geoquímico")

st.sidebar.markdown("---")

st.sidebar.markdown("""
### Herramientas

- Isótopos Sr-Nd
- Diagramas TAS
- Patrones REE
- Fusión parcial
- Clustering geoquímico
- Visualización interactiva
""")

st.sidebar.markdown("---")

st.sidebar.info("""
Aplicación científica interactiva para análisis geoquímico
de muestras volcánicas de Galápagos.
""")

# =========================================================
# HERO PRINCIPAL
# =========================================================

st.markdown("""
<div class="hero-box">

    <div class="mini-tag">
        Geoquímica · Petrología · Visualización Científica
    </div>

    <div class="main-title">
        Análisis Geoquímico de Galápagos
    </div>

    <p class="subtitle">
        Plataforma interactiva para explorar relaciones isotópicas,
        patrones de tierras raras, clasificación TAS,
        procesos de fusión parcial y dominios geoquímicos.
    </p>

</div>
""", unsafe_allow_html=True)

# =========================================================
# SUBIR EXCEL
# =========================================================

archivo = st.file_uploader(
    "Sube tu archivo Excel",
    type=["xlsx", "xls"]
)

if archivo is None:
    st.info("Primero sube tu archivo Excel para comenzar el análisis.")
    st.stop()

# =========================================================
# LEER EXCEL
# =========================================================

df = pd.read_excel(archivo)

df.columns = df.columns.str.strip()

st.success("Excel cargado correctamente.")

# =========================================================
# PREVIEW
# =========================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)

st.subheader("Vista previa de datos")

st.dataframe(
    df.head(),
    use_container_width=True
)

st.markdown('</div>', unsafe_allow_html=True)
