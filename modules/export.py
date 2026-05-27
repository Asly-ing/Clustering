from fpdf import FPDF
import tempfile
import os

class SERReport(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 15)
        self.set_text_color(30, 58, 95) # Azul institucional #1E3A5F
        self.cell(0, 10, "SER - Sistema de Evaluación de Retención Estudiantil", border=0, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "I", 10)
        self.set_text_color(201, 168, 76) # Dorado #C9A84C
        self.cell(0, 10, "Reporte de Perfiles de Deserción y Estrategias", border=0, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128)
        self.cell(0, 10, f"Página {self.page_no()}/{{nb}}", align="C")

def generate_pdf_report(profiles, metrics, best_algo):
    pdf = SERReport()
    pdf.add_page()
    
    # Resumen Ejecutivo
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(30, 58, 95)
    pdf.cell(0, 10, "1. Resumen Ejecutivo", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    texto_resumen = (
        f"Este reporte detalla los perfiles estudiantiles identificados mediante técnicas de clustering. "
        f"El algoritmo seleccionado como más óptimo fue {best_algo}. A continuación, se presentan los "
        f"perfiles identificados junto con su nivel de riesgo y las estrategias de retención recomendadas."
    )
    pdf.multi_cell(0, 8, texto_resumen)
    pdf.ln(5)
    
    # Métricas de validación
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(30, 58, 95)
    pdf.cell(0, 10, "2. Métricas de Validación del Modelo", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    if metrics:
        for k, v in metrics.items():
            pdf.cell(0, 8, f"- {k}: {v}", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 8, "Métricas no disponibles.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Perfiles y Estrategias
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(30, 58, 95)
    pdf.cell(0, 10, "3. Perfiles de Estudiantes y Estrategias Recomendadas", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    
    for p in profiles:
        # Título del Perfil
        pdf.set_font("helvetica", "B", 11)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 8, f"Cluster {p['cluster']}: {p['name']} (N={p['size']})", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
        
        # Riesgo
        pdf.set_font("helvetica", "B", 10)
        risk_color = (200, 0, 0) if p['risk'] == 'ALTO' else ((200, 150, 0) if p['risk'] == 'MEDIO' else (0, 150, 0))
        pdf.set_text_color(*risk_color)
        pdf.cell(0, 6, f"Nivel de Riesgo: {p['risk']}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        
        # Estadísticas
        pdf.set_font("helvetica", "I", 9)
        stats_str = ", ".join([f"{k}: {v}" for k, v in p['stats'].items()])
        pdf.multi_cell(0, 6, f"Medianas: {stats_str}")
        
        # Estrategias
        pdf.set_font("helvetica", "", 10)
        pdf.cell(0, 6, "Estrategias de Retención:", new_x="LMARGIN", new_y="NEXT")
        for idx, strategy in enumerate(p['strategies'], 1):
            pdf.set_x(pdf.l_margin + 10)
            pdf.multi_cell(pdf.epw - 10, 6, f"{idx}. {strategy}")
            
        pdf.ln(5)
        
    # Guardar a temp file
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, "reporte_ser.pdf")
    pdf.output(temp_path)
    
    return temp_path
