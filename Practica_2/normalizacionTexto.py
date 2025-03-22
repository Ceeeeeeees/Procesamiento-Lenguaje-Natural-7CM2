

class Normalizador ():

    def __init__(self, texto, archivoCSVArticulos):
        archivoCSVArticulos = archivoCSVArticulos
        pass

    def abrirArchivoCSV (self, archivoCSVArticulos):
        with open(archivoCSVArticulos, "r") as archivo:
            texto = archivo.read()
        return texto


    def guardarArchivoNormalizado (self, textoNormalizado, nombreArchivoNormalizado = "ArchivoNormalizado.csv") :
        with open(nombreArchivoNormalizado, "w") as archivoNormalizado:
            archivoNormalizado.write(textoNormalizado)
        print("Archivo normalizado guardado con éxito")
        return archivoNormalizado