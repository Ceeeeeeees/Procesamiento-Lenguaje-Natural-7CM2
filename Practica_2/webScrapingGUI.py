import tkinter as tk
from tkinter import messagebox


class WebScrapingGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("InterfazWeb Scraping")
        self.root.geometry("750x250")

        #Etiquetas
        self.etiquetaRepositorio = tk.Label(root, text="Repositorio (arXiv o Pubmed)")
        self.etiquetaRepositorio.grid(row=0, column=0)

        #Selecciona Categoria de arXiv(Computacion&Lenguaje o Vision&Patrones) - radio button
        self.categoria = tk.StringVar()
        self.radioComputacion = tk.Radiobutton(root, text="Computacion&Lenguaje", variable=self.categoria, value="Computacion&Lenguaje")
        self.radioComputacion.grid(row=0, column=2)
        self.radioVision = tk.Radiobutton(root, text="Vision&Patrones", variable=self.categoria, value="Vision&Patrones")
        self.radioVision.grid(row=0, column=3)
        

        self.etiquetaNumArticulos = tk.Label(root, text="Numero de Articulos")
        self.etiquetaNumArticulos.grid(row=1, column=0)

        #Cajas de texto
        self.cajaRepositorio = tk.Entry(root)
        self.cajaRepositorio.grid(row=0, column=1)

        self.cajaNumArticulos = tk.Entry(root)
        self.cajaNumArticulos.grid(row=1, column=1)
        
        #Botones
        self.botonScraping = tk.Button(root, text="Generar articulos", command=self.generarArticulos)
        self.botonScraping.grid(row=3, column=0, columnspan=2)

    def generarArticulos(self):
        try:
            repositorio = self.cajaRepositorio.get().strip()
            numArticulosStr = self.cajaNumArticulos.get().strip()

            if not repositorio or not numArticulosStr:
                messagebox.showerror("Error", "Debe ingresar un repositorio y un número de artículos")
                return

            numArticulos = int(numArticulosStr)

            # 📌 Crear la instancia de WebScraping sin obtener los artículos aún
            from webScraping import WebScraping
            RepositorioWebScraping = WebScraping(repositorio, numArticulos)

            # 📌 Ahora sí, obtener los artículos
            articulos = RepositorioWebScraping.obtenerArticulos()

            if not articulos:
                messagebox.showinfo("Sin Resultados", "No se encontraron artículos")
                return

            # 📌 Generar el archivo
            #nombre_archivo = f"Articulos_{repositorio}.csv"
            #RepositorioWebScraping.generaArchivo(articulos, nombre_archivo)
            #messagebox.showinfo("Éxito", f"Artículos guardados en {nombre_archivo}")

        except ValueError:
            messagebox.showerror("Error", "El número de artículos debe ser un número entero válido")
        except Exception as e:
            messagebox.showerror("Error inesperado", f"Ocurrió un error: {e}")

        
try:
    root = tk.Tk()
    app = WebScrapingGUI(root)
    root.mainloop()
except Exception as e:
    print(f"Error al iniciar la aplicación: {e}")
        
        
        