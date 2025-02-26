import re

class ConversorBase:

    def __init__(self, archivo) -> None:
        """
        Este metodo hace inicializa el archivo que se va a procesar 
        
        Argumentos:
        - archivo: Es el archivo que se va a procesar
        """
        self.archivo = archivo

    def convertir_Contenido(self, contenido):
        """
        Convierte el contenido proporcionado.

        Este método aplica la lógica para convertir el contenido del archivo a un formato deseado.
        Si la lógica de conversión no se encuentra implementada en clases derivadas, se lanza un NotImplementedError
        para indicar que la conversión no puede realizarse.

        Parámetros:
            contenido: Es el contenido original del archivo que se desea convertir.

        Retorna:
            str: El contenido convertido, si la conversión se implementa correctamente.

        Excepciones:
            NotImplementedError: Si la conversión no está implementada.

        """
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
            #contenidos = contenidoNormalizado.splitlines()          # Dividimos el vontenido en lineas
            contenidoProcesado = self.convertir_Contenido(contenidoProcesado)
        with open(nombreArchivoDestino , 'w', encoding='utf-8') as archivo_procesado:
            archivo_procesado.write(contenidoProcesado)
        return nombreArchivoDestino

