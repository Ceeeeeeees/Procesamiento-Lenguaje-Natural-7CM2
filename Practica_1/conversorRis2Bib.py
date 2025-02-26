import re
from conversorBase import ConversorBase

class ConversorRis2Bib(ConversorBase):
    def convertir_Contenido(self, contenido):
        contenido = self.convertirAutor(contenido)
        contenido = self.convertirTitulo(contenido)
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
        contenido = self.convertirID(contenido)
        contenido = self.convertirTipoReferencia(contenido)
        
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
        return contenido
    
    def convertirFecha(self, contenido):
        return contenido
    
    def convertirVolumen(self, contenido):
        return contenido
    
    def convertirNumeroError(self, contenido):
        return contenido
    
    def convertirPaginas(self, contenido):
        return contenido
    
    def convertirDOI(self, contenido):
        return contenido
    
    def convertirURL(self, contenido):
        return contenido
    
    def convertirEditorial(self, contenido):
        return contenido
    
    def convertirJournal(self, contenido):
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
        return contenido
    
    def convertirPalabrasClave(self, contenido):
        return contenido
    
    def convertirISBNorISSN(self, contenido):
        return contenido
    
    def convertirDireccion(self, contenido):
        return contenido
    
    def convertirAbstract(self, contenido):
        return contenido
    
    def convertirID(self, contenido):
        return contenido
    
    def convertirTipoReferencia(self, contenido):
        return contenido
    
archivoRuta = "./archivosPrueba/conference1.ris"
conversorRis2Bib  = ConversorRis2Bib(archivoRuta)
conversorRis2Bib.procesarArchivo("Bib")