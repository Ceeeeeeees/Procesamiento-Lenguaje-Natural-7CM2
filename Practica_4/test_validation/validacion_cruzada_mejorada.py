"""
Módulo para mejorar la validación cruzada en el detector de clickbait.
Este archivo contiene la implementación mejorada del método de validación cruzada
que utiliza StratifiedKFold para mantener la proporción de clases en cada fold.
"""

from sklearn.model_selection import cross_validate, StratifiedKFold

def validacion_cruzada_mejorada(pipeline, X, y, n_splits=5):
    """
    Realiza validación cruzada estratificada con múltiples métricas.
    
    Parámetros:
    -----------
    pipeline : Pipeline de scikit-learn
        El pipeline a evaluar
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
        pipeline, X, y, 
        cv=cv,
        scoring=scoring,
        return_train_score=True  # También devuelve resultados en conjunto de entrenamiento
    )
    
    # Calcular estadísticas de los resultados
    results_summary = {}
    
    # Para cada métrica, calcular media y desviación estándar
    for metric in scoring.keys():
        test_metric = f'test_{metric}'
        train_metric = f'train_{metric}'
        
        # Resultados en test
        results_summary[f'{metric}_test_scores'] = cv_results[test_metric]
        results_summary[f'{metric}_test_mean'] = cv_results[test_metric].mean()
        results_summary[f'{metric}_test_std'] = cv_results[test_metric].std()
        
        # Resultados en train
        results_summary[f'{metric}_train_scores'] = cv_results[train_metric]
        results_summary[f'{metric}_train_mean'] = cv_results[train_metric].mean()
        results_summary[f'{metric}_train_std'] = cv_results[train_metric].std()
    
    # Para mantener compatibilidad con la implementación original
    results_summary['resultados'] = cv_results['test_f1_macro']
    results_summary['media'] = cv_results['test_f1_macro'].mean()
    results_summary['desviacion_estandar'] = cv_results['test_f1_macro'].std()
    
    # Guardar todos los resultados detallados
    results_summary['cv_results_raw'] = cv_results
    
    return results_summary

# Ejemplo de cómo modificar la clase ClickBaitDetector:
"""
def validacionCruzada(self, X, y, n_splits=5):
    if not self.pipeline:
        raise ValueError("El pipeline no ha sido creado. Llama a crearPipeline primero.")
    
    return validacion_cruzada_mejorada(self.pipeline, X, y, n_splits)
"""
