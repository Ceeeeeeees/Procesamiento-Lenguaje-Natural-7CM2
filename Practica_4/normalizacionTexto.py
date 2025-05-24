import spacy
import csv

class NormalizadorTexto():

    def __init__(self, archivoCSVTweets):
        self.archivoCSVTweets = archivoCSVTweets
        self.pln = self.cargarModelo()
        self.categoriasExcluir = ["DET", "ADP", "CCONJ", "SCONJ", "PRON"]
        
    def cargarModelo(self):
        """Carga el modelo de spaCy para español"""
        try:
            return spacy.load("es_core_news_sm")
        except:
            print("Modelo 'es_core_news_sm' no encontrado. Ejecuta:")
            print("python -m spacy download es_core_news_sm")
            exit()
            
    def tokenizar(self, texto):
        """Realiza solo la tokenización del texto"""
        contenido = self.pln(texto)
        tokens = [token.text for token in contenido if not token.is_space]
        return tokens
    
    def eliminarPalabrasVacias(self, tokens_con_pos):
        """Elimina las palabras vacías basándose en las categorías gramaticales"""
        return [token for token, pos, _, _ in tokens_con_pos if pos not in self.categoriasExcluir]
    
    def lematizar(self, tokens_con_pos):
        """Devuelve solo los lemas de los tokens"""
        return [lemma for _, _, _, lemma in tokens_con_pos if lemma.isalpha()]
    
    def eliminarPalabrasVaciasDelTexto(self, texto):
        """Elimina stopwords directamente del texto sin devolver tokens"""
        doc = self.pln(texto)
        palabras = [token.text for token in doc if token.pos_ not in self.categoriasExcluir and not token.is_space]
        return " ".join(palabras)
    
    def lematizarTexto(self, texto):
        """Lematiza directamente el texto sin eliminar stopwords"""
        doc = self.pln(texto)
        lemas = [token.lemma_ for token in doc if token.lemma_.isalpha() and not token.is_space]
        return " ".join(lemas)
    
    def lematizarSinStopwords(self, texto):
        """Lematiza el texto y elimina stopwords sin tokenización explícita"""
        doc = self.pln(texto)
        lemas_filtrados = [token.lemma_ for token in doc 
                         if token.pos_ not in self.categoriasExcluir 
                         and token.lemma_.isalpha() 
                         and not token.is_space]
        return " ".join(lemas_filtrados)
    
    def obtenerTokensConMetadata(self, texto):
        """Obtiene tokens con su información gramatical"""
        contenido = self.pln(texto)
        return [(token.text, token.pos_, token.tag_, token.lemma_) for token in contenido if not token.is_space]
    
    def procesarTexto(self, texto, modo="original"):
        """
        Procesa un texto según el modo seleccionado
        
        Modos disponibles:
        - "original": texto sin procesar
        - "tokenizacion": solo tokenización
        - "stopwords": solo eliminación de stopwords
        - "lematizacion": solo lematización
        - "tokenizacion_stopwords": tokenización + eliminación de stopwords
        - "tokenizacion_lematizacion": tokenización + lematización
        - "stopwords_lematizacion": eliminación de stopwords + lematización
        - "completo": tokenización + stopwords + lematización
        """
        if modo == "original":
            return texto
            
        if modo == "tokenizacion":
            tokens = self.tokenizar(texto)
            return tokens
            
        if modo == "stopwords":
            return self.eliminarPalabrasVaciasDelTexto(texto)
            
        if modo == "lematizacion":
            return self.lematizarTexto(texto)
            
        if modo == "stopwords_lematizacion":
            return self.lematizarSinStopwords(texto)
            
        # Para los modos que retornan tokens explícitamente
        tokens_con_metadata = self.obtenerTokensConMetadata(texto)
        
        if modo == "tokenizacion_stopwords":
            tokens_filtrados = self.eliminarPalabrasVacias(tokens_con_metadata)
            return tokens_filtrados
            
        if modo == "tokenizacion_lematizacion":
            lemas = self.lematizar(tokens_con_metadata)
            return lemas
            
        if modo == "completo":
            # Tokenización + eliminación de stopwords + lematización
            tokens_filtrados = []
            for token, pos, tag, lemma in tokens_con_metadata:
                if pos not in self.categoriasExcluir and lemma.isalpha():
                    tokens_filtrados.append(lemma)
            return tokens_filtrados
            
        # Si se proporciona un modo no reconocido, devolver el texto original
        return texto
        
    def procesarArchivo(self, nombreArchivoSalida, modo="original"):
        """
        Procesa el archivo CSV según el modo seleccionado
        """
        nombreArchivoEntrada = self.archivoCSVTweets

        tokensPreProcesados = []
        with open(nombreArchivoEntrada, newline='', encoding="utf-8") as archivoSinTokenizar:
            leerArchivo = csv.DictReader(archivoSinTokenizar, delimiter=",")

            for fila in leerArchivo:
                teaserTweet = fila["Teaser Text"]
                
                # Aplicar el modo de procesamiento seleccionado
                resultado_procesado = self.procesarTexto(teaserTweet, modo=modo)
                
                # Convertir lista de tokens a texto para guardar en CSV (si es necesario)
                resultado_texto = " ".join(resultado_procesado) if isinstance(resultado_procesado, list) else resultado_procesado
                
                registro = {
                    "Tweet_ID": fila["Tweet ID"],
                    "Tweet_Date": fila["Tweet Date"],
                    "Media_Name": fila["Media Name"],
                    "Media_Origin": fila["Media Origin"],
                    "Teaser_Tokens": resultado_texto
                }
                
                if "Tag Value" in fila:
                    registro["Tag_Value"] = fila["Tag Value"]
                    
                tokensPreProcesados.append(registro)

        # Determinar los campos del CSV de salida
        if tokensPreProcesados and "Tag_Value" in tokensPreProcesados[0]:
            campos = ["Tweet_ID", "Tweet_Date", "Media_Name", "Media_Origin", "Teaser_Tokens", "Tag_Value"]
        else:
            campos = ["Tweet_ID", "Tweet_Date", "Media_Name", "Media_Origin", "Teaser_Tokens"]

        # Escribir en el archivo de salida
        with open(nombreArchivoSalida, mode='w', newline='', encoding="utf-8") as archivoTokenizado:
            escritorCSV = csv.DictWriter(archivoTokenizado, fieldnames=campos)
            escritorCSV.writeheader()
            escritorCSV.writerows(tokensPreProcesados)
            
        print(f"Archivo procesado y guardado como {nombreArchivoSalida}")
        return tokensPreProcesados


