import re

class ConversorBase:

    def __init__(self, archivo) -> None:
        self.archivo = archivo

    def convertir_Contenido(self, contenido):
        raise NotImplementedError("No se pudo convertir el contenido del archivo")
        return contenido

    

    def procesarArchivo(self, formatoArchivoDestino):
        """
        Este metodo permitira reemplazar las contenidos en un archivo
        
        Argumentos: 
        - formatoArchivoDestino: Permitira especificar el formato del archivo de salida
        
        Retorna:
        - formatoArchivoDestino: Devuelve el archivo con el formato especificado
        """

        archivoOriginal = self.archivo
        
        if formatoArchivoDestino == "Bib":
            nombreArchivoDestino = "Conversion_" + formatoArchivoDestino + ".bib"
        elif formatoArchivoDestino == "Ris":
            nombreArchivoDestino = "Conversion_" + formatoArchivoDestino + ".ris"
        else:
            print("Formato no válido para el archivo de salida")
            return None

        with open (archivoOriginal , 'r', encoding='utf-8') as archivo:
            contenidoProcesado = archivo.read()
            #contenidoNormalizado = self.preProcesarArchivo(contenido)
            #contenidos = contenidoNormalizado.splitlines()          # Dividimos el vontenido en contenidos
            contenidoProcesado = self.convertir_Contenido(contenidoProcesado)
        with open(nombreArchivoDestino , 'w', encoding='utf-8') as archivo_procesado:
            archivo_procesado.write(contenidoProcesado)
        return nombreArchivoDestino


