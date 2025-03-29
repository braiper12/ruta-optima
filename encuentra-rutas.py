import json
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import argparse
import folium
from folium.plugins import MarkerCluster
import numpy as np
from tabulate import tabulate
import logging
import sys
from colorama import Fore, Style, init
import webbrowser

# Inicializar colorama para colores en la terminal
init()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/transporte.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SistemaTransporte:
    def __init__(self, archivo_datos):
        """Inicializa el sistema de transporte con datos desde un archivo JSON."""
        self.archivo_datos = archivo_datos
        self.G = nx.Graph()
        self.datos = None
        self.df_estaciones = None
        self.df_rutas = None
        self.directorio_resultados = "resultados" 
        #self.directorio_resultados = "resultados_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Cargar datos desde JSON
            with open(archivo_datos, "r", encoding="utf-8") as f:
                self.datos = json.load(f)
                
            # Crear directorio para resultados si no existe
            if not os.path.exists(self.directorio_resultados):
                os.makedirs(self.directorio_resultados)
                
            # Procesar datos
            self._procesar_datos()
            logger.info(f"Sistema inicializado correctamente con datos de {archivo_datos}")
        except FileNotFoundError:
            logger.error(f"Archivo {archivo_datos} no encontrado.")
            print(f"{Fore.RED}Error: Archivo {archivo_datos} no encontrado.{Style.RESET_ALL}")
            sys.exit(1)
        except json.JSONDecodeError:
            logger.error(f"Error al decodificar el archivo JSON {archivo_datos}.")
            print(f"{Fore.RED}Error: El archivo {archivo_datos} no tiene un formato JSON válido.{Style.RESET_ALL}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error al inicializar el sistema: {str(e)}")
            print(f"{Fore.RED}Error inesperado: {str(e)}{Style.RESET_ALL}")
            sys.exit(1)
    
    def _procesar_datos(self):
        """Procesa los datos del JSON y construye el grafo."""
        #DataFrames para el manejo de datos
        self.df_estaciones = pd.DataFrame(self.datos["estaciones"])
        self.df_rutas = pd.DataFrame(self.datos["rutas"])
        
        # Agregar nodos (estaciones)
        for estacion in self.datos["estaciones"]:
            self.G.add_node(
                estacion["id"], 
                pos=(estacion["lon"], estacion["lat"]), 
                nombre=estacion["nombre"],
                tipo=estacion.get("tipo", "normal"),  # Tipo de estación (normal, intermodal, etc.)
                servicios=estacion.get("servicios", [])  # Servicios disponibles
            )

        # Agregar aristas (rutas)
        for ruta in self.datos["rutas"]:
            self.G.add_edge(
                ruta["origen"], 
                ruta["destino"], 
                tiempo=ruta["tiempo"], 
                costo=ruta["costo"],
                distancia=ruta.get("distancia", 0),  # Distancia en km
                medio=ruta.get("medio", "bus"),  # Medio de transporte
                frecuencia=ruta.get("frecuencia", 15)  # Frecuencia en minutos
            )
    
    def listar_estaciones(self):
        """Muestra una lista formateada de todas las estaciones."""
        if self.df_estaciones is not None:
            print(f"\n{Fore.CYAN}=== Estaciones Disponibles ==={Style.RESET_ALL}")
            tabla = []
            for _, estacion in self.df_estaciones.iterrows():
                tabla.append([
                    estacion["id"],
                    estacion["nombre"],
                    estacion.get("tipo", "normal"),
                    ", ".join(estacion.get("servicios", []))
                ])
            
            headers = ["ID", "Nombre", "Tipo", "Servicios"]
            print(tabulate(tabla, headers=headers, tablefmt="pretty"))
            return True
        return False
    
    def listar_rutas(self):
        """Muestra una lista formateada de todas las rutas."""
        if self.df_rutas is not None:
            print(f"\n{Fore.CYAN}=== Rutas Disponibles ==={Style.RESET_ALL}")
            tabla = []
            for _, ruta in self.df_rutas.iterrows():
                origen_nombre = self.df_estaciones[self.df_estaciones["id"] == ruta["origen"]]["nombre"].values[0]
                destino_nombre = self.df_estaciones[self.df_estaciones["id"] == ruta["destino"]]["nombre"].values[0]
                
                tabla.append([
                    ruta["origen"],
                    ruta["destino"],
                    f"{origen_nombre} → {destino_nombre}",
                    ruta["tiempo"],
                    ruta["costo"],
                    ruta.get("distancia", "N/A"),
                    ruta.get("medio", "bus"),
                    ruta.get("frecuencia", 15)
                ])
            
            headers = ["Origen", "Destino", "Ruta", "Tiempo (min)", "Costo ($)", "Distancia (km)", "Medio", "Frecuencia (min)"]
            print(tabulate(tabla, headers=headers, tablefmt="pretty"))
            return True
        return False
    
    def validar_estacion(self, id_estacion):
        """Valida que una estación exista en el sistema."""
        return id_estacion in self.G.nodes
    
    def encontrar_ruta(self, origen, destino, criterio="tiempo", algoritmo="dijkstra"):
        """
        Encuentra la ruta óptima entre dos estaciones según un criterio.
        
        Parámetros:
        - origen: ID de la estación de origen
        - destino: ID de la estación de destino
        - criterio: "tiempo", "costo", "distancia" o "combinado"
        - algoritmo: "dijkstra" o "astar" para el cálculo de rutas
        
        Retorna:
        - camino_optimo: Lista de estaciones en la ruta
        - valor_optimo: Valor total según el criterio
        - etiqueta_valor: Descripción del valor
        - detalles_ruta: DataFrame con detalles de cada segmento
        """
        # Validar estaciones
        if not self.validar_estacion(origen):
            logger.error(f"Estación de origen '{origen}' no encontrada.")
            return None, None, None, None
        
        if not self.validar_estacion(destino):
            logger.error(f"Estación de destino '{destino}' no encontrada.")
            return None, None, None, None
        
        # Si el origen y destino son iguales
        if origen == destino:
            logger.warning("Origen y destino son la misma estación.")
            return [origen], 0, "Sin movimiento", pd.DataFrame()
        
        # Determinar el peso a utilizar según el criterio
        if criterio == "costo":
            weight = "costo"
            etiqueta_valor = "Costo total ($)"
        elif criterio == "tiempo":
            weight = "tiempo"
            etiqueta_valor = "Tiempo total (min)"
        elif criterio == "distancia":
            weight = "distancia"
            etiqueta_valor = "Distancia total (km)"
        elif criterio == "combinado":
            # Crear peso combinado (personalizable según necesidades)
            for u, v, d in self.G.edges(data=True):
                # Ejemplo: 0.5*tiempo + 0.3*costo + 0.2*distancia
                d["combinado"] = 0.5 * d["tiempo"] + 0.3 * d["costo"] + 0.2 * d.get("distancia", 0)
            weight = "combinado"
            etiqueta_valor = "Valor combinado"
        else:
            logger.error(f"Criterio '{criterio}' no válido.")
            return None, None, None, None
        
        try:
            # Seleccionar algoritmo
            if algoritmo == "dijkstra":
                camino_optimo = nx.dijkstra_path(self.G, source=origen, target=destino, weight=weight)
                valor_optimo = nx.dijkstra_path_length(self.G, source=origen, target=destino, weight=weight)
            elif algoritmo == "astar":
                camino_optimo = nx.astar_path(self.G, source=origen, target=destino, weight=weight)
                valor_optimo = nx.astar_path_length(self.G, source=origen, target=destino, weight=weight)
            else:
                logger.error(f"Algoritmo '{algoritmo}' no válido.")
                return None, None, None, None
                
            # Crear DataFrame con detalles de la ruta
            detalles_ruta = self._generar_detalles_ruta(camino_optimo, criterio)
            
            return camino_optimo, valor_optimo, etiqueta_valor, detalles_ruta
            
        except nx.NetworkXNoPath:
            logger.error(f"No existe ruta entre {origen} y {destino}.")
            return None, None, None, None
        except Exception as e:
            logger.error(f"Error al buscar ruta: {str(e)}")
            return None, None, None, None
    
    def _generar_detalles_ruta(self, camino, criterio):
        """Genera un DataFrame con los detalles de cada segmento de la ruta."""
        detalles = []
        
        for i in range(len(camino) - 1):
            origen = camino[i]
            destino = camino[i + 1]
            
            # Obtener datos de la arista
            datos_arista = self.G.get_edge_data(origen, destino)
            
            # Obtener nombres de las estaciones
            nombre_origen = self.G.nodes[origen]["nombre"]
            nombre_destino = self.G.nodes[destino]["nombre"]
            
            detalles.append({
                "Segmento": f"{i+1}",
                "Origen ID": origen,
                "Destino ID": destino,
                "Origen": nombre_origen,
                "Destino": nombre_destino,
                "Tiempo (min)": datos_arista["tiempo"],
                "Costo ($)": datos_arista["costo"],
                "Distancia (km)": datos_arista.get("distancia", "N/A"),
                "Medio": datos_arista.get("medio", "bus"),
                "Frecuencia (min)": datos_arista.get("frecuencia", "N/A")
            })
        
        return pd.DataFrame(detalles)
    
    def visualizar_grafo(self, camino=None, criterio=None, guardar=True, mostrar=True, interactivo=False):
        """
        Visualiza el grafo de la red de transporte, opcionalmente resaltando una ruta.
        
        Parámetros:
        - camino: Lista de estaciones en la ruta a resaltar
        - criterio: "tiempo", "costo", "distancia" o "combinado"
        - guardar: Si es True, guarda la visualización como archivo
        - mostrar: Si es True, muestra la visualización
        - interactivo: Si es True, genera un mapa interactivo con Folium en lugar de matplotlib
        """
        if interactivo:
            return self._visualizar_mapa_folium(camino, criterio, guardar)
        else:
            return self._visualizar_grafo_matplotlib(camino, criterio, guardar, mostrar)
    
    def _visualizar_grafo_matplotlib(self, camino=None, criterio=None, guardar=True, mostrar=True):
        """Visualiza el grafo usando matplotlib."""
        plt.figure(figsize=(12, 10))
        pos = nx.get_node_attributes(self.G, "pos")
        nombres = nx.get_node_attributes(self.G, "nombre")
        tipos = nx.get_node_attributes(self.G, "tipo")
        
        # Colores según tipo de estación
        color_map = []
        for nodo in self.G.nodes():
            if tipos.get(nodo) == "principal":
                color_map.append("red")
            elif tipos.get(nodo) == "intermodal":
                color_map.append("orange")
            else:
                color_map.append("skyblue")
        
        # Tamaños según tipo de estación
        size_map = []
        for nodo in self.G.nodes():
            if tipos.get(nodo) == "principal":
                size_map.append(800)
            elif tipos.get(nodo) == "intermodal":
                size_map.append(600)
            else:
                size_map.append(400)
        
        # Dibujar nodos
        nx.draw_networkx_nodes(self.G, pos, node_size=size_map, node_color=color_map, alpha=0.8)
        
        # Dibujar aristas con diferentes estilos según medio de transporte
        edge_styles = {}
        for u, v, data in self.G.edges(data=True):
            if data.get("medio") == "metro":
                edge_styles[(u, v)] = "solid"
            elif data.get("medio") == "bus":
                edge_styles[(u, v)] = "dashed"
            elif data.get("medio") == "tren":
                edge_styles[(u, v)] = "dashdot"
            else:
                edge_styles[(u, v)] = "dotted"
        
        # Dibujar todas las aristas según su estilo
        for style in set(edge_styles.values()):
            edges_with_style = [e for e, s in edge_styles.items() if s == style]
            nx.draw_networkx_edges(
                self.G, pos, 
                edgelist=edges_with_style, 
                edge_color="gray", 
                style=style,
                alpha=0.7
            )
        
        # Dibujar etiquetas de los nodos
        nx.draw_networkx_labels(self.G, pos, labels=nombres, font_size=8, font_weight="bold")
        
        # Resaltar el camino óptimo si se proporciona
        if camino:
            edges_camino = [(camino[i], camino[i + 1]) for i in range(len(camino) - 1)]
            nx.draw_networkx_edges(
                self.G, pos, 
                edgelist=edges_camino, 
                edge_color="red", 
                width=3
            )
            
            # Añadir etiquetas con peso en las aristas del camino óptimo
            edge_labels = {}
            for i in range(len(camino) - 1):
                u, v = camino[i], camino[i + 1]
                data = self.G.get_edge_data(u, v)
                
                if criterio == "tiempo":
                    edge_labels[(u, v)] = f"{data['tiempo']} min"
                elif criterio == "costo":
                    edge_labels[(u, v)] = f"${data['costo']}"
                elif criterio == "distancia":
                    edge_labels[(u, v)] = f"{data.get('distancia', 0)} km"
                else:
                    edge_labels[(u, v)] = f"{data['tiempo']}m/${data['costo']}"
                    
            nx.draw_networkx_edge_labels(
                self.G, pos, 
                edge_labels=edge_labels, 
                font_size=8,
                font_color="red"
            )
        
        # Añadir leyenda
        import matplotlib.patches as mpatches
        leyenda = [
            mpatches.Patch(color="red", label="Estación Principal"),
            mpatches.Patch(color="orange", label="Estación Intermodal"),
            mpatches.Patch(color="skyblue", label="Estación Normal")
        ]
        
        from matplotlib.lines import Line2D
        leyenda.extend([
            Line2D([0], [0], color="gray", linestyle="solid", label="Metro"),
            Line2D([0], [0], color="gray", linestyle="dashed", label="Bus"),
            Line2D([0], [0], color="gray", linestyle="dashdot", label="Tren"),
            Line2D([0], [0], color="gray", linestyle="dotted", label="Otro")
        ])
        
        if camino:
            leyenda.append(Line2D([0], [0], color="red", linewidth=3, label="Ruta Óptima"))
        
        plt.legend(handles=leyenda, loc="upper right")
        
        # Título y ajustes
        if camino:
            origen_nombre = self.G.nodes[camino[0]]["nombre"]
            destino_nombre = self.G.nodes[camino[-1]]["nombre"]
            plt.title(f"Ruta Óptima: {origen_nombre} a {destino_nombre} ({criterio})", fontsize=14)
        else:
            plt.title("Red de Transporte Público", fontsize=14)
        
        plt.axis("off")
        plt.tight_layout()
        
        # Guardar la imagen
        if guardar:
            nombre_archivo = f"{self.directorio_resultados}/grafo"
            if camino:
                nombre_archivo += f"_ruta_{camino[0]}_a_{camino[-1]}_{criterio}"
            nombre_archivo += ".png"
            
            plt.savefig(nombre_archivo, dpi=300, bbox_inches="tight")
            logger.info(f"Gráfico guardado como {nombre_archivo}")
        
        if mostrar:
            plt.show()
        else:
            plt.close()
        
        return nombre_archivo if guardar else None
    
    def _visualizar_mapa_folium(self, camino=None, criterio=None, guardar=True):
        """Visualiza el grafo como un mapa interactivo usando Folium."""
        # Crear mapa base
        lats = [data["pos"][1] for node, data in self.G.nodes(data=True)]
        lons = [data["pos"][0] for node, data in self.G.nodes(data=True)]
        
        centro_lat = sum(lats) / len(lats)
        centro_lon = sum(lons) / len(lons)
        
        mapa = folium.Map(location=[centro_lat, centro_lon], zoom_start=12)
        
        # Crear cluster de marcadores para estaciones
        marker_cluster = MarkerCluster().add_to(mapa)
        
        # Añadir estaciones como marcadores
        for node, data in self.G.nodes(data=True):
            lat, lon = data["pos"][1], data["pos"][0]
            nombre = data["nombre"]
            tipo = data.get("tipo", "normal")
            servicios = ", ".join(data.get("servicios", []))
            
            if tipo == "principal":
                color = "red"
            elif tipo == "intermodal":
                color = "orange"
            else:
                color = "blue"
            
            popup_html = f"""
            <div style="width: 200px">
                <h4>{nombre}</h4>
                <b>ID:</b> {node}<br>
                <b>Tipo:</b> {tipo}<br>
                <b>Servicios:</b> {servicios}
            </div>
            """
            
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=nombre,
                icon=folium.Icon(color=color, icon="info-sign")
            ).add_to(marker_cluster)
        
        # Añadir rutas como líneas
        for u, v, data in self.G.edges(data=True):
            u_pos = self.G.nodes[u]["pos"]
            v_pos = self.G.nodes[v]["pos"]
            
            coords = [
                [u_pos[1], u_pos[0]],
                [v_pos[1], v_pos[0]]
            ]
            
            if data.get("medio") == "metro":
                color = "blue"
                weight = 3
                dash = "5,5"
            elif data.get("medio") == "bus":
                color = "green"
                weight = 2
                dash = "10,10"
            elif data.get("medio") == "tren":
                color = "purple"
                weight = 4
                dash = "15,10,1,10"
            else:
                color = "gray"
                weight = 2
                dash = "1,10"
            
            popup_html = f"""
            <div>
                <h4>Ruta: {self.G.nodes[u]["nombre"]} → {self.G.nodes[v]["nombre"]}</h4>
                <b>Tiempo:</b> {data["tiempo"]} min<br>
                <b>Costo:</b> ${data["costo"]}<br>
                <b>Distancia:</b> {data.get("distancia", "N/A")} km<br>
                <b>Medio:</b> {data.get("medio", "N/A")}<br>
                <b>Frecuencia:</b> {data.get("frecuencia", "N/A")} min
            </div>
            """
            
            folium.PolyLine(
                locations=coords,
                weight=weight,
                color=color,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{self.G.nodes[u]['nombre']} → {self.G.nodes[v]['nombre']}",
                opacity=0.7,
                dash_array=dash
            ).add_to(mapa)
        
        # Resaltar camino óptimo si se proporciona
        if camino:
            camino_coords = []
            for i in range(len(camino) - 1):
                u, v = camino[i], camino[i + 1]
                u_pos = self.G.nodes[u]["pos"]
                v_pos = self.G.nodes[v]["pos"]
                camino_coords.append([u_pos[1], u_pos[0]])
                camino_coords.append([v_pos[1], v_pos[0]])
            
            folium.PolyLine(
                locations=camino_coords,
                weight=5,
                color="red",
                opacity=0.8,
                tooltip="Ruta Óptima"
            ).add_to(mapa)
            
            # Añadir marcadores de inicio y fin
            origen = camino[0]
            destino = camino[-1]
            
            folium.Marker(
                location=[self.G.nodes[origen]["pos"][1], self.G.nodes[origen]["pos"][0]],
                tooltip="Origen: " + self.G.nodes[origen]["nombre"],
                icon=folium.Icon(color="green", icon="play", prefix="fa")
            ).add_to(mapa)
            
            folium.Marker(
                location=[self.G.nodes[destino]["pos"][1], self.G.nodes[destino]["pos"][0]],
                tooltip="Destino: " + self.G.nodes[destino]["nombre"],
                icon=folium.Icon(color="red", icon="stop", prefix="fa")
            ).add_to(mapa)
        
        # Añadir leyenda
        leyenda_html = """
        <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; padding: 10px; background-color: white; border: 2px solid grey; border-radius: 5px;">
            <p><b>Tipos de Estaciones:</b></p>
            <p><i class="fa fa-map-marker" style="color:red"></i> Principal</p>
            <p><i class="fa fa-map-marker" style="color:orange"></i> Intermodal</p>
            <p><i class="fa fa-map-marker" style="color:blue"></i> Normal</p>
            <p><b>Tipos de Rutas:</b></p>
            <p><hr style="border: 2px solid blue; width: 50px;"> Metro</p>
            <p><hr style="border: 2px dashed green; width: 50px;"> Bus</p>
            <p><hr style="border: 2px solid purple; width: 50px;"> Tren</p>
            <p><hr style="border: 2px dashed gray; width: 50px;"> Otro</p>
        """
        
        if camino:
            leyenda_html += """
            <p><b>Ruta:</b></p>
            <p><hr style="border: 3px solid red; width: 50px;"> Óptima</p>
            """
        
        leyenda_html += "</div>"
        mapa.get_root().html.add_child(folium.Element(leyenda_html))
        
        # Guardar mapa interactivo
        if guardar:
            nombre_archivo = f"{self.directorio_resultados}/mapa"
            if camino:
                nombre_archivo += f"_ruta_{camino[0]}_a_{camino[-1]}_{criterio}"
            nombre_archivo += ".html"
            mapa.save(nombre_archivo)
            logger.info(f"Mapa interactivo guardado como {nombre_archivo}")
        
        return mapa
    
    def generar_informe(self, camino, valor, etiqueta_valor, detalles_ruta, criterio):
        """Genera un informe detallado de la ruta en formato HTML."""
        if not camino:
            logger.error("No se puede generar informe sin un camino válido.")
            return None
        
        try:
            # Obtener nombres de origen y destino
            origen_nombre = self.G.nodes[camino[0]]["nombre"]
            destino_nombre = self.G.nodes[camino[-1]]["nombre"]
            
            # Crear tabla HTML con los detalles
            tabla_html = detalles_ruta.to_html(index=False, classes="table table-striped")
            
            # Estadísticas adicionales
            tiempo_total = sum(detalles_ruta["Tiempo (min)"])
            costo_total = sum(detalles_ruta["Costo ($)"])
            distancia_total = sum([d for d in detalles_ruta["Distancia (km)"] if d != "N/A"])
            
            # Calcular velocidad promedio
            if distancia_total > 0 and tiempo_total > 0:
                velocidad_promedio = (distancia_total / tiempo_total) * 60  # km/h
            else:
                velocidad_promedio = 0
            
            # Crear HTML del informe
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Informe de Ruta: {origen_nombre} a {destino_nombre}</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .summary {{ margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 5px; }}
                    .footer {{ margin-top: 30px; text-align: center; font-size: 0.8em; color: #6c757d; }}
                    .table {{ width: 100%; margin-bottom: 20px; }}
                    .stats {{ display: flex; justify-content: space-around; flex-wrap: wrap; }}
                    .stat-card {{ 
                        width: 200px; 
                        padding: 15px; 
                        margin: 10px; 
                        text-align: center; 
                        border-radius: 5px; 
                        box-shadow: 0 4px 8px rgba(0,0,0,0.1); 
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Informe de Ruta Óptima</h1>
                        <h3>{origen_nombre} a {destino_nombre}</h3>
                        <p>Criterio: {criterio.capitalize()}</p>
                    </div>
                    
                    <div class="summary">
                        <h4>Resumen de la Ruta</h4>
                        <p><strong>Estaciones:</strong> {len(camino)}</p>
                        <p><strong>Segmentos:</strong> {len(camino) - 1}</p>
                        <p><strong>{etiqueta_valor}:</strong> {valor}</p>
                        
                        <div class="stats">
                            <div class="stat-card bg-info text-white">
                                <h5>Tiempo Total</h5>
                                <h3>{tiempo_total} min</h3>
                            </div>
                            <div class="stat-card bg-success text-white">
                                <h5>Costo Total</h5>
                                <h3>${costo_total}</h3>
                            </div>
                            <div class="stat-card bg-warning text-white">
                                <h5>Distancia Total</h5>
                                <h3>{distancia_total} km</h3>
                            </div>
                            <div class="stat-card bg-secondary text-white">
                                <h5>Velocidad Promedio</h5>
                                <h3>{velocidad_promedio:.2f} km/h</h3>
                            </div>
                        </div>
                    </div>
                    
                    <div>
                        <h4>Detalles de la Ruta</h4>
                        {tabla_html}
                    </div>
                    
                    <div class="footer">
                        <p>Generado el {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Guardar el informe en un archivo HTML
            # nombre_archivo = f"{self.directorio_resultados}/informe_ruta_{camino[0]}_a_{camino[-1]}_{criterio}.html"
            nombre_archivo = f"{self.directorio_resultados}/informe_ruta.html"
            with open(nombre_archivo, "w", encoding="utf-8") as f:
                f.write(html)
            
            logger.info(f"Informe generado y guardado como {nombre_archivo}")
            return nombre_archivo
        except Exception as e:
            logger.error(f"Error al generar informe: {str(e)}")
            return None


if __name__ == "__main__":
    sistema = SistemaTransporte("datos_transporte.json")
    sistema.listar_estaciones()
    sistema.listar_rutas()
    
    # Pedir al usuario el origen y destino
    origen = input("Selecciona la estación de origen: ").strip()
    destino = input("Selecciona la estación de destino: ").strip()
    
    _criterio = input("¿Desea la ruta más económica (costo) o la más corta en tiempo (tiempo)? ").lower()
    
    # Buscar la ruta óptima según el criterio deseado (por ejemplo, "tiempo")
    camino, valor, etiqueta, detalles = sistema.encontrar_ruta(origen, destino, criterio=_criterio)
    
    if camino:
        sistema.visualizar_grafo(camino, criterio=_criterio)
        nombre_archivo = sistema.generar_informe(camino, valor, etiqueta, detalles, criterio=_criterio)
        
        ruta_completa = os.path.abspath(nombre_archivo)
        url = f"file://{ruta_completa}"
        webbrowser.open(url)
    else:
        print("No se encontró una ruta entre las estaciones seleccionadas.")