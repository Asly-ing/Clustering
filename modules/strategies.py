import pandas as pd
import numpy as np

def generate_profiles(df_original, df_clustered, cluster_col='cluster'):
    # df_original has original unscaled values but same index as df_clustered
    profiles = []
    
    clusters = sorted(df_clustered[cluster_col].unique())
    # Exclude noise if DBSCAN
    clusters = [c for c in clusters if c != -1]
    
    global_median_promedio = df_original['promedio_acumulado'].median()
    global_median_reprobadas = df_original['materias_reprobadas'].median()
    global_median_estrato = df_original['estrato_socioeconomico'].median()
    global_median_semestre = df_original['semestre_actual'].median()
    
    for c in clusters:
        idx = df_clustered[df_clustered[cluster_col] == c].index
        c_data = df_original.loc[idx]
        
        med_prom = c_data['promedio_acumulado'].median()
        med_repr = c_data['materias_reprobadas'].median()
        med_estr = c_data['estrato_socioeconomico'].median()
        med_sem = c_data['semestre_actual'].median()
        
        # Calculate predominant categorical values manually to avoid mode()[0] index out of bounds if empty
        if not c_data.empty:
            moda_fin = c_data['tipo_financiamiento'].mode()
            moda_fin = moda_fin.iloc[0] if not moda_fin.empty else "N/A"
        else:
            moda_fin = "N/A"
            
        # Determine Profile Name and Risk
        name = "Perfil General"
        risk = "MEDIO"
        strategies = []
        
        if med_prom < global_median_promedio and med_estr <= global_median_estrato:
            name = "Perfil de Alta Vulnerabilidad"
            risk = "ALTO"
            strategies = [
                "Beca o auxilio de emergencia",
                "Tutoría académica personalizada semanal",
                "Acompañamiento psicológico activo"
            ]
        elif med_prom < global_median_promedio and moda_fin == 'propio':
            name = "Perfil Académico-Económico"
            risk = "ALTO"
            strategies = [
                "Asesoría para crédito educativo",
                "Cursos de nivelación académica",
                "Programa de mentoring con estudiantes avanzados"
            ]
        elif med_sem <= 3 and med_repr > global_median_reprobadas:
            name = "Perfil de Adaptación"
            risk = "ALTO"
            strategies = [
                "Nivelación intensiva en materias de fundamentación",
                "Acompañamiento psicopedagógico grupal",
                "Taller de técnicas de estudio y manejo del tiempo"
            ]
        elif med_prom >= global_median_promedio and med_estr <= global_median_estrato:
            name = "Perfil Socioeconómico"
            risk = "MEDIO"
            strategies = [
                "Subsidio de transporte o alimentación",
                "Apoyo económico condicionado a rendimiento",
                "Inclusión en bolsa de empleo universitario"
            ]
        elif med_prom > global_median_promedio and med_repr <= global_median_reprobadas:
            name = "Perfil de Bajo Riesgo"
            risk = "BAJO"
            strategies = [
                "Invitación a semilleros de investigación",
                "Programa de excelencia académica",
                "Participación en actividades extracurriculares de liderazgo"
            ]
        else:
            name = "Perfil Estándar"
            risk = "MEDIO"
            strategies = [
                "Seguimiento semestral estándar",
                "Talleres de fortalecimiento académico",
                "Inclusión en actividades de bienestar universitario"
            ]
            
        profiles.append({
            'cluster': c,
            'size': len(c_data),
            'name': name,
            'risk': risk,
            'strategies': strategies,
            'stats': {
                'Promedio Acumulado': round(med_prom, 2),
                'Materias Reprobadas': med_repr,
                'Estrato': med_estr,
                'Semestre': med_sem,
                'Financiamiento Predominante': moda_fin
            }
        })
        
    return profiles