# Ejemplo de uso para las diferentes combinaciones:
# Creamos el normalizador con nuestro archivo de entrada
normalizador = NormalizadorTexto("./corpus/TA1C_dataset_detection_dev.csv")

# 1. Solo tokenización
normalizador.procesarArchivo("TA1C_dataset_dev_Tokenizacion.csv", modo="tokenizacion")

# 2. Solo eliminación de stopwords
normalizador.procesarArchivo("TA1C_dataset_dev_Stopwords.csv", modo="stopwords")

# 3. Solo lematización
normalizador.procesarArchivo("TA1C_dataset_dev_Lematizacion.csv", modo="lematizacion")

# 4. Tokenización + eliminación de stopwords
normalizador.procesarArchivo("TA1C_dataset_dev_Tokenizacion_Stopwords.csv", modo="tokenizacion_stopwords")

# 5. Tokenización + lematización
normalizador.procesarArchivo("TA1C_dataset_dev_Tokenizacion_Lematizacion.csv", modo="tokenizacion_lematizacion")

# 6. Eliminación de stopwords + lematización (lo que específicamente pediste)
normalizador.procesarArchivo("TA1C_dataset_dev_Stopwords_Lematizacion.csv", modo="stopwords_lematizacion")

# 7. Proceso completo (tokenización + stopwords + lematización)
normalizador.procesarArchivo("TA1C_dataset_dev_Completo.csv", modo="completo")


