#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cálculo de Score de Longevidad
"""

from config import PESO_OBJETIVO, PAI_OBJETIVO_SEMANAL, VO2MAX_EXCELENTE, VO2MAX_BUENO, SUENO_OBJETIVO_HORAS


def calcular_score_longevidad(peso_actual, pai_semanal, vo2max, promedio_sueno_horas):
    """
    Calcula score de longevidad (0-100).
    
    Args:
        peso_actual: Peso actual en kg
        pai_semanal: PAI semanal acumulado
        vo2max: VO2max calculado o None
        promedio_sueno_horas: Horas promedio de sueño
    
    Returns:
        int: Score de 0-100
    """
    score = 0
    
    # Peso (25 puntos) - VALIDACIÓN AHORA ESTÁ DENTRO DE _puntaje_peso
    score += _puntaje_peso(peso_actual)
    
    # PAI (25 puntos)
    score += _puntaje_pai(pai_semanal)
    
    # VO2max (25 puntos)
    if vo2max is not None:
        score += _puntaje_vo2max(vo2max)
    else:
        # Si no hay VO2max, dar 15 puntos base
        score += 15
    
    # Sueño (25 puntos)
    score += _puntaje_sueno(promedio_sueno_horas)
    
    return max(0, min(100, int(score)))


def _puntaje_peso(peso_actual):
    """Calcula puntaje por peso (0-25)."""
    # 🚨 CORRECCIÓN CLAVE: Manejar None o cero antes de la resta 🚨
    if peso_actual is None or peso_actual <= 0:
        return 10  # Puntaje base si el dato de peso falta
    
    # Línea 49 original que causaba el error:
    diferencia = abs(peso_actual - PESO_OBJETIVO)
    
    if diferencia <= 2:
        return 25
    elif diferencia <= 5:
        return 20
    elif diferencia <= 10:
        return 15
    else:
        return 10


def _puntaje_pai(pai_semanal):
    """Calcula puntaje por PAI (0-25)."""
    if pai_semanal >= PAI_OBJETIVO_SEMANAL * 1.5:
        return 25
    elif pai_semanal >= PAI_OBJETIVO_SEMANAL:
        return 20
    elif pai_semanal >= PAI_OBJETIVO_SEMANAL * 0.75:
        return 15
    elif pai_semanal >= PAI_OBJETIVO_SEMANAL * 0.5:
        return 10
    else:
        return 5


def _puntaje_vo2max(vo2max):
    """Calcula puntaje por VO2max (0-25). Valida que no sea None."""
    # Nota: Aunque la función principal ya verifica 'vo2max is not None', mantenemos la validación aquí
    if vo2max is None or vo2max == 0:
        return 15  # Puntaje neutral si no hay datos
    
    if vo2max >= VO2MAX_EXCELENTE:
        return 25
    elif vo2max >= VO2MAX_BUENO:
        return 20
    elif vo2max >= VO2MAX_BUENO * 0.9:
        return 15
    else:
        return 10


def _puntaje_sueno(promedio_sueno_horas):
    """Calcula puntaje por sueño (0-25)."""
    if promedio_sueno_horas == 0:
        return 0
    
    if promedio_sueno_horas >= SUENO_OBJETIVO_HORAS:
        return 25
    elif promedio_sueno_horas >= SUENO_OBJETIVO_HORAS - 1:
        return 20
    elif promedio_sueno_horas >= SUENO_OBJETIVO_HORAS - 2:
        return 15
    else:
        return 10


def generar_recomendaciones(peso_actual, pai_semanal, promedio_sueno_horas):
    """Genera recomendaciones personalizadas."""
    recomendaciones = []
    
    # Peso
    # 🚨 CORRECCIÓN CLAVE: Validar que haya datos de peso antes de calcular la diferencia 🚨
    if peso_actual is not None and peso_actual > 0:
        diferencia_peso = peso_actual - PESO_OBJETIVO
        if abs(diferencia_peso) > 5:
            if diferencia_peso > 0:
                recomendaciones.append(f"🎯 Reducir {abs(diferencia_peso):.1f} kg para peso objetivo")
            else:
                recomendaciones.append(f"🎯 Ganar {abs(diferencia_peso):.1f} kg para peso objetivo")
    
    # PAI
    if pai_semanal < PAI_OBJETIVO_SEMANAL:
        deficit = PAI_OBJETIVO_SEMANAL - pai_semanal
        recomendaciones.append(f"💪 Aumentar PAI en {deficit:.0f} para objetivo semanal")
    
    # Sueño
    if promedio_sueno_horas < SUENO_OBJETIVO_HORAS:
        deficit_sueno = SUENO_OBJETIVO_HORAS - promedio_sueno_horas
        recomendaciones.append(f"😴 Dormir {deficit_sueno:.1f}h más por noche")
    
    if not recomendaciones:
        recomendaciones.append("🎉 ¡Excelente! Mantén tu rutina actual")
    
    return recomendaciones