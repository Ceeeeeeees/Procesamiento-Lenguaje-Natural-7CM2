import csv
import pickle
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, cross_validate
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from imblearn.over_sampling import RandomOverSampler
import sys

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
        # Usar solo unos pocos experimentos para demostracion
        self.experimentos = [
            ("naive_bayes", "tfidf", (1, 1), {}),
            ("logistic_regression", "tfidf", (1, 1), {"max_iter": 200}),
            ("svc", "tfidf", (1, 1), {"kernel": "linear", "C": 1.0}),
        ]

    def cargarDatos(self):
        try:
            with open(self.archivoNormalizado, mode='r', encoding='utf-8') as tokens:
                reader = csv.DictReader(tokens)
                # Limitar a 1000 samples para prueba rápida
                count = 0
                for fila in reader:
                    if count >= 1000:  # Limitar a 1000 muestras para demostración
                        break
                    self.corpus["Tweet_ID"].append(fila["Tweet_ID"])
                    self.corpus["Teaser_Tokens"].append(fila["Teaser_Tokens"])
                    self.corpus["Tag_Value"].append(fila["Tag_Value"])
                    count += 1
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
        if tipoVectorizacion == "tfidf":
            vectorizador = TfidfVectorizer(ngram_range=ngram_range, token_pattern=r'(?u)\w+|\w+\n|\.|\¿|\?')
        else:
            raise ValueError(f"Tipo de vectorización '{tipoVectorizacion}' no soportado.")
        
        if nombreModelo == "naive_bayes":
            clasificador = MultinomialNB(**(parametros or {}))
        elif nombreModelo == "logistic_regression":
            clasificador = LogisticRegression(**(parametros or {}))
        elif nombreModelo == "svc":
            clasificador = SVC(**(parametros or {}))
        else:
            raise ValueError(f"Modelo '{nombreModelo}' no soportado.")

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
        
        # Mostrar las puntuaciones individuales de cada fold
        print("\nPuntuaciones por fold:")
        for fold_idx, (f1, acc, prec, rec) in enumerate(zip(
            cv_results['test_f1_macro'],
            cv_results['test_accuracy'],
            cv_results['test_precision_macro'],
            cv_results['test_recall_macro']
        )):
            print(f"  Fold {fold_idx+1}: F1={f1:.4f}, Accuracy={acc:.4f}, Precision={prec:.4f}, Recall={rec:.4f}")
        
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
            self.entrenarModelo(X_train, y_train)
            reporte = self.evaluarModelo(X_test, y_test)
            print(f"Reporte de clasificación:\n")
            for clave, valor in reporte.items():
                if clave in ['accuracy', 'macro avg', 'weighted avg']:
                    print(f"{clave}: {valor}")
                
            cv_resultados = self.validacionCruzada(X_train, y_train, n_splits=5)
            
            resultado = {
                "modelo": modelo,
                "tipoVectorizacion": tipoVectorizacion,
                "ngram_range": ngram_range,
                "f1_macro": reporte['macro avg']['f1-score'],
                "cv_media": cv_resultados['media'],
                "cv_desviacion": cv_resultados['desviacion_estandar']
            }
            
            # Agregar métricas adicionales de validación cruzada
            if 'metricas_detalladas' in cv_resultados:
                resultado["cv_accuracy"] = cv_resultados['metricas_detalladas']['accuracy_media']
                resultado["cv_precision"] = cv_resultados['metricas_detalladas']['precision_macro_media']
                resultado["cv_recall"] = cv_resultados['metricas_detalladas']['recall_macro_media']
            
            resultados.append(resultado)
            
        mejoresResultados = sorted(resultados, key=lambda x: x['cv_media'], reverse=True)

        mejorResultado = mejoresResultados[0]
        print("**"*100)
        print(f"Mejor resultado: {mejorResultado['modelo']} + {mejorResultado['tipoVectorizacion']} + {mejorResultado['ngram_range']}")
        print(f"F1-Macro: {mejorResultado['f1_macro']:.4f}")
        print(f"CV Media: {mejorResultado['cv_media']:.4f} ± {mejorResultado['cv_desviacion']:.4f}")
        if 'cv_accuracy' in mejorResultado:
            print(f"CV Accuracy: {mejorResultado['cv_accuracy']:.4f}")
            print(f"CV Precision: {mejorResultado['cv_precision']:.4f}")
            print(f"CV Recall: {mejorResultado['cv_recall']:.4f}")
        print("**"*100)
        
        return mejoresResultados

    def ejecutar(self):
        print("Cargando datos...")
        self.cargarDatos()
        print("\nEjecutando experimentos con validación cruzada estratificada...")
        resultados = self.ejecutarExperimentos()
        
        print("\nResultados ordenados por F1-macro en validación cruzada:")
        for i, res in enumerate(resultados):
            print(f"{i+1}. {res['modelo']} + {res['tipoVectorizacion']} + {res['ngram_range']}: CV={res['cv_media']:.4f} ± {res['cv_desviacion']:.4f}")
        
        return resultados

if __name__ == "__main__":
    detector = ClickBaitDetector(tipoVectorizacion="tfidf", nombreModelo="naive_bayes")
    detector.ejecutar()
