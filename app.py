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
# Creamos un gráfico de dispersión (scatter) con Plotly Express
fig = px.scatter(
    df,
    x='Sr87_Sr86',  # Columna que irá en el eje X
    y='Nd143_Nd144',  # Columna que irá en el eje Y
    color='Location',  # Cada isla/localidad tendrá un color distinto
    hover_name='Sample',  # Nombre principal que aparece al pasar el mouse sobre un punto
    hover_data=['SiO2', 'MgO', 'La', 'Yb'],  # Datos extra que aparecerán en el recuadro emergente
    title='Sr vs Nd',  # Título del gráfico
    labels={  # Nombres bonitos para los ejes y la leyenda
        'Sr87_Sr86': 'Isótopo 87Sr / 86Sr',
        'Nd143_Nd144': 'Isótopo 143Nd / 144Nd',
        'Location': 'Isla / Localidad'
    },
    template='plotly_white'  # Estilo visual limpio, con fondo blanco
)

# Hacemos que los puntos se vean mejor:
# más grandes y con un borde oscuro para distinguirlos
fig.update_traces(
    marker=dict(
        size=10,
        line=dict(width=1, color='DarkSlateGrey')
    )
)

# Mostramos el gráfico dentro de la página de Streamlit
st.plotly_chart(fig, use_container_width=True)

import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.image as mpimg

# Ruta de la imagen de fondo del diagrama Sr-Nd
ruta_imagen_srnd = '/content/GALAPAGOS.csv/MyDrive/SRvsND.png'

# Leemos la imagen para usarla como fondo del gráfico
ruta_imagen_srnd = "SRvsND.png"

# Creamos la figura y el eje donde se dibujará todo
fig, ax = plt.subplots(figsize=(9, 10), dpi=150)
plt.style.use('default')
ax.set_facecolor('white')

# Definimos los límites exactos que ocupará la imagen de fondo en el gráfico:
# [xmin, xmax, ymin, ymax]
limites_grafico = [0.703, 0.711, 0.5120, 0.5132]

# Dibujamos la imagen de fondo en esas coordenadas
ax.imshow(ruta_imagen_srnd, extent=limites_grafico, aspect='auto', zorder=1)
# -------------------------
# 3. TIPO DE MAGMA (Plotly)
# -------------------------
# Dibujamos los datos reales encima de la imagen
sns.scatterplot(
    data=df,
    x='Sr87_Sr86',
    y='Nd143_Nd144',
    hue='Location',  # Un color distinto para cada isla/localidad
    ax=ax,
    s=110,  # Tamaño del punto para que destaque bien
    edgecolor='black',  # Borde negro para resaltar los puntos
    linewidth=0.8,
    alpha=0.9,  # Un poco de transparencia
    zorder=2  # Esto obliga a que los puntos queden por encima de la imagen
)

# Título y nombres de ejes
ax.set_title('Diagrama Sr vs Nd', fontsize=13, pad=15)
ax.set_xlabel('$^{87}$Sr / $^{86}$Sr', fontsize=12, fontweight='bold')
ax.set_ylabel('$^{143}$Nd / $^{144}$Nd', fontsize=12, fontweight='bold')

# Límites visibles del gráfico
ax.set_xlim(0.703, 0.711)
ax.set_ylim(0.5120, 0.5132)

# Hacemos que los ticks entren hacia dentro, como en gráficos de publicación
ax.tick_params(direction='in', top=True, right=True, labelsize=10)

# Colocamos la leyenda a la derecha
ax.legend(title='Isla / Localidad', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)

# Ajustamos el diseño para que no se corte nada
plt.tight_layout()

# Mostramos el gráfico dentro de Streamlit
st.pyplot(fig)

# -------------------------
# 4. La/Sm vs Sm/Yb (Plotly)
# -------------------------

# 1. Hacemos que Python calcule automáticamente las razones geoquímicas
df['La_Sm'] = df['La'] / df['Sm']
df['Sm_Yb'] = df['Sm'] / df['Yb']

