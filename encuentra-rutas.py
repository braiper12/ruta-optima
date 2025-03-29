import json
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

# Cargar datos desde JSON
with open("datos_transporte.json", "r") as f:
    datos = json.load(f)

# Creamos el grafo
G = nx.Graph()

# Agregar nodos (estaciones)
for estacion in datos["estaciones"]:
    G.add_node(estacion["id"], pos=(estacion["lon"], estacion["lat"]), nombre=estacion["nombre"])

# Agregar aristas (rutas)
for ruta in datos["rutas"]:
    G.add_edge(ruta["origen"], ruta["destino"], tiempo=ruta["tiempo"], costo=ruta["costo"])

# Función para encontrar la ruta óptima
def encontrar_ruta(origen, destino, criterio):
    if criterio == "costo":
        camino_optimo = nx.shortest_path(G, source=origen, target=destino, weight="costo")
        valor_optimo = nx.shortest_path_length(G, source=origen, target=destino, weight="costo")
        etiqueta_valor = "Costo total"
    elif criterio == "tiempo":
        camino_optimo = nx.shortest_path(G, source=origen, target=destino, weight="tiempo")
        valor_optimo = nx.shortest_path_length(G, source=origen, target=destino, weight="tiempo")
        etiqueta_valor = "Tiempo total (min)"
    else:
        return None, None, None

    return camino_optimo, valor_optimo, etiqueta_valor

#muestra las estaciones
df_estaciones = pd.DataFrame(datos["estaciones"])
df_rutas = pd.DataFrame(datos["rutas"])
    
print("\nEstaciones:\n", df_estaciones)
print("\nRutas:\n", df_rutas)
    
# Interacción con el usuario
origen = input("\nIngrese el punto de origen: ").upper()
destino = input("\nIngrese el punto de destino: ").upper()
criterio = input("¿Desea la ruta más económica (costo) o la más corta en tiempo (tiempo)? ").lower()

# Encontrar ruta
camino, valor, etiqueta_valor = encontrar_ruta(origen, destino, criterio)

if camino:
    
    # Crear DataFrames
    df_camino = pd.DataFrame({"Orden": range(1, len(camino) + 1), "Estación": camino})
    df_resumen = pd.DataFrame({etiqueta_valor: [valor]})

    # Imprimir DataFrames
    print("\nDataFrame del Camino Óptimo:\n", df_camino)
    print("\nDataFrame de Resumen:\n", df_resumen)

    # Visualización del grafo
    plt.figure(figsize=(10, 8))
    pos = nx.get_node_attributes(G, "pos")
    nombres = nx.get_node_attributes(G, "nombre")

    # Dibujar nodos y aristas
    nx.draw_networkx_nodes(G, pos, node_size=600, node_color="skyblue")
    nx.draw_networkx_edges(G, pos, edge_color="gray")
    nx.draw_networkx_labels(G, pos, labels=nombres, font_size=8)
    
     # Anotaciones detalladas en las aristas
    for u, v, data in G.edges(data=True):
        peso = data["tiempo"] if criterio == "costo" else data["costo"]
        unidad = "m" if criterio == "costo" else "$"
        etiqueta = f"{nombres[u]} -> {nombres[v]}: {peso} {unidad}"
        x = (pos[u][0] + pos[v][0]) / 2
        y = (pos[u][1] + pos[v][1]) / 2
        plt.annotate(etiqueta, xy=(x, y), xytext=(x, y + 0.01), fontsize=7, ha="center")


    # Anotaciones de tiempo/costo en las aristas
    etiquetas_aristas = nx.get_edge_attributes(G, "tiempo" if criterio == "tiempo" else "costo")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=etiquetas_aristas)

    # Resaltar el camino óptimo
    edges_camino = [(camino[i], camino[i + 1]) for i in range(len(camino) - 1)]
    nx.draw_networkx_edges(G, pos, edgelist=edges_camino, edge_color="red", width=2)

    plt.title(f"Ruta Óptima ({origen} a {destino}) - {criterio.capitalize()}")
    plt.savefig(f"ruta_optima_{criterio}.png", dpi=300)
    plt.show()

else:
    print("Criterio no válido.")