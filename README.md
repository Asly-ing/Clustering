# Manual de Usuario: SER - Sistema de Evaluación de Retención Estudiantil

Bienvenido al manual de uso del aplicativo **SER**. Esta guía te explicará paso a paso cómo iniciar y utilizar la plataforma para identificar perfiles de estudiantes y generar estrategias de retención.

---

## Parte 1: Iniciar la Aplicación

1. **Abrir la Terminal:**
   Abre tu terminal de comandos (Símbolo del sistema, PowerShell o la terminal integrada de tu editor de código como VS Code).

2. **Navegar a la Carpeta del Proyecto:**
   Asegúrate de estar en la carpeta donde está el código del proyecto.
   ```bash
   cd "C:\Users\Asly Acuña\Documents\Clustering"
   ```

3. **Ejecutar el Servidor:**
   Escribe el siguiente comando y presiona Enter:
   ```bash
   python -m streamlit run app.py
   ```
   *Nota: Se abrirá automáticamente una pestaña en tu navegador web. Si no lo hace, abre tu navegador y entra a `http://localhost:8501`.*

---

## Parte 2: Uso de la Plataforma

La aplicación está dividida en 5 secciones en la barra lateral izquierda. Debes seguirlas en orden:

### Paso 1: Carga de Datos
1. Ve a la sección **"1. Carga de Datos"** en el menú izquierdo.
2. Tienes dos opciones:
   - **Subir un archivo:** Si tienes tu propia base de datos (Excel o CSV), arrástrala a la caja que dice "Sube tu archivo".
   - **Generar Dataset Sintético:** Haz clic en este botón si no tienes datos y quieres probar el sistema con datos de prueba autogenerados (300 estudiantes).
3. Revisa la tabla de vista previa y las gráficas interactivas que aparecen para entender tus datos.

### Paso 2: Preprocesamiento
1. Ve a **"2. Preprocesamiento"**.
2. Selecciona la **Técnica de Normalización** (recomendado: Estandarización Z-Score para algoritmos como K-Means).
3. Deja marcadas las variables que deseas que la Inteligencia Artificial analice.
4. Elige cómo tratar los valores vacíos (Nulos).
5. Haz clic en el botón **"Aplicar Preprocesamiento"**. 
6. Compara los diagramas de caja (boxplots) que aparecen abajo para ver cómo cambiaron los datos tras normalizarlos.

### Paso 3: Clustering (Inteligencia Artificial)
1. Ve a **"3. Clustering"**.
2. Verás 3 pestañas: **K-Means**, **Clustering Jerárquico** y **DBSCAN**.
3. **Para K-Means (Ejemplo recomendado):**
   - Usa el botón **"Determinar k óptimo"** para ver los gráficos del método del codo y silueta. Esto te dirá cuántos grupos (clusters) existen de forma natural en los datos.
   - Ajusta el deslizador a ese número ideal (por ejemplo, 3 o 4).
   - Haz clic en **"Ejecutar K-Means"**.
4. Repite el proceso para Jerárquico o DBSCAN si quieres comparar algoritmos.
5. Al final de la página, verás un gráfico 2D (PCA) interactivo con los grupos creados.

### Paso 4: Evaluación y Validación
1. Ve a **"4. Evaluación y Validación"**.
2. Observa la **Tabla Comparativa**. Aquí la aplicación evalúa matemáticamente qué tan bien se crearon los grupos.
3. Haz clic en el botón **"Seleccionar Mejor Algoritmo"**. El sistema elegirá automáticamente el que tuvo mejor desempeño general.
4. Revisa el "Heatmap" (Mapa de calor) para entender qué caracteriza a cada cluster (ej: qué cluster tiene promedios más bajos).

### Paso 5: Estrategias de Retención
1. Ve a **"5. Estrategias de Retención"**.
2. El sistema cargará unas "Tarjetas de Perfil" para cada grupo descubierto por el mejor algoritmo.
3. Cada tarjeta incluye:
   - Nombre automático del perfil (ej: "Perfil de Alta Vulnerabilidad").
   - Nivel de riesgo (ALTO, MEDIO, BAJO).
   - 3 Estrategias accionables recomendadas por el sistema.
4. **Generar Informe:** Haz clic en el botón azul **"📥 Descargar PDF"** para exportar un reporte ejecutivo con todos estos hallazgos para presentar a directivos.

---
**Tip:** Si deseas detener la aplicación, ve a tu terminal y presiona `Ctrl + C`.
