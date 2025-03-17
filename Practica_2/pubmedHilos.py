import math
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import time
import datetime

def _obtener_pubmed_articulos(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        try:
            print("Obteniendo artículos de PubMed...")
            maximoPaginas = math.ceil(self.numArticulos / 10)
            repositorioURL = self.urls["pubmed"]["repositorioTendenciaPubmed"]
            articulos = []
            

            # Primero obtenemos todos los IDs de artículos de las páginas necesarias
            todos_articulos_ids = []
            
            for pagina in range(1, maximoPaginas + 1):
                urlPagina = f"{repositorioURL}?page={pagina}"
                response = requests.get(urlPagina, timeout=10, headers=headers)
                
                soup = BeautifulSoup(response.text, "html.parser")
                articulos_en_pagina = soup.find_all("article", class_="full-docsum")
                
                for articulo in articulos_en_pagina:
                    try:
                        articuloID = articulo.find("a", class_="docsum-title")["href"]
                        articuloID = articuloID.split("/")[1]
                        todos_articulos_ids.append(articuloID)
                    except Exception:
                        continue
                    
                if len(todos_articulos_ids) >= self.numArticulos:
                    todos_articulos_ids = todos_articulos_ids[:self.numArticulos]
                    break
                
            print(f"Se encontraron {len(todos_articulos_ids)} IDs de artículos")
            
            # Función para procesar un solo artículo
            def procesar_articulo(articuloID):
                try:
                    articuloURL = f"https://pubmed.ncbi.nlm.nih.gov/{articuloID}"
                    respuestaArticulo = requests.get(articuloURL, timeout=10, headers=headers)
                    articuloSoup = BeautifulSoup(respuestaArticulo.text, "html.parser")
                    
                    # Obtener el título
                    tituloContenedor = articuloSoup.find("h1", class_="heading-title")
                    titulo = tituloContenedor.text.strip() if tituloContenedor else "Sin título"
                    
                    # Obtener el DOI
                    try:
                        DOIContenedor = articuloSoup.find("span", class_="identifier doi")
                        if DOIContenedor:
                            elementoDOI = DOIContenedor.find("a", class_="id-link").text.strip()
                        else:
                            # Intentar obtener DOI desde meta tag
                            metaDOI = articuloSoup.find("meta", {"name": "citation_doi"})
                            elementoDOI = metaDOI.get("content") if metaDOI else ""
                    except AttributeError:
                        elementoDOI = ""
                    
                    # Obtener los autores
                    try:
                        autoresContenedor = articuloSoup.find("div", class_="authors-list")
                        if autoresContenedor:                                
                            autores = [autor.text.strip() for autor in autoresContenedor.find_all("a", class_="full-name")]
                        else:
                            autores = []
                    except AttributeError:
                        autores = []
                    
                    # Obtener el abstract
                    abstractContenedor = articuloSoup.find("div", class_="abstract-content selected")
                    abstract = abstractContenedor.p.get_text(" ", strip=True) if abstractContenedor and abstractContenedor.p else "Sin Abstract"
                    
                    # Obtener la fecha de publicación
                    fechaContenedor = articuloSoup.find("meta", {"name": "citation_date"})
                    if fechaContenedor:
                        fecha = fechaContenedor.get("content")
                        
                        if len(fecha.split("/")) == 3:
                            fecha = datetime.strptime(fecha, "%m/%d/%Y").strftime("%d/%m/%Y")
                        elif len(fecha.split()) == 2:
                            fecha = datetime.strptime(fecha, "%Y %b").strftime("%m/%Y")
                    else:
                        fecha = "Sin fecha"
                    
                    # Obtener el journal
                    journalContenedor = articuloSoup.find("meta", {"name": "citation_journal_title"})
                    journal = journalContenedor.get("content") if journalContenedor else "Sin journal"
                    
                    return {
                        "DOI": elementoDOI,
                        "Titulo": titulo,
                        "Autores": ",".join(autores),
                        "Abstract": abstract,
                        "Fecha": fecha,
                        "Seccion": journal
                    }
                    
                except Exception as e:
                    print(f"Error procesando artículo {articuloID}: {e}")
                    return None
            
            # Usar ThreadPoolExecutor para procesar artículos en paralelo
            print("Iniciando procesamiento en paralelo...")
            inicio = time.time()
            
            # Ajustar el número máximo de workers según necesidad
            max_workers = min(20, len(todos_articulos_ids))  # Limitar a 20 workers máximo
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Iniciar todas las tareas y obtener futuros
                futuros = {executor.submit(procesar_articulo, articuloID): articuloID for articuloID in todos_articulos_ids}
                
                # Procesar resultados a medida que se completan
                for i, futuro in enumerate(concurrent.futures.as_completed(futuros)):
                    articuloID = futuros[futuro]
                    try:
                        resultado = futuro.result()
                        if resultado:
                            articulos.append(resultado)
                            print(f"Procesado artículo {len(articulos)} de {self.numArticulos} (ID: {articuloID})")
                    except Exception as e:
                        print(f"Error en artículo {articuloID}: {e}")
            
            fin = time.time()
            print(f"Procesamiento en paralelo completado en {fin - inicio:.2f} segundos")
            
            return articulos
        
        except Exception as ErrorGeneral:
            print(f"Error al intentar hacer peticiones al repositorio de PubMed: {ErrorGeneral}")
            return None