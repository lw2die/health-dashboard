#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cálculo de Healthspan Index
Score compuesto para medir años de vida saludable proyectados
"""

from config import (
    PESO_OBJETIVO, PAI_OBJETIVO_SEMANAL, 
    VO2MAX_EXCELENTE, VO2MAX_BUENO,
    SUENO_OBJETIVO_HORAS, FC_REPOSO, TSB_OPTIMO_MIN, TSB_OPTIMO_MAX
)


def calcular_healthspan_index(metricas):
    """
    Calcula Healthspan Index (0-100). TODAS LAS MÉTRICAS USAN VENTANAS DE 7 DÍAS
    
    Componentes:
    - Fitness Score (30%): PAI semanal, TSB promedio 7d, VO2max
    - Body Score (20%): Peso promedio 7d, grasa promedio 7d, músculo promedio 7d
    - Recovery Score (20%): Sueño promedio 7d, FC reposo promedio 7d, SpO2 promedio 7d
    - Metabolic Score (20%): Datos de laboratorio
    - Functional Score (10%): Pasos promedio 7d
    
    Args:
        metricas: Dict con todas las métricas calculadas
    
    Returns:
        dict: {
            "healthspan_index": int (0-100),
            "status": str,
            "fitness_score": int,
            "body_score": int,
            "recovery_score": int,
            "metabolic_score": int,
            "functional_score": int
        }
    """
    
    # Calcular sub-scores
    fitness_score = _calcular_fitness_score(metricas)
    body_score = _calcular_body_score(metricas)
    recovery_score = _calcular_recovery_score(metricas)
    metabolic_score = _calcular_metabolic_score(metricas)
    functional_score = _calcular_functional_score(metricas)
    
    # Healthspan Index = promedio ponderado
    healthspan_index = int(
        fitness_score * 0.30 +
        body_score * 0.20 +
        recovery_score * 0.20 +
        metabolic_score * 0.20 +
        functional_score * 0.10
    )
    
    # Determinar status
    if healthspan_index >= 85:
        status = "EXCELENTE"
    elif healthspan_index >= 70:
        status = "BUENO"
    elif healthspan_index >= 55:
        status = "ACEPTABLE"
    else:
        status = "NECESITA MEJORA"
    
    return {
        "healthspan_index": healthspan_index,
        "status": status,
        "fitness_score": fitness_score,
        "body_score": body_score,
        "recovery_score": recovery_score,
        "metabolic_score": metabolic_score,
        "functional_score": functional_score
    }


def _calcular_fitness_score(metricas):
    """
    Calcula Fitness Score (0-100).
    
    Componentes:
    - PAI semanal (40%)
    - TSB óptimo (30%)
    - VO2max (30%)
    """
    score = 0
    
    # PAI (40 puntos) - Objetivo realista: ≥100 en ventana móvil 7 días
    pai_semanal = metricas.get("pai_semanal", 0)
    if pai_semanal >= 100:
        score += 40  # Objetivo cumplido
    elif pai_semanal >= 75:
        score += 35  # Cerca del objetivo
    elif pai_semanal >= 50:
        score += 25  # Aceptable
    elif pai_semanal >= 25:
        score += 15  # Bajo pero activo
    else:
        score += 5   # Muy sedentario
    
    # TSB (30 puntos) - Óptimo: entre -10 y +10
    tsb_promedio = metricas.get("tsb_promedio_7d", 0)
    if -10 <= tsb_promedio <= 10:
        score += 30  # Óptimo - equilibrio perfecto
    elif tsb_promedio < -10:
        score += 30  # Entrenando duro = bueno, NO se penaliza
    elif 10 < tsb_promedio <= 20:
        score += 25  # Demasiado fresco
    elif 20 < tsb_promedio <= 30:
        score += 20  # Muy descansado (poco entrenamiento)
    else:
        score += 15  # Inactividad prolongada
    
    # VO2max (30 puntos) - Según Samsung Health para rango 50-59 años
    vo2max = metricas.get("vo2max")
    if vo2max is not None and vo2max > 0:
        if vo2max >= 47.6:
            score += 30  # Superior
        elif vo2max >= 38.3:
            score += 30  # Excelente (38.3-47.5)
        elif vo2max >= 31.8:
            score += 25  # Bueno (31.8-38.2)
        elif vo2max >= 26.9:
            score += 20  # Regular (26.9-31.7)
        elif vo2max >= 22.2:
            score += 15  # Malo (22.2-26.8)
        else:
            score += 10  # Muy malo (<22.2)
    else:
        score += 15  # Puntaje base si no hay datos
    
    return min(100, score)


def _calcular_body_score(metricas):
    """
    Calcula Body Score (0-100).
    
    Componentes:
    - Peso vs objetivo (35%)
    - % Grasa corporal (35%)
    - Masa muscular (30%)
    """
    score = 0
    
    # Peso (35 puntos)
    peso_actual = metricas.get("peso_actual")
    if peso_actual is not None and peso_actual > 0:
        diferencia = abs(peso_actual - PESO_OBJETIVO)
        if diferencia <= 2:
            score += 35
        elif diferencia <= 5:
            score += 28
        elif diferencia <= 10:
            score += 20
        else:
            score += 10
    else:
        score += 15  # Puntaje base
    
    # Grasa corporal (35 puntos)
    grasa = metricas.get("grasa_actual")
    if grasa is not None:
        if grasa < 15:
            score += 35
        elif grasa < 20:
            score += 28
        elif grasa < 25:
            score += 20
        else:
            score += 10
    else:
        score += 15  # Puntaje base
    
    # Masa muscular (30 puntos)
    masa_muscular = metricas.get("masa_muscular_actual")
    if masa_muscular is not None:
        # Asumiendo que >50kg es bueno para hombre adulto
        if masa_muscular >= 55:
            score += 30
        elif masa_muscular >= 50:
            score += 25
        elif masa_muscular >= 45:
            score += 20
        else:
            score += 15
    else:
        score += 15  # Puntaje base
    
    return min(100, score)


def _calcular_recovery_score(metricas):
    """
    Calcula Recovery Score (0-100).
    
    Componentes:
    - Sueño promedio (40%)
    - FC reposo (35%)
    - SpO2 (25%)
    """
    score = 0
    
    # Sueño (40 puntos)
    sueno = metricas.get("promedio_sueno")
    if sueno is not None and sueno > 0:
        if sueno >= SUENO_OBJETIVO_HORAS:
            score += 40
        elif sueno >= SUENO_OBJETIVO_HORAS - 1:
            score += 32
        elif sueno >= SUENO_OBJETIVO_HORAS - 2:
            score += 24
        else:
            score += 15
    else:
        score += 20  # Puntaje base
    
    # FC reposo (35 puntos)
    fc_reposo = metricas.get("fc_reposo_promedio")
    if fc_reposo is not None:
        if fc_reposo < 55:
            score += 35
        elif fc_reposo < 65:
            score += 30
        elif fc_reposo < 75:
            score += 22
        else:
            score += 15
    else:
        score += 20  # Puntaje base
    
    # SpO2 (25 puntos)
    spo2 = metricas.get("spo2_promedio")
    if spo2 is not None:
        if spo2 >= 96:
            score += 25
        elif spo2 >= 94:
            score += 20
        elif spo2 >= 90:
            score += 15
        else:
            score += 10
    else:
        score += 15  # Puntaje base
    
    return min(100, score)


def _calcular_metabolic_score(metricas):
    """
    Calcula Metabolic Score (0-100).
    
    Usa datos de laboratorio si están disponibles.
    Si no hay datos de laboratorio, usa datos básicos disponibles.
    """
    # TODO: Cuando implementes integración con laboratorio, usar esos datos
    # Por ahora, usar un score base de 75 (neutral/bueno)
    
    # Podrías usar presión arterial y glucosa si están disponibles
    score = 75  # Score base neutro
    
    presion_sistolica = metricas.get("presion_sistolica")
    if presion_sistolica is not None:
        if presion_sistolica < 120:
            score = min(100, score + 10)
        elif presion_sistolica < 130:
            score = min(100, score + 5)
        elif presion_sistolica >= 140:
            score = max(0, score - 15)
    
    return min(100, score)


def _calcular_functional_score(metricas):
    """
    Calcula Functional Score (0-100).
    
    Componentes:
    - Pasos diarios promedio (100%)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    score = 0
    
    # Pasos (100 puntos) - Objetivo realista: ≥10,000 pasos/día promedio
    pasos = metricas.get("pasos_promedio")
    
    logger.info(f"🔍 FUNCTIONAL SCORE - Pasos recibidos: {pasos}")
    
    if pasos is not None:
        if pasos >= 10000:
            score = 100  # Objetivo cumplido (60k/semana con 1 día descanso)
        elif pasos >= 8000:
            score = 85   # Muy cerca
        elif pasos >= 6000:
            score = 70   # Aceptable
        elif pasos >= 4000:
            score = 50   # Bajo
        else:
            score = 30   # Sedentario
        
        logger.info(f"✅ Functional Score calculado: {score}/100 (para {pasos:,.0f} pasos/día)")
    else:
        score = 50  # Puntaje base
        logger.warning("⚠️ No hay datos de pasos - usando score base: 50")
    
    return min(100, score)


