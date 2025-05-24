import csv
import pickle
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, cross_validate
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from imblearn.over_sampling import RandomOverSampler
from sklearn.decomposition import TruncatedSVD


class ClickBaitDetector:

    def __init__(self, tipoVectorizacion, nombreModelo):
        self.nombreModelo = nombreModelo
        self.archivoNormalizado = "./corpus_tokenizado/TA1C_dataset_Completo.csv"
        self.corpus = {
            "Tweet_ID": [],
            "Teaser_Tokens": [],
            "Tag_Value": []
        }
        self.pipeline = None
        self.experimentos = [
            ("naive_bayes", "binaria", (1, 1), {}),
            ("naive_bayes", "frecuencia", (1, 1), {}),

            ("logistic_regression", "binaria", (1, 1), {"max_iter": 200}),
            ("logistic_regression", "tfidf", (1, 1), {"max_iter": 200}),

            
            ("svc", "binaria", (1, 1), {"kernel": "linear", "C": 1.0}),
            
            # ("mlp", "frecuencia", (1, 1), {"hidden_layer_sizes": (100,), "max_iter": 100}),
            # ("mlp", "binaria", (1, 1), {"hidden_layer_sizes": (100,), "max_iter": 100}),
            # ("mlp", "tfidf", (1, 1), {"hidden_layer_sizes": (100,), "max_iter": 100}),
            ("random_forest", "frecuencia", (1, 1), {"n_estimators": 100}),
            ("random_forest", "binaria", (1, 1), {"n_estimators": 100}),
            ("random_forest", "tfidf", (1, 1), {"n_estimators": 100}),
            ("gradient_boosting", "frecuencia", (1, 1), {"n_estimators": 100}),
            ("gradient_boosting", "binaria", (1, 1), {"n_estimators": 100}),
            ("gradient_boosting", "tfidf", (1, 1), {"n_estimators": 100}),
            ("naive_bayes", "frecuencia", (2, 2), {}),
            ("naive_bayes", "binaria", (2, 2), {}),
            ("naive_bayes", "tfidf", (2, 2), {}),
            ("logistic_regression", "frecuencia", (2, 2), {"max_iter": 200}),
            ("logistic_regression", "binaria", (2, 2), {"max_iter": 200}),
            ("logistic_regression", "tfidf", (2, 2), {"max_iter": 200}),
            ("svc", "frecuencia", (2, 2), {"kernel": "linear", "C": 1.0}),
            ("svc", "binaria", (2, 2), {"kernel": "linear", "C": 1.0}),
            ("svc", "tfidf", (2, 2), {"kernel": "linear", "C": 1.0}),
            # ("mlp", "frecuencia", (2, 2), {"hidden_layer_sizes": (100,), "max_iter": 100}),
            # ("mlp", "binaria", (2, 2), {"hidden_layer_sizes": (100,), "max_iter": 100}),
            # ("mlp", "tfidf", (2, 2), {"hidden_layer_sizes": (100,), "max_iter": 100}),
            ("random_forest", "frecuencia", (2, 2), {"n_estimators": 100}),
            ("random_forest", "binaria", (2, 2), {"n_estimators": 100}),
            ("random_forest", "tfidf", (2, 2), {"n_estimators": 100}),
            ("gradient_boosting", "frecuencia", (2, 2), {"n_estimators": 100}),
            ("gradient_boosting", "binaria", (2, 2), {"n_estimators": 100}),
            ("gradient_boosting", "tfidf", (2, 2), {"n_estimators": 100}),
            ("naive_bayes", "frecuencia", (3, 3), {}),
            ("naive_bayes", "binaria", (3, 3), {}),
            ("naive_bayes", "tfidf", (3, 3), {}),
            ("logistic_regression", "frecuencia", (3, 3), {"max_iter": 200}),
            ("logistic_regression", "binaria", (3, 3), {"max_iter": 200}),
            ("logistic_regression", "tfidf", (3, 3), {"max_iter": 200}),
            ("svc", "frecuencia", (3, 3), {"kernel": "linear", "C": 1.0}),
            ("svc", "binaria", (3, 3), {"kernel": "linear", "C": 1.0}),
            ("svc", "tfidf", (3, 3), {"kernel": "linear", "C": 1.0}),
            # ("mlp", "frecuencia", (3, 3), {"hidden_layer_sizes": (100,), "max_iter": 100}),
            # ("mlp", "binaria", (3, 3), {"hidden_layer_sizes": (100,), "max_iter": 100}),
            # ("mlp", "tfidf", (3, 3), {"hidden_layer_sizes": (100,), "max_iter": 100}),
            ("random_forest", "frecuencia", (3, 3), {"n_estimators": 100}),
            ("random_forest", "binaria", (3, 3), {"n_estimators": 100}),
            ("random_forest", "tfidf", (3, 3), {"n_estimators": 100}),
            ("gradient_boosting", "frecuencia", (3, 3), {"n_estimators": 100}),
            ("gradient_boosting", "binaria", (3, 3), {"n_estimators": 100}),
            ("gradient_boosting", "tfidf", (3, 3), {"n_estimators": 100}),
            ("logistic_regression", "svd", (1, 1), {"max_iter": 200}),
            ("svc", "svd", (1, 1), {"kernel": "linear", "C": 1.0}),
            # ("mlp", "svd", (1, 1), {"hidden_layer_sizes": (100,), "max_iter": 100}),
            ("logistic_regression", "svd", (2, 2), {"max_iter": 200}),
            ("svc", "svd", (2, 2), {"kernel": "linear", "C": 1.0}),
            # ("mlp", "svd", (2, 2), {"hidden_layer_sizes": (100,), "max_iter": 100})
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
        reporte = classification_report(y_test, y_pred, output_dict=True)
        return reporte
    
    def validacionCruzada(self, X, y, n_splits = 5):
        """
        Realiza validación cruzada estratificada del pipeline actual.
        Utiliza StratifiedKFold para mantener la proporción de clases en cada fold.
        
        Parámetros:
        -----------
        X : array-like, shape (n_samples, n_features)
            Los datos de entrada
        y : array-like, shape (n_samples,)
            Los valores target
        n_splits : int, default=5
            Número de folds para la validación cruzada
            
        Retorna:
        --------
        dict
            Diccionario con los resultados de la validación cruzada
        """
        if not self.pipeline:
            raise ValueError("El pipeline no ha sido creado. Llama a crearPipeline primero.")
        
        # Usar StratifiedKFold para mantener la proporción de clases en cada fold
        cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=0)
        
        # Métricas a evaluar
        scoring = {
            'accuracy': 'accuracy',
            'precision_macro': 'precision_macro',
            'recall_macro': 'recall_macro',
            'f1_macro': 'f1_macro'
        }
        
        # Realizar validación cruzada con múltiples métricas
        cv_results = cross_validate(
            self.pipeline, X, y, 
            cv=cv,
            scoring=scoring,
            return_train_score=True  # También devuelve resultados en conjunto de entrenamiento
        )
        
        # Para mantener compatibilidad con la implementación original
        resultados = cv_results['test_f1_macro']
        media = resultados.mean()
        desviacion_estandar = resultados.std()
        
        # Imprimir resultados detallados
        print("\n=== Resultados de Validación Cruzada Estratificada ===")
        print(f"F1-Macro: {media:.4f} ± {desviacion_estandar:.4f}")
        print(f"Accuracy: {cv_results['test_accuracy'].mean():.4f} ± {cv_results['test_accuracy'].std():.4f}")
        print(f"Precision-Macro: {cv_results['test_precision_macro'].mean():.4f} ± {cv_results['test_precision_macro'].std():.4f}")
        print(f"Recall-Macro: {cv_results['test_recall_macro'].mean():.4f} ± {cv_results['test_recall_macro'].std():.4f}")
        
        return {
            "resultados": resultados,
            "media": media,
            "desviacion_estandar": desviacion_estandar,
            "metricas_detalladas": {
                'accuracy': cv_results['test_accuracy'],
                'precision_macro': cv_results['test_precision_macro'],
                'recall_macro': cv_results['test_recall_macro'],
                'f1_macro': cv_results['test_f1_macro'],
                'accuracy_media': cv_results['test_accuracy'].mean(),
                'precision_macro_media': cv_results['test_precision_macro'].mean(),
                'recall_macro_media': cv_results['test_recall_macro'].mean()
            }
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
            self.crearPipeline(tipoVectorizacion=tipoVectorizacion, ngram_range=ngram_range, modelo=modelo, parametros=extra_parametros) 
            self.entrenarModeloBalanceado(X_train, y_train)
            metodoBalanceo = "RandomOverSampler"
            reporte = self.evaluarModelo(X_test, y_test)
            print(f"Reporte de clasificación:\n\n{reporte}")
            cv_resultados = self.validacionCruzada(X_train, y_train, n_splits=5)

            if "Tokenizacion_Stopwords" in self.archivoNormalizado:
                normalizacionTexto = "Tokenizacion + Stopwords"
            elif "Tokenizacion_Lematizacion" in self.archivoNormalizado[1]:
                normalizacionTexto = "Tokenizacion + Lematizacion"
            elif "Stopwords_Lematizacion" in self.archivoNormalizado:
                normalizacionTexto = "Stopwords + Lematizacion"
            elif "Tokenizacion" in self.archivoNormalizado:
                normalizacionTexto = "Solo Tokenizacion"
            elif "Lematizacion" in self.archivoNormalizado:
                normalizacionTexto = "Solo Lematizacion"
            elif "Stopwords" in self.archivoNormalizado:
                normalizacionTexto = "Solo Stopwords"
            elif "Completo" in self.archivoNormalizado:
                normalizacionTexto = "Tokenizacion + Stopwords + Lematizacion"
            else:
                normalizacionTexto = "Desconocido"
            
            resultado = {
                # Construir tabla de requerimiento practica
                "modelo"            : modelo,
                "tipoVectorizacion" : tipoVectorizacion,
                "ngram_range"       : ngram_range,
                "parametros"        : extra_parametros,
                "normalizacionTexto": normalizacionTexto,
                "metodoBalanceo"    : metodoBalanceo,
                # Mas informacion
                "reporte"           : reporte, 
                "accuracy"          : reporte['accuracy'],  
                "f1_macro"          : reporte['macro avg']['f1-score'],
                "precision_macro"   : reporte['macro avg']['precision'],
                "recall_macro"      : reporte['macro avg']['recall'],
                "f1_weighted"       : reporte['weighted avg']['f1-score'],
                "cv_score"          : cv_resultados['resultados'],
                "cv_media"          : cv_resultados['media'],
                "cv_desviacion"     : cv_resultados['desviacion_estandar']
            }
            
            # Agregar métricas adicionales de validación cruzada si están disponibles
            if 'metricas_detalladas' in cv_resultados:
                resultado["cv_accuracy"] = cv_resultados['metricas_detalladas']['accuracy_media']
                resultado["cv_precision"] = cv_resultados['metricas_detalladas']['precision_macro_media']
                resultado["cv_recall"] = cv_resultados['metricas_detalladas']['recall_macro_media']
            
            resultados.append(resultado)
            print(f"F1 - Macro {resultado['f1_macro']:.4f}")
            print(f"\nResultados de validación cruzada: {cv_resultados['resultados']}")
            
        mejoresResultados = sorted(resultados, key = lambda x: x['f1_macro'], reverse=True)

        mejorResultado = mejoresResultados[0]
        print("**"*100)
        print(f"Mejor resultado: {mejorResultado['modelo']} + {mejorResultado['tipoVectorizacion']} + {mejorResultado['ngram_range']} + {mejorResultado['parametros']}")
        print(f"F1 - Macro: {mejorResultado['f1_macro']:.4f}")
        print(f"CV Media: {mejorResultado['cv_media']:.4f} ± {mejorResultado['cv_desviacion']:.4f}")
        print("**"*100)
        return mejoresResultados
    
    def cargarDatosPrueba(self, archivo_prueba):
        """Carga los datos del conjunto de prueba."""
        try:
            with open(archivo_prueba, mode='r', encoding='utf-8') as tokens:
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
        
        # Crear pipeline con la mejor configuración
        self.crearPipeline(
            tipoVectorizacion=tipoVectorizacion, 
            ngram_range=ngram_range, 
            modelo=modelo, 
            parametros=parametros
        )
        
        # Entrenar con todo el corpus
        X = self.corpus["Teaser_Tokens"]
        y = self.corpus["Tag_Value"]
        self.pipeline.fit(X, y)
        
        print(f"Modelo reentrenado con todo el corpus usando {modelo} + {tipoVectorizacion} + {ngram_range}")
        return self.pipeline

    def predecirYGuardar(self, datos_prueba, archivo_salida="detection.csv"):
        """Hace predicciones en el conjunto de prueba y guarda los resultados."""
        if not self.pipeline:
            raise ValueError("El pipeline no ha sido entrenado. Llama a reentrenarMejorModelo primero.")
        
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

    def ejecutar(self, modo = None):
        if modo == "completo":
            print("Cargando datos...")
            self.cargarDatos()
            print("\n\n\t\tEjecutando experimentos...\n")
            resultados = self.ejecutarExperimentos()
            generarReporte(resultados, "resultados_experimentos_8.csv")
            generarTablaResultados(resultados, "Evidencia4.csv")
        
            print("\nResultados ordenados por F1-macro:")
            for i, res in enumerate(resultados[:10]):
                print(f"{i+1}. {res['modelo']} + {res['tipoVectorizacion']} + {res['ngram_range']}: F1={res['f1_macro']:.4f}, CV={res['cv_media']:.4f}")
            
            self.guardarModelo() 
        
        elif modo == "prediccion":
            self.cargarModelo()
            print("\n\n\t\tRealizando predicciones en el conjunto de prueba...\n")

            datos_prueba = self.cargarDatosPrueba("./corpus_tokenizado/TA1C_dataset_Normalize_detection_dev.csv")
            if datos_prueba:
                self.predecirYGuardar(datos_prueba, "predicciones_4.csv")
                print(f"\nPredicciones realizadas y guardadas en predicciones_4.csv")
            else:
                print("No se pudieron cargar los datos de prueba.")


def generarReporte(resultados, archivo_salida="experimentos_resultados.csv"):
    df = pd.DataFrame(resultados)
    df.to_csv(archivo_salida, index=False)
    print(f"Resultados guardados en {archivo_salida}")
    return df

def generarTablaResultados(resultados, archivo_salida="Evidencia.csv"):
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

if __name__ == "__main__":
    import sys
    
    # Valor por defecto
    modo = "prediccion"  
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        if sys.argv[1] in ["completo", "prediccion"]:
            modo = sys.argv[1]
        else:
            print(f"Modo '{sys.argv[1]}' no reconocido. Usando modo 'prediccion'.")
    
    detector = ClickBaitDetector(tipoVectorizacion="tfidf", nombreModelo="naive_bayes")
    detector.ejecutar(modo=modo)
