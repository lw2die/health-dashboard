#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculador de Scores Científicos de Longevidad
CardioScore, MetabolicScore, InflammationScore, HormoneScore
+ Score Integrado de Longevidad (0-100)
"""

from typing import Dict, Optional, Tuple
import math

class PolynomioCalculator:
    """Calcula scores de longevidad basados en parámetros clínicos"""
    
    def __init__(self):
        """Inicializa calculador"""
        self.scores = {}
        self.detalles = {}
    
    def calcular_cardio_score(self, ldl: float = None, hdl: float = None, 
                            trigliceridos: float = None, pa_sistolica: float = None) -> Tuple[float, Dict]:
        """
        CardioScore: Riesgo cardiovascular
        Basado en: LDL, HDL, Trigliceridos, Presión Arterial
        Rango: 0-100
        """
        puntos = 100
        detalles = {}
        
        # LDL (peor factor)
        if ldl:
            if ldl <= 100:
                pts_ldl = 25
            elif ldl <= 130:
                pts_ldl = 20
            elif ldl <= 160:
                pts_ldl = 15
            else:
                pts_ldl = 5
            puntos -= (25 - pts_ldl)
            detalles["ldl"] = f"{pts_ldl}/25 ({int(ldl)} mg/dL)"
        
        # HDL (factor protector)
        if hdl:
            if hdl >= 60:
                pts_hdl = 25
            elif hdl >= 50:
                pts_hdl = 20
            elif hdl >= 40:
                pts_hdl = 15
            else:
                pts_hdl = 5
            puntos = puntos - (25 - pts_hdl) + 5  # Bonus por protección
            detalles["hdl"] = f"{pts_hdl}/25 ({int(hdl)} mg/dL)"
        
        # Trigliceridos
        if trigliceridos:
            if trigliceridos <= 150:
                pts_trig = 25
            elif trigliceridos <= 200:
                pts_trig = 20
            elif trigliceridos <= 300:
                pts_trig = 10
            else:
                pts_trig = 5
            puntos -= (25 - pts_trig)
            detalles["triglic"] = f"{pts_trig}/25 ({int(trigliceridos)} mg/dL)"
        
        # Presión arterial
        if pa_sistolica:
            if pa_sistolica <= 120:
                pts_pa = 25
            elif pa_sistolica <= 140:
                pts_pa = 20
            else:
                pts_pa = 10
            puntos -= (25 - pts_pa)
            detalles["pa"] = f"{pts_pa}/25 ({int(pa_sistolica)} mmHg)"
        
        score = max(0, min(100, puntos))
        return score, detalles
    
    def calcular_metabolic_score(self, glucosa: float = None, hba1c: float = None, 
                                imc: float = None, peso: float = None, altura: float = None) -> Tuple[float, Dict]:
        """
        MetabolicScore: Control glucémico e índice de masa corporal
        Basado en: Glucosa, HbA1c, IMC
        Rango: 0-100
        """
        puntos = 100
        detalles = {}
        
        # Glucosa (ayuno)
        if glucosa:
            if glucosa <= 100:
                pts_glu = 30
            elif glucosa <= 125:
                pts_glu = 20  # Prediabetes
            elif glucosa <= 200:
                pts_glu = 10  # Diabetes
            else:
                pts_glu = 5
            puntos -= (30 - pts_glu)
            detalles["glucosa"] = f"{pts_glu}/30 ({int(glucosa)} mg/dL)"
        
        # HbA1c (promedio 3 meses)
        if hba1c:
            if hba1c <= 5.7:
                pts_a1c = 30
            elif hba1c <= 6.4:
                pts_a1c = 15  # Prediabetes
            else:
                pts_a1c = 5   # Diabetes
            puntos -= (30 - pts_a1c)
            detalles["hba1c"] = f"{pts_a1c}/30 ({hba1c:.1f}%)"
        
        # IMC
        if imc is None and peso and altura:
            imc = peso / ((altura/100) ** 2)
        
        if imc:
            if 18.5 <= imc <= 24.9:
                pts_imc = 40
            elif 25 <= imc <= 29.9:
                pts_imc = 30
            elif 30 <= imc <= 39.9:
                pts_imc = 15
            else:
                pts_imc = 5
            puntos -= (40 - pts_imc)
            detalles["imc"] = f"{pts_imc}/40 ({imc:.1f})"
        
        score = max(0, min(100, puntos))
        return score, detalles
    
    def calcular_inflammation_score(self, pcr: float = None, urea: float = None, 
                                   creatinina: float = None) -> Tuple[float, Dict]:
        """
        InflammationScore: Inflamación sistémica y función renal
        Basado en: PCR, Urea, Creatinina
        Rango: 0-100
        """
        puntos = 100
        detalles = {}
        
        # PCR (marcador inflamación)
        if pcr:
            if pcr <= 1.0:
                pts_pcr = 40
            elif pcr <= 3.0:
                pts_pcr = 30
            elif pcr <= 5.0:
                pts_pcr = 20
            else:
                pts_pcr = 10
            puntos -= (40 - pts_pcr)
            detalles["pcr"] = f"{pts_pcr}/40 ({pcr:.1f} mg/L)"
        
        # Urea (función renal)
        if urea:
            if 7 <= urea <= 20:
                pts_urea = 30
            elif 20 < urea <= 30:
                pts_urea = 20
            else:
                pts_urea = 10
            puntos -= (30 - pts_urea)
            detalles["urea"] = f"{pts_urea}/30 ({urea:.1f} mg/dL)"
        
        # Creatinina (función renal)
        if creatinina:
            if 0.6 <= creatinina <= 1.2:
                pts_crea = 30
            elif 1.2 < creatinina <= 1.5:
                pts_crea = 20
            else:
                pts_crea = 10
            puntos -= (30 - pts_crea)
            detalles["crea"] = f"{pts_crea}/30 ({creatinina:.1f} mg/dL)"
        
        score = max(0, min(100, puntos))
        return score, detalles
    
    def calcular_hormone_score(self, tsh: float = None, t4l: float = None, 
                              testosterone: float = None) -> Tuple[float, Dict]:
        """
        HormoneScore: Balance hormonal (tiroides, testosterona)
        Basado en: TSH, T4L, Testosterona
        Rango: 0-100
        """
        puntos = 100
        detalles = {}
        
        # TSH (tiroides)
        if tsh:
            if 0.4 <= tsh <= 2.0:
                pts_tsh = 40
            elif 0.4 <= tsh <= 4.0:
                pts_tsh = 30
            else:
                pts_tsh = 15
            puntos -= (40 - pts_tsh)
            detalles["tsh"] = f"{pts_tsh}/40 ({tsh:.2f} mIU/mL)"
        
        # T4L (tiroides)
        if t4l:
            if 0.93 <= t4l <= 1.7:
                pts_t4l = 30
            else:
                pts_t4l = 20
            puntos -= (30 - pts_t4l)
            detalles["t4l"] = f"{pts_t4l}/30 ({t4l:.2f} ng/dL)"
        
        # Testosterona
        if testosterone:
            if testosterone >= 600:
                pts_test = 30
            elif testosterone >= 400:
                pts_test = 20
            else:
                pts_test = 10
            puntos -= (30 - pts_test)
            detalles["test"] = f"{pts_test}/30 ({testosterone:.0f} ng/dL)"
        
        score = max(0, min(100, puntos))
        return score, detalles
    
    def calcular_longevity_score(self, cardio: float, metabolic: float, 
                                 inflammation: float, hormone: float) -> float:
        """
        Longevity Score Integrado
        Ponderación: CardioScore 42% + MetabolicScore 28% + InflammationScore 18% + HormoneScore 12%
        Rango: 0-100
        """
        score = (
            cardio * 0.42 +
            metabolic * 0.28 +
            inflammation * 0.18 +
            hormone * 0.12
        )
        return round(max(0, min(100, score)), 1)
    
    def calcular_todos(self, parametros: Dict) -> Dict:
        """
        Calcula todos los scores de una vez
        Retorna dict con scores e impacto
        """
        # Extraer parámetros
        ldl = parametros.get("ldl_mg_dl")
        hdl = parametros.get("hdl_mg_dl")
        triglic = parametros.get("triglic_mg_dl")
        pa_sys = parametros.get("pa_sistolica")
        glucosa = parametros.get("glucosa_mg_dl")
        hba1c = parametros.get("hba1c_porciento")
        pcr = parametros.get("pcr_mg_l")
        urea = parametros.get("urea_mg_dl")
        crea = parametros.get("creatinina_mg_dl")
        tsh = parametros.get("tsh_uiu_ml")
        
        # Calcular scores individuales
        cardio_score, det_cardio = self.calcular_cardio_score(ldl, hdl, triglic, pa_sys)
        metabolic_score, det_metab = self.calcular_metabolic_score(glucosa, hba1c)
        inflammation_score, det_inflam = self.calcular_inflammation_score(pcr, urea, crea)
        hormone_score, det_horm = self.calcular_hormone_score(tsh)
        
        # Calcular score integrado
        longevity_score = self.calcular_longevity_score(
            cardio_score, metabolic_score, inflammation_score, hormone_score
        )
        
        # Clasificación
        if longevity_score >= 80:
            clasificacion = "EXCELENTE"
            color = "#3fb950"
        elif longevity_score >= 70:
            clasificacion = "BUENO"
            color = "#d29922"
        elif longevity_score >= 50:
            clasificacion = "MODERADO"
            color = "#f85149"
        else:
            clasificacion = "CRÍTICO"
            color = "#ff0000"
        
        return {
            "longevity_score": longevity_score,
            "clasificacion": clasificacion,
            "color": color,
            "scores": {
                "cardio": round(cardio_score, 1),
                "metabolic": round(metabolic_score, 1),
                "inflammation": round(inflammation_score, 1),
                "hormone": round(hormone_score, 1)
            },
            "detalles": {
                "cardio": det_cardio,
                "metabolic": det_metab,
                "inflammation": det_inflam,
                "hormone": det_horm
            },
            "ponderacion": {
                "cardio_42%": round(cardio_score * 0.42, 1),
                "metabolic_28%": round(metabolic_score * 0.28, 1),
                "inflammation_18%": round(inflammation_score * 0.18, 1),
                "hormone_12%": round(hormone_score * 0.12, 1)
            }
        }