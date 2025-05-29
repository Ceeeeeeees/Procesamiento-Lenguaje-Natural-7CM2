import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
import logging


from torch.utils.data import Dataset
from transformers import (
    BertTokenizer, RobertaTokenizer, ElectraTokenizerFast,
    RobertaModel, BertForSequenceClassification, ElectraForSequenceClassification,
    AutoTokenizer, AutoModelForSequenceClassification, 
    TrainingArguments, Trainer, pipeline
)
from sklearn.metrics import f1_score, accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log',  # Omitir para solo consola
    filemode='a'         # 'w' para sobrescribir, 'a' para añadir
)

logger = logging.getLogger("ClickBait_Models")

class DetectorClickBait:
    
    def __init__(self, tipoModelo="bert"):
        self.modelosDisponibles = {
            "bert" : {
                "nombre" : "dccuchile/bert-base-spanish-wwm-cased",
                "descripcion" : "Modelo BERT Base en español"
            },
            "roberta" : {
                "nombre" : "PlanTL-GOB-ES/roberta-base-bne",
                "descripcion" : "Modelo RoBERTa Base en español"
            },
            "electra" : {
                "nombre" : "google/electra-base-discriminator",
                "descripcion" : "Modelo ELECTRA Base en español"
            }
        }
        self.tipoModelo = tipoModelo
        self.tokenizador = None
        self.modelo = None
        self.codificadorEtiquetas = None
        self.modeloEntrenado = False

        if tipoModelo in self.modelosDisponibles:
            self.configuracionModelo = self.modelosDisponibles[tipoModelo]
            self.nombreModelo = self.configuracionModelo["nombre"]
            logger.info(f"Modelo seleccionado: \t {self.configuracionModelo["descripcion"]}")
            logger.info(f"Ruta del modelo: \t {self.nombreModelo}")
        
        else:
            logger.warning(f"Modelo {tipoModelo} no disponible o no reconocido.\n Modelos disponibles:\n")
            for clave, configuracion in self.modelosDisponibles.items():
                logger.info(f"{clave}: {configuracion['descripcion']}")
            raise ValueError(f"Modelo {tipoModelo} no disponible.")
        
    def cargarYProcesarDatos(self, rutaArchivo, columnaTeaser, columnaTarget):
        logger.info(f"Cargando datos desde {rutaArchivo}...")
        try:
            df_data = pd.read_csv(rutaArchivo, sep=",", engine="python", usecols=[columnaTeaser])
            df_target = pd.read_csv(rutaArchivo, sep=",", engine="python", usecols=[columnaTarget])
        except Exception as ErrorCargarArchivo:
            logger.error(f"Error al cargar el archivo: {ErrorCargarArchivo}")

        X = df_data.iloc[:, 0].tolist()
        y = df_target.iloc[:, 0].tolist()
        etiquetasTarget = np.unique(y)
        logger.info(f"Dataset cargado con {len(X)} muestras, {len(etiquetasTarget)} clases.")
        logger.info(f"Clases: {etiquetasTarget}")
        return X, y, etiquetasTarget
        
    def dividirDataset(self, X, y, tamanioTest=0.2, tamanioValidacion=0.25):
        logger.info(f"Dividiendo el dataset para el conjunto de entrenamiento...")
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=tamanioTest,
            random_state=0,
            stratify=y)
        
        logger.info(f"Dividiendo el dataset para el conjunto de validacion... ")
        X_train_val, X_val, y_train_val, y_val = train_test_split(
            X_train,
            y_train,
            test_size=tamanioValidacion,
            random_state=0,
            stratify=y_train)
        
        logger.info(f"Tamanio de los conjuntos antes de la primera particion:")
        logger.info(f"Conjunto de entrenamiento: {len(X_train)}")
        logger.info(f"Conjunto de validacion: {len(X_val)}")
        logger.info(f"Conjunto de prueba: {len(X_test)}")

        return X_train, X_train_val, X_val, X_test, y_train, y_train_val, y_val, y_test
    
    def codificarEtiquetas(self, y_train, y_val, y_test):
        logger.info(f"Codificando las etiquetas...")
        self.codificadorEtiquetas = LabelEncoder()
        
        y_train_encoded = self.codificadorEtiquetas.fit_transform(y_train)
        y_val_encoded = self.codificadorEtiquetas.transform(y_val)
        y_test_encoded = self.codificadorEtiquetas.transform(y_test)
        logger.info(f"Mapeo de etiquetas: {self.codificadorEtiquetas.classes_}")

        return y_train_encoded, y_val_encoded, y_test_encoded
    
    def prepararDataset(self, X_train, X_test, X_val, y_train_encoded, y_val_encoded, y_test_encoded):
        logger.info(f"Tokenizando los textos....")
         
        if self.tipoModelo == "bert":
            logger.info(f"Configurando a BertTokenizer...")
            self.tokenizador = BertTokenizer.from_pretrained('dccuchile/bert-base-spanish-wwm-cased')
        elif self.tipoModelo == "roberta":
            logger.info(f"Configurando a RoBERTaTokenizer...")
            self.tokenizador = RobertaTokenizer.from_pretrained('PlanTL-GOB-ES/roberta-base-bne')
        elif self.tipoModelo == "electra":
            self.tokenizador = ElectraTokenizerFast.from_pretrained("google/electra-base-discriminator")
        else:
            logger.error(f"Tipo de modelo no reconocido: {self.tipoModelo}. No se puede configurar un tokenizador.")

        logger.info(f"Tokenizador configurado: {self.tokenizador}")

        logger.info(f"Tokenizando el conjunto de entrenamiento...")
        train_encodings = self.tokenizador(X_train, truncation=True, padding=True)

        logger.info("Tokenizando conjunto de validacion...")
        validation_encodings = self.tokenizador(X_val, truncation=True, padding=True)

        logger.info("Tokenizando conjunto de prueba...")
        test_encodings = self.tokenizador(X_test, truncation=True, padding=True)

        trainDataset = DatasetPersonalizado(train_encodings, y_train_encoded)
        valDataset = DatasetPersonalizado(validation_encodings, y_val_encoded)
        testDataset = DatasetPersonalizado(test_encodings, y_test_encoded)

        return trainDataset, valDataset, testDataset
    
    def calcularMetricas(self, pred):
        etiquetas = pred.label_ids
        predicciones = pred.predictions.argmax(-1)
        f1 = f1_score(etiquetas, predicciones, average="macro")
        accuracy = accuracy_score(etiquetas, predicciones)
        return {"accuracy": accuracy, "f1": f1}
    
    def entrenarModelo(self, trainDataset, valDataset, numeroEpocas = 3):
        logger.info(f"Definiendo los parametros para el entrenamiento del modelo...")
        numeroEtiquetas = len(self.codificadorEtiquetas.classes_)
        try:
                if self.tipoModelo == "bert":
                    directorioSalida = "bert_output"
                    modelo = BertForSequenceClassification.from_pretrained('dccuchile/bert-base-spanish-wwm-cased', num_labels=numeroEtiquetas)
                elif self.tipoModelo == "roberta":
                    directorioSalida = "roberta_output"
                    modelo = RobertaModel.from_pretrained('PlanTL-GOB-ES/roberta-base-bne',  num_labels=numeroEtiquetas)
                elif self.tipoModelo ==  "electra":
                    directorioSalida = "electra_output"
                    modelo = ElectraForSequenceClassification.from_pretrained('google/electra-base-discriminator', num_labels=numeroEtiquetas)
                else:
                    logger.error(f"No se puede generar el modelo para el tipo de modelo {self.tipoModelo}")
        except Exception as error:
            logger.error(f"Error al generar el modelo: {error}")
            raise ValueError(f"Error al generar el modelo: {error}")
        
        logger.info(f"Configurando el entrenamiento del modelo...")
        trainingArgs = TrainingArguments(
            output_dir=directorioSalida,
            eval_strategy="steps",
            eval_steps=100,
            num_train_epochs=numeroEpocas,
            seed=0,
            load_best_model_at_end=True,
            fp16=True
            )
        trainer = Trainer(
            model = modelo,
            args = trainingArgs,
            train_dataset=trainDataset,
            eval_dataset=valDataset,
            compute_metrics=self.calcularMetricas
        )
        try:
            logger.info(f"Comenzando el entrenamiento del modelo...")
            trainer.train()
            self.modeloEntrenado = True
            logger.info(f"Entrenamiento completado exitosamente.")
        except Exception as error:
            logger.error(f"Error al entrenar el modelo: {error}")
            raise ValueError(f"Error al entrenar el modelo: {error}")
        return trainer
    
    def evaluarModelo(self, trainer, testDataset, y_test_encoded):
        logger.info(f"Evaluando el modelo...")

        predicciones = trainer.predict(testDataset)
        prediccionesClases = np.argmax(predicciones.predictions, axis=-1)
        etiquetasVerdaderas = predicciones.label_ids

        reporteClasificacion = classification_report(
            etiquetasVerdaderas,
            prediccionesClases,
            target_names=y_test_encoded,
            )
        logger.info(f"Reporte de clasificacion del modelo {self.tipoModelo}: \n {reporteClasificacion}")
        self.crearMatrizConfusion(prediccionesClases, etiquetasVerdaderas, y_test_encoded)

        return reporteClasificacion
    
    def crearMatrizConfusion(self, prediccionesClases, etiquetasVerdaderas, etiquetasTarget):
        logger.info(f"Creando la matriz de confusión...")
        matrizConfusion = confusion_matrix(etiquetasVerdaderas, prediccionesClases, normalize="true")

        fig, ax = plt.subplots(figsize=(6,6))
        disp = ConfusionMatrixDisplay(confusion_matrix=matrizConfusion, display_labels=etiquetasTarget)
        disp.plot(cmap="Blues", values_format=".2f", ax=ax, colorbar=False)
        plt.title("Matriz de confusión normalizada")
        plt.tight_layout()
        plt.savefig(f"matriz_confusion_{self.tipoModelo}.png")
        plt.close()