# 2. Creamos el gráfico de dispersión interactivo con Plotly
fig = px.scatter(
    df,
    x='Sm_Yb',  # Eje X: indica mayor profundidad de fusión cuando el valor aumenta
    y='La_Sm',  # Eje Y: indica una fuente más enriquecida cuando el valor aumenta
    color='Location',  # Coloreamos por isla/localidad
    hover_name='Sample',  # Nombre de la muestra al pasar el mouse
    title='La/Sm vs Sm/Yb',
    labels={
        'Sm_Yb': 'Sm / Yb (A mayor valor, fusión más profunda)',
        'La_Sm': 'La / Sm (A mayor valor, fuente más enriquecida)',
        'Location': 'Isla'
    },
    template='plotly_white'  # Estilo visual limpio
)

# 3. Mejoramos la apariencia de los puntos
fig.update_traces(
    marker=dict(
        size=12,
        line=dict(width=1, color='black')
    ),
    selector=dict(mode='markers')
)

# 4. Mostramos el gráfico dentro de la página de Streamlit
st.plotly_chart(fig, use_container_width=True)
# -------------------------
# 5. OIB y MORB (Plotly)
# -------------------------

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# 1. Cargamos los datos desde el archivo Excel
df = pd.read_excel(archivo)
df.columns = df.columns.str.strip()

# Definimos los nombres de las columnas clave
nombre_columna_localidad = 'Location'
nombre_columna_muestra = 'Sample'

# 2. Valores de referencia universales (Sun & McDonough, 1989)
# Condrito: sirve para normalizar los elementos REE
condrito = {
    'La': 0.237, 'Ce': 0.613, 'Pr': 0.0928, 'Nd': 0.457, 'Sm': 0.148,
    'Eu': 0.0563, 'Gd': 0.199, 'Tb': 0.0361, 'Dy': 0.246, 'Ho': 0.0546,
    'Er': 0.160, 'Tm': 0.0247, 'Yb': 0.161, 'Lu': 0.0246
}

# Valores de referencia para OIB
oib_ref = {
    'La': 37, 'Ce': 80, 'Pr': 9.7, 'Nd': 38.5, 'Sm': 10,
    'Eu': 3, 'Gd': 7.62, 'Tb': 1.05, 'Dy': 5.6, 'Ho': 1.06,
    'Er': 2.62, 'Tm': 0.35, 'Yb': 2.16, 'Lu': 0.3
}

# Valores de referencia para N-MORB
morb_ref = {
    'La': 2.5, 'Ce': 7.5, 'Pr': 1.32, 'Nd': 7.3, 'Sm': 2.63,
    'Eu': 1.02, 'Gd': 3.68, 'Tb': 0.67, 'Dy': 4.55, 'Ho': 1.01,
    'Er': 2.97, 'Tm': 0.456, 'Yb': 3.05, 'Lu': 0.455
}

# Lista ordenada de elementos REE
elementos_ree = list(condrito.keys())

# 3. Limpiamos y normalizamos los datos
df_spider = df.copy()

# Convertimos a numérico, forzamos errores raros a NaN y quitamos ceros
for col in elementos_ree:
    if col in df_spider.columns:
        df_spider[col] = pd.to_numeric(df_spider[col], errors='coerce')
        df_spider[col] = df_spider[col].replace(0, np.nan)

# Normalizamos cada elemento respecto al condrito
for elemento in elementos_ree:
    if elemento in df_spider.columns:
        df_spider[elemento] = df_spider[elemento] / condrito[elemento]

# Reorganizamos los datos a formato largo para que Plotly los grafique mejor
df_melted = df_spider.melt(
    id_vars=[nombre_columna_muestra, nombre_columna_localidad],
    value_vars=[e for e in elementos_ree if e in df_spider.columns],
    var_name='Elemento',
    value_name='Concentracion_Normalizada'
).dropna(subset=['Concentracion_Normalizada'])

# 4. Creamos el gráfico base con las muestras
fig = px.line(
    df_melted,
    x='Elemento',
    y='Concentracion_Normalizada',
    color=nombre_columna_localidad,
    line_group=nombre_columna_muestra,
    hover_name=nombre_columna_muestra,
    title='<b>OIB y MORB</b>',
    log_y=True,  # Escala logarítmica en Y
    markers=True  # Dibuja puntos además de líneas
)

# Hacemos las líneas de las muestras más finas y semitransparentes
fig.update_traces(
    line=dict(width=1),
    opacity=0.4,
    marker=dict(size=4)
)

# 5. Calculamos y añadimos las líneas de referencia de OIB y N-MORB
oib_norm = [oib_ref[e] / condrito[e] for e in elementos_ree]
morb_norm = [morb_ref[e] / condrito[e] for e in elementos_ree]

