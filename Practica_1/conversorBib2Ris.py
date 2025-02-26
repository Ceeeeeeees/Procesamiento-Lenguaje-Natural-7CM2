import re
from conversorBase import ConversorBase

class ConversorBib2Ris(ConversorBase):

    def convertir_Contenido(self, contenido):
        """
        Es el método de la clase heredada, donde le pasamos el contenido del archivo y
        se encargara de aplicar ciertas reglas para convertir el contenido del archivo a un formato RIS
        
        Argumentos:
        - contenido: Es el contenido del archivo que se va a convertir

        Retorna:
        - contenido: Devuelve el contenido convertido a formato
        """
        contenido = self.convertirTipoReferencia(contenido)
        contenido = self.convertirAutor_es(contenido)
        contenido = self.convertirEditor(contenido)
        contenido = self.convertirTituloOrTituloLibro(contenido)
        #contenido = self.convertirAnio(contenido)
        contenido = self.convertirFecha(contenido)
        contenido = self.convertirVolumen(contenido)
        contenido = self.convertirNumeroError(contenido)
        contenido = self.convertirEditorial(contenido)
        contenido = self.convertirDireccion(contenido)
        contenido = self.convertirPaginas(contenido)
        contenido = self.convertirAbstract(contenido)
        contenido = self.convertirISBNorISSN(contenido)
        contenido = self.convertirDOI(contenido)
        contenido = self.convertirURL(contenido)
        contenido = self.convertirEdicion(contenido)
        contenido = self.convertirPalabrasClave(contenido)
        contenido = self.convertirJournal(contenido)
        contenido = self.verificaLlaveFinal(contenido)
        return contenido
    
    def convertirTipoReferencia(self, contenido):
        """
        Este método se encarga de convertir el tipo de referencia de un archivo BibTex a un formato RIS
        """
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
        Este método se encarga de convertir los autores de un archivo BibTex a un formato RIS
        """
        regexAutor = re.compile(r'author\s*=\s*\{(.*?)\}\,', re.IGNORECASE | re.DOTALL)   # Las banderas re.IGNORECASE y re.DOTALL permite que la busqueda identifique las coincidencias con mayusculas y minusculas y tambien con saltos de linea.
        coincidencia = regexAutor.search(contenido)
        
        if not coincidencia:
            return contenido
        
        autores_texto = coincidencia.group(1)
        autores = [autor.strip() for autor in re.split(r'\band\b', autores_texto, flags=re.IGNORECASE)] # Dividimos el contenido por "and" y eliminamos los espacios en blanco. Agregamos cada autor a la lista
        escribirRis = "\n".join(f"AU - {autor}" for autor in autores) # Agregamos el prefijo "AU" a cada autor en la lista
        contenido = regexAutor.sub(escribirRis, contenido)
        return contenido

    def convertirEditor(self, contenido):
        """
        Este método se encarga de convertir los editores de un archivo BibTex a un formato RIS
        """
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
        """
        Este método se encarga de convertir el titulo o el titulo del libro de un archivo BibTex a un formato RIS
        """
        regexTitulo = re.compile(r'\b(title|booktitle)\b\s*=\s*\{(.*?)\}\,')
        coincidencias = regexTitulo.findall(contenido)

        if not coincidencias:
            return contenido

        for coincidencia in coincidencias:
            tipoTitulo = coincidencia[0].lower()
            contenidoTitulo = coincidencia[1]
            
            if tipoTitulo == "title":
                escribirRis = f"TI - {contenidoTitulo}"
            elif tipoTitulo == "booktitle":
                escribirRis = f"BT - {contenidoTitulo}"

            contenido = regexTitulo.sub(escribirRis, contenido, 1) # El tercer argumento 
        return contenido
    
    def convertirFecha(self, contenido):
        """
        ESte método se encarga de convertir la fecha de un archivo BibTex a un formato RIS
        Busca si existe la parte de mes y día, posteriormente la convierte a un formato RIS con YYYY/MM/DD
        """

        regexFecha = re.compile(
            r'\byear\s*=\s*\{(\d{4})\}(?:,\s*month\s*=\s*\{([A-Za-z]+)\})?(?:,\s*day\s*=\s*\{(\d{2})\})?,'
        )
        coincidencia = regexFecha.search(contenido)

        conversionMes = {
            "jan": "01",
            "feb": "02",
            "mar": "03",
            "apr": "04",
            "may": "05",
            "jun": "06",
            "jul": "07",
            "aug": "08",
            "sep": "09",
            "oct": "10",
            "nov": "11",
            "dec": "12"
        }
        
        if not coincidencia:
            return contenido
        
        contenidoAnio = coincidencia.group(1)
        contenidoMes = coincidencia.group(2)
        contenidoDia = coincidencia.group(3)

        if contenidoMes:
            contenidoMes = contenidoMes.lower()
            equivalenciaMes = conversionMes[contenidoMes]
            escribirRis = f"PY - {contenidoAnio}/{equivalenciaMes}/{contenidoDia}"
        else:
            escribirRis = f"PY - {contenidoAnio}"

        contenido = regexFecha.sub(escribirRis, contenido)
        return contenido

    def convertirAnio(self, contenido):
        regexAnio = re.compile(r'\byear\b\s*=\s*\{([\d]{4})\}\,')
        coincidencia = regexAnio.search(contenido)
        
        if not coincidencia:
            return contenido
        
        contenidoAnio = coincidencia.group(1)
        escribirRis = f"PY - {contenidoAnio}"
        contenido = regexAnio.sub(escribirRis, contenido)
        return contenido
    
    def convertirVolumen(self, contenido):
        """
        Este método se encarga de convertir el volumen de un archivo BibTex a un formato RIS
        """
        regexVolumen = re.compile(r'volume\s*=\s*\{(\d+)\}\,')
        coincidencia = regexVolumen.search(contenido)

        if not coincidencia:
            return contenido
        
        contenidoVolumen = coincidencia.group(1)
        escribirRis = f"VL - {contenidoVolumen}"
        contenido = regexVolumen.sub(escribirRis, contenido)
        return contenido
    
    def convertirNumeroError(self, contenido):
        """
        Este método se encarga de convertir el número de error de un archivo BibTex a un formato RIS
        """
        regexNumeroError = re.compile(r'number\s*=\s*\{(\d+)\}\,')
        coincidencia = regexNumeroError.search(contenido)

        if not coincidencia:
            return contenido
        
        contenidoNumero = coincidencia.group(1)
        escribirRis = f"IS - {contenidoNumero}"
        contenido = regexNumeroError.sub(escribirRis, contenido)
        return contenido

    def convertirEditorial(self, contenido):
        """
        Este método se encarga de convertir la editorial de un archivo BibTex a un formato RIS
        """
        regexEditorial = re.compile(r'publisher\s*=\s*\{(.*)\}\,')
        coincidencia = regexEditorial.search(contenido)
        
        if not coincidencia:
            return contenido
        
        contenidoEditorial = coincidencia.group(1)
        escribirRis = f"PB - {contenidoEditorial}"
        contenido = regexEditorial.sub(escribirRis, contenido)
        return contenido

    def convertirDireccion(self, contenido):
        """
        Este método permite convertir una dirección de un archivo BibTex a un formato RIS
        """
        regexDireccion = re.compile(r'address\s*=\s*\{(.*?)\}\,')
        coincidencia = regexDireccion.search(contenido)

        if not coincidencia:
            return contenido
        
        contenidoDireccion = coincidencia.group(1)
        escribirRis = f"CY - {contenidoDireccion}"
        contenido = regexDireccion.sub(escribirRis, contenido)
        return contenido

    def convertirPaginas(self, contenido):
        """
        Este método permite convertir las páginas de un archivo BibTex a un formato RIS (SP - EP)
        """
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
        """
        ESte método permite convertir el abstract de un archivo BibTex a un formato RIS
        """
        regexAbstract = re.compile(r'abstract\s*=\s*\{(.*?)\}\,')
        coincidencia = regexAbstract.search(contenido)

        if not coincidencia:
            return contenido
        
        contenidoAbstract = coincidencia.group(1)
        escribirRis = f"AB - {contenidoAbstract}"
        contenido = regexAbstract.sub(escribirRis, contenido)
        return contenido

    def convertirISBNorISSN(self, contenido):
        """
        Este método permite convertir el ISBN o ISSN de un archivo BibTex a un formato RIS
        """
        regexISBNorISSN = re.compile(r'\b(isbn|issn)\b\s*=\s*\{([\d-]+)\}')
        coincidencias = regexISBNorISSN.findall(contenido)

        if not coincidencias:
            return contenido    

        for coincidencia in coincidencias:
            tipoISBNorISSN = coincidencia[0].lower()
            contenidoISBNorISSN = coincidencia[1]

            if tipoISBNorISSN == "isbn":
                escribirRis = f"SN - {contenidoISBNorISSN}"
            elif tipoISBNorISSN == "issn":
                escribirRis = f"SN - {contenidoISBNorISSN}"
            
            contenido = regexISBNorISSN.sub(escribirRis, contenido, 1)

        return contenido
    
    def convertirDOI(self, contenido):
        """
        Este método permite convertir el DOI de un archivo BibTex a un formato RIS
        
        La BUSQUEda se realiza con un prefijo (10.) que identifica la editorial y un sufijo (cualquier carácter) que identifica el DOI
        """
        regexDOI = re.compile(r'\bdoi\b\s*=\s*\{(10\.[\d]+\/[\S]*)\}\,')    #Coincide con cualquier carácter que NO sea un espacio en blanco
        coincidencia = regexDOI.search(contenido)

        if not coincidencia:
            return contenido

        contenidoDOI = coincidencia.group(1)
        escribirRis = f"DO - {contenidoDOI}"
        contenido = regexDOI.sub(escribirRis, contenido)
        return contenido
    
    def convertirURL(self, contenido):
        """
        Este método permite convertir la URL de un archivo BibTex a un formato RIS
        
        La búsqueda la realiza con un prefjo (http://) o (https://) y un sufijo que identifica la URL,
        el sufijo no puede contener espacios en blanco ni llaves
        """
        regexURL = re.compile(r'\burl\b\s*=\s*\{(https?://[^\s{}]+)\}')     #No busca espacios en blanco, ni llaves
        coincidencia = regexURL.search(contenido)

        if not coincidencia:
            return contenido
        
        contenidoURL = coincidencia.group(1)
        escribirRis = f"UR - {contenidoURL}"
        contenido = regexURL.sub(escribirRis, contenido)
        return contenido
    
    def convertirEdicion(self, contenido):
        """
        Este método permite convertir la edición de un archivo BibTex a un formato RIS
        edition = {2nd} → ET - 2nd
        """
        regexEdicion = re.compile(r'\bedition\b\s*=\s*\{.*?\}')
        coincidencia = regexEdicion.search(contenido)

        if not coincidencia:
            return contenido
        
        contenidoEdicion = coincidencia.group(1)
        escribirRis = f"ET - {contenidoEdicion}"
        contenido = regexEdicion.sub(escribirRis, contenido)
        return contenido
    
    def convertirPalabrasClave(self, contenido):
        """
        Este método permite convertir las palabras clave de un archivo BibTex a un formato RIS
        keywords = {citation, formats} → KW - citation / KW - formats -> No lo termine de comprender }="""
        regexPalabrasClave = re.compile(r'\bkeywords\b\s*=\s*\{(.*?)\}')
        coincidencia = regexPalabrasClave.search(contenido)

        if not coincidencia:
            return contenido
        
        contenidoPalabrasClave = coincidencia.group(1)
        palabrasClave = [palabraClave.strip() for palabraClave in contenidoPalabrasClave.split(",")]
        escribirRis = "\n".join(f"KW - {palabraClave}" for palabraClave in palabrasClave)
        contenido = regexPalabrasClave.sub(escribirRis, contenido)

        return contenido
    

    def convertirJournal(self, contenido):
        """
        Este método permite convertir el journal de un archivo BibTex a un formato RIS
        journal = {Revista de Ciencia Avanzada} → JO - Revista de Ciencia Avanzada
        """
        regexJournal = re.compile(r'\bjournal\b\s*=\s*\{(.*?)\}\,')
        coincidencia = regexJournal.search(contenido)

        if not coincidencia:
            return contenido
        
        contenidoJournal = coincidencia.group(1)
        escribirRis = f"JO - {contenidoJournal}"
        contenido = regexJournal.sub(escribirRis, contenido)
        return contenido
    
    def verificaLlaveFinal(self, contenido):
        """
        Este método verifica la existencia de la llave final en el archivo bib y la elimina
        """
        regexLlaveFinal = re.compile(r'(\})\s*$')
        coincidencia = regexLlaveFinal.search(contenido)

        if not coincidencia:
            return contenido
        
        contenido = regexLlaveFinal.sub("", contenido)
        return contenido
    
archivoRuta = "./archivosPrueba/conference1.bib"
conversor2Ris = ConversorBib2Ris(archivoRuta)
contenidoConvertido = conversor2Ris.procesarArchivo("Ris")