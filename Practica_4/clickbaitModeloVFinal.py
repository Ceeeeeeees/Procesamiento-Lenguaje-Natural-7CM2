import csv
import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from imblearn.over_sampling import RandomOverSampler
from sklearn.decomposition import TruncatedSVD


class ClickBaitDetector:

    def __init__(self, tipoVectorizacion, nombreModelo, tipoNormalizacion = "Completo"):
        self.nombreModelo = nombreModelo
        self.archivoNormalizacion = {
        "Completo": "./corpus_tokenizado/train/TA1C_dataset_Completo.csv",
        "Tokenizacion": "./corpus_tokenizado/train/TA1C_dataset_Tokenizacion.csv",
        "Stopwords": "./corpus_tokenizado/train/TA1C_dataset_Stopwords.csv",
        "Lematizacion": "./corpus_tokenizado/train/TA1C_dataset_Lematizacion.csv",
        "Tokenizacion_Stopwords": "./corpus_tokenizado/train/TA1C_dataset_Tokenizacion_Stopwords.csv",
        "Tokenizacion_Lematizacion": "./corpus_tokenizado/train/TA1C_dataset_Tokenizacion_Lematizacion.csv",
        "Stopwords_Lematizacion": "./corpus_tokenizado/train/TA1C_dataset_Stopwords_Lematizacion.csv"
    }
        self.archivoDevNormalizacion = {
        "Completo": "./corpus_tokenizado/dev/TA1C_dataset_dev_Completo.csv",
        "Tokenizacion": "./corpus_tokenizado/dev/TA1C_dataset_dev_Tokenizacion.csv",
        "Stopwords": "./corpus_tokenizado/dev/TA1C_dataset_dev_Stopwords.csv",
        "Lematizacion": "./corpus_tokenizado/dev/TA1C_dataset_dev_Lematizacion.csv",
        "Tokenizacion_Stopwords": "./corpus_tokenizado/dev/TA1C_dataset_dev_Tokenizacion_Stopwords.csv",
        "Tokenizacion_Lematizacion": "./corpus_tokenizado/dev/TA1C_dataset_dev_Tokenizacion_Lematizacion.csv",
        "Stopwords_Lematizacion": "./corpus_tokenizado/dev/TA1C_dataset_dev_Stopwords_Lematizacion.csv"
    }
        self.tipoNormalizacion = tipoNormalizacion
        self.archivoNormalizado = self.archivoNormalizacion[tipoNormalizacion]
        self.archivoDevNormalizado = self.archivoDevNormalizacion[tipoNormalizacion]
        self.tipoVectorizacion = tipoVectorizacion
        self.corpus = {
            "Tweet_ID": [],
            "Teaser_Tokens": [],
            "Tag_Value": []
        }
        self.pipeline = None
        self.experimentos = [
            ("naive_bayes", "frecuencia", (1, 1), {}),
            ("naive_bayes", "binaria", (1, 1), {}),
            ("naive_bayes", "tfidf", (1, 1), {}),
            
            ("logistic_regression", "frecuencia", (1, 1), {"max_iter": 200}),
            ("logistic_regression", "binaria", (1, 1), {"max_iter": 200}),
            ("logistic_regression", "tfidf", (1, 1), {"max_iter": 200}),

            ("svc", "frecuencia", (1, 1), {"kernel": "linear", "C": 1.0}),
            ("svc", "binaria", (1, 1), {"kernel": "linear", "C": 1.0}),
            ("svc", "tfidf", (1, 1), {"kernel": "linear", "C": 1.0}),

            #("mlp", "frecuencia", (1, 1), {"hidden_layer_sizes": (100,), "max_iter": 100}),
            #("mlp", "binaria", (1, 1), {"hidden_layer_sizes": (100,), "max_iter": 100}),
            #("mlp", "tfidf", (1, 1), {"hidden_layer_sizes": (100,), "max_iter": 100}),
        
            ("random_forest", "frecuencia", (1, 1), {"n_estimators": 100}),
            ("random_forest", "binaria", (1, 1), {"n_estimators": 100}),
            ("random_forest", "tfidf", (1, 1), {"n_estimators": 100}),#
#
            #("gradient_boosting", "frecuencia", (1, 1), {"n_estimators": 100}),
            #("gradient_boosting", "binaria", (1, 1), {"n_estimators": 100}),
            #("gradient_boosting", "tfidf", (1, 1), {"n_estimators": 100}),
            
            ("naive_bayes", "frecuencia", (2, 2), {}),
            ("naive_bayes", "binaria", (2, 2), {}),
            ("naive_bayes", "tfidf", (2, 2), {}),
            
            ("logistic_regression", "frecuencia", (2, 2), {"max_iter": 200}),
            ("logistic_regression", "binaria", (2, 2), {"max_iter": 200}),
            ("logistic_regression", "tfidf", (2, 2), {"max_iter": 200}),
            
            ("svc", "frecuencia", (2, 2), {"kernel": "linear", "C": 1.0}),
            ("svc", "binaria", (2, 2), {"kernel": "linear", "C": 1.0}),
            ("svc", "tfidf", (2, 2), {"kernel": "linear", "C": 1.0}),
            
            #("mlp", "frecuencia", (2, 2), {"hidden_layer_sizes": (100,), "max_iter": 100}),
            #("mlp", "binaria", (2, 2), {"hidden_layer_sizes": (100,), "max_iter": 100}),
            #("mlp", "tfidf", (2, 2), {"hidden_layer_sizes": (100,), "max_iter": 100}),
        
            ("random_forest", "frecuencia", (2, 2), {"n_estimators": 100}),
            ("random_forest", "binaria", (2, 2), {"n_estimators": 100}),
            ("random_forest", "tfidf", (2, 2), {"n_estimators": 100}),
            
            #("gradient_boosting", "frecuencia", (2, 2), {"n_estimators": 100}),
            #("gradient_boosting", "binaria", (2, 2), {"n_estimators": 100}),
            #("gradient_boosting", "tfidf", (2, 2), {"n_estimators": 100}),
            
            ("naive_bayes", "frecuencia", (3, 3), {}),
            ("naive_bayes", "binaria", (3, 3), {}),
            ("naive_bayes", "tfidf", (3, 3), {}),
            
            ("logistic_regression", "frecuencia", (3, 3), {"max_iter": 200}),
            ("logistic_regression", "binaria", (3, 3), {"max_iter": 200}),
            ("logistic_regression", "tfidf", (3, 3), {"max_iter": 200}),
            
            ("svc", "frecuencia", (3, 3), {"kernel": "linear", "C": 1.0}),
            ("svc", "binaria", (3, 3), {"kernel": "linear", "C": 1.0}),
            ("svc", "tfidf", (3, 3), {"kernel": "linear", "C": 1.0}),
            
            #("mlp", "frecuencia", (3, 3), {"hidden_layer_sizes": (100,), "max_iter": 100}),
            #("mlp", "binaria", (3, 3), {"hidden_layer_sizes": (100,), "max_iter": 100}),
            #("mlp", "tfidf", (3, 3), {"hidden_layer_sizes": (100,), "max_iter": 100}),
           
            ("random_forest", "frecuencia", (3, 3), {"n_estimators": 100}),
            ("random_forest", "binaria", (3, 3), {"n_estimators": 100}),
            ("random_forest", "tfidf", (3, 3), {"n_estimators": 100}),
            
            #("gradient_boosting", "frecuencia", (3, 3), {"n_estimators": 100}),
            #("gradient_boosting", "binaria", (3, 3), {"n_estimators": 100}),
            #("gradient_boosting", "tfidf", (3, 3), {"n_estimators": 100}),
        ]

    def cargarDatos(self):
        try:
            with open(self.archivoNormalizado, mode='r', encoding='utf-8') as tokens:
                reader = csv.DictReader(tokens)
                for fila in reader:
                    self.corpus["Tweet_ID"].append(fila["Tweet_ID"])
                    self.corpus["Teaser_Tokens"].append(fila["Teaser_Tokens"])
                    self.corpus["Tag_Value"].append(fila["Tag_Value"])
            print(f"Se cargaron {len(self.corpus['Tweet_ID'])} tweets.")
            return self.corpus
        except FileNotFoundError:
            print(f"Error: El archivo {self.archivoNormalizado} no se encuentra.")
            return None
        except Exception as e:
            print(f"Error al cargar el archivo: {e}")
            return None
    
    def crearPipeline(self, tipoVectorizacion="tfidf", ngram_range=(1,1), modelo = None, parametros = None):
        nombreModelo = modelo or self.nombreModelo

        # Vectorización normal
        if tipoVectorizacion == "frecuencia":
            vectorizador = CountVectorizer(ngram_range=ngram_range, token_pattern=r'(?u)\w+|\w+\n|\.|\¿|\?')
        elif tipoVectorizacion == "tfidf":
            vectorizador = TfidfVectorizer(ngram_range=ngram_range, token_pattern=r'(?u)\w+|\w+\n|\.|\¿|\?')
        elif tipoVectorizacion == "binaria":
            vectorizador = CountVectorizer(binary=True, ngram_range=ngram_range, token_pattern=r'(?u)\w+|\w+\n|\.|\¿|\?')
        elif tipoVectorizacion == "svd":
            # Pipeline de tfidf + reducción dimensional
            tfidf = TfidfVectorizer(ngram_range=ngram_range, token_pattern=r'(?u)\w+|\w+\n|\.|\¿|\?')
            svd = TruncatedSVD(n_components=100, random_state=0)
            vectorizador = Pipeline([
                ('tfidf', tfidf),
                ('svd', svd)
            ])
        else:
            raise ValueError(f"Tipo de vectorización '{tipoVectorizacion}' no soportado.\n"
                            f"Tipos soportados: \n[1]frecuencia\n[2]tfidf\n[3]binaria\n[4]svd")
        
        if nombreModelo == "naive_bayes":
            clasificador = MultinomialNB(**(parametros or {}))
        elif nombreModelo == "logistic_regression":
            clasificador = LogisticRegression(**(parametros or {}))
        elif nombreModelo == "svc":
            clasificador = SVC(**(parametros or {}))
        elif nombreModelo == "mlp":
            clasificador = MLPClassifier(**(parametros or {}))
        elif nombreModelo == "random_forest":
            clasificador = RandomForestClassifier(**(parametros or {}))
        elif nombreModelo == "gradient_boosting":
            clasificador = GradientBoostingClassifier(**(parametros or {}))
        else:
            raise ValueError(f"Modelo '{nombreModelo}' no soportado.\n"
                            f"Modelos soportados: [1]naive_bayes\n[2]logistic_regression\n[3]svc\n[4]mlp "
                            f"[5]random_forest\n[6]gradient_boosting")

        self.pipeline = Pipeline([
            ('text_representation', vectorizador),
            ('classifier', clasificador)
        ])
        print(f"\nPipeline creado con el modelo {nombreModelo} y vectorizador {tipoVectorizacion}.")
        return self.pipeline
    
    def entrenarModelo(self, X_train, y_train):
        if not self.pipeline:
            raise ValueError("El pipeline no ha sido creado. Llama a crearPipeline primero.")
    
        self.pipeline.fit(X_train, y_train)
        
        return self.pipeline
    
    def entrenarModeloBalanceado(self, X_train, y_train): 
        if not self.pipeline:
            raise ValueError("El pipeline no ha sido creado. Llama a crearPipeline primero.")


        vectorizador = self.pipeline.named_steps['text_representation']
        clasificador = self.pipeline.named_steps['classifier']


        X_vect = vectorizador.fit_transform(X_train)

        sampler = RandomOverSampler(random_state=0)
        X_bal, y_bal = sampler.fit_resample(X_vect, y_train)

    
        clasificador.fit(X_bal, y_bal)

   
        self.pipeline = Pipeline([
            ('text_representation', vectorizador),
            ('classifier', clasificador)
        ])
        
        return self.pipeline

    
    def evaluarModelo(self, X_test, y_test):
        if not self.pipeline:
            raise ValueError("El pipeline no ha sido entrenado. Llama a entrenarModelo primero.")
        y_pred = self.pipeline.predict(X_test)
        reporte_dict = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        reporte_str = classification_report(y_test, y_pred, zero_division=0)
        return reporte_dict, reporte_str
    
    def validacionCruzada(self, X, y, n_splits = 5):
        if not self.pipeline:
            raise ValueError("El pipeline no ha sido creado. Llama a crearPipeline primero.")
    
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=0)
        f1_scores = []
        for i ,(train_index, test_index) in enumerate(skf.split(X, y)):
            print(f"Fold {i+1}/{n_splits}")
            X_train = [X[i] for i in train_index]
            y_train = [y[i] for i in train_index]
            X_test = [X[i] for i in test_index]
            y_test = [y[i] for i in test_index]

            self.pipeline.fit(X_train, y_train)

            y_pred = self.pipeline.predict(X_test)
            
            reporte = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
          
            f1_macro = reporte['macro avg']['f1-score']
            f1_scores.append(f1_macro)

            print(f"F1-Macro del fold {i+1}: {f1_macro:.4f}")
        
        media = np.mean(f1_scores)
        desviacion = np.std(f1_scores)

        print(f"F1-Macro promedio: {media:.4f} ± {desviacion:.4f}")

        return {
            "resultados": f1_scores,
            "media": media,
            "desviacion_estandar": desviacion
        }
    
    def ejecutarExperimentos(self):
        if not self.corpus["Teaser_Tokens"]:
            raise ValueError("El corpus está vacío. Primero carga los datos.")
        X = self.corpus["Teaser_Tokens"]
        y = self.corpus["Tag_Value"]

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size       = 0.25,
            shuffle         = True,
            random_state    = 0,
            stratify        = y
        )

        resultados = []

        for i, (modelo, tipoVectorizacion, ngram_range, extra_parametros) in enumerate(self.experimentos):
            print("="*100)
            print(f"\nExperimento {i+1}/{len(self.experimentos)}: {modelo} + {tipoVectorizacion} + {ngram_range} + {extra_parametros}")
            
            # Crear pipeline con la configuración actual
            self.crearPipeline(tipoVectorizacion=tipoVectorizacion, ngram_range=ngram_range, modelo=modelo, parametros=extra_parametros)
            
            # Entrenar modelo (sin balanceo, como requiere el usuario)
            self.entrenarModelo(X_train, y_train)
            
            # Evaluar en conjunto de prueba
            reporte_dict, reporte_str = self.evaluarModelo(X_test, y_test)
            print(f"Reporte de clasificación:\n\n{reporte_str}")

            # Realizar validación cruzada
            cv_resultados = self.validacionCruzada(X_train, y_train, n_splits=5)

            normalizacionTexto = {
                "Completo": "Tokenizacion + Stopwords + Lematizacion",
                "Tokenizacion": "Solo Tokenizacion",
                "Stopwords": "Solo Stopwords",
                "Lematizacion": "Solo Lematizacion",
                "Tokenizacion_Stopwords": "Tokenizacion + Stopwords",
                "Tokenizacion_Lematizacion": "Tokenizacion + Lematizacion",
                "Stopwords_Lematizacion": "Stopwords + Lematizacion"
            }.get(self.tipoNormalizacion, "Desconocido")

            metodoBalanceo = "None"  
            
            # Guardar resultados tanto en formato diccionario como valores planos
            resultado = {
                # Construir tabla de requerimiento practica
                "modelo"            : modelo,
                "tipoVectorizacion" : tipoVectorizacion,
                "ngram_range"       : ngram_range,
                "parametros"        : extra_parametros,
                "normalizacionTexto": normalizacionTexto,
                "metodoBalanceo": metodoBalanceo,
                # Mas informacion
                "reporte"           : reporte_dict, 
                "accuracy"          : reporte_dict['accuracy'],  
                "f1_macro"          : reporte_dict['macro avg']['f1-score'],
                "precision_macro"   : reporte_dict['macro avg']['precision'],
                "recall_macro"      : reporte_dict['macro avg']['recall'],
                "f1_weighted"       : reporte_dict['weighted avg']['f1-score'],
                "cv_score"          : cv_resultados['resultados'],
                "cv_media"          : cv_resultados['media'],
                "cv_desviacion"     : cv_resultados['desviacion_estandar']

            }
            
            resultados.append(resultado)
            print(f"F1 - Macro {resultado['f1_macro']:.4f}")
            print(f"\nResultados de validación cruzada: {cv_resultados['resultados']}")
                
        # Ordenar resultados por F1-macro de mayor a menor
        mejoresResultados = sorted(resultados, key=lambda x: x['f1_macro'], reverse=True)

        # Guardar el mejor modelo encontrado
        mejorResultado = mejoresResultados[0]
        print("**"*100)
        print(f"Mejor resultado: {mejorResultado['modelo']} + {mejorResultado['tipoVectorizacion']} + {mejorResultado['ngram_range']} + {mejorResultado['parametros']}")
        print(f"F1 - Macro: {mejorResultado['f1_macro']:.4f}")
        print(f"CV Media: {mejorResultado['cv_media']:.4f} ± {mejorResultado['cv_desviacion']:.4f}")
        
        # Importante: Reentrenar el mejor modelo para guardar su configuración
        self.reentrenarMejorModelo(mejorResultado)
        
        # Guardar el modelo entrenado
        self.guardarModelo(f"modelo_{self.tipoNormalizacion}.pkl")
        
        print("**"*100)
        return mejoresResultados
    
    def cargarDatosPrueba(self, archivo_prueba = None):
        """Carga los datos del conjunto de prueba."""
        try:
            archivo_a_usar = archivo_prueba if archivo_prueba else self.archivoDevNormalizado
        
            print(f"Cargando datos de prueba desde: {archivo_a_usar}")
            with open(archivo_a_usar, mode='r', encoding='utf-8') as tokens:
                reader = csv.DictReader(tokens)
                corpus_prueba = {
                    "Tweet_ID": [],
                    "Teaser_Tokens": []
                }
                for fila in reader:
                    corpus_prueba["Tweet_ID"].append(fila["Tweet_ID"])
                    corpus_prueba["Teaser_Tokens"].append(fila["Teaser_Tokens"])
            print(f"Se cargaron {len(corpus_prueba['Tweet_ID'])} tweets de prueba.")
            return corpus_prueba
        except Exception as e:
            print(f"Error al cargar el archivo de prueba: {e}")
            return None

    def reentrenarMejorModelo(self, mejor_configuracion):
        """Reentrena el mejor modelo con todo el conjunto de datos."""
        modelo = mejor_configuracion["modelo"]
        tipoVectorizacion = mejor_configuracion["tipoVectorizacion"]
        ngram_range = mejor_configuracion["ngram_range"]
        parametros = mejor_configuracion["parametros"]
        
        print(f"Reentrenando mejor modelo: {modelo} + {tipoVectorizacion} + {ngram_range}")
        
        # Crear pipeline con la mejor configuración
        self.crearPipeline(
            modelo=modelo, 
            tipoVectorizacion=tipoVectorizacion, 
            ngram_range=ngram_range, 
            parametros=parametros
        )
        
        # Entrenar con todo el corpus
        X = self.corpus["Teaser_Tokens"]
        y = self.corpus["Tag_Value"]
        
        # Entrenamiento normal (sin balanceo)
        self.entrenarModelo(X, y)
        
        print(f"Modelo reentrenado con todo el corpus usando {modelo} + {tipoVectorizacion} + {ngram_range}")
        return self.pipeline

    def predecirYGuardar(self, datos_prueba, archivo_salida="detection.csv"):
        """Hace predicciones en el conjunto de prueba y guarda los resultados."""
        if not self.pipeline:
            raise ValueError("El pipeline no ha sido entrenado. Llama a reentrenarMejorModelo primero.")
        
        # Comprobar si el pipeline está entrenado
        try:
            # Hacer predicciones
            X_test = datos_prueba["Teaser_Tokens"]
            predicciones = self.pipeline.predict(X_test)
            
            # Guardar resultados
            with open(archivo_salida, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Tweet ID", "Tag Value"])
                for tweet_id, prediccion in zip(datos_prueba["Tweet_ID"], predicciones):
                    writer.writerow([tweet_id, prediccion])
            
            print(f"Predicciones guardadas en {archivo_salida}")
        except Exception as e:
            print(f"Error al predecir: {e}")
            print("Asegúrate de que el modelo está correctamente entrenado o cargado.")

    def guardarModelo(self, nombre_archivo="modelo.pkl"):
        try:
            with open(nombre_archivo, 'wb') as f:
                pickle.dump(self.pipeline, f)
            print(f"Modelo guardado en {nombre_archivo}")
        except Exception as e:
            print(f"Error al guardar el modelo: {e}")
        return None
    
    def cargarModelo(self, nombre_archivo="modelo.pkl"):
        self.pipeline = pickle.load(open(nombre_archivo, 'rb'))
        print(f"Modelo cargado desde {nombre_archivo}")
        return self.pipeline

    def ejecutar(self, modo=None, tipoNormalizacion=None):
        """
        Ejecuta el detector en el modo especificado, opcionalmente con un tipo específico de normalización.
        """
        # Actualizar tipo de normalización si se especifica
        if tipoNormalizacion is not None and tipoNormalizacion in self.archivoNormalizacion:
            self.tipoNormalizacion = tipoNormalizacion
            self.archivoNormalizado = self.archivoNormalizacion[tipoNormalizacion]
            # Reiniciar el corpus para el nuevo archivo
            self.corpus = {
                "Tweet_ID": [],
                "Teaser_Tokens": [],
                "Tag_Value": []
            }
                
        if modo == "completo":
            print(f"\n{'='*50}")
            print(f"PROCESANDO NORMALIZACIÓN: {self.tipoNormalizacion}")
            print(f"{'='*50}\n")
            
            print("Cargando datos...")
            self.cargarDatos()
            print(f"\n\n\t\tEl nombre del archivo es: {self.archivoNormalizado}")
            print("\n\n\t\tEjecutando experimentos...\n")
            resultados = self.ejecutarExperimentos()
            
            # Generar archivos con nombres personalizados para cada tipo de normalización
            archivo_resultados = f"resultados_experimentos_{self.tipoNormalizacion}.csv"
            archivo_evidencia = f"Evidencia_{self.tipoNormalizacion}.csv"
            
            # Generar ambos reportes - diccionario y tabla
            generarReporte(resultados, archivo_resultados)
            generarTablaResultados(resultados, archivo_evidencia)

            print("\nResultados ordenados por F1-macro:")
            for i, res in enumerate(resultados[:10]):
                print(f"{i+1}. {res['modelo']} + {res['tipoVectorizacion']} + {res['ngram_range']}: F1={res['f1_macro']:.4f}, CV={res['cv_media']:.4f}")
            
            return resultados
            
        elif modo == "prediccion":
            print("Cargando datos de entrenamiento...")
            self.cargarDatos()  # Necesario para tener el vocabulario

            modelo_archivo = f"modelo_{self.tipoNormalizacion}.pkl"
            try:
                print(f"Intentando cargar modelo desde {modelo_archivo}...")
                self.cargarModelo(modelo_archivo)
                print("Modelo cargado exitosamente.")
            except Exception as e:
                print(f"No se pudo cargar el modelo específico: {e}")
                print("Reentrenando modelo desde cero...")
                
                # Entrenar el modelo desde cero si no se puede cargar
                print("Ejecutando experimentos para encontrar mejor configuración...")
                resultados = self.ejecutarExperimentos()
                mejorResultado = sorted(resultados, key=lambda x: x['f1_macro'], reverse=True)[0]
                self.reentrenarMejorModelo(mejorResultado)
                    
            print("\n\n\t\tRealizando predicciones en el conjunto de prueba...\n")
            print("Usando archivo de desarrollo con normalización:", self.tipoNormalizacion)

            datos_prueba = self.cargarDatosPrueba()
            if datos_prueba:
                archivo_predicciones = f"predicciones_{self.tipoNormalizacion}.csv"
                self.predecirYGuardar(datos_prueba, archivo_predicciones)
                print(f"\nPredicciones realizadas y guardadas en {archivo_predicciones}")
            else:
                print("No se pudieron cargar los datos de prueba.")

def generarReporte(resultados, archivo_salida="experimentos_resultados2.csv"):
    df = pd.DataFrame(resultados)
    df.to_csv(archivo_salida, index=False)
    print(f"Resultados guardados en {archivo_salida}")
    return df

def generarTablaResultados(resultados, archivo_salida):
    columnas = ["modelo", "tipoVectorizacion", "ngram_range", "parametros", "normalizacionTexto", "metodoBalanceo", "f1_macro"]
    df = pd.DataFrame(resultados)[columnas]
    df = df.rename(columns={
        "modelo": "ML_Model",
        "parametros": "ML_Hyperparameters",
        "normalizacionTexto": "Text_Normalization",
        "tipoVectorizacion": "Text_Representation",
        "metodoBalanceo": "Balance_Methods",
        "f1_macro": "Average_f-score_Macro"
    })
    df.to_csv(archivo_salida, index=False)
    print(f"Resultados guardados en {archivo_salida}")
    return df

def ejecutar_todos_tipos(modo="completo"):
    """
    Ejecuta el detector para todos los tipos de normalización disponibles.
    """
    # Lista para almacenar los mejores resultados de cada tipo
    mejores_por_tipo = []
    
    # Crear una instancia temporal para obtener los tipos disponibles
    detector_temp = ClickBaitDetector(tipoVectorizacion="tfidf", nombreModelo="naive_bayes")
    tipos_normalizacion = list(detector_temp.archivoNormalizacion.keys())
    
    print(f"\n\n{'*'*80}")
    print(f"EJECUTANDO EXPERIMENTOS PARA {len(tipos_normalizacion)} TIPOS DE NORMALIZACIÓN")
    print(f"{'*'*80}\n")
    
    for tipo in tipos_normalizacion:
        print(f"\n{'#'*80}")
        print(f"INICIANDO {modo.upper()} PARA NORMALIZACIÓN: {tipo}")
        print(f"{'#'*80}\n")
        
        # Crear una nueva instancia para cada tipo para evitar interferencias
        detector = ClickBaitDetector(
            tipoVectorizacion="tfidf", 
            nombreModelo="naive_bayes", 
            tipoNormalizacion=tipo
        )
        
        # Ejecutar en modo especificado
        resultados = detector.ejecutar(modo=modo)
        
        if modo == "completo" and resultados:
            # Guardar el mejor resultado para este tipo
            mejor = sorted(resultados, key=lambda x: x['f1_macro'], reverse=True)[0]
            mejor['tipoNormalizacion'] = tipo
            mejores_por_tipo.append(mejor)
    
    if modo == "completo" and mejores_por_tipo:
        # Generar reporte comparativo final
        print(f"\n\n{'='*80}")
        print("RESUMEN COMPARATIVO DE MEJORES RESULTADOS POR TIPO DE NORMALIZACIÓN")
        print(f"{'='*80}\n")
        
        # Ordenar por F1-macro
        mejores_por_tipo.sort(key=lambda x: x['f1_macro'], reverse=True)
        
        for i, mejor in enumerate(mejores_por_tipo):
            print(f"{i+1}. {mejor['tipoNormalizacion']} - {mejor['modelo']} + {mejor['tipoVectorizacion']} + {mejor['ngram_range']}: F1={mejor['f1_macro']:.4f}, CV={mejor['cv_media']:.4f}")
        
        # Guardar reporte comparativo
        df_comparativo = pd.DataFrame([{
            "Tipo_Normalizacion": m['tipoNormalizacion'],
            "Mejor_Modelo": m['modelo'],
            "Vectorizacion": m['tipoVectorizacion'],
            "N-grams": str(m['ngram_range']),
            "F1_Macro": m['f1_macro'],
            "CV_Media": m['cv_media'],
            "CV_Desviacion": m['cv_desviacion']
        } for m in mejores_por_tipo])
        
        df_comparativo.to_csv("comparativo_normalizaciones.csv", index=False)
        print("\nReporte comparativo guardado en 'comparativo_normalizaciones.csv'")

if __name__ == "__main__":
    import sys
    
    # Valor por defecto
    modo = "completo"  
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        if sys.argv[1] in ["completo", "prediccion"]:
            modo = sys.argv[1]
        else:
            print(f"Modo '{sys.argv[1]}' no reconocido. Usando modo 'completo'.")
    
    # Determinar si ejecutar uno o todos los tipos
    if len(sys.argv) > 2 and sys.argv[2] == "todos":
        # Ejecutar para todos los tipos de normalización
        ejecutar_todos_tipos(modo=modo)
    else:
        # Valor por defecto o especificado
        tipo_norm = "Completo"
        if len(sys.argv) > 2:
            tipo_norm = sys.argv[2]
            
        # Ejecutar para un tipo específico
        detector = ClickBaitDetector(
            tipoVectorizacion="tfidf", 
            nombreModelo="naive_bayes", 
            tipoNormalizacion=tipo_norm
        )
        detector.ejecutar(modo=modo)