# Línea de referencia OIB
fig.add_trace(go.Scatter(
    x=elementos_ree,
    y=oib_norm,
    mode='lines+markers',
    name='OIB (Referencia)',
    line=dict(color='red', width=4, dash='dash'),
    marker=dict(size=8, color='red', symbol='diamond')
))

# Línea de referencia N-MORB
fig.add_trace(go.Scatter(
    x=elementos_ree,
    y=morb_norm,
    mode='lines+markers',
    name='N-MORB (Referencia)',
    line=dict(color='blue', width=4, dash='dash'),
    marker=dict(size=8, color='blue', symbol='square')
))

# 6. Ajustamos la estética final del gráfico
fig.update_layout(
    xaxis_title='<b>Elementos de Tierras Raras (LREE -> HREE)</b>',
    yaxis_title='<b>Muestra</b>',
    template='plotly_white',
    hovermode='closest',
    width=950,
    height=600
)

# 7. Mostramos el gráfico en la página de Streamlit
st.plotly_chart(fig, use_container_width=True)
# -------------------------
# 6. TAS con % de Fusión (Plotly)
# -------------------------

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import base64

# 1. Cargamos los datos y calculamos el porcentaje de fusión parcial
df = pd.read_excel(archivo)

# Parámetros usados para estimar la fracción de fusión a partir de La
C0_La = 0.687
D_La = 0.01

# Calculamos la fracción de fusión y luego la convertimos a porcentaje
df['F_fraccion'] = (C0_La / df['La'] - D_La) / (1 - D_La)
df['F_porcentaje'] = (df['F_fraccion'] * 100).clip(lower=0.1, upper=30)

# 2. Clasificación geográfica: separamos el dominio occidental del resto
occidental = [
    'Isla Fernandina', 'Isla Isabela', 'Volcan Wolf', 'Volcan Darwin',
    'Volcan Alcedo', 'Sierra Negra', 'Cerro Azul', 'Volcan Ecuador',
    'Isla Tortuga', 'Roca Redonda'
]

# Creamos una columna nueva para identificar la región tectono-volcánica
df['Region'] = df['Location'].apply(
    lambda x: 'Occidental (Pluma Activa)' if x in occidental else 'Central / Oriental'
)

# 3. Preparamos los ejes del diagrama TAS
# Alkalis = Na2O + K2O
df['Alkalis'] = df['Na2O'] + df['K2O']

# Nos quedamos solo con filas útiles para este gráfico
df_tas = df.dropna(subset=['SiO2', 'Alkalis', 'F_porcentaje', 'Region']).copy()

# 4. Creamos el gráfico TAS
fig = px.scatter(
    df_tas,
    x='SiO2',
    y='Alkalis',
    color='F_porcentaje',  # El color representa el % de fusión
    color_continuous_scale='viridis',
    symbol='Region',  # La forma del punto diferencia el dominio geográfico
    hover_name='Sample',
    hover_data=['Location', 'La'],
    title='<b>Clasificación TAS con los % de Fusión Parcial</b>',
    labels={
        'SiO2': 'SiO2 (wt%)',
        'Alkalis': 'Na2O + K2O (wt%)',
        'F_porcentaje': '% Fusión',
        'Region': 'Dominio Geográfico'
    }
)

# 5. Cargamos la imagen de fondo del diagrama TAS
ruta_imagen = '/content/GALAPAGOS.csv/MyDrive/Diagrama tas.png'

