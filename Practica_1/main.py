import os
from conversorBib2Ris import ConversorBib2Ris
from conversorRis2Bib import ConversorRis2Bib

rutaResultado = "./archivosConvertidos"
if not os.path.exists("archivosConvertidos"):
    os.mkdir("archivosConvertidos")

archivosBib1 = ["./archivosPrueba/conference1.bib",
                "./archivosPrueba/conference2.bib", 
                "./archivosPrueba/journal1.bib",
                "./archivosPrueba/journal2.bib"]

archivosBib2 = ["./archivosPruebas2/BibTeX/conference_test1.bib",
                "./archivosPruebas2/BibTeX/conference_test2.bib",
                "./archivosPruebas2/BibTeX/conference_test3.bib",
                "./archivosPruebas2/BibTeX/journal_test1.bib",
                "./archivosPruebas2/BibTeX/journal_test2.bib",
                "./archivosPruebas2/BibTeX/journal_test3.bib"]

archivosRis1 = ["./archivosPrueba/conference1.ris",
                "./archivosPrueba/conference2.ris",
                "./archivosPrueba/journal1.ris",
                "./archivosPrueba/journal2.ris"]

archivosRis2 = ["./archivosPruebas2/RIS/conference_test1.ris",
                "./archivosPruebas2/RIS/conference_test2.ris",
                "./archivosPruebas2/RIS/conference_test3.ris",
                "./archivosPruebas2/RIS/journal_test1.ris",
                "./archivosPruebas2/RIS/journal_test2.ris",
                "./archivosPruebas2/RIS/journal_test3.ris"] 
while True:

    print("Convertir de RIS a BibTeX")
    print("\nElige el tipo de prueba[conversion] a realizar [Bib o RIS]:")
    print("1 - Bib a Ris")
    print("2 - RIS a Bib")
    opcion = input("Opcion conversion:\t")

    if opcion == "1":
        for indice, archivoBib in enumerate(archivosBib2, start=1):
            conversorBib2Ris = ConversorBib2Ris(archivoBib)
            salida = conversorBib2Ris.procesarArchivo("Ris")
            nuevoNombre = os.path.join(rutaResultado, f"archivo{indice}.ris")
            os.rename(salida, nuevoNombre)
    elif opcion == "2":
        for indice, archivoRis in enumerate(archivosRis2, start=1):
            conversorRis2Bib = ConversorRis2Bib(archivoRis)
            salida = conversorRis2Bib.procesarArchivo("Bib")
            nuevoNombre = os.path.join(rutaResultado, f"archivo{indice}.bib")
            os.rename(salida, nuevoNombre)

    else: print("Opcion no valida")

    print("\n\tPuedes revisar los archivos convertidos en la carpeta archivosConvertidos")

    condicionCierre = input("Desea realizar otra conversion? [s/n]: ")
    
    if condicionCierre.lower() != 's':
        break