class DatasetPersonalizado(Dataset):

    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

def entrenamientoCompleto(rutaDataset, tipoModelo):

    logger.info(f"Iniciando el entrenamiento para el modelo {tipoModelo} ...")
    detector = DetectorClickBait(tipoModelo)

    X, y, etiquetasTarget = detector.cargarYProcesarDatos(rutaDataset, 4, 5)

    X_train, X_train_val, X_val, X_test, y_train, y_train_val, y_val, y_test = detector.dividirDataset(X, y)
    
    # Codificar etiquetas
    y_train_enc, y_val_enc, y_test_enc = detector.codificarEtiquetas(y_train, y_val, y_test)
    
    # Preparar datasets
    train_dataset, val_dataset, test_dataset = detector.prepararDataset(
        X_train, X_val, X_test, y_train_enc, y_val_enc, y_test_enc
    )

    trainer = detector.entrenarModelo(train_dataset, val_dataset)    
    if trainer is None:
        return None
    
    detector.evaluarModelo(trainer, test_dataset, y_test_enc)

    logger.info(f"Entrenamiento completado exitosamente.")
    return detector

        
# Ejemplo de uso
if __name__ == "__main__":
    # Entrenar modelo
    rutaDataset = "/home/servidor/Documentos/GitHub/Procesamiento-Lenguaje-Natural-7CM2/Practica_5/corpus/TA1C_dataset_detection_train.csv"
    
    # Entrenar con BERT
    detector = entrenamientoCompleto(rutaDataset, "bert")




                            
