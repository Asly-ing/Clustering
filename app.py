import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import scipy.cluster.hierarchy as shc
import matplotlib.pyplot as plt
import seaborn as sns
import io
import os

from data.synthetic_data import generate_synthetic_data
from modules.preprocessing import preprocess_data
from modules.clustering import evaluate_kmeans_k, run_kmeans, run_hierarchical, get_k_distances, run_dbscan, reduce_to_2d
from modules.validation import calculate_metrics, interpret_silhouette, rank_algorithms
from modules.strategies import generate_profiles
from modules.export import generate_pdf_report

# Configuracion de Pagina
st.set_page_config(page_title="SER - Evaluación de Retención", page_icon="🎓", layout="wide")

# Estilos CSS Personalizados
st.markdown("""
<style>
    :root {
        --primary: #1E3A5F;
        --secondary: #C9A84C;
        --bg: #0E1117;
        --text: #FAFAFA;
    }
    .header-title {
        color: var(--primary);
        font-weight: 800;
        margin-bottom: 0px;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.1);
    }
    .header-subtitle {
        color: var(--secondary);
        font-weight: 600;
        margin-top: 0px;
        margin-bottom: 2rem;
    }
    .stProgress .st-bo {
        background-color: var(--secondary);
    }
    .profile-card {
        background-color: #1E1E1E;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid var(--secondary);
        margin-bottom: 1rem;
    }
    .badge-alto { background-color: #ff4b4b; color: white; padding: 3px 8px; border-radius: 12px; font-weight: bold; }
    .badge-medio { background-color: #faca2b; color: black; padding: 3px 8px; border-radius: 12px; font-weight: bold; }
    .badge-bajo { background-color: #00cc96; color: white; padding: 3px 8px; border-radius: 12px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Header
col1, col2 = st.columns([1, 10])
with col1:
    st.markdown("<h1 style='text-align: center; color: #C9A84C;'>🎓</h1>", unsafe_allow_html=True)
with col2:
    st.markdown("<h1 class='header-title'>SER</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='header-subtitle'>Sistema de Evaluación de Retención Estudiantil</h3>", unsafe_allow_html=True)

# State initialization
if 'df_raw' not in st.session_state:
    st.session_state.df_raw = None
if 'df_processed' not in st.session_state:
    st.session_state.df_processed = None
if 'encoders' not in st.session_state:
    st.session_state.encoders = None
if 'scaler' not in st.session_state:
    st.session_state.scaler = None
if 'clustering_results' not in st.session_state:
    # dict with algo names as keys, values: {'labels': labels, 'model': model, 'metrics': metrics}
    st.session_state.clustering_results = {}
if 'best_algo' not in st.session_state:
    st.session_state.best_algo = None

# Sidebar Navigation
st.sidebar.title("Navegación")
section = st.sidebar.radio("Ir a:", [
    "1. Carga de Datos", 
    "2. Preprocesamiento", 
    "3. Clustering", 
    "4. Evaluación y Validación", 
    "5. Estrategias de Retención"
])

# ProgressBar
progress_map = {
    "1. Carga de Datos": 0.2,
    "2. Preprocesamiento": 0.4,
    "3. Clustering": 0.6,
    "4. Evaluación y Validación": 0.8,
    "5. Estrategias de Retención": 1.0
}
st.sidebar.progress(progress_map[section])

# ----------------- SECTION 1: CARGA DE DATOS -----------------
if section == "1. Carga de Datos":
    st.header("1. Carga de Datos")
    
    uploaded_file = st.file_uploader("Sube tu archivo (CSV o Excel)", type=['csv', 'xlsx'])
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cargar Datos de Archivo") and uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                st.session_state.df_raw = df
                st.success("Archivo cargado exitosamente.")
            except Exception as e:
                st.error(f"Error al cargar archivo: {e}")
                
    with col2:
        if st.button("Generar Dataset Sintético", help="Carga datos generados automáticamente para 300 estudiantes."):
            st.session_state.df_raw = generate_synthetic_data()
            st.success("Dataset sintético generado y cargado.")
            
    if st.session_state.df_raw is not None:
        df = st.session_state.df_raw
        st.subheader("Vista Previa (Primeros 10 registros)")
        st.dataframe(df.head(10), use_container_width=True)
        
        st.subheader("Estadísticas Descriptivas")
        st.dataframe(df.describe().T, use_container_width=True)
        
        st.subheader("Distribución de Variables")
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        cat_cols = df.select_dtypes(exclude=np.number).columns.tolist()
        
        var_to_plot = st.selectbox("Selecciona una variable para visualizar", df.columns)
        
        if var_to_plot in numeric_cols:
            fig = px.histogram(df, x=var_to_plot, marginal="box", color_discrete_sequence=['#1E3A5F'])
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig = px.bar(df[var_to_plot].value_counts().reset_index(), x='count', y=var_to_plot, orientation='h', color_discrete_sequence=['#C9A84C'])
            st.plotly_chart(fig, use_container_width=True)

# ----------------- SECTION 2: PREPROCESAMIENTO -----------------
elif section == "2. Preprocesamiento":
    st.header("2. Preprocesamiento")
    if st.session_state.df_raw is None:
        st.warning("Por favor, carga los datos en la sección 1 primero.")
    else:
        df = st.session_state.df_raw
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("Técnica de Normalización")
            norm_technique = st.radio("Selecciona:", ["Normalización Min-Max", "Estandarización Z-Score"], 
                                      help="Min-Max escala de 0 a 1. Z-Score centra en 0 con desv. est. de 1.")
        with col2:
            st.subheader("Variables a Incluir")
            all_cols = [c for c in df.columns if c != 'desertor']
            default_cols = [c for c in all_cols if c in ['promedio_acumulado', 'materias_reprobadas', 'semestre_actual', 'estrato_socioeconomico', 'tipo_financiamiento', 'modalidad_ingreso']]
            selected_vars = st.multiselect("Variables para clustering:", all_cols, default=default_cols)
        with col3:
            st.subheader("Tratamiento de Nulos")
            null_strategy = st.radio("Acción:", ["Imputación por mediana/moda", "Eliminar filas con nulos"])
            
        if st.button("Aplicar Preprocesamiento"):
            with st.spinner("Procesando datos..."):
                if len(selected_vars) < 2:
                    st.error("Selecciona al menos 2 variables para el clustering.")
                else:
                    df_processed, encoders, scaler = preprocess_data(df, selected_vars, norm_technique, null_strategy)
                    st.session_state.df_processed = df_processed
                    st.session_state.encoders = encoders
                    st.session_state.scaler = scaler
                    st.session_state.selected_vars = selected_vars
                    
                    st.success("Preprocesamiento completado exitosamente.")
                    
        if st.session_state.df_processed is not None:
            st.subheader("Datos Transformados")
            st.dataframe(st.session_state.df_processed.head(), use_container_width=True)
            
            st.subheader("Comparación de Distribuciones (Boxplots)")
            var_compare = st.selectbox("Variable numérica para comparar:", [c for c in st.session_state.selected_vars if df[c].dtype in ['int64', 'float64']])
            
            c1, c2 = st.columns(2)
            with c1:
                fig1 = px.box(df, y=var_compare, title="Antes", color_discrete_sequence=['#1E3A5F'])
                st.plotly_chart(fig1, use_container_width=True)
            with c2:
                fig2 = px.box(st.session_state.df_processed, y=var_compare, title="Después (Transformada)", color_discrete_sequence=['#C9A84C'])
                st.plotly_chart(fig2, use_container_width=True)

# ----------------- SECTION 3: CLUSTERING -----------------
elif section == "3. Clustering":
    st.header("3. Clustering")
    if st.session_state.df_processed is None:
        st.warning("Por favor, aplica el preprocesamiento en la sección 2 primero.")
    else:
        X = st.session_state.df_processed.values
        
        tab1, tab2, tab3 = st.tabs(["K-Means", "Clustering Jerárquico", "DBSCAN"])
        
        with tab1:
            st.subheader("K-Means")
            k_range = st.slider("Rango para determinar k óptimo", 2, 8, (2, 8))
            
            if st.button("Determinar k óptimo"):
                with st.spinner("Calculando métricas para K-Means..."):
                    inertias, silhouettes, metrics_df = evaluate_kmeans_k(X, range(k_range[0], k_range[1]+1))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        fig_elbow = px.line(x=range(k_range[0], k_range[1]+1), y=inertias, markers=True, title="Método del Codo (Inercia)", labels={'x':'k', 'y':'Inercia'})
                        st.plotly_chart(fig_elbow, use_container_width=True)
                    with col2:
                        fig_sil = px.line(x=range(k_range[0], k_range[1]+1), y=silhouettes, markers=True, title="Coeficiente de Silueta", labels={'x':'k', 'y':'Silueta'})
                        st.plotly_chart(fig_sil, use_container_width=True)
                        
                    st.dataframe(metrics_df, use_container_width=True)
            
            st.markdown("---")
            k_final = st.slider("Selecciona k final para K-Means", 2, 10, 3)
            if st.button("Ejecutar K-Means"):
                with st.spinner("Ejecutando K-Means..."):
                    labels, model = run_kmeans(X, k_final)
                    metrics = calculate_metrics(X, labels)
                    st.session_state.clustering_results['K-Means'] = {'labels': labels, 'model': model, 'metrics': metrics}
                    st.success(f"K-Means ejecutado. Se encontraron {k_final} clusters.")
                    
        with tab2:
            st.subheader("Clustering Jerárquico (Ward)")
            
            if st.button("Mostrar Dendrograma"):
                with st.spinner("Generando dendrograma..."):
                    fig, ax = plt.subplots(figsize=(10, 5))
                    plt.title("Dendrograma")
                    dend = shc.dendrogram(shc.linkage(X, method='ward'), ax=ax, truncate_mode='level', p=5)
                    st.pyplot(fig)
            
            n_clusters_hc = st.slider("Número de clusters (corte del dendrograma)", 2, 8, 3)
            if st.button("Ejecutar Clustering Jerárquico"):
                with st.spinner("Ejecutando Jerárquico..."):
                    labels, model = run_hierarchical(X, n_clusters_hc)
                    metrics = calculate_metrics(X, labels)
                    st.session_state.clustering_results['Jerarquico'] = {'labels': labels, 'model': model, 'metrics': metrics}
                    st.success(f"Clustering Jerárquico ejecutado. Se encontraron {n_clusters_hc} clusters.")
                    
        with tab3:
            st.subheader("DBSCAN")
            col1, col2 = st.columns(2)
            with col1:
                eps_val = st.slider("Epsilon", 0.1, 2.0, 0.5, 0.1)
            with col2:
                min_samples = st.slider("Min Samples", 2, 10, 5)
                
            if st.button("Mostrar curva k-distancias"):
                distances = get_k_distances(X, min_samples)
                fig = px.line(y=distances, title=f"K-distancias (k={min_samples})", labels={'index':'Puntos ordenados', 'y':'Distancia'})
                st.plotly_chart(fig, use_container_width=True)
                
            if st.button("Ejecutar DBSCAN"):
                with st.spinner("Ejecutando DBSCAN..."):
                    labels, model = run_dbscan(X, eps_val, min_samples)
                    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
                    n_noise = list(labels).count(-1)
                    
                    if n_clusters == 0:
                        st.warning("DBSCAN clasificó todos los puntos como ruido. Ajusta los parámetros.")
                    else:
                        metrics = calculate_metrics(X, labels)
                        st.session_state.clustering_results['DBSCAN'] = {'labels': labels, 'model': model, 'metrics': metrics}
                        st.success(f"DBSCAN ejecutado. Clusters: {n_clusters}, Puntos ruido: {n_noise}")

        # VISUALIZACIÓN DE RESULTADOS
        st.markdown("---")
        st.subheader("Resultados Recientes")
        
        if st.session_state.clustering_results:
            algo_to_view = st.selectbox("Ver resultados de:", list(st.session_state.clustering_results.keys()))
            labels = st.session_state.clustering_results[algo_to_view]['labels']
            
            col1, col2 = st.columns([2, 1])
            with col1:
                # PCA 2D
                df_pca = reduce_to_2d(X)
                df_pca['Cluster'] = labels.astype(str)
                fig_pca = px.scatter(df_pca, x='PCA1', y='PCA2', color='Cluster', title=f"Visualización 2D (PCA) - {algo_to_view}", 
                                     color_discrete_sequence=px.colors.qualitative.Plotly)
                st.plotly_chart(fig_pca, use_container_width=True)
                
            with col2:
                st.write("Conteo de estudiantes por cluster:")
                unique, counts = np.unique(labels, return_counts=True)
                count_df = pd.DataFrame({'Cluster': unique, 'Estudiantes': counts})
                st.dataframe(count_df, use_container_width=True)

# ----------------- SECTION 4: EVALUACIÓN Y VALIDACIÓN -----------------
elif section == "4. Evaluación y Validación":
    st.header("4. Evaluación y Validación")
    
    if not st.session_state.clustering_results:
        st.warning("No hay algoritmos ejecutados. Ve a la sección 3 y ejecuta al menos uno.")
    else:
        # Build comparison table
        metrics_dict = {}
        table_data = []
        for algo, res in st.session_state.clustering_results.items():
            if res['metrics']:
                metrics_dict[algo] = res['metrics']
                row = {'Algoritmo': algo}
                row.update(res['metrics'])
                table_data.append(row)
                
        if not table_data:
            st.warning("No se pudieron calcular métricas válidas (posiblemente porque solo hay ruido o 1 cluster).")
        else:
            df_metrics = pd.DataFrame(table_data).set_index('Algoritmo')
            st.subheader("Tabla Comparativa")
            st.dataframe(df_metrics.style.highlight_max(subset=['Silueta', 'Calinski-Harabasz'], color='lightgreen')
                                         .highlight_min(subset=['Davies-Bouldin'], color='lightgreen'), 
                         use_container_width=True)
            
            # Interpretación y Selección de Mejor Algoritmo
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Interpretación de Silueta (Mejor resultado):**")
                best_sil = df_metrics['Silueta'].max()
                st.info(f"Max Silueta ({best_sil}): {interpret_silhouette(best_sil)}")
                
            with col2:
                if st.button("Seleccionar Mejor Algoritmo"):
                    best_a = rank_algorithms(metrics_dict)
                    st.session_state.best_algo = best_a
                    st.success(f"El mejor algoritmo según el ranking ponderado es: **{best_a}**")
                    
            algo_to_analyze = st.session_state.best_algo if st.session_state.best_algo else list(st.session_state.clustering_results.keys())[0]
            st.markdown(f"### Análisis Detallado: {algo_to_analyze}")
            
            labels = st.session_state.clustering_results[algo_to_analyze]['labels']
            
            # Heatmap de centroides
            # We construct a dataframe with processed features to find centroids
            df_proc = pd.DataFrame(st.session_state.df_processed.values, columns=st.session_state.selected_vars)
            df_proc['Cluster'] = labels
            
            centroids = df_proc[df_proc['Cluster'] != -1].groupby('Cluster').mean()
            fig_heat = px.imshow(centroids, text_auto=True, aspect="auto", title="Heatmap de Variables Promedio por Cluster", color_continuous_scale='Blues')
            st.plotly_chart(fig_heat, use_container_width=True)
            
            # Boxplots
            st.write("**Distribución de Variables por Cluster**")
            var_box = st.selectbox("Variable:", st.session_state.selected_vars, key='box_eval')
            fig_box = px.box(df_proc, x='Cluster', y=var_box, color='Cluster', color_discrete_sequence=px.colors.qualitative.Plotly)
            st.plotly_chart(fig_box, use_container_width=True)

# ----------------- SECTION 5: ESTRATEGIAS DE RETENCIÓN -----------------
elif section == "5. Estrategias de Retención":
    st.header("5. Estrategias de Retención")
    
    if not st.session_state.clustering_results:
        st.warning("Ejecuta al menos un algoritmo de clustering en la sección 3.")
    else:
        algo = st.session_state.best_algo if st.session_state.best_algo else list(st.session_state.clustering_results.keys())[0]
        st.info(f"Mostrando perfiles basados en el modelo: **{algo}**")
        
        labels = st.session_state.clustering_results[algo]['labels']
        
        # Necesitamos el dataframe original pero alineado con las filas procesadas.
        # Si eliminamos nulos, los índices deben coincidir.
        idx = st.session_state.df_processed.index
        df_orig_aligned = st.session_state.df_raw.loc[idx]
        
        df_proc = pd.DataFrame({'cluster': labels}, index=idx)
        
        profiles = generate_profiles(df_orig_aligned, df_proc, 'cluster')
        
        col1, col2 = st.columns([3, 1])
        with col2:
            metrics_to_export = st.session_state.clustering_results[algo]['metrics']
            if st.button("Exportar Informe PDF", type="primary"):
                with st.spinner("Generando PDF..."):
                    pdf_path = generate_pdf_report(profiles, metrics_to_export, algo)
                    with open(pdf_path, "rb") as pdf_file:
                        pdf_bytes = pdf_file.read()
                    st.download_button(label="📥 Descargar PDF", data=pdf_bytes, file_name="Reporte_SER.pdf", mime='application/pdf')
                    
        with col1:
            for p in profiles:
                # Determinar clase del badge
                badge_class = f"badge-{p['risk'].lower()}"
                
                html_card = f"""
                <div class="profile-card">
                    <h3 style="margin-top:0;">Cluster {p['cluster']} - {p['name']}</h3>
                    <p><span class="{badge_class}">Riesgo {p['risk']}</span> • Estudiantes: {p['size']}</p>
                    <hr style="border-color: #333;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.9em; margin-bottom: 1rem;">
                        <div><b>Promedio:</b> {p['stats']['Promedio Acumulado']}</div>
                        <div><b>Reprobadas:</b> {p['stats']['Materias Reprobadas']}</div>
                        <div><b>Estrato:</b> {p['stats']['Estrato']}</div>
                        <div><b>Semestre:</b> {p['stats']['Semestre']}</div>
                        <div><b>Financiamiento:</b> {p['stats']['Financiamiento Predominante']}</div>
                    </div>
                    <b>Estrategias Recomendadas:</b>
                    <ul>
                        <li>{p['strategies'][0]}</li>
                        <li>{p['strategies'][1]}</li>
                        <li>{p['strategies'][2]}</li>
                    </ul>
                </div>
                """
                st.markdown(html_card, unsafe_allow_html=True)
