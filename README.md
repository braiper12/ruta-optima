## **Métodos de aprendizaje supervisado**

### **Actividad #3**
**Curso** Inteligencia Artificial      
**Estudiantes** 
- Edwin Andres Legro Agudelo (elegroag@estudiante.ibero.edu.co)    
- Braian Alejandro Perez Castillo (baperezc@estudiante.ibero.edu.co)    

**Facultad** Ingenieria De Software    
**Universidad Iberoamercicana**     
**Sistema Inteligente de Predicción de Rutas de Transporte Masivo**

**DataSet**  
[Descargar DataSet dataset_transporte_enriquecido.json](./dataset_transporte_enriquecido.json)

### Introducción

Se desarrolla un sistema de aprendizaje automático en Python que, utilizando datos históricos de rutas de transporte masivo, predice y analiza patrones de viaje para optimizar la planificación de rutas. El sistema procesa datos enriquecidos de estaciones y rutas históricas para generar insights valiosos sobre el comportamiento del sistema de transporte.

### Preparación
Es necesario preparar el ambiente de trabajo e instalar las librerías y dependencias necesarias para la actividad. Se puede utilizar anaconda/miniconda o pip con Python 3.10:

```bash
conda create --name ruta-optima python=3.10
conda activate ruta-optima
conda install pandas numpy scikit-learn matplotlib seaborn -c conda-forge
```

### Tecnologías utilizadas:

+ Python: Lenguaje de programación principal para la implementación del sistema.
+ JSON: Formato de datos para almacenar la información histórica de rutas y estaciones.
+ Pandas: Librería principal para el análisis y manipulación de datos, utilizada para procesar los datasets de rutas y estaciones.
+ NumPy: Biblioteca para computación científica y manipulación de arrays.
+ Scikit-learn: Framework de machine learning para el análisis predictivo.
+ Matplotlib/Seaborn: Librerías para la visualización de datos y resultados del análisis.
+ RandomForestRegressor: Algoritmo de machine learning para la predicción de tiempo de viaje.
+ OneHotEncoder: Algoritmo de machine learning para la codificación de variables categóricas.
+ ColumnTransformer: Algoritmo de machine learning para la transformación de variables.
+ Pipeline: Algoritmo de machine learning para la creación de pipelines de machine learning.
+ GridSearchCV: Algoritmo de machine learning para la búsqueda de hiperparámetros.
+ train_test_split: Algoritmo de machine learning para la división de datos.
+ mean_squared_error: Algoritmo de machine learning para el cálculo del error cuadrático medio.
+ r2_score: Algoritmo de machine learning para el cálculo del coeficiente de determinación.
+ mean_absolute_error: Algoritmo de machine learning para el cálculo del error absoluto medio.
+ StandardScaler: Algoritmo de machine learning para la normalización de variables.

### Implementación:

1. Carga y Preprocesamiento de Datos:
   + Lectura de datos JSON enriquecidos con información histórica
   + Transformación de datos a DataFrames de Pandas para su análisis
   + Limpieza y preparación de datos para el modelado

2. Análisis Exploratorio de Datos (EDA):
   + Análisis estadístico de patrones de viaje
   + Visualización de distribuciones y correlaciones
   + Identificación de tendencias y anomalías

3. Modelado y Predicción:
   + Selección y entrenamiento de modelos de machine learning
   + Validación y evaluación de resultados
   + Ajuste de hiperparámetros para optimización

4. Visualización de Resultados:
   + Generación de gráficas y visualizaciones interactivas
   + Presentación de métricas de rendimiento
   + Interpretación de predicciones y patrones descubiertos

### Estructura de Datos

El sistema trabaja con dos conjuntos principales de datos:

1. Rutas Históricas:
   + Información temporal de viajes
   + Métricas de utilización
   + Patrones de demanda

2. Estaciones:
   + Ubicación y características
   + Capacidad y servicios
   + Métricas operativas

## Resultados

El análisis de los datos ha permitido:

1. Identificar patrones de uso del sistema de transporte
2. Predecir demanda en diferentes horarios y rutas
3. Optimizar la planificación de recursos

### Visualizaciones

**Resultados del Modelo**  
![Predicciones](resultados_modelo)
