#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo: polinomio_calculator.py
Función: Calcular CardioScore, MetabolicScore, InflammationScore, HormoneScore
Entrada: Parámetros de laboratorio normalizados
Salida: 4 scores + Longevity Score integrado (0-100)
"""

import logging
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ScoresCalculados:
    """Contenedor para todos los scores calculados"""
    cardio_score: float
    metabolic_score: float
    inflammation_score: float
    hormone_score: float
    longevity_score: float
    detalles_cardio: Dict
    detalles_metabolic: Dict
    detalles_inflammation: Dict
    detalles_hormone: Dict


class PolinomioCalculator:
    """Calcula scores científicos para evaluación de longevidad"""
    
    def __init__(self, edad: int = 61, altura_cm: int = 177, peso_objetivo: float = 79.0):
        """
        Inicializar con datos del paciente
        
        Args:
            edad: Edad del paciente
            altura_cm: Altura en centímetros
            peso_objetivo: Peso objetivo para IMC
        """
        self.edad = edad
        self.altura_cm = altura_cm
        self.peso_objetivo = peso_objetivo
        logger.info(f"PolinomioCalculator inicializado - Edad: {edad}, Altura: {altura_cm}cm")
    
    # ============ CARDIO SCORE (42% del total) ============
    def calcular_cardio_score(self, 
                             ldl: Optional[float] = None,
                             hdl: Optional[float] = None,
                             trigliceridos: Optional[float] = None,
                             pas: Optional[float] = 130) -> Tuple[float, Dict]:
        """
        CardioScore = función de (LDL, HDL, TG, PA)
        
        Fórmula:
        CardioScore = 100 - [((LDL-70)/30)² + ((50-HDL)/10)² + ((TG-100)/50)² + ((PAS-120)/20)²] × 25
        """
        detalles = {}
        
        # Valores por defecto si no se proporcionan
        if ldl is None:
            ldl = 100
            logger.warning("LDL no proporcionado, usando default 100")
        if hdl is None:
            hdl = 50
            logger.warning("HDL no proporcionado, usando default 50")
        if trigliceridos is None:
            trigliceridos = 100
            logger.warning("Triglicéridos no proporcionado, usando default 100")
        
        # Calcular componentes
        ldl_component = ((ldl - 70) / 30) ** 2
        hdl_component = ((50 - hdl) / 10) ** 2
        tg_component = ((trigliceridos - 100) / 50) ** 2
        pas_component = ((pas - 120) / 20) ** 2
        
        # Sumar componentes y aplicar peso
        suma_componentes = ldl_component + hdl_component + tg_component + pas_component
        cardio_score = max(0, min(100, 100 - (suma_componentes * 25)))
        
        detalles = {
            'LDL': {'valor': ldl, 'componente': ldl_component, 'optimo': 70},
            'HDL': {'valor': hdl, 'componente': hdl_component, 'optimo': 50},
            'Trigliceridos': {'valor': trigliceridos, 'componente': tg_component, 'optimo': 100},
            'PAS': {'valor': pas, 'componente': pas_component, 'optimo': 120},
            'suma_componentes': suma_componentes,
            'clasificacion': self._clasificar_cardio(cardio_score)
        }
        
        logger.info(f"CardioScore calculado: {cardio_score:.1f}/100 ({detalles['clasificacion']})")
        return cardio_score, detalles
    
    def _clasificar_cardio(self, score: float) -> str:
        """Clasificar CardioScore"""
        if score >= 80:
            return "EXCELENTE (Riesgo muy bajo)"
        elif score >= 70:
            return "BUENO (Riesgo bajo)"
        elif score >= 60:
            return "MODERADO (Riesgo medio)"
        else:
            return "CRÍTICO (Riesgo elevado)"
    
    # ============ METABOLIC SCORE (28% del total) ============
    def calcular_metabolic_score(self,
                                glucemia: Optional[float] = None,
                                hba1c: Optional[float] = None,
                                peso_actual: Optional[float] = None) -> Tuple[float, Dict]:
        """
        MetabolicScore = función de (Glucemia, HbA1c, IMC)
        
        Fórmula mejorada:
        MetabolicScore = 100 - [((Glucosa-85)/15)² + ((HbA1c-5.2)/0.5)² + ((IMC-22)/3)²] × 15
        (Factor reducido de 25 a 15 para mejor calibración)
        """
        detalles = {}
        
        if glucemia is None:
            glucemia = 85
        if hba1c is None:
            hba1c = 5.2
        if peso_actual is None:
            peso_actual = self.peso_objetivo
        
        # Calcular IMC
        altura_m = self.altura_cm / 100
        imc = peso_actual / (altura_m ** 2)
        
        # Calcular componentes
        glucemia_component = ((glucemia - 85) / 15) ** 2
        hba1c_component = ((hba1c - 5.2) / 0.5) ** 2
        imc_component = ((imc - 22) / 3) ** 2
        
        # Sumar y calcular score
        suma_componentes = glucemia_component + hba1c_component + imc_component
        metabolic_score = max(0, min(100, 100 - (suma_componentes * 15)))
        
        detalles = {
            'Glucemia': {'valor': glucemia, 'componente': glucemia_component, 'optimo': 85},
            'HbA1c': {'valor': hba1c, 'componente': hba1c_component, 'optimo': 5.2},
            'IMC': {'valor': imc, 'componente': imc_component, 'optimo': 22, 'peso': peso_actual},
            'suma_componentes': suma_componentes,
            'clasificacion': self._clasificar_metabolic(hba1c)
        }
        
        logger.info(f"MetabolicScore calculado: {metabolic_score:.1f}/100 ({detalles['clasificacion']})")
        return metabolic_score, detalles
    
    def _clasificar_metabolic(self, hba1c: float) -> str:
        """Clasificar MetabolicScore basado en HbA1c"""
        if hba1c < 5.7:
            return "ÓPTIMO (Metabolismo normal)"
        elif hba1c < 6.4:
            return "PREDIABETES (Acción requerida)"
        elif hba1c < 7.0:
            return "PREDIABETES MODERADA (Urgente)"
        else:
            return "DIABETES (Crítico)"
    
    # ============ INFLAMMATION SCORE (18% del total) ============
    def calcular_inflammation_score(self,
                                   pcr: Optional[float] = None,
                                   urea: Optional[float] = None,
                                   creatinina: Optional[float] = None) -> Tuple[float, Dict]:
        """
        InflammationScore = función de (PCR, Urea, Creatinina)
        
        PCR es el mejor predictor de envejecimiento y mortalidad
        
        Fórmula:
        InflammationScore = 100 - [((PCR/0.6)² × 30) + ((Cr-0.9)/0.3)² × 20]
        """
        detalles = {}
        
        if pcr is None:
            pcr = 0.5
        if urea is None:
            urea = 30
        if creatinina is None:
            creatinina = 0.9
        
        # PCR es el factor dominante (mejor predictor de longevidad)
        pcr_normalized = pcr / 0.6  # Normalizar a óptimo
        pcr_component = min((pcr_normalized ** 2) * 30, 50)  # Cap máximo
        
        # Creatinina (función renal)
        cr_component = ((creatinina - 0.9) / 0.3) ** 2 * 20
        
        # Bonus si ambos están excelentes
        bonus = 0
        if pcr < 0.6 and creatinina < 1.0:
            bonus = 15  # Bonus importante por buena salud inflamatoria y renal
        
        # Calcular score
        suma_componentes = pcr_component + cr_component
        inflammation_score = max(0, min(100, 100 - suma_componentes + bonus))
        
        detalles = {
            'PCR': {'valor': pcr, 'componente': pcr_component, 'optimo': 0.6, 
                   'importancia': 'CRÍTICA - Mejor predictor de longevidad'},
            'Urea': {'valor': urea, 'rango_normal': '13-50'},
            'Creatinina': {'valor': creatinina, 'componente': cr_component, 'optimo': 0.9},
            'bonus_renal': bonus,
            'suma_componentes': suma_componentes,
            'clasificacion': self._clasificar_inflammation(pcr)
        }
        
        logger.info(f"InflammationScore calculado: {inflammation_score:.1f}/100 ({detalles['clasificacion']})")
        return inflammation_score, detalles
    
    def _clasificar_inflammation(self, pcr: float) -> str:
        """Clasificar InflammationScore basado en PCR"""
        if pcr < 0.6:
            return "EXCELENTE (Inflamación muy baja - mejor predictor longevidad)"
        elif pcr < 3.0:
            return "NORMAL (Inflamación controlada)"
        elif pcr < 10.0:
            return "ELEVADA (Inflamación presente)"
        else:
            return "CRÍTICA (Inflamación severa)"
    
    # ============ HORMONE SCORE (12% del total) ============
    def calcular_hormone_score(self,
                              tsh: Optional[float] = None,
                              t4l: Optional[float] = None,
                              testosterona: Optional[float] = None) -> Tuple[float, Dict]:
        """
        HormoneScore = función de (TSH, T4L, Testosterona)
        
        TSH es crítico: valores altos = hipotiroidismo subclinical (causa fatiga, sueño)
        
        Fórmula:
        HormoneScore = 100 - [((TSH-1.5)/1)² × 30] - [((Test-6.0)/2)² × 20] + Bonus_T4L
        """
        detalles = {}
        
        if tsh is None:
            tsh = 2.5
        if t4l is None:
            t4l = 1.3
        if testosterona is None:
            testosterona = 6.5
        
        # TSH: rango óptimo 0.5-2.5, valores altos = hipotiroidismo
        tsh_optimo = 1.5
        tsh_component = ((tsh - tsh_optimo) / 1.0) ** 2 * 30
        
        # Testosterona: importante para hombres >49 años
        test_optimo = 6.0
        test_component = ((testosterona - test_optimo) / 2.0) ** 2 * 20
        
        # T4L (bonus si está en rango óptimo 0.8-1.8)
        bonus_t4l = 10 if 0.8 <= t4l <= 1.8 else 0
        
        # Calcular score
        suma_componentes = tsh_component + test_component
        hormone_score = max(0, min(100, 100 - suma_componentes + bonus_t4l))
        
        detalles = {
            'TSH': {'valor': tsh, 'componente': tsh_component, 'optimo': 1.5,
                   'alerta': tsh > 2.5, 'interpretacion': self._interpretar_tsh(tsh)},
            'T4L': {'valor': t4l, 'optimo_min': 0.8, 'optimo_max': 1.8, 'bonus': bonus_t4l},
            'Testosterona': {'valor': testosterona, 'componente': test_component, 'optimo': 6.0},
            'suma_componentes': suma_componentes,
            'clasificacion': self._clasificar_hormone(tsh, testosterona)
        }
        
        logger.info(f"HormoneScore calculado: {hormone_score:.1f}/100 ({detalles['clasificacion']})")
        return hormone_score, detalles
    
    def _interpretar_tsh(self, tsh: float) -> str:
        """Interpretar TSH"""
        if tsh < 0.5:
            return "BAJO - Posible hipertiroidismo"
        elif 0.5 <= tsh <= 2.5:
            return "ÓPTIMO"
        elif 2.5 < tsh <= 4.2:
            return "ELEVADO - Hipotiroidismo subclinical (fatiga, sueño)"
        elif tsh > 4.2:
            return "MUY ELEVADO - Hipotiroidismo clínico"
        return "DESCONOCIDO"
    
    def _clasificar_hormone(self, tsh: float, testosterona: float) -> str:
        """Clasificar HormoneScore"""
        if tsh > 4.2:
            return "CRÍTICO (TSH muy elevado)"
        elif tsh > 2.5:
            return "ALERTA (TSH elevado - hipotiroidismo subclinical)"
        elif testosterona < 4.0:
            return "ALERTA (Testosterona baja)"
        else:
            return "BUENO (Balance hormonal adecuado)"
    
    # ============ LONGEVITY SCORE INTEGRADO ============
    def calcular_longevity_score_completo(self,
                                         ldl: Optional[float] = None,
                                         hdl: Optional[float] = None,
                                         trigliceridos: Optional[float] = None,
                                         pas: Optional[float] = 130,
                                         glucemia: Optional[float] = None,
                                         hba1c: Optional[float] = None,
                                         peso_actual: Optional[float] = None,
                                         pcr: Optional[float] = None,
                                         urea: Optional[float] = None,
                                         creatinina: Optional[float] = None,
                                         tsh: Optional[float] = None,
                                         t4l: Optional[float] = None,
                                         testosterona: Optional[float] = None) -> ScoresCalculados:
        """
        Calcular todos los scores y el Longevity Score integrado
        
        Ponderación final:
        - CardioScore: 42%
        - MetabolicScore: 28%
        - InflammationScore: 18%
        - HormoneScore: 12%
        """
        
        # Calcular cada score
        cardio_score, det_cardio = self.calcular_cardio_score(ldl, hdl, trigliceridos, pas)
        metabolic_score, det_metabolic = self.calcular_metabolic_score(glucemia, hba1c, peso_actual)
        inflammation_score, det_inflammation = self.calcular_inflammation_score(pcr, urea, creatinina)
        hormone_score, det_hormone = self.calcular_hormone_score(tsh, t4l, testosterona)
        
        # Calcular Longevity Score ponderado
        longevity_score = (
            cardio_score * 0.42 +
            metabolic_score * 0.28 +
            inflammation_score * 0.18 +
            hormone_score * 0.12
        )
        
        # Redondear a 1 decimal
        longevity_score = round(longevity_score, 1)
        
        # Logging
        logger.info(f"\n{'='*60}")
        logger.info(f"LONGEVITY SCORE INTEGRADO: {longevity_score}/100")
        logger.info(f"{'='*60}")
        logger.info(f"CardioScore      (42%): {cardio_score:.1f}/100 → {cardio_score * 0.42:.1f} pts")
        logger.info(f"MetabolicScore   (28%): {metabolic_score:.1f}/100 → {metabolic_score * 0.28:.1f} pts")
        logger.info(f"InflammationScore(18%): {inflammation_score:.1f}/100 → {inflammation_score * 0.18:.1f} pts")
        logger.info(f"HormoneScore     (12%): {hormone_score:.1f}/100 → {hormone_score * 0.12:.1f} pts")
        logger.info(f"{'='*60}\n")
        
        return ScoresCalculados(
            cardio_score=cardio_score,
            metabolic_score=metabolic_score,
            inflammation_score=inflammation_score,
            hormone_score=hormone_score,
            longevity_score=longevity_score,
            detalles_cardio=det_cardio,
            detalles_metabolic=det_metabolic,
            detalles_inflammation=det_inflammation,
            detalles_hormone=det_hormone
        )
    
    def clasificar_longevity_score(self, score: float) -> str:
        """Clasificar Longevity Score"""
        if score >= 80:
            return "EXCELENTE - Riesgo cardiovascular muy bajo, longevidad optimizada"
        elif score >= 70:
            return "BUENO - Hay áreas específicas a mejorar"
        elif score >= 60:
            return "MODERADO - Requiere intervención médica"
        else:
            return "CRÍTICO - Acción inmediata recomendada"


def main():
    """Test de funcionamiento"""
    
    # Datos de ejemplo (tu situación actual)
    calc = PolinomioCalculator(edad=61, altura_cm=177, peso_objetivo=79.0)
    
    # Calcular con tus parámetros reales (Octubre 2025)
    scores = calc.calcular_longevity_score_completo(
        ldl=79,                    # LDL bueno
        hdl=49,                    # HDL bajo (alerta)
        trigliceridos=45,          # Excelente
        pas=130,                   # Estimado
        glucemia=97,               # Ligeramente elevada
        hba1c=5.7,                 # PREDIABETES
        peso_actual=83.3,          # Actual
        pcr=0.55,                  # Excelente
        urea=40,                   # Normal
        creatinina=1.15,           # Ligeramente elevada
        tsh=2.67,                  # ELEVADO (hipotiroidismo subclinical)
        t4l=1.57,                  # Normal
        testosterona=7.77          # Bueno
    )
    
    print(f"""
    ╔════════════════════════════════════════════════════════════╗
    ║           RESULTADOS FINALES - OCTUBRE 2025               ║
    ╚════════════════════════════════════════════════════════════╝
    
    🎯 LONGEVITY SCORE: {scores.longevity_score}/100 
    Clasificación: {calc.clasificar_longevity_score(scores.longevity_score)}
    
    ┌────────────────────────────────────────────────────────────┐
    │ SCORES COMPONENTES:                                        │
    ├────────────────────────────────────────────────────────────┤
    │ CardioScore (42%):         {scores.cardio_score:.1f}/100           │
    │ MetabolicScore (28%):      {scores.metabolic_score:.1f}/100           │
    │ InflammationScore (18%):   {scores.inflammation_score:.1f}/100           │
    │ HormoneScore (12%):        {scores.hormone_score:.1f}/100           │
    └────────────────────────────────────────────────────────────┘
    
    ⚠️  ALERTAS DETECTADAS:
    • HbA1c 5.7% → PREDIABETES (Acción: Metformina + Dieta IG bajo)
    • TSH 2.67 → ELEVADO (Explica sueño 2.3h, acción: Selenio + Zinc)
    • HDL 49 → BAJO (Acción: Omega-3 + Cardio intenso)
    
    ✅ FORTALEZAS:
    • PCR <0.6 → EXCELENTE (Mejor predictor de longevidad)
    • Triglicéridos 45 → EXCELENTE
    • Testosterona 7.77 → BUENO
    """)


if __name__ == '__main__':
    main()