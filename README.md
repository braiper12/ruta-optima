## **Sistema Inteligente de Rutas de Transporte Masivo**

### **Actividad #3**
**Grupo:**  
Edwin Andres Legro Agudelo  

**Curso** Inteligencia Artificial       
**Facultad** Ingenieria De Software    
**Universidad Iberoamercicana**     


### Introducción

Se desarrolla un Script en Python, que a partir de una base de conocimiento de rutas de transporte masivo, encuentra la ruta óptima entre dos puntos, considerando criterios de costo o tiempo.   

### Tecnologías utilizadas:

+ Python: Lenguaje de programación principal para la implementación del sistema.
+ JSON: Formato de datos para almacenar la información de las estaciones, rutas y reglas.
+ NetworkX: Librería de Python para la manipulación y análisis de grafos, utilizada para representar la red de transporte y aplicar el algoritmo de Dijkstra.
+ Pandas: Librería de Python para el análisis y manipulación de datos, utilizada para estructurar y presentar los resultados en DataFrames.
+ Matplotlib: Librería de Python para la visualización de datos, utilizada para representar gráficamente la red de transporte y la ruta óptima.

El uso de NetworkX permite una implementación eficiente del algoritmo de Dijkstra.  
Pandas facilita el análisis y la presentación de los resultados.    
Matplotlib genera graficas optimas para la correcta visualización de los datos.     

### Implementación:

1.  Carga de datos JSON:
    + Se utiliza la librería json para cargar los datos de las estaciones, rutas y reglas desde un archivo JSON.   
   
2.  Creación del grafo con NetworkX:
    + Se crea un grafo dirigido utilizando networkx.DiGraph() para representar la red de transporte.
    + Los nodos del grafo representan las estaciones, y las aristas representan las rutas entre las estaciones.
    + Se asignan atributos a los nodos (nombre, coordenadas) y aristas (tiempo, costo).     
  
3.  Implementación del algoritmo de Dijkstra:
    + Se utiliza la función nx.shortest_path() de NetworkX para encontrar el camino más corto entre dos estaciones.
    + El algoritmo de Dijkstra se aplica considerando el costo o el tiempo como peso de las aristas, según la elección del usuario.     
  
4.  Análisis de datos con Pandas:
    + Se crean DataFrames de Pandas para estructurar y presentar los resultados del algoritmo de Dijkstra.
    + Se generan DataFrames para las estaciones, rutas, camino óptimo y resumen del camino.  
     
5.  Visualización con Matplotlib:
    + Se utiliza matplotlib.pyplot para visualizar la red de transporte y el camino óptimo.
    + Se dibujan los nodos, aristas y etiquetas del grafo.
    + Se resaltan las aristas que forman el camino óptimo.
    + Se crean anotaciones sobre el tiempo o precio que toma cada ruta.     

6.  Interacción con el usuario:
    + Se solicita al usuario que ingrese el origen, el destino y el criterio de la ruta.
    + Se muestran los resultados en forma de DataFrames y en una visualización gráfica.

## Pruebas
Se realizan pruebas para evaluar los resultados al seleccionar dos rutas del trayecto.

* **Resultado 1**  En este caso se valida del punto A al D, en base al costo:  

![alt text](ruta_optima_costo.png)

* **Resultado 2**  En este caso se valida del punto A al D, en base al tiempo:    

![alt text](ruta_optima_tiempo.png)