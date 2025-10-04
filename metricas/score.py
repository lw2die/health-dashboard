#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cálculo del Score de Longevidad (0-100)
Combina múltiples métricas de salud
"""

from config import (
    PESO_OBJETIVO,
    PAI_OBJETIVO_SEMANAL,
    VO2MAX_EXCELENTE,
    VO2MAX_BUENO,
    SUENO_OBJETIVO_HORAS
)


def calcular_score_longevidad(peso_actual, pai_semanal, vo2max, sueno_promedio):
    """
    Calcula score de longevidad (0-100) basado en múltiples factores.
    
    Distribución de puntos:
    - Composición corporal: 40%
    - Fitness cardiovascular: 30% (PAI 20% + VO2max 10%)
    - Sueño: 20%
    - Balance entrenamiento: 10%
    
    Args:
        peso_actual (float): Peso actual en kg
        pai_semanal (float): PAI de los últimos 7 días
        vo2max (float): VO2max estimado
        sueno_promedio (float): Horas de sueño promedio
    
    Returns:
        int: Score de 0 a 100
    """
    score = 0
    
    # Composición corporal (40 puntos)
    score += _puntaje_peso(peso_actual)
    
    # Fitness cardiovascular (30 puntos)
    score += _puntaje_pai(pai_semanal)
    score += _puntaje_vo2max(vo2max)
    
    # Sueño (20 puntos)
    score += _puntaje_sueno(sueno_promedio)
    
    # Balance de entrenamiento (10 puntos)
    # Por ahora siempre otorga 10 puntos
    # En el futuro podría considerar TSB
    score += 10
    
    return min(100, score)


def _puntaje_peso(peso_actual):
    """
    Calcula puntaje de composición corporal (0-40 puntos).
    """
    if peso_actual <= 0:
        return 0
    
    delta_peso = abs(peso_actual - PESO_OBJETIVO)
    
    if delta_peso == 0:
        return 40
    elif delta_peso <= 2:
        return 35
    elif delta_peso <= 5:
        return 25
    elif delta_peso <= 10:
        return 15
    else:
        return 5


def _puntaje_pai(pai_semanal):
    """
    Calcula puntaje de PAI semanal (0-20 puntos).
    """
    if pai_semanal >= PAI_OBJETIVO_SEMANAL:
        return 20
    elif pai_semanal >= 75:
        return 15
    elif pai_semanal >= 50:
        return 10
    else:
        return 5


def _puntaje_vo2max(vo2max):
    """
    Calcula puntaje de VO2max (0-10 puntos).
    """
    if vo2max >= VO2MAX_EXCELENTE:
        return 10
    elif vo2max >= VO2MAX_BUENO:
        return 7
    else:
        return 3


def _puntaje_sueno(sueno_promedio):
    """
    Calcula puntaje de sueño (0-20 puntos).
    """
    if sueno_promedio >= SUENO_OBJETIVO_HORAS:
        return 20
    elif sueno_promedio >= 6:
        return 15
    elif sueno_promedio >= 5:
        return 10
    else:
        return 5


def generar_recomendaciones(peso_actual, pai_semanal, sueno_promedio):
    """
    Genera recomendaciones personalizadas basadas en métricas.
    
    Args:
        peso_actual (float): Peso actual en kg
        pai_semanal (float): PAI semanal
        sueno_promedio (float): Horas de sueño promedio
    
    Returns:
        list: Lista de recomendaciones HTML
    """
    recomendaciones = []
    
    # Recomendación de peso
    delta_peso = peso_actual - PESO_OBJETIVO
    if delta_peso > 0:
        deficit_diario = 300 if delta_peso <= 5 else 400
        semanas_objetivo = int((delta_peso * 7700) / (deficit_diario * 7))
        recomendaciones.append(
            f"<strong>Ajuste Fino:</strong> Estás {abs(delta_peso):.1f} kg sobre objetivo. "
            f"Con un déficit moderado de {deficit_diario} kcal/día alcanzarás el objetivo "
            f"en {semanas_objetivo} semanas."
        )
    
    # Recomendación de sueño
    if sueno_promedio < SUENO_OBJETIVO_HORAS and sueno_promedio > 0:
        recomendaciones.append(
            f"<strong>Sueño Insuficiente:</strong> Promedias {sueno_promedio:.1f}h/noche. "
            f"El sueño <{SUENO_OBJETIVO_HORAS}h está asociado con mayor mortalidad y "
            f"dificulta la pérdida de peso."
        )
    
    # Recomendación de PAI
    if pai_semanal < PAI_OBJETIVO_SEMANAL:
        recomendaciones.append(
            f"<strong>PAI Bajo:</strong> Alcanzaste {pai_semanal:.1f} PAI esta semana "
            f"(objetivo: {PAI_OBJETIVO_SEMANAL}). Aumenta intensidad o frecuencia de entrenamientos."
        )
    
    return recomendaciones