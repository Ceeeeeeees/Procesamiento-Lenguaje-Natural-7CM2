import csv
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

class ModeloMLNLP:
    """
    Clase para crear y entrenar modelos de aprendizaje automático aplicados a problemas de NLP.
    Esta clase implementa un pipeline completo para procesamiento de texto y clasificación,
    permitiendo cargar datos normalizados, vectorizarlos con diferentes métodos y entrenar
    modelos de clasificación como Naive Bayes o Regresión Logística.
    Attributes:
        nombreModelo (str): Nombre del modelo a utilizar ('naive_bayes' o 'logistic_regression').
        archivoNormalized (str): Ruta al archivo CSV que contiene el corpus normalizado.
        corpus (dict): Diccionario que almacena los datos del corpus (títulos, abstracts, etc.).
        pipeline (Pipeline): Pipeline de scikit-learn que combina vectorización y clasificación.
    Methods:
        cargarDatos(): Carga los datos del archivo normalizado en el corpus.
        crearPipeline(tipoVectorizacion, ngram_range): Crea un pipeline con vectorizador y clasificador.
        entrenamientoYEvaluar(prueba, columna): Entrena y evalúa el modelo con los datos cargados.
        modeloEntrenamientoPrueba(): Ejecuta el flujo completo de carga, creación y evaluación.
    """
    def __init__(self,nombreModelo):
        self.nombreModelo = nombreModelo
        self.archivoNormalized = "./archivosNormalizados/arxiv_normalized_corpus.csv"
        self.corpus = {
            "Titulo_Tokens": [],
            "Abstract_Tokens": [],
            "TextoConcatenado": [], 
            "Seccion" : []
        }
        self.pipeline = None

    def cargarDatos(self):
        try:
            with open(self.archivoNormalized, 'r', encoding="UTF-8") as tokens:
                reader = csv.DictReader(tokens)
                for fila in reader:
                    self.corpus["Titulo_Tokens"].append(fila["Titulo_Tokens"])
                    self.corpus["Abstract_Tokens"].append(fila["Abstract_Tokens"])
                    
                    textoConcatenado = fila["Titulo_Tokens"] + " " + fila["Abstract_Tokens"]
                    self.corpus["TextoConcatenado"].append(textoConcatenado) 
                    
                    self.corpus["Seccion"].append(fila["Seccion"])
            print(f"Se cargaron {len(self.corpus['Titulo_Tokens'])} títulos y {len(self.corpus['Abstract_Tokens'])} abstracts.")


            return self.corpus
        except Exception as corpusError:
            print(f"Error al cargar el corpus: {corpusError}")
            return None
    
    def crearPipeline(self, tipoVectorizacion="tfidf", ngram_range=(2,2)):
        modelo = self.nombreModelo.lower()

        if modelo == "naive_bayes":
            clasificador = MultinomialNB()
        elif modelo == "logistic_regression":
            clasificador = LogisticRegression()
        else:
            raise ValueError("Modelo no soportado. Usa un modelo soportado [NaiveBayes, LogisticRegression].")
        
        if tipoVectorizacion.lower() == "frequency":
            vectorizador = CountVectorizer(ngram_range=ngram_range, token_pattern=r'(?u)\w+|\w+\n|\.|\¿|\?')
        elif tipoVectorizacion.lower() == "tfidf":
            vectorizador = TfidfVectorizer(ngram_range=ngram_range, token_pattern=r'(?u)\w+|\w+\n|\.|\¿|\?')
        elif tipoVectorizacion.lower() == "binary":
            vectorizador = CountVectorizer(binary=True, ngram_range=ngram_range, token_pattern=r'(?u)\w+|\w+\n|\.|\¿|\?')
        else:
            raise ValueError("Tipo de vectorización no soportado. Usa 'frequency', 'tfidf' o 'binary'.")
        
        self.pipeline = Pipeline([
            ('text_representation', vectorizador),
            ('classifier', clasificador)
        ])

        print(f"Pipeline creado con el modelo {modelo} y vectorizador {vectorizador.__class__.__name__}.")
        return self.pipeline
    
    def entrenamientoYEvaluar(self, prueba = 0.3, columna = "TextoConcatenado" ):
        try:
            if self.pipeline is None:
                raise ValueError("El pipeline no ha sido creado. Primero crea el pipeline.")
            if not self.corpus[columna]:
                raise ValueError("El corpus está vacío. Primero carga los datos.")
            
            X_train, X_test, y_train, y_test = train_test_split(
                self.corpus[columna],
                self.corpus["Seccion"], 
                test_size=prueba, 
                shuffle=True,
                random_state=0)
            
            print(f"Entrenando con {len(X_train)} muestras, probando con {len(X_test)} muestras")

            self.pipeline.fit(X_train, y_train)

            n_features = self.pipeline['text_representation'].get_feature_names_out() #Caracteristicas extraidas
            print(f"Número de características extraídas: {len(n_features)}\n{n_features}")

            y_pred = self.pipeline.predict(X_test)
            report = classification_report(y_test, y_pred)
            
            print("Reporte de clasificación:")
            print(report)
            return {
                'X_train': X_train,
                'X_test': X_test,
                'y_train': y_train,
                'y_test': y_test,
                'y_pred': y_pred,
                'report': report,
                'n_features': n_features
            }

        except Exception as pipelineError:
            print(f"Error al crear el pipeline: {pipelineError}")
            return None
        
    def modeloEntrenamientoPrueba(self):
        self.cargarDatos()
        self.crearPipeline("tfidf")
        self.entrenamientoYEvaluar(prueba=0.3, columna="TextoConcatenado")

modelo = ModeloMLNLP("naive_bayes")
modelo.modeloEntrenamientoPrueba()

