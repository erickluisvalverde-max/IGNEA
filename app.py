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
# CONFIG
# =========================================================

st.set_page_config(
    page_title="Análisis Geoquímico de Galápagos",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# ESTILOS
# =========================================================

st.markdown("""
<style>
html {
    scroll-behavior: smooth;
}

.stApp {
    background: linear-gradient(180deg, #f8fafc 0%, #edf2f7 100%);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
    max-width: 1450px;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #081224 0%, #10284a 100%);
}

h1, h2, h3 {
    font-family: "Segoe UI", sans-serif;
    color: #0f172a;
}

.hero-box {
    background: linear-gradient(135deg, #081224 0%, #10284a 50%, #1d4e89 100%);
    border-radius: 28px;
    padding: 2.3rem;
    margin-bottom: 2rem;
    box-shadow: 0 14px 40px rgba(15, 23, 42, 0.20);
}

.main-title {
    color: white !important;
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 0.6rem;
}

.subtitle {
    color: #dbeafe !important;
    font-size: 1.08rem;
    line-height: 1.8;
    margin-bottom: 0;
}

.mini-tag {
    display: inline-block;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.12);
    color: #dbeafe !important;
    padding: 0.45rem 0.9rem;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 700;
    margin-bottom: 1rem;
}

.section-card {
    background: white;
    border-radius: 22px;
    padding: 1.5rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 6px 22px rgba(0,0,0,0.05);
    margin-bottom: 1rem;
}

.section-title {
    margin-top: 0;
    margin-bottom: 0.5rem;
    font-size: 1.8rem;
    font-weight: 800;
    color: #0f172a !important;
}

.section-text {
    color: #64748b !important;
    font-size: 1rem;
    line-height: 1.7;
    margin-bottom: 0;
}

div[data-testid="metric-container"] {
    background: white;
    border: 1px solid #e2e8f0;
    padding: 1rem;
    border-radius: 18px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.04);
}

div[data-testid="stDataFrame"] {
    background: white;
    border-radius: 18px;
    padding: 0.4rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 14px rgba(0,0,0,0.04);
}

div[data-testid="stPlotlyChart"],
div[data-testid="stPyplot"] {
    background: white;
    border-radius: 20px;
    padding: 1rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 6px 18px rgba(0,0,0,0.05);
    margin-bottom: 1.5rem;
}

div[data-testid="stFileUploader"] {
    background: white;
    border-radius: 18px;
    padding: 1rem;
    border: 1px dashed #94a3b8;
    box-shadow: 0 6px 18px rgba(0,0,0,0.04);
}

.sidebar-title {
    font-size: 1.7rem;
    font-weight: 800;
    color: white;
    margin-bottom: 1rem;
}

.sidebar-card {
    background: rgba(255,255,255,0.08);
    padding: 1rem;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.08);
}

.sidebar-card a {
    text-decoration: none;
    color: white !important;
    font-size: 1rem;
    line-height: 2.2;
    font-weight: 500;
}

.sidebar-card a:hover {
    color: #93c5fd !important;
}

hr {
    margin-top: 2rem;
    margin-bottom: 2rem;
    border: none;
    height: 1px;
    background: linear-gradient(to right, transparent, #cbd5e1, transparent);
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown("""
<div class="sidebar-title">
    Panel Geoquímico
</div>

<div class="sidebar-card">
<a href="#top">Vista General</a><br>
<a href="#srnd">Sr vs Nd</a><br>
<a href="#ree">REE</a><br>
<a href="#tas">TAS</a><br>
<a href="#clustering">Clustering</a>
</div>
""", unsafe_allow_html=True)

# =========================================================
# HERO PRINCIPAL
# =========================================================

st.markdown("""
<div id="top"></div>
<div class="hero-box">
    <div class="mini-tag">
        Geoquímica · Visualización · Galápagos
    </div>
    <h1 class="main-title">
        Análisis Geoquímico de Galápagos
    </h1>
    <p class="subtitle">
        Plataforma interactiva para explorar relaciones isotópicas,
        clasificación TAS, tierras raras, fusión parcial
        y dominios geoquímicos.
    </p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# FILE UPLOADER
# =========================================================

archivo = st.file_uploader(
    "Sube tu archivo Excel",
    type=["xlsx", "xls"]
)

if archivo is None:
    st.info("Primero sube tu archivo Excel para visualizar los análisis geoquímicos.")
    st.stop()

# =========================================================
# CARGA DE DATOS
# =========================================================

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

# =========================================================
# MENSAJE
# =========================================================

st.success("¡Excel cargado correctamente!")

# =========================================================
# VISTA GENERAL
# =========================================================

st.markdown("""
<div class="section-card">
    <h2 class="section-title">Vista General del Dataset</h2>
    <p class="section-text">
        Visualización inicial del archivo geoquímico cargado.
        Aquí puedes inspeccionar muestras, variables químicas
        y relaciones isotópicas antes del análisis.
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Número de muestras", value=len(df))

with col2:
    st.metric(label="Variables geoquímicas", value=len(df.columns))

with col3:
    st.metric(label="Valores faltantes", value=int(df.isna().sum().sum()))

st.markdown("## Dataset Geoquímico")
st.dataframe(df, use_container_width=True, height=500)

# =========================================================
# 1. Diagrama Sr vs Nd
# =========================================================

st.markdown('<div id="srnd"></div>', unsafe_allow_html=True)

st.markdown("""
<div class="section-card">
    <h2 class="section-title">Diagrama Sr vs Nd</h2>
    <p class="section-text">
        Relaciones isotópicas entre Sr y Nd para interpretar
        fuentes mantélicas y dominios geoquímicos.
    </p>
</div>
""", unsafe_allow_html=True)

if {'Sr87_Sr86', 'Nd143_Nd144', 'Location'}.issubset(df.columns):
    sns.set_theme(style="whitegrid")

    fig, ax = plt.subplots(figsize=(10, 6), facecolor="white")
    ax.set_facecolor("#f8fafc")

    sns.scatterplot(
        data=df.dropna(subset=['Sr87_Sr86', 'Nd143_Nd144', 'Location']),
        x="Sr87_Sr86",
        y="Nd143_Nd144",
        hue="Location",
        palette="tab10",
        s=120,
        edgecolor="black",
        linewidth=0.8,
        alpha=0.95,
        ax=ax
    )

    ax.set_title(
        "Relación isotópica Sr vs Nd",
        fontsize=16,
        fontweight="bold",
        color="#0f172a",
        pad=16
    )

    ax.set_xlabel(
        r"$^{87}$Sr / $^{86}$Sr",
        fontsize=12,
        fontweight="bold",
        color="#334155"
    )

    ax.set_ylabel(
        r"$^{143}$Nd / $^{144}$Nd",
        fontsize=12,
        fontweight="bold",
        color="#334155"
    )

    ax.grid(True, linestyle="--", linewidth=0.6, alpha=0.35)

    for spine in ax.spines.values():
        spine.set_visible(False)

    legend = ax.legend(
        title="Localidad",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        frameon=True
    )

    legend.get_frame().set_facecolor("white")
    legend.get_frame().set_edgecolor("#cbd5e1")

    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
else:
    st.warning("Faltan columnas para el diagrama Sr vs Nd.")

# =========================================================
# 2. Sr vs Nd interactivo (Plotly)
# =========================================================

if {'Sr87_Sr86', 'Nd143_Nd144', 'Location', 'Sample'}.issubset(df.columns):
    st.markdown("""
    <div class="section-card">
        <h2 class="section-title">Sr vs Nd interactivo</h2>
        <p class="section-text">
            Exploración interactiva de relaciones isotópicas con detalles por muestra.
        </p>
    </div>
    """, unsafe_allow_html=True)

    hover_cols = [c for c in ['SiO2', 'MgO', 'La', 'Yb'] if c in df.columns]

    fig = px.scatter(
        df.dropna(subset=['Sr87_Sr86', 'Nd143_Nd144']),
        x='Sr87_Sr86',
        y='Nd143_Nd144',
        color='Location',
        hover_name='Sample',
        hover_data=hover_cols,
        title='Sr vs Nd',
        labels={
            'Sr87_Sr86': 'Isótopo 87Sr / 86Sr',
            'Nd143_Nd144': 'Isótopo 143Nd / 144Nd',
            'Location': 'Isla / Localidad'
        },
        template='plotly_white'
    )

    fig.update_traces(
        marker=dict(size=10, line=dict(width=1, color='DarkSlateGrey'))
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# 3. Sr vs Nd con imagen de fondo
# =========================================================

st.markdown("""
<div class="section-card">
    <h2 class="section-title">Diagrama Sr vs Nd con fondo</h2>
    <p class="section-text">
        Superposición de muestras sobre la base visual isotópica del diagrama Sr-Nd.
    </p>
</div>
""", unsafe_allow_html=True)

if {'Sr87_Sr86', 'Nd143_Nd144', 'Location'}.issubset(df.columns):
    ruta_imagen_srnd = "SRvsND.png.png"

    if os.path.exists(ruta_imagen_srnd):
        imagen_fondo = mpimg.imread(ruta_imagen_srnd)

        fig, ax = plt.subplots(figsize=(9, 10), dpi=150)
        plt.style.use('default')
        ax.set_facecolor('white')

        limites_grafico = [0.703, 0.711, 0.5120, 0.5132]
        ax.imshow(imagen_fondo, extent=limites_grafico, aspect='auto', zorder=1)

        sns.scatterplot(
            data=df.dropna(subset=['Sr87_Sr86', 'Nd143_Nd144', 'Location']),
            x='Sr87_Sr86',
            y='Nd143_Nd144',
            hue='Location',
            ax=ax,
            s=110,
            edgecolor='black',
            linewidth=0.8,
            alpha=0.9,
            zorder=2
        )

        ax.set_title('Diagrama Sr vs Nd', fontsize=13, pad=15)
        ax.set_xlabel('$^{87}$Sr / $^{86}$Sr', fontsize=12, fontweight='bold')
        ax.set_ylabel('$^{143}$Nd / $^{144}$Nd', fontsize=12, fontweight='bold')
        ax.set_xlim(0.703, 0.711)
        ax.set_ylim(0.5120, 0.5132)
        ax.tick_params(direction='in', top=True, right=True, labelsize=10)
        ax.legend(title='Isla / Localidad', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)

        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.warning("No se encontró la imagen SRvsND.png.png.")

# =========================================================
# 4. La/Sm vs Sm/Yb
# =========================================================

st.markdown('<div id="ree"></div>', unsafe_allow_html=True)

st.markdown("""
<div class="section-card">
    <h2 class="section-title">La/Sm vs Sm/Yb</h2>
    <p class="section-text">
        Variaciones geoquímicas de elementos de tierras raras
        para interpretar enriquecimiento mantélico y profundidad de fusión.
    </p>
</div>
""", unsafe_allow_html=True)

if {'La', 'Sm', 'Yb', 'Location', 'Sample'}.issubset(df.columns):
    df_ree = df.dropna(subset=['La', 'Sm', 'Yb']).copy()

    if not df_ree.empty:
        df_ree['La_Sm'] = df_ree['La'] / df_ree['Sm']
        df_ree['Sm_Yb'] = df_ree['Sm'] / df_ree['Yb']

        fig = px.scatter(
            df_ree,
            x='Sm_Yb',
            y='La_Sm',
            color='Location',
            hover_name='Sample',
            title='',
            labels={
                'Sm_Yb': 'Sm / Yb',
                'La_Sm': 'La / Sm',
                'Location': 'Isla'
            },
            template='plotly_white'
        )

        fig.update_traces(
            marker=dict(
                size=13,
                line=dict(width=1, color='black'),
                opacity=0.92
            ),
            selector=dict(mode='markers')
        )

        fig.update_layout(
            height=620,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='white',
            font=dict(family='Segoe UI', size=13, color='#0f172a'),
            legend=dict(
                title='Localidad',
                bgcolor='rgba(255,255,255,0.85)',
                bordercolor='#cbd5e1',
                borderwidth=1
            ),
            margin=dict(l=40, r=40, t=30, b=40)
        )

        fig.update_xaxes(showgrid=True, gridcolor='rgba(148,163,184,0.25)', zeroline=False)
        fig.update_yaxes(showgrid=True, gridcolor='rgba(148,163,184,0.25)', zeroline=False)

        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Faltan columnas necesarias para el diagrama La/Sm vs Sm/Yb.")

# =========================================================
# 5. Patrones REE · OIB y MORB
# =========================================================

st.markdown("""
<div class="section-card">
    <h2 class="section-title">Patrones REE · OIB y MORB</h2>
    <p class="section-text">
        Comparación de patrones de tierras raras normalizados a condrito
        para identificar afinidades tipo OIB y MORB.
    </p>
</div>
""", unsafe_allow_html=True)

nombre_columna_localidad = 'Location'
nombre_columna_muestra = 'Sample'

condrito = {
    'La': 0.237, 'Ce': 0.613, 'Pr': 0.0928, 'Nd': 0.457, 'Sm': 0.148,
    'Eu': 0.0563, 'Gd': 0.199, 'Tb': 0.0361, 'Dy': 0.246, 'Ho': 0.0546,
    'Er': 0.160, 'Tm': 0.0247, 'Yb': 0.161, 'Lu': 0.0246
}

oib_ref = {
    'La': 37, 'Ce': 80, 'Pr': 9.7, 'Nd': 38.5, 'Sm': 10,
    'Eu': 3, 'Gd': 7.62, 'Tb': 1.05, 'Dy': 5.6, 'Ho': 1.06,
    'Er': 2.62, 'Tm': 0.35, 'Yb': 2.16, 'Lu': 0.3
}

morb_ref = {
    'La': 2.5, 'Ce': 7.5, 'Pr': 1.32, 'Nd': 7.3, 'Sm': 2.63,
    'Eu': 1.02, 'Gd': 3.68, 'Tb': 0.67, 'Dy': 4.55, 'Ho': 1.01,
    'Er': 2.97, 'Tm': 0.456, 'Yb': 3.05, 'Lu': 0.455
}

elementos_ree = list(condrito.keys())

if nombre_columna_localidad in df.columns and nombre_columna_muestra in df.columns:
    df_spider = df.copy()

    for col in elementos_ree:
        if col in df_spider.columns:
            df_spider[col] = pd.to_numeric(df_spider[col], errors='coerce')
            df_spider[col] = df_spider[col].replace(0, np.nan)

    ree_disponibles = [e for e in elementos_ree if e in df_spider.columns]

    for elemento in ree_disponibles:
        df_spider[elemento] = df_spider[elemento] / condrito[elemento]

    if ree_disponibles:
        df_melted = df_spider.melt(
            id_vars=[nombre_columna_muestra, nombre_columna_localidad],
            value_vars=ree_disponibles,
            var_name='Elemento',
            value_name='Concentracion_Normalizada'
        ).dropna(subset=['Concentracion_Normalizada'])

        fig = px.line(
            df_melted,
            x='Elemento',
            y='Concentracion_Normalizada',
            color=nombre_columna_localidad,
            line_group=nombre_columna_muestra,
            hover_name=nombre_columna_muestra,
            title='',
            log_y=True,
            markers=True,
            template='plotly_white'
        )

        fig.update_traces(
            line=dict(width=1.3),
            opacity=0.45,
            marker=dict(size=5)
        )

        oib_norm = [oib_ref[e] / condrito[e] for e in ree_disponibles]
        morb_norm = [morb_ref[e] / condrito[e] for e in ree_disponibles]

        fig.add_trace(go.Scatter(
            x=ree_disponibles,
            y=oib_norm,
            mode='lines+markers',
            name='OIB (Referencia)',
            line=dict(color='red', width=4, dash='dash'),
            marker=dict(size=9, color='red', symbol='diamond')
        ))

        fig.add_trace(go.Scatter(
            x=ree_disponibles,
            y=morb_norm,
            mode='lines+markers',
            name='N-MORB (Referencia)',
            line=dict(color='blue', width=4, dash='dash'),
            marker=dict(size=9, color='blue', symbol='square')
        ))

        fig.update_layout(
            height=680,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='white',
            hovermode='closest',
            font=dict(family='Segoe UI', size=13, color='#0f172a'),
            legend=dict(
                bgcolor='rgba(255,255,255,0.85)',
                bordercolor='#cbd5e1',
                borderwidth=1
            ),
            margin=dict(l=40, r=40, t=30, b=40),
            xaxis_title='Elementos de Tierras Raras (LREE → HREE)',
            yaxis_title='Muestra / Condrito'
        )

        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor='rgba(148,163,184,0.25)')

        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Faltan columnas necesarias para generar patrones REE.")

# =========================================================
# 6. TAS con % de Fusión
# =========================================================

st.markdown('<div id="tas"></div>', unsafe_allow_html=True)

st.markdown("""
<div class="section-card">
    <h2 class="section-title">TAS con % de Fusión Parcial</h2>
    <p class="section-text">
        Clasificación TAS integrada con estimaciones de
        fusión parcial y dominios geoquímicos.
    </p>
</div>
""", unsafe_allow_html=True)

if {'SiO2', 'Na2O', 'K2O', 'La', 'Location', 'Sample'}.issubset(df.columns):
    df_fusion = df.dropna(
        subset=['La', 'SiO2', 'Na2O', 'K2O', 'Location', 'Sample']
    ).copy()

    if not df_fusion.empty:
        C0_La = 0.687
        D_La = 0.01

        df_fusion['F_fraccion'] = ((C0_La / df_fusion['La']) - D_La) / (1 - D_La)
        df_fusion['F_porcentaje'] = (df_fusion['F_fraccion'] * 100).clip(lower=0.1, upper=30)

        occidental = [
            'Isla Fernandina', 'Isla Isabela', 'Volcan Wolf', 'Volcan Darwin',
            'Volcan Alcedo', 'Sierra Negra', 'Cerro Azul', 'Volcan Ecuador',
            'Isla Tortuga', 'Roca Redonda'
        ]

        df_fusion['Region'] = df_fusion['Location'].apply(
            lambda x: 'Occidental (Pluma Activa)' if x in occidental else 'Central / Oriental'
        )

        df_fusion['Alkalis'] = df_fusion['Na2O'] + df_fusion['K2O']

        fig = px.scatter(
            df_fusion,
            x='SiO2',
            y='Alkalis',
            color='F_porcentaje',
            color_continuous_scale='viridis',
            symbol='Region',
            hover_name='Sample',
            hover_data=['Location', 'La'],
            title='Clasificación TAS con % de Fusión Parcial',
            labels={
                'SiO2': 'SiO2 (wt%)',
                'Alkalis': 'Na2O + K2O (wt%)',
                'F_porcentaje': '% Fusión',
                'Region': 'Dominio Geográfico'
            },
            template='plotly_white'
        )

        ruta_imagen_tas = "Diagrama tas.png"

        if os.path.exists(ruta_imagen_tas):
            with open(ruta_imagen_tas, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()

            img_str = f"data:image/png;base64,{encoded_string}"

            fig.add_layout_image(
                dict(
                    source=img_str,
                    xref="x",
                    yref="y",
                    x=35,
                    y=16,
                    sizex=40,
                    sizey=16,
                    sizing="stretch",
                    opacity=1,
                    layer="below"
                )
            )

        fig.update_layout(
            xaxis_range=[35, 75],
            yaxis_range=[0, 16],
            template='plotly_white',
            plot_bgcolor='rgba(0,0,0,0)',
            coloraxis_colorbar=dict(title="Fusión (%)"),
            width=950,
            height=600,
            title_x=0.02,
            title_font_size=22
        )

        fig.update_traces(
            marker=dict(size=12, line=dict(width=1, color='black')),
            selector=dict(mode='markers')
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        <div class="section-card">
            <h2 class="section-title" style="font-size:1.3rem;">Promedio de fusión parcial por isla</h2>
            <p class="section-text">Resumen promedio de fusión parcial estimada para cada localidad.</p>
        </div>
        """, unsafe_allow_html=True)

        resumen_fusion = (
            df_fusion.groupby('Location')['F_porcentaje']
            .mean()
            .sort_values(ascending=False)
            .reset_index()
        )

        resumen_fusion.rename(
            columns={
                'Location': 'Isla / Localidad',
                'F_porcentaje': 'Fusión Parcial Promedio (%)'
            },
            inplace=True
        )

        resumen_fusion['Fusión Parcial Promedio (%)'] = resumen_fusion['Fusión Parcial Promedio (%)'].round(2)

        st.dataframe(resumen_fusion, use_container_width=True)
else:
    st.warning("Faltan columnas necesarias para el TAS con fusión parcial.")

# =========================================================
# 7. TAS + Fusión Parcial con línea alcalina interactiva
# =========================================================

if {'SiO2', 'Na2O', 'K2O', 'La', 'Sample', 'Location'}.issubset(df.columns):
    st.markdown("""
    <div class="section-card">
        <h2 class="section-title">TAS + Fusión Parcial con línea alcalina</h2>
        <p class="section-text">
            Visualización interactiva del grado de fusión parcial y el límite alcalino.
        </p>
    </div>
    """, unsafe_allow_html=True)

    df_tas = df.dropna(subset=['SiO2', 'Na2O', 'K2O', 'La', 'Sample', 'Location']).copy()

    if not df_tas.empty:
        df_tas['Alkalis'] = df_tas['Na2O'] + df_tas['K2O']

        C0_La = 0.687
        D_La = 0.01
        df_tas['F_fraccion'] = (C0_La / df_tas['La'] - D_La) / (1 - D_La)
        df_tas['F_porcentaje'] = df_tas['F_fraccion'] * 100
        df_tas['F_porcentaje'] = df_tas['F_porcentaje'].clip(lower=0.1, upper=25)

        fig = px.scatter(
            df_tas,
            x='SiO2',
            y='Alkalis',
            color='F_porcentaje',
            color_continuous_scale='Plasma_r',
            hover_name='Sample',
            hover_data=['Location', 'La'],
            title='Grado de Fusión Parcial',
            labels={
                'SiO2': 'Sílice (SiO2 %)',
                'Alkalis': 'Álcalis Totales (Na2O + K2O %)',
                'F_porcentaje': '% Fusión Parcial'
            },
            template='plotly_white'
        )

        x_linea = np.linspace(43, 54, 300)
        y_linea = (0.37 * x_linea) - 14.43

        fig.add_trace(go.Scatter(
            x=x_linea,
            y=y_linea,
            mode='lines',
            name='Límite alcalino',
            line=dict(color='#00C2FF', width=4, dash='dash'),
            hovertemplate='Límite alcalino<br>SiO2: %{x:.2f}<br>Na2O + K2O: %{y:.2f}<extra></extra>'
        ))

        fig.update_traces(
            marker=dict(size=12, line=dict(width=1, color='black')),
            selector=dict(mode='markers')
        )

        fig.update_layout(
            xaxis_range=[43, 54],
            yaxis_range=[0.5, 7],
            coloraxis_colorbar=dict(title='Fusión (%)')
        )

        fig.update_xaxes(showgrid=True, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridcolor='lightgray')

        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# 8. TAS y Evolución Magmática
# =========================================================

if {'SiO2', 'Na2O', 'K2O', 'Sample', 'Location'}.issubset(df.columns):
    st.markdown("""
    <div class="section-card">
        <h2 class="section-title">TAS y Evolución Magmática</h2>
        <p class="section-text">
            Distribución composicional de las muestras sobre el diagrama TAS.
        </p>
    </div>
    """, unsafe_allow_html=True)

    df_tas2 = df.dropna(subset=['SiO2', 'Na2O', 'K2O', 'Sample', 'Location']).copy()

    if not df_tas2.empty:
        df_tas2['Alkalis'] = df_tas2['Na2O'] + df_tas2['K2O']

        fig = px.scatter(
            df_tas2,
            x='SiO2',
            y='Alkalis',
            color='Location',
            hover_name='Sample',
            title='Clasificación TAS y Evolución Magmática',
            labels={
                'SiO2': 'SiO2 (wt%)',
                'Alkalis': 'Na2O + K2O (wt%)',
                'Location': 'Localidad'
            },
            template='plotly_white'
        )

        ruta_imagen = 'Diagrama tas.png'
        if os.path.exists(ruta_imagen):
            img = Image.open(ruta_imagen)

            fig.add_layout_image(
                dict(
                    source=img,
                    xref="x",
                    yref="y",
                    x=35,
                    y=16,
                    sizex=40,
                    sizey=16,
                    sizing="stretch",
                    opacity=1,
                    layer="below"
                )
            )

        fig.update_layout(
            xaxis_range=[35, 75],
            yaxis_range=[0, 16],
            template='plotly_white',
            width=900,
            height=600
        )

        fig.update_traces(
            marker=dict(size=11, line=dict(width=1, color='black')),
            selector=dict(mode='markers')
        )

        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# 9. Clustering K-Means
# =========================================================

st.markdown('<div id="clustering"></div>', unsafe_allow_html=True)

st.markdown("""
<div class="section-card">
    <h2 class="section-title">Clustering Geoquímico K-Means</h2>
    <p class="section-text">
        Agrupamiento geoquímico automático basado en
        relaciones isotópicas y elementos REE para
        interpretar dominios mantélicos y tendencias
        geoquímicas entre muestras volcánicas.
    </p>
</div>
""", unsafe_allow_html=True)

columnas_ml = ['Sr87_Sr86', 'Nd143_Nd144', 'La', 'Sm', 'Yb']

if set(columnas_ml).issubset(df.columns):
    df_ml = df.dropna(subset=columnas_ml).copy()

    if len(df_ml) >= 3:
        X = df_ml[columnas_ml]
        scaler = StandardScaler()
        X_escalado = scaler.fit_transform(X)

        kmeans = KMeans(
            n_clusters=3,
            random_state=42,
            n_init=10
        )

        df_ml['Cluster_IA'] = kmeans.fit_predict(X_escalado)
        df_ml['Cluster_IA'] = 'Grupo Químico ' + df_ml['Cluster_IA'].astype(str)

        nombres_geologicos = {
            'Grupo Químico 0': 'OIB',
            'Grupo Químico 1': 'MORB',
            'Grupo Químico 2': 'Zona de Transición'
        }

        df_ml['Interpretacion_Geologica'] = df_ml['Cluster_IA'].map(nombres_geologicos)

        fig = px.scatter(
            df_ml,
            x='Sr87_Sr86',
            y='Nd143_Nd144',
            color='Interpretacion_Geologica',
            hover_name='Sample',
            hover_data=['Location'],
            title='Fuente Mantélica',
            labels={
                'Sr87_Sr86': '87Sr / 86Sr',
                'Nd143_Nd144': '143Nd / 144Nd',
                'Interpretacion_Geologica': 'Dominio del Manto'
            },
            template='plotly_white',
            color_discrete_map={
                'OIB': 'red',
                'MORB': 'blue',
                'Zona de Transición': 'orange'
            }
        )

        fig.update_traces(
            marker=dict(size=14, line=dict(width=1, color='black'))
        )

        st.plotly_chart(fig, use_container_width=True)

        resumen_clusters = (
            df_ml[['Sample', 'Location', 'Interpretacion_Geologica']]
            .rename(columns={
                'Sample': 'Muestra',
                'Location': 'Localidad',
                'Interpretacion_Geologica': 'Dominio Geoquímico'
            })
        )

        st.dataframe(resumen_clusters, use_container_width=True)
    else:
        st.warning("No hay suficientes muestras para ejecutar K-Means con 3 clústeres.")
else:
    st.warning("Faltan columnas necesarias para ejecutar el clustering geoquímico.")