def generar_recomendaciones_healthspan(healthspan_data, metricas):
    """
    Genera recomendaciones personalizadas basadas en Healthspan Index.
    
    Returns:
        list: Lista de tuplas (prioridad, recomendación)
              prioridad = "alta", "media", "baja"
    """
    recomendaciones = []
    
    # Analizar cada sub-score
    fitness_score = healthspan_data["fitness_score"]
    body_score = healthspan_data["body_score"]
    recovery_score = healthspan_data["recovery_score"]
    functional_score = healthspan_data["functional_score"]
    
    # PRIORIDAD ALTA: Score <70
    if fitness_score < 70:
        pai_semanal = metricas.get("pai_semanal", 0)
        if pai_semanal < PAI_OBJETIVO_SEMANAL:
            deficit = PAI_OBJETIVO_SEMANAL - pai_semanal
            recomendaciones.append(("alta", f"💪 Aumentar actividad cardiovascular: Te faltan {deficit:.0f} puntos PAI para la meta semanal. Considera agregar 20-30 min de ejercicio moderado."))
    
    if body_score < 70:
        grasa = metricas.get("grasa_actual")
        if grasa is not None and grasa > 20:
            recomendaciones.append(("alta", f"🎯 Reducir grasa corporal: Tu grasa está en {grasa:.1f}%. Meta: <20%. Considera déficit calórico moderado (300-500 kcal/día) y entrenamiento de fuerza."))
    
    if recovery_score < 70:
        sueno = metricas.get("promedio_sueno")
        if sueno is not None and sueno < SUENO_OBJETIVO_HORAS:
            deficit = SUENO_OBJETIVO_HORAS - sueno
            recomendaciones.append(("alta", f"😴 Priorizar sueño: Promedio actual {sueno:.1f}h. Objetivo: {SUENO_OBJETIVO_HORAS}h. Intenta dormir {deficit:.1f}h más por noche."))
    
    # PRIORIDAD MEDIA: Score 70-85
    if 70 <= fitness_score < 85:
        recomendaciones.append(("media", "⚡ Optimizar entrenamiento: Buen nivel de fitness. Considera agregar entrenamiento de alta intensidad 1-2 veces por semana para mejorar VO2max."))
    
    if 70 <= body_score < 85:
        recomendaciones.append(("media", "🏋️ Mantener composición corporal: Cerca del objetivo. Continúa con entrenamiento de fuerza 2-3 veces por semana."))
    
    # PRIORIDAD BAJA: Score >=85 (mantener)
    if fitness_score >= 85:
        recomendaciones.append(("baja", "✅ Fitness excelente: Mantén tu rutina actual de entrenamiento."))
    
    if body_score >= 85:
        recomendaciones.append(("baja", "✅ Composición corporal óptima: Continúa con tus hábitos actuales."))
    
    if recovery_score >= 85:
        recomendaciones.append(("baja", "✅ Recuperación excelente: Tu sueño y descanso son óptimos."))
    
    # Si no hay recomendaciones, agregar una positiva
    if not recomendaciones:
        recomendaciones.append(("baja", "🎉 ¡Excelente trabajo! Tu Healthspan Index es óptimo. Mantén tus hábitos actuales."))
    
    return recomendaciones