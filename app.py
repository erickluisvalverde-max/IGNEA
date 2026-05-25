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

st.set_page_config(
    page_title="Análisis Geoquímico de Galápagos",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.markdown("""
### Herramientas

- [Vista general](#top)
- [Sr vs Nd](#srnd)
- [REE](#ree)
- [TAS](#tas)
- [Clustering](#clustering)
""", unsafe_allow_html=True)

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #f4f7fb 0%, #eaf0f8 100%);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
        max-width: 1400px;
    }

    h1, h2, h3 {
        color: #0f172a;
        font-family: "Segoe UI", sans-serif;
    }

    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0b1f3a;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }

    .hero-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
        padding: 1.4rem 1.6rem;
        border-radius: 18px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.18);
        margin-bottom: 1.5rem;
    }

    .hero-box h1 {
        color: white !important;
        margin-bottom: 0.3rem;
    }

    .hero-box p {
        color: #dbeafe;
        margin: 0;
        font-size: 1rem;
    }

    .section-card {
        background: white;
        border-radius: 18px;
        padding: 1.2rem 1.2rem 0.8rem 1.2rem;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.2rem;
    }

    div[data-testid="stDataFrame"] {
        background: white;
        border-radius: 14px;
        padding: 0.4rem;
        border: 1px solid #dbe2ea;
        box-shadow: 0 4px 14px rgba(0,0,0,0.04);
    }

    div[data-testid="stPlotlyChart"],
    div[data-testid="stPyplot"] {
        background: white;
        border-radius: 16px;
        padding: 0.8rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 6px 18px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }

    div[data-testid="stFileUploader"] {
        background: white;
        border-radius: 16px;
        padding: 1rem;
        border: 1px dashed #94a3b8;
        box-shadow: 0 6px 18px rgba(0,0,0,0.04);
    }

    .mini-tag {
        display: inline-block;
        background: #dbeafe;
        color: #1d4ed8;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }

    hr {
        margin-top: 1.8rem;
        margin-bottom: 1.2rem;
        border: none;
        height: 1px;
        background: linear-gradient(to right, transparent, #94a3b8, transparent);
    }
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="hero-box">
    <div class="mini-tag">Geoquímica · Visualización · Galápagos</div>
    <h1 class="main-title">Análisis geoquímico de Galápagos</h1>
    <p class="subtitle">
        Plataforma interactiva para explorar relaciones isotópicas, clasificación TAS,
        tierras raras, fusión parcial y dominios geoquímicos.
    </p>
</div>
""", unsafe_allow_html=True)
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

# =========================================================
# 1. Diagrama Sr vs Nd
# =========================================================

st.markdown('<div id="srnd"></div>', unsafe_allow_html=True)

st.markdown("""
<div class="section-card">
    <h2>Diagrama Sr vs Nd</h2>
    <p>
        Relaciones isotópicas entre Sr y Nd para interpretar
        fuentes mantélicas y dominios geoquímicos.
    </p>
""", unsafe_allow_html=True)

if {'Sr87_Sr86', 'Nd143_Nd144', 'Location'}.issubset(df.columns):

    sns.set_theme(style="whitegrid")

    fig, ax = plt.subplots(
        figsize=(10, 6),
        facecolor="white"
    )

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

    ax.grid(
        True,
        linestyle="--",
        linewidth=0.6,
        alpha=0.35
    )

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

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# -------------------------
# 2. Sr vs Nd interactivo (Plotly)
# -------------------------
if {'Sr87_Sr86', 'Nd143_Nd144', 'Location', 'Sample'}.issubset(df.columns):
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
        marker=dict(
            size=10,
            line=dict(width=1, color='DarkSlateGrey')
        )
    )

    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# 3. Sr vs Nd con imagen de fondo
# -------------------------
st.subheader("Diagrama Sr vs Nd con fondo")

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

# -------------------------
# 4. La/Sm vs Sm/Yb (Plotly)
# -------------------------
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
            title='La/Sm vs Sm/Yb',
            labels={
                'Sm_Yb': 'Sm / Yb',
                'La_Sm': 'La / Sm',
                'Location': 'Isla'
            },
            template='plotly_white'
        )

        fig.update_traces(
            marker=dict(
                size=12,
                line=dict(width=1, color='black')
            ),
            selector=dict(mode='markers')
        )

        st.plotly_chart(fig, use_container_width=True)

# -------------------------
# 5. OIB y MORB
# -------------------------
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
            title='OIB y MORB',
            log_y=True,
            markers=True
        )

        fig.update_traces(
            line=dict(width=1),
            opacity=0.4,
            marker=dict(size=4)
        )

        oib_norm = [oib_ref[e] / condrito[e] for e in ree_disponibles]
        morb_norm = [morb_ref[e] / condrito[e] for e in ree_disponibles]

        fig.add_trace(go.Scatter(
            x=ree_disponibles,
            y=oib_norm,
            mode='lines+markers',
            name='OIB (Referencia)',
            line=dict(color='red', width=4, dash='dash'),
            marker=dict(size=8, color='red', symbol='diamond')
        ))

        fig.add_trace(go.Scatter(
            x=ree_disponibles,
            y=morb_norm,
            mode='lines+markers',
            name='N-MORB (Referencia)',
            line=dict(color='blue', width=4, dash='dash'),
            marker=dict(size=8, color='blue', symbol='square')
        ))

        fig.update_layout(
            xaxis_title='Elementos de Tierras Raras (LREE -> HREE)',
            yaxis_title='Muestra / Condrito',
            template='plotly_white',
            hovermode='closest',
            width=950,
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

# -------------------------
# 6. TAS con % de Fusión
# -------------------------
if {'SiO2', 'Na2O', 'K2O', 'La', 'Location', 'Sample'}.issubset(df.columns):
    df_fusion = df.dropna(subset=['La', 'SiO2', 'Na2O', 'K2O', 'Location', 'Sample']).copy()

    if not df_fusion.empty:
        C0_La = 0.687
        D_La = 0.01

        df_fusion['F_fraccion'] = (C0_La / df_fusion['La'] - D_La) / (1 - D_La)
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
            title='Clasificación TAS con los % de Fusión Parcial',
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
            height=600
        )

        fig.update_traces(
            marker=dict(
                size=12,
                line=dict(width=1, color='black')
            ),
            selector=dict(mode='markers')
        )

        st.plotly_chart(fig, use_container_width=True)

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

        st.subheader("Promedio de fusión parcial por isla")
        st.dataframe(resumen_fusion, use_container_width=True)

# -------------------------
# 7. TAS + Fusión Parcial con línea alcalina interactiva
# -------------------------
if {'SiO2', 'Na2O', 'K2O', 'La', 'Sample', 'Location'}.issubset(df.columns):
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

# -------------------------
# 8. TAS y Evolución Magmática
# -------------------------
if {'SiO2', 'Na2O', 'K2O', 'Sample', 'Location'}.issubset(df.columns):
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
            marker=dict(
                size=11,
                line=dict(width=1, color='black')
            ),
            selector=dict(mode='markers')
        )

        st.plotly_chart(fig, use_container_width=True)

# -------------------------
# 9. Clustering K-Means
# -------------------------
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
            marker=dict(
                size=14,
                line=dict(width=1, color='black')
            ),
            selector=dict(mode='markers')
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay suficientes muestras para ejecutar K-Means con 3 clústeres.")
