from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
import numpy as np

def calculate_metrics(X, labels):
    # If only 1 cluster or all noise, return None
    if len(np.unique(labels)) <= 1:
        return None
        
    # Ignore noise points (-1) for metric calculation if desired, 
    # but standard is to include them or exclude them. Let's exclude -1 for fair comparison if DBSCAN.
    mask = labels != -1
    if len(np.unique(labels[mask])) <= 1:
        return None
        
    sil = silhouette_score(X[mask], labels[mask])
    db = davies_bouldin_score(X[mask], labels[mask])
    ch = calinski_harabasz_score(X[mask], labels[mask])
    
    return {
        'Silueta': np.round(sil, 4),
        'Davies-Bouldin': np.round(db, 4),
        'Calinski-Harabasz': np.round(ch, 4)
    }

def interpret_silhouette(sil_score):
    if sil_score is None:
        return "No aplicable"
    if sil_score > 0.5:
        return "Clustering de buena calidad"
    elif sil_score >= 0.25:
        return "Clustering aceptable"
    else:
        return "Clustering débil, considere ajustar parámetros"

def rank_algorithms(metrics_dict):
    """
    metrics_dict: dict of format {'Algoritmo': {'Silueta': val, 'Davies-Bouldin': val, 'Calinski-Harabasz': val}}
    Returns the name of the best algorithm
    """
    # Silueta ↑, Davies-Bouldin ↓, Calinski-Harabasz ↑
    # Simple ranking: min-max scale each metric across algorithms and sum
    if not metrics_dict:
        return None
        
    algos = list(metrics_dict.keys())
    
    sil_vals = [metrics_dict[a]['Silueta'] for a in algos]
    db_vals = [metrics_dict[a]['Davies-Bouldin'] for a in algos]
    ch_vals = [metrics_dict[a]['Calinski-Harabasz'] for a in algos]
    
    # Normalize 0-1
    def norm_up(vals):
        if max(vals) == min(vals): return [1.0]*len(vals)
        return [(v - min(vals)) / (max(vals) - min(vals)) for v in vals]
        
    def norm_down(vals):
        if max(vals) == min(vals): return [1.0]*len(vals)
        return [(max(vals) - v) / (max(vals) - min(vals)) for v in vals]

    sil_norm = norm_up(sil_vals)
    db_norm = norm_down(db_vals)
    ch_norm = norm_up(ch_vals)
    
    scores = []
    for i in range(len(algos)):
        # Equal weights
        score = sil_norm[i] + db_norm[i] + ch_norm[i]
        scores.append(score)
        
    best_idx = np.argmax(scores)
    return algos[best_idx]
