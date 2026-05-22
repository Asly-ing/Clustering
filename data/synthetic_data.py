import pandas as pd
import numpy as np

def generate_synthetic_data(n_students=300):
    np.random.seed(42)
    
    # Generate data
    promedio_acumulado = np.random.uniform(2.0, 4.8, n_students)
    materias_reprobadas = np.random.randint(0, 8, n_students)
    semestre_actual = np.random.randint(1, 11, n_students)
    estrato_socioeconomico = np.random.randint(1, 7, n_students)
    
    tipos_fin = ["propio", "beca", "credito", "mixto"]
    tipo_financiamiento = np.random.choice(tipos_fin, n_students, p=[0.4, 0.2, 0.3, 0.1])
    
    mod_ingreso = ["regular", "transfer", "convenio"]
    modalidad_ingreso = np.random.choice(mod_ingreso, n_students, p=[0.7, 0.15, 0.15])
    
    # Logical correlation for dropout (desertor) just for reference
    # Higher prob of dropout if low grades, high fails, low strata, own finance
    prob_dropout = (
        (5.0 - promedio_acumulado) * 0.1 + 
        materias_reprobadas * 0.05 + 
        (7 - estrato_socioeconomico) * 0.05 +
        (tipo_financiamiento == 'propio') * 0.1
    )
    prob_dropout = np.clip(prob_dropout, 0, 1)
    desertor = np.random.binomial(1, prob_dropout)
    
    # Create DataFrame
    df = pd.DataFrame({
        'promedio_acumulado': np.round(promedio_acumulado, 2),
        'materias_reprobadas': materias_reprobadas,
        'semestre_actual': semestre_actual,
        'estrato_socioeconomico': estrato_socioeconomico,
        'tipo_financiamiento': tipo_financiamiento,
        'modalidad_ingreso': modalidad_ingreso,
        'desertor': desertor
    })
    
    return df
