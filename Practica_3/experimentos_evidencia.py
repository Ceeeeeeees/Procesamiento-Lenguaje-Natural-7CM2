from modelos import ModeloMLNLP
from sklearn.metrics import classification_report, f1_score
import pandas as pd
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier

# Configuraciones a probar
experimentos = [
    # (modelo, vectorizacion, ngram_range, parametros extra)
    ("naive_bayes", "frequency", (2,2), {}),
    ("naive_bayes", "binary", (2,2), {}),
    ("naive_bayes", "tfidf", (2,2), {}),
    ("logistic_regression", "frequency", (2,2), {"max_iter": 200}),
    ("logistic_regression", "binary", (2,2), {"max_iter": 200}),
    ("logistic_regression", "tfidf", (2,2), {"max_iter": 200}),
    ("svc", "frequency", (2,2), {"kernel": "linear", "C": 1.0}),
    ("svc", "binary", (2,2), {"kernel": "linear", "C": 1.0}),
    ("svc", "tfidf", (2,2), {"kernel": "linear", "C": 1.0}),
    ("mlp", "frequency", (2,2), {"hidden_layer_sizes": (100,), "max_iter": 300}),
    ("mlp", "binary", (2,2), {"hidden_layer_sizes": (100,), "max_iter": 300}),
    ("mlp", "tfidf", (2,2), {"hidden_layer_sizes": (100,), "max_iter": 300}),
]

resultados = []

for modelo, vector, ngram, extra_params in experimentos:
    print("="*60)
    print(f"Modelo: {modelo}, Vectorización: {vector}, ngram_range: {ngram}, Extra: {extra_params}")
    m = ModeloMLNLP("naive_bayes" if modelo in ["naive_bayes", "svc", "mlp"] else modelo)
    m.cargarDatos()
    m.crearPipeline(vector, ngram_range=ngram)
    # Patch classifier for SVC and MLP
    if modelo == "logistic_regression" and extra_params:
        from sklearn.linear_model import LogisticRegression
        m.pipeline.named_steps['classifier'] = LogisticRegression(**extra_params)
    elif modelo == "svc":
        m.pipeline.named_steps['classifier'] = SVC(**extra_params)
    elif modelo == "mlp":
        m.pipeline.named_steps['classifier'] = MLPClassifier(**extra_params)
    res = m.entrenamientoYEvaluar(prueba=0.2, columna="TextoConcatenado")
    if res:
        # Calcular F1 macro
        y_test = res['y_test']
        y_pred = res['y_pred']
        f1_macro = f1_score(y_test, y_pred, average='macro')
        print(f"F1-score macro: {f1_macro:.4f}")
        resultados.append({
            "Modelo": modelo,
            "Vectorización": vector,
            "ngram_range": ngram,
            "Extra": extra_params,
            "F1_macro": f1_macro,
            "Reporte": res['report']
        })

# Mostrar tabla resumen
df = pd.DataFrame(resultados)
print("\nResumen de experimentos:")
print(df[["Modelo", "Vectorización", "ngram_range", "Extra", "F1_macro"]])