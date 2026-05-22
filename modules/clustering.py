import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.neighbors import NearestNeighbors

def evaluate_kmeans_k(X, k_range):
    inertias = []
    silhouettes = []
    metrics_list = []
    
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)
        
        inertia = kmeans.inertia_
        inertias.append(inertia)
        
        sil = silhouette_score(X, labels)
        silhouettes.append(sil)
        
        db = davies_bouldin_score(X, labels)
        ch = calinski_harabasz_score(X, labels)
        
        metrics_list.append({
            'k': k,
            'Silhouette': np.round(sil, 4),
            'Davies-Bouldin': np.round(db, 4),
            'Calinski-Harabasz': np.round(ch, 4)
        })
        
    return inertias, silhouettes, pd.DataFrame(metrics_list)

def run_kmeans(X, k):
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)
    return labels, kmeans

def run_hierarchical(X, n_clusters):
    hc = AgglomerativeClustering(n_clusters=n_clusters, metric='euclidean', linkage='ward')
    labels = hc.fit_predict(X)
    return labels, hc

def get_k_distances(X, min_samples):
    neigh = NearestNeighbors(n_neighbors=min_samples)
    nbrs = neigh.fit(X)
    distances, indices = nbrs.kneighbors(X)
    distances = np.sort(distances, axis=0)
    distances = distances[:,1]
    return distances

def run_dbscan(X, eps, min_samples):
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(X)
    return labels, dbscan

def reduce_to_2d(X):
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)
    return pd.DataFrame(X_pca, columns=['PCA1', 'PCA2'])
