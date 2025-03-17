import requests 
import re
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import math

class WebScraping():

    def __init__ (self, repositorio, numArticulos):
        self.repositorio = repositorio
        self.numArticulos = numArticulos
        self.urls = {
            "arxiv" : {
                "repositorioComputacion&Lenguaje" : "https://arxiv.org/list/cs.CL/recent",
                "repositorioVision&Patrones" : "https://arxiv.org/list/cs.CV/recent"
            },
            "pubmed" : {
                "repositorioTendenciaPubmed" : "https://pubmed.ncbi.nlm.nih.gov/trending/"
            }
        }
        self.articulos = []
        self.validosConsulta = [25, 50, 100, 250, 500, 1000, 2000]

    def _mejorConsultaArXiv(self):
        for valor in self.validosConsulta:
            if self.numArticulos <= valor:
                return valor
        return 2000 #Valor máximo permitido para la consulta
    
    def obtenerArticulos(self, categoria = None):

        if self.repositorio == "arxiv":
            if categoria not in ["Computacion&Lenguaje", "Vision&Patrones"]:
                print("Categoria no valida")
                return None
            return self._obtener_arxiv_articulos(categoria)
        elif self.repositorio == "pubmed":
            return self._obtener_pubmed_articulos()
        else:
            print("Repositorio no establecido o no válido")
            return None
        
    def _obtener_arxiv_articulos(self, categoria):
        try:
            if categoria == "Computacion&Lenguaje":
                url = self.urls["arxiv"]["repositorioComputacion&Lenguaje"]
                numArticulos = self._mejorConsultaArXiv()
                urlMejorConsulta = f"{url}?skip=0&show={numArticulos}"
                response = requests.get(urlMejorConsulta)
            elif categoria == "Vision&Patrones":
                url = self.urls["arxiv"]["repositorioVision&Patrones"]
                numArticulos = self._mejorConsultaArXiv()
                urlMejorConsulta = f"{url}?skip=0&show={numArticulos}"
                response = requests.get(urlMejorConsulta)
            else:
                print("Categoria no valida")
                return None
            
            print("Obteniendo articulos de Arxiv...")
                
            soup = BeautifulSoup(response.text, "html.parser")
            articulos = []
            #entidades = soup.find("dl", id="articles").find_all("dt")[:self.numArticulos]   #Limite de articulos
            contenedoresArticulos = soup.find_all("dl", id="articles")          #Lista con todos los dl de articulos
            entidades = [dt for dl in contenedoresArticulos for dt in dl.find_all("dt")][:self.numArticulos]

            for entidad in entidades:
                try:
                    doiLink = entidad.find("a", title="Abstract")   #Obtengo esto: <a href="/abs/2503.10620" id="2503.10620" title="Abstract">arXiv:2503.10620</a>
                    arxivID = doiLink.text.strip().split(":")[-1]   #Obtengo el texto y lo divido por ":" y obtengo el ultimo elemento
                    articuloURL = f"https://arxiv.org/abs/{arxivID}"

                    #Obtener el contenido del articulo
                    respuestaArticulo = requests.get(articuloURL)
                    articuloSoup = BeautifulSoup(respuestaArticulo.text, "html.parser")

                    #Obtener el titulo
                    #<h1 class="title mathjax"><span class="descriptor">Title:</span>From TOWER to SPIRE: Adding the Speech Modality to a Text-Only LLM</h1>
                    tituloContenedor = articuloSoup.find("h1", class_="title mathjax")
                    titulo = tituloContenedor.text.replace("Title:", "").strip()

                    #Obtener los autores
                    #<div class="authors"><span class="descriptor">Authors:</span><a href="https://arxiv.org/search/cs?searchtype=author&amp;query=Zhou,+A" rel="nofollow">Andy Zhou</a></div>
                    autoresContenedor = articuloSoup.find("div", class_="authors")
                    autores = autoresContenedor.text.replace("Authors:", "").strip()

                    #Obtener el abstract
                    #<blockquote class="abstract mathjax"><span class="descriptor">Abstract:</span>Adapting large language models to multiple tasks can cause cross-skill interference, where improvements for one skill degrade another. While methods such as LoRA impose orthogonality constraints at the weight level, they do not fully address interference in hidden-state representations. We propose Compositional Subspace Representation Fine-tuning (CS-ReFT), a novel representation-based approach that learns multiple orthonormal subspace transformations, each specializing in a distinct skill, and composes them via a lightweight router. By isolating these subspace edits in the hidden state, rather than weight matrices, CS-ReFT prevents cross-task conflicts more effectively. On the AlpacaEval benchmark, applying CS-ReFT to Llama-2-7B achieves a 93.94% win rate, surpassing GPT-3.5 Turbo (86.30%) while requiring only 0.0098% of model parameters. These findings show that specialized representation edits, composed via a simple router, significantly enhance multi-task instruction following with minimal overhead.</blockquote>
                    abstractContenedor = articuloSoup.find("blockquote", class_="abstract mathjax")
                    abstract = abstractContenedor.text.replace("Abstract:", "").strip()


                    #Obtener la fecha de publicacion
                    #<div class="dateline">[Submitted on 13 Mar 2025]</div>
                    fechaContenedor = articuloSoup.find("div", class_="dateline")
                    if fechaContenedor:
                        fechaTexto = fechaContenedor.text.strip()
                        fechaCoincidencia = re.search(r"\d{1,2}\s*\w{3}\s*\d{4}", fechaTexto)
                        if fechaCoincidencia:
                            fecha = fechaCoincidencia.group(0)
                            fecha = datetime.strptime(fecha, "%d %b %Y").date()
                            fecha = fecha.strftime("%d/%m/%Y")
                        else:
                            fecha = None
                    else:
                        fecha = None
                    #Almacenar los datos
                    articulos.append({
                        "DOI" : "10.48550./arXiv." + arxivID,
                        "Titulo" : titulo,
                        "Autores" : autores,
                        "Abstract" : abstract,
                        "Fecha" : fecha,
                        "Seccion" : categoria
                    })
                    
                except Exception as ErrorObtener:
                    print(f"Error al obtener articulos: {ErrorObtener}")
                    return None
                
            return articulos
            
        except Exception as ErrorGeneral:
            print(f"Error al intentar hacer una peticion al repositorio de Arxiv y obtener los articulos: {ErrorGeneral}")
            return None

    def _obtener_pubmed_articulos(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        try:
            print("Obteniendo articulos de PubMed...")
            maximoPaginas = math.ceil(self.numArticulos / 10)
            repositorioURL = self.urls["pubmed"]["repositorioTendenciaPubmed"]
            articulos = []
            
            for pagina in range(1, maximoPaginas + 1):
                urlPagina = f"{repositorioURL}?page={pagina}"
                response = requests.get(urlPagina, timeout=20)

                # Obtener el contenido de la lista de los articulos
                soup = BeautifulSoup(response.text, "html.parser")
                articuloLink = soup.find_all("article", class_="full-docsum")

                for articulo in articuloLink:
                    try:
                        articuloID = articulo.find("a", class_="docsum-title")["href"]
                        articuloID = articuloID.split("/")[1]
                        articuloURL = f"https://pubmed.ncbi.nlm.nih.gov/{articuloID}"

                        #Obtener el contenido de los articulos
                        respuestaArticulo = requests.get(articuloURL, timeout=20)
                        articuloSoup = BeautifulSoup(respuestaArticulo.text, "html.parser")

                        #Obtener el titulo
                        tituloContenedor = articuloSoup.find("h1", class_="heading-title")
                        titulo = tituloContenedor.text.strip()

                        #Obtener el DOI del documento       Otra forma de capturar el DOI es a través de la etiqueta 
                        #<meta name="citation_doi" content="">
                        #<span class="identifier doi"><span class="id-label">DOI:</span><a class="id-link" target="_blank" rel="noopener" ref="linksrc=article_id_link&amp;article_id=10.1016/j.foodchem.2018.04.067&amp;id_type=DOI" href="https://doi.org/10.1016/j.foodchem.2018.04.067" data-ga-category="full_text" data-ga-action="DOI">10.1016/j.foodchem.2018.04.067</a></span>
                        try:
                            DOIContenedor = articuloSoup.find("span", class_="identifier doi")
                            if DOIContenedor:
                                elementoDOI = DOIContenedor.find("a", class_="id-link").text.strip()
                            else:
                                raise AttributeError
                        except AttributeError:
                            print(f"No se encontro el DOI del articulo {len(articulos)} de {self.numArticulos}")
                            elementoDOI = ""

                        #Obtener los autores
                        #<a class="full-name" href="/?term=Mihalcea+L&amp;cauthor_id=29751918" ref="linksrc=author_name_link" data-ga-category="search" data-ga-action="author_link" data-ga-label="Liliana Mihalcea">Liliana Mihalcea</a>
                        try:
                            autoresContenedor = articuloSoup.find("div", class_="authors-list")
                            if autoresContenedor:                                
                                autores = [autor.text.strip() for autor in autoresContenedor.find_all("a", class_="full-name")]
                            else:
                                raise AttributeError
                        except AttributeError:
                            print(f"No se encontraron los autores/autor del articulo {len(articulos)} de {self.numArticulos}")
                            autores = []

                        #Obtener el abstract
                        #<div class="abstract-content selected" id="eng-abstract"><p>Sea buckthorn carotenoids extracted using CO<sub>2</sub> supercritical fluids method were encapsulated within whey proteins isolate by transglutaminase (TG) mediated crosslinking reaction, coacervation and freeze drying. The encapsulation efficiency was 36.23 ± 1.58%, with β-carotene the major carotenoid present in the powder. The confocal analysis revealed that TG-ase mediated cross-linking reaction enhanced the complexes stability to such a manner that a double microencapsulation was performed. The powder showed an antioxidant activity of 2.16 ± 0.14 mMol Trolox/g DW and an antifungal activity against Penicillium expansum MIUG M11. Four variants of domestic ice creams were obtained, with a total carotenoids content variation of 1.63 ± 0.03 mg/g D.W. in sample with 2% powder and 6.38 ± 0.04 mg/g D.W. in samples with 4% extract, having satisfactory antioxidant activity. The storage stability test showed a decrease in both total carotenoids content and antioxidant activity in all samples during 21 days at -18 °C. A protective effect of microencapsulation was evidenced.</p></div>
                        abstractContenedor = articuloSoup.find("div", class_="abstract-content selected")
                        abstract = abstractContenedor.p.get_text(" ", strip=True) if abstractContenedor and abstractContenedor.p else "Sin Abstract"    # Obtiene el texto del abstract y lo separa por espacios, strip=True sirve para eliminar los espacios en blanco

                        #Obtener la fecha de publicacion
                        #<div class="article-source"><div class="journal-actions dropdown-block"><button id="full-view-journal-trigger" class="journal-actions-trigger trigger" ref="linksrc=journal_actions_btn" title="Food chemistry" tabindex="0" aria-controls="full-view-journal" aria-expanded="false" aria-label="Toggle dropdown menu for journal Food chemistry" data-pinger-ignore="">Food Chem</button><div id="full-view-journal" class="journal-actions-dropdown dropdown dropdown-container" aria-label="Dropdown menu for journal Food chemistry" aria-hidden="true"><div class="title">Actions</div><div class="content"><ul class="journal-actions-links"><li><a class="search-in-pubmed-link dropdown-block-link" href="/?term=%22Food+Chem%22%5Bjour%5D&amp;sort=date&amp;sort_order=desc" data-href="/?term=%22Food+Chem%22%5Bjour%5D&amp;sort=date&amp;sort_order=desc" ref="linksrc=search_in_pubmed_journal_name_link&amp;journal_abbrev=Food Chem" data-ga-category="search" data-ga-action="journal_link" data-ga-label="Food Chem">Search in PubMed</a></li><li><a class="search-in-nlm-catalog-link dropdown-block-link" ref="linksrc=search_in_nlm_catalog_link" href="https://www.ncbi.nlm.nih.gov/nlmcatalog?term=%22Food+Chem%22%5BTitle+Abbreviation%5D" data-ga-category="search_catalog" data-ga-action="journal_link" data-ga-label="Food Chem">Search in NLM Catalog</a></li><li><a class="add-to-search-link dropdown-block-link" ref="linksrc=add_to_search_link" role="button" data-search-term="&quot;Food Chem&quot;[jour]" data-ga-category="search" data-ga-action="add_to_search" data-ga-label="&quot;Food Chem&quot;[jour]" href="#">Add to Search</a></li></ul></div></div></div><span class="period">. </span><spanclass="cit">2018 Oct 1:262:30-38.</span></div>
                        #<meta name="citation_date" content="03/10/2025">
                        fechaContenedor = articuloSoup.find("meta", {"name": "citation_date"})
                        fecha = fechaContenedor.get("content")
                        
                        if len(fecha.split("/")) == 3:
                            fecha = datetime.strptime(fecha, "%m/%d/%Y").strftime("%d/%m/%Y")
                        elif len(fecha.split()) == 2:
                            fecha = datetime.strptime(fecha, "%Y %b").strftime("%m/%Y")
                        else:
                            fecha = fecha

                        #Obtener el journal
                        #<meta name="citation_journal_title" content="Nature genetics">
                        journalContenedor = articuloSoup.find("meta", {"name": "citation_journal_title"})
                        journal = journalContenedor.get("content")


                        articulos.append({
                            "DOI" : elementoDOI,
                            "Titulo" : titulo,
                            "Autores" : ",".join(autores),
                            "Abstract" : abstract,
                            "Fecha" : fecha,
                            "Seccion" : journal         #Preguntar si se puede renombrar a Seccion
                        })

                        print(f"Obteniendo articulo {len(articulos)} de {self.numArticulos}")

                        if len(articulos) >= self.numArticulos: return articulos

                    except Exception as ErrorObtenerArticulo:
                        print(f"Error al obtener el articulo {len(articulos)} de {self.numArticulos}: {ErrorObtenerArticulo}")
                        return None

            return articulos
        
        except Exception as ErrorGeneral:
            print(f"Error al intentar hacer una peticion al repositorio de PubMed y obtener los articulos: {ErrorGeneral}")
            return None

    def generaArchivo(self, articulos, nombreArchivo = "ArticulosArXiv.csv"):
        campos = ["DOI", "Titulo", "Autores", "Abstract", "Fecha", "Seccion"]
        
        with open(nombreArchivo, "w", newline="", encoding="utf-8") as archivo:
            escribirArchivo = csv.DictWriter(archivo, fieldnames=campos)
            escribirArchivo.writeheader()

            for articulo in articulos:
                escribirArchivo.writerow(articulo)
        
        print(f"Se han guardado {len(articulos)} articulos en el archivo {nombreArchivo}")
        return archivo

#WebScraping01 = WebScraping("arxiv", 5)
#print(WebScraping01.obtenerArticulos("Computacion&Lenguaje"))
#WebScraping01.generaArchivo(WebScraping01.obtenerArticulos("Vision&Patrones"), "ArticulosArXivVision&Patrones.csv")
#WebScraping01.generaArchivo(WebScraping01.obtenerArticulos("Computacion&Lenguaje"), "ArticulosArXivComputacion&Lenguaje.csv")
#WebScraping01.generaArchivo(WebScraping01.obtenerArticulos("Computacion&Lenguaje"), "ArticulosArXivComputacion&Lenguaje2.csv")


#-------------------------------------------------------------------------------------------------------------------------

#Obtener 150 archivos de arxiv de Vision&Patrones
#WebScraping01 = WebScraping("arxiv", 150)
#WebScraping01.generaArchivo(WebScraping01.obtenerArticulos("Vision&Patrones"), "ArticulosArXivVision&Patrones.csv")

#Obtener 150 archivos de arxiv de Computacion&Lenguaje
#WebScraping02 = WebScraping("arxiv", 150)
#WebScraping02.generaArchivo(WebScraping02.obtenerArticulos("Computacion&Lenguaje"), "ArticulosArXivComputacion&Lenguaje.csv")

#-------------------------------------------------------------------------------------------------------------------------

#Obtener 300 archivos de pubmed
WebScraping03 = WebScraping("pubmed", 300)       # Con 30 articulos funciona pero tarda
articulos = WebScraping03.obtenerArticulos()
#print(articulos)
if articulos:  # Verifica que no sea None
    WebScraping03.generaArchivo(articulos, "ArticulosPubMed300_VFinal02.csv")
else:
    print("No se pudieron obtener artículos")

#-------------------------------------------------------------------------------------------------------------------------

#Obtener 300 archivos de arxiv [150 Vision&Patrones y 150 Computacion&Lenguaje]
#WebScraping04 = WebScraping("arxiv", 150)
#archivosVision_Patrones = WebScraping04.obtenerArticulos("Vision&Patrones")

#WebScraping05 = WebScraping("arxiv", 150)
#archivosComputacion_Lenguaje = WebScraping05.obtenerArticulos("Computacion&Lenguaje")

#Escribir los archivos en un solo archivo
#archivos = archivosVision_Patrones + archivosComputacion_Lenguaje
#WebScraping05.generaArchivo(archivos, "ArticulosArXiv.csv")

#-------------------------------------------------------------------------------------------------------------------------