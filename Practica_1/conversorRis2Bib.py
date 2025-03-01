import re
from conversorBase import ConversorBase

class ConversorRis2Bib(ConversorBase):
    def convertir_Contenido(self, contenido):
        contenido = self.convertirAutor(contenido)
        contenido = self.convertirTitulo(contenido)
        contenido = self.convertirTituloLibro(contenido)
        contenido = self.convertirFecha(contenido)
        contenido = self.convertirVolumen(contenido)
        contenido = self.convertirNumeroError(contenido)
        contenido = self.convertirPaginas(contenido)
        contenido = self.convertirDOI(contenido)
        contenido = self.convertirURL(contenido)
        contenido = self.convertirEditorial(contenido)
        contenido = self.convertirJournal(contenido)
        contenido = self.convertirEditores(contenido)
        contenido = self.convertirEdicion(contenido)
        contenido = self.convertirPalabrasClave(contenido)
        contenido = self.convertirISBNorISSN(contenido)
        contenido = self.convertirDireccion(contenido)
        contenido = self.convertirAbstract(contenido)
        #contenido = self.convertirID(contenido)
        contenido = self.convertirTipoReferencia(contenido)
        contenido = self.agregarLlaveFinArchivo(contenido)
        
        return contenido
    
    def convertirAutor(self, contenido):
        regexAutor = re.compile(r'\s*AU\s*-\s*(.+)$', re.IGNORECASE | re.MULTILINE)
        coincidencia = regexAutor.findall(contenido)

        if not coincidencia:
            return contenido
        
        escribirBib = "\nauthor = {" + " and ".join(coincidencia) + "},"
        contenido = regexAutor.sub(escribirBib, contenido, count=1)
        contenido = regexAutor.sub("", contenido)
        return contenido
    
    def convertirTitulo(self, contenido):           # También servira para booktitle
        regexTitulo = re.compile(r'\bTI\b\s*-\s*(.+)')
        coincidencia = regexTitulo.search(contenido)

        if not coincidencia:
            return contenido
        
        tituloTexto = coincidencia.group(1)
        escribirBib = "title = {" + tituloTexto + "},"
        contenido = regexTitulo.sub(escribirBib, contenido)
        return contenido
    
    def convertirTituloLibro(self, contenido):
        regexTituloLibro = re.compile(r'\bBT\b\s*-\s*(.+)')
        coincidencia = regexTituloLibro.search(contenido)

        if not coincidencia:
            return contenido
        
        tituloLibroTexto = coincidencia.group(1)
        escribirBib = "booktitle = {" + tituloLibroTexto + "},"
        contenido = regexTituloLibro.sub(escribirBib, contenido)
        return contenido
    
    def convertirFecha(self, contenido):
        regexFecha = re.compile(r'\bPY\b\s*-\s*(\d{4})(?:/(\d{2}))?(?:/(\d{2}))?')        
        coincidencia = regexFecha.search(contenido)

        if not coincidencia:
            return contenido
        
        conversionMes = {
            "01": "Jan", "02": "Feb", "03": "Mar",
            "04": "Apr", "05": "May", "06": "Jun",
            "07": "Jul", "08": "Aug", "09": "Sep",
            "10": "Oct", "11": "Nov", "12": "Dec"
        }

        contenidoAnio = coincidencia.group(1)
        contenidoMes = coincidencia.group(2) if coincidencia.group(2) is not None else None

        if contenidoMes is None:
            escribirBib = "year = {" + contenidoAnio + "},"
        else:
            equivalenciaMes = conversionMes.get(conversionMes)
            escribirBib = "year = {" + contenidoAnio + "},\nmonth = {" + equivalenciaMes + "},\n" + "day = {" + contenidoDia + "},"

        contenido = regexFecha.sub(escribirBib, contenido, count=1)
        return contenido
    
    def convertirVolumen(self, contenido):
        regexVolumen = re.compile(r'\bVL\b\s*-\s*(\d+)')
        coincidencia = regexVolumen.search(contenido)

        if not coincidencia:
            return contenido
        
        contenidoVolumen = coincidencia.group(1)
        escribirBib = "volume = {" + contenidoVolumen + "},"
        contenido = regexVolumen.sub(escribirBib, contenido)
        return contenido
    
    def convertirNumeroError(self, contenido):
        regexNumeroError = re.compile(r'\bIS\b\s*-\s*(\d+)')
        coincidencia = regexNumeroError.search(contenido)
        
        if not coincidencia:
            return contenido
        
        contenidoNumeroError = coincidencia.group(1)
        escribirBib = "number = {" + contenidoNumeroError + "},"
        contenido = regexNumeroError.sub(escribirBib, contenido)
        return contenido
    
    def convertirPaginas(self, contenido):
        regexPagInicio = re.compile(r'\bSP\b\s*-\s*(\d+)')
        regexPagFin = re.compile(r'\bEP\b\s*-\s*(\d+)\s*')
        
        pagInicio = regexPagInicio.search(contenido)
        pagFin = regexPagFin.search(contenido)
        
        if not pagInicio or not pagFin:
            return contenido
        
        paginas = f"pages = {{{pagInicio.group(1)}--{pagFin.group(1)}}},"
        contenido = regexPagInicio.sub(paginas, contenido)
        contenido = regexPagFin.sub("", contenido, count=1)
        
        return contenido
    
    def convertirDOI(self, contenido):
        regexDOI = re.compile(r'\bDO\b\s*-\s*(10.[\d]+\/[\S]*)\s*')
        coincidencia = regexDOI.search(contenido)

        if not coincidencia:
            return contenido
        
        contenidoDOI = coincidencia.group(1)
        escribirBib = "doi = {" + contenidoDOI + "},"
        contenido = regexDOI.sub(escribirBib, contenido)
        return contenido
    
    def convertirURL(self, contenido):
        regexURL = re.compile(r'\bUR\b\s*-\s*(https?://[^\s{}]+)\s*')
        coincidencia = regexURL.search(contenido)

        if not coincidencia: return contenido

        contenidoURL = coincidencia.group(1)
        escribirBib = "url = {" + contenidoURL + "},\n"
        contenido = regexURL.sub(escribirBib, contenido)
        return contenido
    
    def convertirEditorial(self, contenido):
        regexEditorial = re.compile(r'\bPB\b\s*-\s*(.*)')
        coincidencia = regexEditorial.search(contenido) 
        
        if not coincidencia: return contenido

        contenidoEditorial = coincidencia.group(1)
        escribirBib = "publisher = {" + contenidoEditorial + "},"
        contenido = regexEditorial.sub(escribirBib, contenido)
        return contenido
    
    def convertirJournal(self, contenido):
        regexJournal = re.compile(r'\bJO\b\s*-\s*(.*)$', re.MULTILINE)
        coincidencia = regexJournal.search(contenido)

        if not coincidencia: return contenido

        contenidoJournal = coincidencia.group(1).strip()
        escribirBib = "journal = {" + contenidoJournal + "},"
        contenido = regexJournal.sub(escribirBib, contenido)
        return contenido

    def convertirEditores(self, contenido):
        #editor = {Lee, Alice} → ED - Lee, Alice
        regexEditores = re.compile(r'\s*\bED\b\s*-\s*(.+)$', re.IGNORECASE | re.MULTILINE)
        coincidencia = regexEditores.findall(contenido)

        if not coincidencia:
            return contenido
        
        escribirBib = "\neditor = {" + " and ".join(coincidencia) + "},"
        contenido = regexEditores.sub(escribirBib, contenido, count=1)
        contenido = regexEditores.sub("", contenido)
        return contenido

    def convertirEdicion(self, contenido):
        regexEdicion = re.compile(r'\bET\b\s*-\s*(.*)')
        coincidencia = regexEdicion.search(contenido)

        if not coincidencia: return contenido

        contenidoEdicion = coincidencia.group(1)
        escribirBib = "edition = {" + contenidoEdicion + "},"
        contenido = regexEdicion.sub(escribirBib, contenido)
        return contenido
    
    def convertirPalabrasClave(self, contenido):
        regexPalabrasClave = re.compile(r'\bKW\b\s*-\s*(.+)$')
        coincidencia = regexPalabrasClave.findall(contenido)    

        if not coincidencia: return contenido

        escribirBib = "keywords = {" + " and ".join(coincidencia) + "},"
        contenido = regexPalabrasClave.sub(escribirBib, contenido, count=1)
        contenido = regexPalabrasClave.sub("", contenido)
        return contenido
    
    def convertirISBNorISSN(self, contenido):
        """
        
        ISBN: 13 dígitos para libros publicados después de 2007, 10 dígitos para libros publicados antes
	
        ISSN: 8 dígitos, agrupados en dos grupos de 4 dígitos
        """
        regexISBNorISSN = re.compile(r'\bSN\b\s*-\s*([\d-]+)')
        coincidencia = regexISBNorISSN.search(contenido)
        
        if not coincidencia: return contenido

        tamanioISBNorISSN = len(coincidencia.group(1))
        if tamanioISBNorISSN == 9:
            escribirBib = "issn = {" + coincidencia.group(1) + "},"
        elif tamanioISBNorISSN == 14 or tamanioISBNorISSN == 17:
            escribirBib = "isbn = {" + coincidencia.group(1) + "},"
        contenido = regexISBNorISSN.sub(escribirBib, contenido)
        return contenido
    
    def convertirDireccion(self, contenido):
        regexDireccion = re.compile(r'\bCY\b\s*-\s*(.*)')
        coincidencia = regexDireccion.search(contenido)
        if not coincidencia: return contenido
        escribirBib = "address = {" + coincidencia.group(1) + "},"
        contenido = regexDireccion.sub(escribirBib, contenido)
        return contenido
    
    def convertirAbstract(self, contenido):
        regexAbstract = re.compile(r'\bAB\b\s*-\s*(.*)')
        coincidencia = regexAbstract.search(contenido)
        if not coincidencia: return contenido
        escribirBib = "abstract = {" + coincidencia.group(1) + "},"
        contenido = regexAbstract.sub(escribirBib, contenido)
        return contenido
    
    def convertirTipoReferencia(self, contenido):
        regexID = re.compile(r'\bID\b\s*-\s*(.*)\s*')
        regexTipoReferencia = re.compile(r'\bTY\b\s*-\s*(.*)')
        
        coincidencia = regexTipoReferencia.search(contenido)
        coincidenciaID = regexID.search(contenido)
        
        if not coincidenciaID: return contenido
        if not coincidencia: return contenido
        
        escribirBibID = coincidenciaID.group(1)
        contenido = regexID.sub("", contenido)

        contenidoTipoReferencia = coincidencia.group(1).lower()
        
        if contenidoTipoReferencia == "conf": contenidoTipoReferencia = "inproceedings"
        elif contenidoTipoReferencia == "jour": contenidoTipoReferencia = "article"

        escribirBib = "@" + contenidoTipoReferencia + "{" + escribirBibID + ","
        contenido = regexTipoReferencia.sub(escribirBib, contenido)
        return contenido
    
    def agregarLlaveFinArchivo(self, contenido):
        contenido = contenido.rstrip()  # Elimina espacios en blanco y saltos de línea finales
        if not contenido.endswith("}"):  # Si no termina con }
            contenido += "\n}"  # Agrega la llave de cierre con un salto de línea
        return contenido

    
archivoRuta = "./archivosPrueba/journal1.ris"
conversorRis2Bib  = ConversorRis2Bib(archivoRuta)
conversorRis2Bib.procesarArchivo("Bib")