class ConversorBib2Ris(ConversorBase):

    def convertir_Contenido(self, contenido):
        contenido = self.convertirTipoReferencia(contenido)
        contenido = self.convertirAutor_es(contenido)
        contenido = self.convertirEditor(contenido)
        contenido = self.convertirTituloOrTituloLibro(contenido)
        contenido = self.convertirAnio(contenido)
        contenido = self.convertirVolumen(contenido)
        contenido = self.convertirNumeroError(contenido)
        contenido = self.convertirEditorial(contenido)
        contenido = self.convertirDireccion(contenido)
        contenido = self.convertirPaginas(contenido)
        contenido = self.convertirAbstract(contenido)
        contenido = self.convertirISBNorISSN(contenido)
        return contenido
    
    def convertirTipoReferencia(self, contenido):
        regexConversionTipoReferencia = re.compile(r'\@([A-Za-z]+)\s*\{\s*(.*?)\s*\,')
        coincidencia = regexConversionTipoReferencia.search(contenido)
        if not coincidencia:
            return contenido
        contenidoTipo = coincidencia.group(1).lower()
        contenidoID = coincidencia.group(2)

        if contenidoTipo == "article":
            risTipo = "TY - JOUR"
        elif contenidoTipo == "inproceedings":
            risTipo = "TY - CONF"
        
        reemplazo = f"{risTipo}\nID - {contenidoID}"
        contenido = regexConversionTipoReferencia.sub(reemplazo, contenido)
        return contenido
    
    def convertirAutor_es(self, contenido):
        """
        
        """
        regexAutor = re.compile(r'author\s*=\s*\{(.*?)\}\,', re.IGNORECASE | re.DOTALL)   # Las banderas re.IGNORECASE y re.DOTALL permiten que la expresión regular sea insensible a mayúsculas y minúsculas y que el punto coincida con cualquier carácter, incluidos los saltos de línea.
        coincidencia = regexAutor.search(contenido)
        if not coincidencia:
            return contenido
        autores_texto = coincidencia.group(1)
        autores = [autor.strip() for autor in re.split(r'\band\b', autores_texto, flags=re.IGNORECASE)] # Dividimos el contenido por "and" y eliminamos los espacios en blanco. Agregamos cada autor a la lista
        escribirRis = "\n".join(f"AU - {autor}" for autor in autores) # Agregamos el prefijo "AU" a cada autor en la lista
        contenido = regexAutor.sub(escribirRis, contenido)
        return contenido

    def convertirEditor(self, contenido):
        regexEditor = re.compile(r'editor\s*=\s*\{(.*?)\}\,', re.IGNORECASE | re.DOTALL)
        coincidencia = regexEditor.search(contenido)

        if not coincidencia:
            return contenido
        
        editores_texto = coincidencia.group(1)
        editores = [editor.strip() for editor in re.split(r'\band\b', editores_texto, flags=re.IGNORECASE)]        # Dividimos el contenido por "and" y eliminamos los espacios en blanco. Agregamos cada editor a la lista.
        escribirRis = "\n".join(f"ED - {editor}" for editor in editores)                               # Agregamos el prefijo "ED" a cada editor y creamos una nueva lista con los editores y eliminando los espacios en blanco.
        contenido = regexEditor.sub(escribirRis, contenido)
        return contenido

    def convertirTituloOrTituloLibro(self, contenido):
        regexTitulo = re.compile(r'\b(title|booktitle)\b\s*=\s*\{(.*?)\}\,')
        coincidencias = regexTitulo.findall(contenido)

        for coincidencia in coincidencias:
            tipoTitulo = coincidencia[0].lower()
            contenidoTitulo = coincidencia[1]
            
            if tipoTitulo == "title":
                escribirRis = f"TI - {contenidoTitulo}"
            elif tipoTitulo == "booktitle":
                escribirRis = f"BT - {contenidoTitulo}"

            contenido = regexTitulo.sub(escribirRis, contenido, 1)
        
        return contenido
    
    def convertirAnio(self, contenido):
        regexAnio = re.compile(r'year\s*=\s*\{([0-9]{4})\}\,')
        coincidencia = regexAnio.search(contenido)
        
        if not coincidencia:
            return contenido
        
        contenidoAnio = coincidencia.group(1)
        escribirRis = f"PY - {contenidoAnio}"
        contenido = regexAnio.sub(escribirRis, contenido)
        return contenido
    
    def convertirVolumen(self, contenido):
        regexVolumen = re.compile(r'volume\s*=\s*\{(\d+)\}\,')
        coincidencia = regexVolumen.search(contenido)

        if not coincidencia:
            return contenido
        
        contenidoVolumen = coincidencia.group(1)
        escribirRis = f"VL - {contenidoVolumen}"
        contenido = regexVolumen.sub(escribirRis, contenido)
        return contenido
    
    def convertirNumeroError(self, contenido):
        regexNumeroError = re.compile(r'number\s*=\s*\{(\d+)\}\,')
        coincidencia = regexNumeroError.search(contenido)

        if not coincidencia:
            return contenido
        
        contenidoNumero = coincidencia.group(1)
        escribirRis = f"IS - {contenidoNumero}"
        contenido = regexNumeroError.sub(escribirRis, contenido)
        return contenido

    def convertirEditorial(self, contenido):
        regexEditorial = re.compile(r'publisher\s*=\s*\{(.*)\}\,')
        coincidencia = regexEditorial.search(contenido)
        
        if not coincidencia:
            return contenido
        
        contenidoEditorial = coincidencia.group(1)
        escribirRis = f"PB - {contenidoEditorial}"
        contenido = regexEditorial.sub(escribirRis, contenido)
        return contenido

    def convertirDireccion(self, contenido):
        regexDireccion = re.compile(r'address\s*=\s*\{(.*?)\}\,')
        coincidencia = regexDireccion.search(contenido)

        if not coincidencia:
            return contenido
        
        contenidoDireccion = coincidencia.group(1)
        escribirRis = f"CY - {contenidoDireccion}"
        contenido = regexDireccion.sub(escribirRis, contenido)
        return contenido

    def convertirPaginas(self, contenido):
        regexPaginas = re.compile(r'pages\s*=\s*\{(\d+)--?(\d+)\}\,')
        coincidencia = regexPaginas.search(contenido)
        
        if not coincidencia:
            return contenido
        
        contenidoPagInicio = coincidencia.group(1)
        contenidoPagFin = coincidencia.group(2)

        escribirRis = f"SP - {contenidoPagInicio}\nEP - {contenidoPagFin}"
        contenido = regexPaginas.sub(escribirRis, contenido)
        return contenido

    def convertirAbstract(self, contenido):
        regexAbstract = re.compile(r'abstract\s*=\s*\{(.*?)\}\,')
        coincidencia = regexAbstract.search(contenido)

        if not coincidencia:
            return contenido
        
        contenidoAbstract = coincidencia.group(1)
        escribirRis = f"AB - {contenidoAbstract}"
        contenido = regexAbstract.sub(escribirRis, contenido)
        return contenido

    def convertirISBNorISSN(self, contenido):
        regexISBNorISSN = re.compile(r'(isbn|issn)\s*=\s*\{()\}\,')

        return contenido
    
    def convertirDOI(self, contenido):
        return contenido
    
    def convertirURL(self, contenido):
        return contenido
    
    def convertirEdicion(self, contenido):
        return contenido
    
    def convertirPalabrasClave(self, contenido):
        return contenido
    

    def convertirJournal(self, contenido):
        return contenido

    
        
        
conversorBib2Ris = ConversorBib2Ris("./archivosPrueba/conference1.bib")
conversorBib2Ris.procesarArchivo("Ris")