try:
    with open(ruta_imagen, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    img_str = f"data:image/png;base64,{encoded_string}"

    # Insertamos la imagen como fondo del gráfico
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
except FileNotFoundError:
    pass

# 6. Ajustamos el encuadre y la estética final
fig.update_layout(
    xaxis_range=[35, 75],
    yaxis_range=[0, 16],
    template='plotly_white',
    plot_bgcolor='rgba(0,0,0,0)',  # Fondo transparente para que se vea la imagen
    coloraxis_colorbar=dict(title="<b>Fusión (%)</b>"),
    width=950,
    height=600
)

# Hacemos los puntos más visibles
fig.update_traces(
    marker=dict(
        size=12,
        line=dict(width=1, color='black')
    )
)

# 7. Mostramos el gráfico dentro de Streamlit
st.plotly_chart(fig, use_container_width=True)
# -------------------------
# 7. Cálculo de Fusión Parcial (Batch Melting)
# -------------------------

import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. Definimos las variables geoquímicas para La (manto primitivo)
C0_La = 0.687  # Concentración inicial de La en el manto
D_La = 0.01    # Coeficiente de partición global de La

# 2. Calculamos F (fracción de fusión) para todas las filas del dataframe
# Fórmula de fusión por lotes (batch melting): F = ((C0/Cl) - D) / (1 - D)
df['F_fraccion'] = (C0_La / df['La'] - D_La) / (1 - D_La)

# 3. Convertimos F a porcentaje
df['F_porcentaje'] = df['F_fraccion'] * 100

# 4. Limpiamos valores físicamente imposibles (0.1 % a 30 %)
df['F_porcentaje'] = df['F_porcentaje'].clip(lower=0.1, upper=30)

# 5. Calculamos el promedio de fusión parcial por isla/localidad
resumen_fusion = (
    df.groupby('Location')['F_porcentaje']
      .mean()
      .sort_values(ascending=False)
      .reset_index()
)

# 6. Mejoramos la presentación de la tabla
resumen_fusion.rename(
    columns={
        'Location': 'Isla / Localidad',
        'F_porcentaje': 'Fusión Parcial Promedio (%)'
    },
    inplace=True
)

resumen_fusion['Fusión Parcial Promedio (%)'] = (
    resumen_fusion['Fusión Parcial Promedio (%)'].round(2)
)

# 7. Mostramos la tabla en Streamlit
st.subheader("Promedio de fusión parcial por isla")
st.dataframe(resumen_fusion, use_container_width=True)
# -------------------------
# 8. TAS + Fusión Parcial (Plotly)
# -------------------------

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. Cargamos los datos
df = pd.read_excel(archivo)

# 2. Filtramos solo las filas que tienen todos los datos necesarios
# Esto evita errores en los cálculos y en el gráfico
df_tas = df.dropna(subset=['SiO2', 'Na2O', 'K2O', 'La']).copy()

# 3. Cálculos geoquímicos
# Eje Y: suma de álcalis
df_tas['Alkalis'] = df_tas['Na2O'] + df_tas['K2O']

# Cálculo del porcentaje de fusión parcial usando La
C0_La = 0.687  # Concentración inicial en manto primitivo
D_La = 0.01    # Coeficiente de partición global

df_tas['F_fraccion'] = (C0_La / df_tas['La'] - D_La) / (1 - D_La)
df_tas['F_porcentaje'] = df_tas['F_fraccion'] * 100

# Recortamos valores físicamente improbables para que no dañen la escala de color
df_tas['F_porcentaje'] = df_tas['F_porcentaje'].clip(lower=0.1, upper=25)

# 4. Creamos el gráfico interactivo TAS + Fusión
fig = px.scatter(
    df_tas,
    x='SiO2',
    y='Alkalis',
    color='F_porcentaje',  # El color representa el % de fusión parcial
    color_continuous_scale='Plasma_r',  # Escala invertida: tonos más cálidos para menor fusión
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

# 5. Añadimos la línea divisoria alcalina / subalcalina
# Referencia: Irvine & Baragar (1971)
x_linea = np.linspace(40, 60, 50)
y_linea = (0.37 * x_linea) - 14.43

fig.add_trace(go.Scatter(
    x=x_linea,
    y=y_linea,
    mode='lines',
    name='Límite Alcalino',
    line=dict(color='black', width=2, dash='dash')
))

# 6. Mejoramos la apariencia de los puntos
fig.update_traces(
    marker=dict(
        size=12,
        line=dict(width=1, color='black')
    )
)

# 7. Ajustamos la vista del gráfico para enfocar el campo basáltico
fig.update_layout(
    xaxis_range=[43, 54],
    yaxis_range=[0.5, 7],
    coloraxis_colorbar=dict(title="<b>Fusión (%)</b>"),
    width=950,
    height=600
)

# 8. Mostramos el gráfico en Streamlit
st.plotly_chart(fig, use_container_width=True)
# -------------------------
# 9. TAS y Evolución Magmática (Plotly)
# -------------------------

import plotly.express as px
import pandas as pd
from PIL import Image

# 1. Filtramos solo las muestras que tienen los datos necesarios para el TAS
df_tas = df.dropna(subset=['SiO2', 'Na2O', 'K2O']).copy()

# 2. Calculamos los álcalis totales
df_tas['Alkalis'] = df_tas['Na2O'] + df_tas['K2O']

# 3. Creamos el gráfico interactivo
fig = px.scatter(
    df_tas,
    x='SiO2',
    y='Alkalis',
    color='Location',  # Cada isla/localidad tendrá su propio color
    hover_name='Sample',  # Nombre de la muestra al pasar el mouse
    title='<b>Clasificación TAS y Evolución Magmática</b>',
    labels={
        'SiO2': 'SiO2 (wt%)',
        'Alkalis': 'Na2O + K2O (wt%)',
        'Location': 'Localidad'
    },
    template='plotly_white'
)

# 4. Definimos la ruta de la imagen del diagrama TAS
ruta_imagen = '/content/GALAPAGOS.csv/MyDrive/Diagrama tas.png'

# 5. Intentamos cargar la imagen como fondo del gráfico
try:
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
            layer="below"  # La imagen queda detrás de los puntos
        )
    )
