from transformers import BertTokenizer, BertForSequenceClassification, TrainingArguments, Trainer
from sklearn.metrics import f1_score, accuracy_score
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import torch
from torch.utils.data import Dataset
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay

rutaDataset = "/home/servidor/Documentos/GitHub/Procesamiento-Lenguaje-Natural-7CM2/Practica_5/corpus/TA1C_dataset_detection_train.csv"

texto_data = pd.read_csv(rutaDataset, sep=",", engine="python", usecols=[4])
etiquetas_data = pd.read_csv(rutaDataset, sep=",", engine="python", usecols=[5])
X = texto_data.iloc[:, 0].tolist()
y = etiquetas_data.iloc[:, 0].tolist()
label_name = np.unique(y)

# Division del dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=0,
    stratify=y)
# Tamanio de los conjuntos antes de partirlos por primera vez:
print("Tamanio antes de la primera partición:")
print(len(X_train))
print(X_train)
#print(len(X_test))

X_train, X_val, y_train, y_val = train_test_split(
    X_train,
    y_train,
    test_size=0.25,
    random_state=0,
    stratify=y_train)
# Tamanio de los conjuntos despues de partirlos la 2a vez
print("Tamanio antes de la segunda partición:")
print(len(X_train))
print(X_train)
#print(len(X_test))

# Codificar etiquetas
le = LabelEncoder()
y_train_labels = le.fit_transform(y_train)
y_test_labels = le.transform(y_test)
y_val_labels = le.transform(y_val)

# Visualización: guardar gráficas
columns = ['values']

# Train
pd.DataFrame(y_train, columns=columns).value_counts(ascending=True).plot.barh()
plt.title('Frecuencia de las clases Clickbait- Train')
plt.tight_layout()
plt.savefig("frecuencia_train_clickbait.png")
plt.close()

# Validation
pd.DataFrame(y_val, columns=columns).value_counts(ascending=True).plot.barh()
plt.title('FFrecuencia de las clases Clickbait - Validation')
plt.tight_layout()
plt.savefig("frecuencia_val_clickbait.png")
plt.close()

# Test
pd.DataFrame(y_test, columns=columns).value_counts(ascending=True).plot.barh()
plt.title('Frecuencia de las clases Clickbait - Test')
plt.tight_layout()
plt.savefig("frecuencia_test_clickbait.png")
plt.close()

# Tokenización y codificación
tokenizer = BertTokenizer.from_pretrained('dccuchile/bert-base-spanish-wwm-cased')

train_encodings = tokenizer(X_train, truncation=True, padding=True)
validation_encodings = tokenizer(X_val, truncation=True, padding=True)
test_encodings = tokenizer(X_test, truncation=True, padding=True)

class CustomDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

train_dataset = CustomDataset(train_encodings, y_train_labels)
validation_dataset = CustomDataset(validation_encodings, y_val_labels)
test_dataset = CustomDataset(test_encodings, y_test_labels)

model = BertForSequenceClassification.from_pretrained('dccuchile/bert-base-spanish-wwm-cased', num_labels = 2)

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    f1 = f1_score(labels, preds, average="macro")
    acc = accuracy_score(labels, preds)
    return {"accuracy": acc, "f1": f1}

training_args = TrainingArguments(
    output_dir="output",
    eval_strategy="steps",
    eval_steps=100,
    num_train_epochs=3,
    seed=0,
    load_best_model_at_end=True,
    fp16=True
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=validation_dataset,
    compute_metrics=compute_metrics
)

trainer.train()

predictions = trainer.predict(test_dataset)
predicted_classes = np.argmax(predictions.predictions, axis=-1)

report = classification_report(y_test_labels, predicted_classes)
print(report)

# Función modificada para guardar matriz de confusión
def plot_confusion_matrix(y_preds, y_true, labels, filename="confusion_matrix.png"):
    cm = confusion_matrix(y_true, y_preds, normalize="true")
    fig, ax = plt.subplots(figsize=(6, 6))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    disp.plot(cmap="Blues", values_format=".2f", ax=ax, colorbar=False)
    plt.title("Normalized confusion matrix")
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

# Guardar matriz
y_test = y_test_labels.tolist()
plot_confusion_matrix(predicted_classes, y_test, label_name, filename="matriz_confusion_test.png")



import logging

# Configuración básica
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log',  # Omitir para solo consola
    filemode='w'         # 'w' para sobrescribir, 'a' para añadir
)

logger = logging.getLogger('mi_logger')

logger.debug("Este es un mensaje DEBUG")
logger.info("Este es un mensaje INFO")
logger.warning("Este es un WARNING")
logger.error("Este es un ERROR")
logger.critical("Este es un CRITICAL")
