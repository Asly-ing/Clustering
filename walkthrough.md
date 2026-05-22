# Walkthrough: Sistema de Evaluación de Retención (SER)

He completado el desarrollo de la aplicación web interactiva **SER** en Streamlit siguiendo estrictamente la arquitectura solicitada.

## Resumen de la Implementación

1. **Gestión de Datos (`data/synthetic_data.py`)**: 
   - Se ha implementado la generación de un dataset sintético de 300 estudiantes con correlaciones lógicas entre sus variables para simular la probabilidad de ser "desertor".

2. **Preprocesamiento (`modules/preprocessing.py`)**:
   - Funcionalidad para seleccionar técnicas de normalización (Min-Max o Z-Score) y para tratar valores nulos de forma robusta.
   - Las variables categóricas se codifican automáticamente empleando `LabelEncoder` de Scikit-Learn.

3. **Clustering (`modules/clustering.py`)**:
   - Se han desarrollado tres estrategias: **K-Means**, **Jerárquico** (Ward) y **DBSCAN**.
   - Integración con gráficas dinámicas para ayudar a seleccionar los hiperparámetros (Método del codo, coeficiente de silueta y k-distancias).

4. **Validación Automática (`modules/validation.py`)**:
   - Para cada modelo ejecutado, se calculan 3 métricas de validación: **Silueta**, **Davies-Bouldin** y **Calinski-Harabasz**.
   - Se incluyó un algoritmo para rankear automáticamente el modelo que ofrezca las mejores métricas combinadas.

5. **Perfiles y Estrategias (`modules/strategies.py`)**:
   - Los estudiantes se dividen en diferentes perfiles (Vulnerabilidad, Riesgo Bajo, etc.) basados en las estadísticas de sus clusters.
   - A cada perfil se le asignan estrategias de retención precisas, mostrando alertas visuales sobre su nivel de riesgo.

6. **Exportación (`modules/export.py`)**:
   - Se utiliza `fpdf2` para generar un PDF pulido y profesional que extrae y formatea las métricas y los perfiles directamente desde Streamlit.

7. **Interfaz Principal (`app.py`)**:
   - UI profesional con colores institucionales (azul oscuro y dorado).
   - Uso intensivo de las gráficas de Plotly para asegurar una visualización interactiva (diagramas de cajas para variables y preprocesamiento, scatter PCA en 2D, line charts para k-means).

## Pasos para la Ejecución

> [!TIP]
> Debido a que ejecutaste directamente el archivo `app.py` mediante Python (lo que generó un error de contexto porque debe ejecutarse mediante Streamlit), te recomiendo utilizar el comando original desde la terminal.

La aplicación ahora mismo **ya se encuentra ejecutándose** en segundo plano mediante `python -m streamlit run app.py` y es accesible desde tu navegador a través de [http://localhost:8501](http://localhost:8501).

Si la aplicación en el futuro se detiene, sólo debes ubicarse en la carpeta `C:\Users\Asly Acuña\Documents\Clustering` y ejecutar desde tu terminal:
```bash
python -m streamlit run app.py
```
*(Nota: usamos `python -m streamlit` en lugar de sólo `streamlit` para evitar problemas con las variables de entorno PATH de Windows).*
