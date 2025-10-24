#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Alertas Inteligentes
Detecta inconsistencias y situaciones de riesgo
8 alertas clasificadas por severidad: ROJO, NARANJA, AMARILLO, VERDE
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum

class SeveridadAlerta(Enum):
    """Niveles de severidad"""
    CRITICA = "🔴 CRÍTICA"
    ALTA = "🟠 ALTA"
    MODERADA = "🟡 MODERADA"
    BUENA = "🟢 BUENA"

class AlertasGenerator:
    """Genera alertas basadas en parámetros clínicos"""
    
    def __init__(self):
        """Inicializa generador de alertas"""
        self.alertas = []
    
    def generar(self, parametros: Dict, scores: Dict) -> List[Dict]:
        """
        Genera lista de alertas
        Recibe: parámetros clínicos + scores calculados
        Retorna: lista de alertas ordenadas por severidad
        """
        self.alertas = []
        
        # Extraer parámetros
        hba1c = parametros.get("hba1c_porciento")
        glucosa = parametros.get("glucosa_mg_dl")
        ldl = parametros.get("ldl_mg_dl")
        hdl = parametros.get("hdl_mg_dl")
        triglic = parametros.get("triglic_mg_dl")
        tsh = parametros.get("tsh_uiu_ml")
        pcr = parametros.get("pcr_mg_l")
        crea = parametros.get("creatinina_mg_dl")
        
        # Alerta 1: PREDIABETES/DIABETES (HbA1c)
        if hba1c:
            self._alerta_prediabetes(hba1c)
        
        # Alerta 2: HIPERGLUCEMIA (Glucosa ayuno)
        if glucosa:
            self._alerta_glucosa(glucosa)
        
        # Alerta 3: LDL ELEVADO
        if ldl:
            self._alerta_ldl_elevado(ldl)
        
        # Alerta 4: HDL BAJO
        if hdl:
            self._alerta_hdl_bajo(hdl)
        
        # Alerta 5: TRIGLICERIDOS ELEVADOS
        if triglic:
            self._alerta_triglic(triglic)
        
        # Alerta 6: TSH ANORMAL (Hipotiroidismo/Hipertiroidismo)
        if tsh:
            self._alerta_tsh(tsh)
        
        # Alerta 7: INFLAMACIÓN SISTÉMICA (PCR elevada)
        if pcr:
            self._alerta_pcr(pcr)
        
        # Alerta 8: FUNCIÓN RENAL (Creatinina)
        if crea:
            self._alerta_creatinina(crea)
        
        # Alerta 9: INCONSISTENCIAS (VO2max alto pero LDL alto)
        if ldl and hdl:
            self._alerta_inconsistencias(ldl, hdl)
        
        # Ordenar por severidad
        self.alertas.sort(key=lambda x: self._orden_severidad(x["severidad"]))
        
        return self.alertas
    
    def _alerta_prediabetes(self, hba1c: float):
        """Detecta prediabetes/diabetes"""
        if hba1c <= 5.7:
            self.alertas.append({
                "id": "1_prediabetes",
                "titulo": "Control Glucémico Excelente",
                "severidad": SeveridadAlerta.BUENA,
                "descripcion": f"HbA1c {hba1c:.1f}% - Dentro de rango normal",
                "accion": "Mantener hábitos actuales",
                "impacto_longevidad": "+5 años"
            })
        elif hba1c <= 6.4:
            self.alertas.append({
                "id": "1_prediabetes",
                "titulo": "🚨 ALERTA: Prediabetes Detectada",
                "severidad": SeveridadAlerta.ALTA,
                "descripcion": f"HbA1c {hba1c:.1f}% - Riesgo de progresión a diabetes",
                "accion": "INICIAR INMEDIATO: Metformina 500mg c/12h + Dieta baja carbohidratos + Ejercicio",
                "impacto_longevidad": "Sin intervención: -7 años"
            })
        else:
            self.alertas.append({
                "id": "1_prediabetes",
                "titulo": "🔴 CRÍTICO: Diabetes Confirmada",
                "severidad": SeveridadAlerta.CRITICA,
                "descripcion": f"HbA1c {hba1c:.1f}% - Diabetes tipo 2 establecida",
                "accion": "URGENTE: Consultar endocrinólogo + Medición de glucosa diaria + Fármacos antidiabéticos",
                "impacto_longevidad": "Sin control: -10 años"
            })
    
    def _alerta_glucosa(self, glucosa: float):
        """Detecta hiperglucemia"""
        if glucosa <= 100:
            pass  # Ya cubierto por HbA1c
        elif glucosa <= 125:
            self.alertas.append({
                "id": "2_glucosa",
                "titulo": "Glucosa en Ayunas Elevada",
                "severidad": SeveridadAlerta.MODERADA,
                "descripcion": f"Glucosa {int(glucosa)} mg/dL - Prediabetes (100-125)",
                "accion": "Aumentar ejercicio aeróbico a 150 min/semana",
                "impacto_longevidad": "-3 años si no se trata"
            })
        else:
            self.alertas.append({
                "id": "2_glucosa",
                "titulo": "🔴 CRÍTICO: Hiperglucemia",
                "severidad": SeveridadAlerta.CRITICA,
                "descripcion": f"Glucosa {int(glucosa)} mg/dL - Muy elevada (>125)",
                "accion": "URGENTE: Control médico + Medición de glucosa capilar",
                "impacto_longevidad": "-8 años"
            })
    
    def _alerta_ldl_elevado(self, ldl: float):
        """Detecta LDL elevado"""
        if ldl <= 100:
            self.alertas.append({
                "id": "3_ldl",
                "titulo": "Colesterol LDL Óptimo",
                "severidad": SeveridadAlerta.BUENA,
                "descripcion": f"LDL {int(ldl)} mg/dL - Nivel cardioprotector",
                "accion": "Mantener dieta y ejercicio",
                "impacto_longevidad": "+3 años"
            })
        elif ldl <= 130:
            self.alertas.append({
                "id": "3_ldl",
                "titulo": "Colesterol LDL Elevado",
                "severidad": SeveridadAlerta.MODERADA,
                "descripcion": f"LDL {int(ldl)} mg/dL - Riesgo cardiovascular medio",
                "accion": "Aumentar fibra soluble + Grasas omega-3 + Estatina si es necesario",
                "impacto_longevidad": "-2 años si no se trata"
            })
        else:
            self.alertas.append({
                "id": "3_ldl",
                "titulo": "🟠 ALERTA: Colesterol LDL Muy Elevado",
                "severidad": SeveridadAlerta.ALTA,
                "descripcion": f"LDL {int(ldl)} mg/dL - Riesgo cardiovascular alto",
                "accion": "INICIAR: Atorvastatina 20-40mg/día + Control en 6 semanas",
                "impacto_longevidad": "-5 años si no se trata"
            })
    
    def _alerta_hdl_bajo(self, hdl: float):
        """Detecta HDL bajo (colesterol "bueno" insuficiente)"""
        if hdl >= 60:
            self.alertas.append({
                "id": "4_hdl",
                "titulo": "Colesterol HDL Excelente",
                "severidad": SeveridadAlerta.BUENA,
                "descripcion": f"HDL {int(hdl)} mg/dL - Protección cardiovascular óptima",
                "accion": "Mantener",
                "impacto_longevidad": "+4 años"
            })
        elif hdl >= 40:
            self.alertas.append({
                "id": "4_hdl",
                "titulo": "🟠 ALERTA: HDL Bajo (Colesterol Protector Insuficiente)",
                "severidad": SeveridadAlerta.ALTA,
                "descripcion": f"HDL {int(hdl)} mg/dL - Falta protección cardiovascular",
                "accion": "AUMENTAR: Ejercicio aeróbico 30min/día + Grasas monoinsaturadas",
                "impacto_longevidad": "-4 años sin aumentarlo"
            })
        else:
            self.alertas.append({
                "id": "4_hdl",
                "titulo": "🔴 CRÍTICO: HDL Peligrosamente Bajo",
                "severidad": SeveridadAlerta.CRITICA,
                "descripcion": f"HDL {int(hdl)} mg/dL - Riesgo cardiovascular muy alto",
                "accion": "URGENTE: Ejercicio intenso 45min/día + Ácido nicotínico considerado",
                "impacto_longevidad": "-6 años"
            })
    
    def _alerta_triglic(self, triglic: float):
        """Detecta trigliceridos elevados"""
        if triglic <= 150:
            self.alertas.append({
                "id": "5_triglic",
                "titulo": "Trigliceridos Normales",
                "severidad": SeveridadAlerta.BUENA,
                "descripcion": f"Trigliceridos {int(triglic)} mg/dL - Nivel óptimo",
                "accion": "Mantener",
                "impacto_longevidad": "+2 años"
            })
        elif triglic <= 200:
            self.alertas.append({
                "id": "5_triglic",
                "titulo": "Trigliceridos Elevados",
                "severidad": SeveridadAlerta.MODERADA,
                "descripcion": f"Trigliceridos {int(triglic)} mg/dL - Riesgo metabólico",
                "accion": "Reducir carbohidratos simples + Omega-3 (Aceite de pescado 2-3g/día)",
                "impacto_longevidad": "-2 años si no se trata"
            })
        else:
            self.alertas.append({
                "id": "5_triglic",
                "titulo": "🟠 ALERTA: Trigliceridos Muy Elevados",
                "severidad": SeveridadAlerta.ALTA,
                "descripcion": f"Trigliceridos {int(triglic)} mg/dL - Riesgo pancreatitis + cardiovascular",
                "accion": "INICIAR: Fenofibrato + Dieta muy baja en carbohidratos + Ejercicio diario",
                "impacto_longevidad": "-5 años"
            })
    
    def _alerta_tsh(self, tsh: float):
        """Detecta disfunción tiroidea"""
        if 0.4 <= tsh <= 2.0:
            self.alertas.append({
                "id": "6_tsh",
                "titulo": "Función Tiroidea Óptima",
                "severidad": SeveridadAlerta.BUENA,
                "descripcion": f"TSH {tsh:.2f} mIU/mL - Rango óptimo",
                "accion": "Mantener",
                "impacto_longevidad": "+2 años"
            })
        elif 2.0 < tsh <= 4.0:
            self.alertas.append({
                "id": "6_tsh",
                "titulo": "🟡 Hipotiroidismo Subclínico",
                "severidad": SeveridadAlerta.MODERADA,
                "descripcion": f"TSH {tsh:.2f} mIU/mL - Síntomas leves (fatiga, frío)",
                "accion": "Considerar L-Tiroxina 25mcg/día + Yodo, Selenio",
                "impacto_longevidad": "-1 año"
            })
        else:
            self.alertas.append({
                "id": "6_tsh",
                "titulo": "🟠 ALERTA: Hipotiroidismo",
                "severidad": SeveridadAlerta.ALTA,
                "descripcion": f"TSH {tsh:.2f} mIU/mL - Muy elevado (>4.0)",
                "accion": "INICIAR: L-Tiroxina con endocrinólogo + Monitoreo cada 6 semanas",
                "impacto_longevidad": "-3 años si no se trata"
            })
    
    def _alerta_pcr(self, pcr: float):
        """Detecta inflamación sistémica"""
        if pcr <= 1.0:
            self.alertas.append({
                "id": "7_pcr",
                "titulo": "Inflamación Sistémica Baja",
                "severidad": SeveridadAlerta.BUENA,
                "descripcion": f"PCR {pcr:.1f} mg/L - Muy bueno",
                "accion": "Mantener dieta antiinflamatoria",
                "impacto_longevidad": "+3 años"
            })
        elif pcr <= 3.0:
            self.alertas.append({
                "id": "7_pcr",
                "titulo": "Inflamación Moderada",
                "severidad": SeveridadAlerta.MODERADA,
                "descripcion": f"PCR {pcr:.1f} mg/L - Inflamación subclínica",
                "accion": "Aumentar antioxidantes: Cúrcuma + Jengibre + Polifenoles",
                "impacto_longevidad": "-1 año"
            })
        else:
            self.alertas.append({
                "id": "7_pcr",
                "titulo": "🟠 ALERTA: Inflamación Sistémica Elevada",
                "severidad": SeveridadAlerta.ALTA,
                "descripcion": f"PCR {pcr:.1f} mg/L - Riesgo de enfermedades crónicas",
                "accion": "URGENTE: Dieta mediterránea + Ayuno intermitente + Omega-3",
                "impacto_longevidad": "-4 años"
            })
    
    def _alerta_creatinina(self, creatinina: float):
        """Detecta disfunción renal"""
        if 0.6 <= creatinina <= 1.2:
            pass  # Normal, no alerta
        elif creatinina <= 1.5:
            self.alertas.append({
                "id": "8_crea",
                "titulo": "Creatinina Ligeramente Elevada",
                "severidad": SeveridadAlerta.MODERADA,
                "descripcion": f"Creatinina {creatinina:.1f} mg/dL - Función renal en límite",
                "accion": "Aumentar hidratación + Reducir sal + Monitoreo anual",
                "impacto_longevidad": "-1 año"
            })
        else:
            self.alertas.append({
                "id": "8_crea",
                "titulo": "🟠 ALERTA: Creatinina Elevada",
                "severidad": SeveridadAlerta.ALTA,
                "descripcion": f"Creatinina {creatinina:.1f} mg/dL - Función renal comprometida",
                "accion": "URGENTE: Consultar nefrólogo + Limitar proteína + Monitoreo cada 3 meses",
                "impacto_longevidad": "-5 años"
            })
    
    def _alerta_inconsistencias(self, ldl: float, hdl: float):
        """Detecta inconsistencias metabólicas"""
        ratio_ldl_hdl = ldl / max(hdl, 0.1)
        
        if ratio_ldl_hdl > 3:
            self.alertas.append({
                "id": "9_ratio",
                "titulo": "🟠 ALERTA: Ratio LDL/HDL Comprometido",
                "severidad": SeveridadAlerta.ALTA,
                "descripcion": f"Ratio LDL/HDL {ratio_ldl_hdl:.1f} - Muy alto (>3)",
                "accion": "Priorizar ejercicio + Fibra soluble + Considerar fármacos",
                "impacto_longevidad": "-3 años"
            })
    
    def _orden_severidad(self, severidad: SeveridadAlerta) -> int:
        """Retorna orden para sorting"""
        orden = {
            SeveridadAlerta.CRITICA: 0,
            SeveridadAlerta.ALTA: 1,
            SeveridadAlerta.MODERADA: 2,
            SeveridadAlerta.BUENA: 3
        }
        return orden.get(severidad, 4)