except FileNotFoundError:
    pass

# 6. Ajustamos el encuadre y el estilo del gráfico
fig.update_layout(
    xaxis_range=[35, 75],
    yaxis_range=[0, 16],
    template='plotly_white',
    width=900,
    height=600
)

# 7. Mejoramos la apariencia de los puntos
fig.update_traces(
    marker=dict(
        size=11,
        line=dict(width=1, color='black')
    )
)

# 8. Mostramos el gráfico en Streamlit
st.plotly_chart(fig, use_container_width=True)
# -------------------------
# 10. Clustering K-Means (Pluma vs Manto)
# -------------------------

# 1. Importamos las herramientas de Machine Learning
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import plotly.express as px

# 2. Seleccionamos las variables clave para detectar la pluma
# Combinamos isótopos radiogénicos y elementos traza
columnas_ml = ['Sr87_Sr86', 'Nd143_Nd144', 'La', 'Sm', 'Yb']

# Creamos una copia limpia solo con muestras completas en esas columnas
df_ml = df.dropna(subset=columnas_ml).copy()

# 3. Extraemos los valores numéricos que usará el algoritmo
X = df_ml[columnas_ml]

# 4. Escalamos los datos (media 0, desviación estándar 1)
scaler = StandardScaler()
X_escalado = scaler.fit_transform(X)

# 5. Definimos el modelo K-Means
# Buscamos 3 grupos principales:
#   - Uno asociado a la pluma
#   - Otro a manto empobrecido
#   - Otro potencialmente de transición
kmeans = KMeans(
    n_clusters=3,
    random_state=42,
    n_init=10
)

# 6. Entrenamos el modelo y añadimos el clúster a la tabla
df_ml['Cluster_IA'] = kmeans.fit_predict(X_escalado)

# Convertimos el número de clúster a texto (categoría) para graficarlo mejor
df_ml['Cluster_IA'] = 'Grupo Químico ' + df_ml['Cluster_IA'].astype(str)

print("¡Modelo K-means entrenado con éxito!")
print(f"El algoritmo analizó {len(df_ml)} muestras y encontró 3 firmas químicas distintas.")
# -------------------------
# 11. Interpretación Geológica de Clústeres (Plotly)
# -------------------------

# 1. Definimos el significado geológico de cada grupo químico
nombres_geologicos = {
    'Grupo Químico 0': 'OIB',
    'Grupo Químico 1': 'MORB',
    'Grupo Químico 2': 'Zona de Transición'
}

# 2. Aplicamos ese cambio de nombre a la tabla
df_ml['Interpretacion_Geologica'] = df_ml['Cluster_IA'].map(nombres_geologicos)

# 3. Graficamos los clústeres usando los nombres geológicos reales
fig = px.scatter(
    df_ml,
    x='Sr87_Sr86',
    y='Nd143_Nd144',
    color='Interpretacion_Geologica',  # Usamos la columna con interpretación geológica
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

# 4. Mejoramos la apariencia de los puntos
fig.update_traces(
    marker=dict(
        size=14,
        line=dict(width=1, color='black')
    )
)

# 5. Mostramos el gráfico en Streamlit
st.plotly_chart(fig, use_container_width=True)
