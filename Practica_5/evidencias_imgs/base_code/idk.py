from transformers import BertTokenizer, BertForSequenceClassification, TrainingArguments, Trainer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from torch.utils.data import TensorDataset, DataLoader
import torch
from torch.utils.data import Dataset
import csv
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
from collections import Counter
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay

print("ok")

# Corpus
text_filepath = "./base_code_ejemplo/emoevent_es.csv"

# Leer datos
text_data = pd.read_csv(text_filepath, sep='\t', engine='python', usecols=[1])
labels_data = pd.read_csv(text_filepath, sep='\t', engine='python', usecols=[2])
X = text_data.iloc[:, 0].tolist()
y = labels_data.iloc[:, 0].tolist()
label_name = np.unique(y)
print(label_name)

# División del dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)
print(len(X_train))
print(len(X_test))
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.25, random_state=0, stratify=y_train)
print(len(X_train))
print(len(X_val))

# Codificación de etiquetas
le = LabelEncoder()
y_train_labels = le.fit_transform(y_train)
y_test_labels = le.transform(y_test)
y_val_labels = le.transform(y_val)
print(y_train)
print(y_train_labels)
print(y_val)
print(y_val_labels)
print(y_test)
print(y_test_labels)

# Visualización: guardar gráficas
columns = ['values']

# Train
pd.DataFrame(y_train, columns=columns).value_counts(ascending=True).plot.barh()
plt.title('Frequency of Classes - Train')
plt.tight_layout()
plt.savefig("frecuencia_train.png")
plt.close()

# Validation
pd.DataFrame(y_val, columns=columns).value_counts(ascending=True).plot.barh()
plt.title('Frequency of Classes - Validation')
plt.tight_layout()
plt.savefig("frecuencia_val.png")
plt.close()

# Test
pd.DataFrame(y_test, columns=columns).value_counts(ascending=True).plot.barh()
plt.title('Frequency of Classes - Test')
plt.tight_layout()
plt.savefig("frecuencia_test.png")
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

# Modelo
model = BertForSequenceClassification.from_pretrained('dccuchile/bert-base-spanish-wwm-cased', num_labels = 7)

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

# Predicción y reporte
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
