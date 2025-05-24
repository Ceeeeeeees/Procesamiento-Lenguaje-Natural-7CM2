
import spacy
import csv

class Normalizador ():

    def __init__(self, archivoCSVArticulos):
        self.archivoCSVArticulos = archivoCSVArticulos
        pass

    def cargarModelo(self):
        try:
            return spacy.load("en_core_web_sm")
        except:
            print("Modelo 'en_core_web_sm' no encontrado. Ejecuta:")
            print("python -m spacy download en_core_web_sm")
            exit()

    def tokenizarTexto(self, nlp, texto):
        contenido = nlp(texto.lower())
        tokens = [(token.text, token.pos_, token.tag_, token.lemma_) for token in contenido if not token.is_punct and not token.is_space]
        tokens = self.eliminarPalabrasVaciasLemmatizacion(tokens)
        return tokens

    def eliminarPalabrasVaciasLemmatizacion(self, tokens):
        categoriasExcluir = ["DET", "ADP", "CCONJ", "SCONJ", "PRON"] # Elimina articulos, preposiciones, conjunciones y pronombres
        tokensFiltrados = [
            token[3] for token in tokens 
            if token[1] not in categoriasExcluir and token[3].isalpha()] 
        return tokensFiltrados
        

    def procesarArchivo(self, nombreArchivoSalida) :
        nlp = self.cargarModelo()
        nombreArchivoEntrada = self.archivoCSVArticulos

        tokenPreProcesados = []
        with open(nombreArchivoEntrada, newline='', encoding="utf-8") as archivoSinTokenizar:
            leerArchivo = csv.DictReader(archivoSinTokenizar, delimiter=",")

            for fila in leerArchivo:
                titulo = fila["Titulo"]
                abstract = fila["Abstract"]

                tituloTokens = self.tokenizarTexto(nlp, titulo)
                abstractTokens = self.tokenizarTexto(nlp, abstract)

                tituloTokensLimpios = " ".join(tituloTokens)
                abstractTokensLimpios = " ".join(abstractTokens)

                tokenPreProcesados.append({
                    "DOI": fila["DOI"],
                    "TokensTitulo": tituloTokensLimpios,
                    "TokensAbstract": abstractTokensLimpios,
                    "Autores": fila["Autores"],
                    "Fecha": fila["Fecha"],
                    "Seccion": fila["Seccion"]
                })
                
        campos = ["DOI", "TokensTitulo", "TokensAbstract", "Autores", "Fecha", "Seccion"]
        with open(nombreArchivoSalida, mode='w', newline='', encoding="utf-8") as archivoTokenizado:
            escritorCSV = csv.DictWriter(archivoTokenizado, fieldnames=campos)
            escritorCSV.writeheader()
            escritorCSV.writerows(tokenPreProcesados)
        print(f"Archivo procesado y guardado como {nombreArchivoSalida}")
        return tokenPreProcesados
    
normalizarTexto = Normalizador("./archivos/ArticulosArXivEjemplo.csv")
normalizarTexto.procesarArchivo("arxiv_normalizaed_corpus2.csv")