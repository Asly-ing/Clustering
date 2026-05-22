import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler, LabelEncoder

def preprocess_data(df, selected_vars, norm_technique, null_strategy):
    df_processed = df[selected_vars].copy()
    
    # 1. Handle Nulls
    if df_processed.isnull().sum().sum() > 0:
        if null_strategy == 'Imputación por mediana/moda':
            for col in df_processed.columns:
                if df_processed[col].dtype in ['int64', 'float64']:
                    df_processed[col] = df_processed[col].fillna(df_processed[col].median())
                else:
                    df_processed[col] = df_processed[col].fillna(df_processed[col].mode()[0])
        elif null_strategy == 'Eliminar filas con nulos':
            df_processed = df_processed.dropna()
            
    # 2. Label Encoding for categorical variables
    encoders = {}
    for col in df_processed.columns:
        if df_processed[col].dtype == 'object' or df_processed[col].dtype.name == 'category':
            le = LabelEncoder()
            df_processed[col] = le.fit_transform(df_processed[col].astype(str))
            encoders[col] = le
            
    # 3. Normalization
    scaler = None
    if norm_technique == 'Normalización Min-Max':
        scaler = MinMaxScaler()
    elif norm_technique == 'Estandarización Z-Score':
        scaler = StandardScaler()
        
    if scaler:
        cols = df_processed.columns
        df_processed[cols] = scaler.fit_transform(df_processed[cols])
        
    return df_processed, encoders, scaler
