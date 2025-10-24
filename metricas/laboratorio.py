#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de procesamiento de laboratorio clínico
Integración con dashboard de HealthConnect - CORREGIDO
"""

import json
from pathlib import Path
from datetime import datetime

def obtener_datos_laboratorio_y_alertas(edad=61, altura_cm=177, peso_kg=83, vo2max_medido=None):
    """
    Procesa laboratorio y genera scores científicos.
    
    Args:
        edad: Edad del usuario
        altura_cm: Altura en cm
        peso_kg: Peso actual en kg
        vo2max_medido: VO2max medido por dispositivo (puede ser None)
        
    Returns:
        dict con scores, alertas y parámetros
    """
    
    # Buscar archivo de laboratorio
    rutas_posibles = [
        Path(r"H:\Mi unidad\HealthConnect Exports\LAB\lab_jcp.json"),
        Path("LAB/lab_jcp.json"),
        Path("../LAB/lab_jcp.json"),
        Path("cache/laboratorio_cache.json")
    ]
    
    laboratorio_data = None
    for ruta in rutas_posibles:
        if ruta.exists():
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    laboratorio_data = json.load(f)
                break
            except:
                continue
    
    # Si no encuentra laboratorio, retornar estructura vacía
    if not laboratorio_data:
        return {
            "longevity_score": 0,
            "scores": {},
            "alertas": [],
            "parametros": {}
        }
    
    # Extraer parámetros del laboratorio
    parametros = laboratorio_data.get("parametros", {})
    if not parametros:
        # Valores por defecto
        parametros = {
            "Colesterol Total": {"valor": 75, "rango": "120-200", "estado": "bajo"},
            "LDL": {"valor": 27, "rango": "<100", "estado": "óptimo"},
            "HDL": {"valor": 43, "rango": ">55", "estado": "bajo"},
            "Triglicéridos": {"valor": 31, "rango": "<150", "estado": "óptimo"},
            "Glucemia": {"valor": 91, "rango": "70-100", "estado": "normal"},
            "HbA1c": {"valor": 5.7, "rango": "<5.7", "estado": "prediabetes"},
            "PCR": {"valor": 0.8, "rango": "<1.0", "estado": "normal"},
            "TSH": {"valor": 5.2, "rango": "0.4-4.0", "estado": "alto"},
            "Vitamina D": {"valor": 32, "rango": "30-100", "estado": "normal"},
            "B12": {"valor": 450, "rango": "200-900", "estado": "normal"},
            "Ferritina": {"valor": 120, "rango": "20-300", "estado": "normal"}
        }
    
    # Calcular scores
    scores = calcular_scores_cientificos(parametros, vo2max_medido, peso_kg, altura_cm, edad)
    
    # Generar alertas
    alertas = generar_alertas_laboratorio(parametros, scores)
    
    # Calcular Longevity Score integrado
    longevity_score = calcular_longevity_score(scores)
    
    return {
        "longevity_score": longevity_score,
        "scores": scores,
        "alertas": alertas,
        "parametros": parametros
    }


def calcular_scores_cientificos(parametros, vo2max, peso, altura, edad):
    """
    Calcula 4 scores científicos basados en laboratorio.
    MANEJA vo2max None correctamente.
    """
    scores = {}
    
    # CardioScore (0-100) - Riesgo cardiovascular
    ldl = parametros.get("LDL", {}).get("valor", 100)
    hdl = parametros.get("HDL", {}).get("valor", 50)
    trig = parametros.get("Triglicéridos", {}).get("valor", 150)
    pcr = parametros.get("PCR", {}).get("valor", 1.0)
    
    cardio_score = 100
    if ldl > 130: cardio_score -= 30
    elif ldl > 100: cardio_score -= 15
    if hdl < 40: cardio_score -= 25
    elif hdl < 55: cardio_score -= 10
    if trig > 150: cardio_score -= 15
    if pcr > 3: cardio_score -= 20
    elif pcr > 1: cardio_score -= 10
    
    # ✅ Bonus por VO2max alto (validar que no sea None)
    if vo2max is not None and vo2max > 40:
        cardio_score += 10
    
    scores["CardioScore"] = max(0, min(100, cardio_score))
    
    # MetabolicScore (0-100) - Salud metabólica
    glucemia = parametros.get("Glucemia", {}).get("valor", 100)
    hba1c = parametros.get("HbA1c", {}).get("valor", 5.7)
    
    metabolic_score = 100
    if hba1c >= 6.5: metabolic_score -= 50
    elif hba1c >= 5.7: metabolic_score -= 25
    if glucemia > 125: metabolic_score -= 30
    elif glucemia > 100: metabolic_score -= 15
    
    # IMC (validar altura > 0)
    if altura > 0:
        imc = peso / ((altura/100) ** 2)
        if imc > 30: metabolic_score -= 20
        elif imc > 25: metabolic_score -= 10
    
    scores["MetabolicScore"] = max(0, min(100, metabolic_score))
    
    # InflammationScore (0-100)
    inflammation_score = 100
    if pcr > 3: inflammation_score -= 40
    elif pcr > 1: inflammation_score -= 20
    
    ferritina = parametros.get("Ferritina", {}).get("valor", 150)
    if ferritina is not None and ferritina > 300:
        inflammation_score -= 15
    
    scores["InflammationScore"] = max(0, min(100, inflammation_score))
    
    # HormoneScore (0-100)
    tsh = parametros.get("TSH", {}).get("valor", 2.0)
    vit_d = parametros.get("Vitamina D", {}).get("valor", 30)
    b12 = parametros.get("B12", {}).get("valor", 400)
    
    hormone_score = 100
    if tsh is not None:
        if tsh > 4.0: hormone_score -= 20
        elif tsh < 0.4: hormone_score -= 15
    if vit_d is not None:
        if vit_d < 20: hormone_score -= 25
        elif vit_d < 30: hormone_score -= 10
    if b12 is not None:
        if b12 < 200: hormone_score -= 20
        elif b12 < 400: hormone_score -= 10
    
    scores["HormoneScore"] = max(0, min(100, hormone_score))
    
    return scores


def calcular_longevity_score(scores):
    """Calcula score integrado de longevidad con ponderación."""
    if not scores:
        return 0
        
    ponderacion = {
        "CardioScore": 0.40,
        "MetabolicScore": 0.30,
        "InflammationScore": 0.20,
        "HormoneScore": 0.10
    }
    
    score_total = 0
    for nombre, peso in ponderacion.items():
        score_total += scores.get(nombre, 0) * peso
    
    return round(score_total, 1)


def generar_alertas_laboratorio(parametros, scores):
    """Genera alertas basadas en valores de laboratorio."""
    alertas = []
    
    # Alertas críticas
    hba1c = parametros.get("HbA1c", {}).get("valor")
    if hba1c is not None and hba1c >= 5.7:
        alertas.append({
            "severidad": "CRITICA",
            "titulo": "Prediabetes Detectada",
            "descripcion": f"HbA1c en {hba1c}% indica prediabetes",
            "accion": "Consultar endocrinólogo",
            "impacto_longevidad": "-5 a -10 años si progresa"
        })
    
    # Alertas de riesgo alto
    hdl = parametros.get("HDL", {}).get("valor")
    if hdl is not None and hdl < 40:
        alertas.append({
            "severidad": "ALTA",
            "titulo": "HDL Muy Bajo",
            "descripcion": f"HDL en {hdl} mg/dL aumenta riesgo CV",
            "accion": "Aumentar ejercicio aeróbico y omega-3",
            "impacto_longevidad": "-3 años por riesgo CV"
        })
    
    tsh = parametros.get("TSH", {}).get("valor")
    if tsh is not None and tsh > 4.0:
        alertas.append({
            "severidad": "ALTA",
            "titulo": "Hipotiroidismo Subclínico",
            "descripcion": f"TSH en {tsh} mUI/L indica tiroides lenta",
            "accion": "Evaluar T3/T4",
            "impacto_longevidad": "Fatiga crónica, metabolismo lento"
        })
    
    # Alertas moderadas
    pcr = parametros.get("PCR", {}).get("valor")
    if pcr is not None and pcr > 1.0:
        alertas.append({
            "severidad": "MODERADA",
            "titulo": "Inflamación Sistémica Leve",
            "descripcion": f"PCR en {pcr} mg/L indica inflamación",
            "accion": "Dieta antiinflamatoria",
            "impacto_longevidad": "Envejecimiento acelerado"
        })
    
    # Alertas positivas
    ldl = parametros.get("LDL", {}).get("valor")
    if ldl is not None and ldl < 70:
        alertas.append({
            "severidad": "BUENA",
            "titulo": "LDL Excelente",
            "descripcion": f"LDL en {ldl} mg/dL es óptimo",
            "accion": "Mantener régimen actual",
            "impacto_longevidad": "+3 años de protección CV"
        })
    
    return alertas