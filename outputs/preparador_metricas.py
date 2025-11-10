#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preparador de Métricas - Cálculo de todas las métricas del dashboard
Centraliza el cálculo de PAI, TSB, VO2max, sueño, SpO2, etc.
"""

from datetime import datetime, timedelta
from collections import defaultdict
from utils.logger import logger
from metricas.pai import calcular_pai_semanal
from metricas.fitness import calcular_tsb
from metricas.score import calcular_score_longevidad, generar_recomendaciones
from metricas.healthspan import calcular_healthspan_index


def calcular_metricas(ejercicios, peso, sueno, spo2, grasa_corporal, 
                     masa_muscular, vo2max_medido, fc_reposo, pasos, 
                     presion_arterial, nutrition, tasa_metabolica, calorias_totales):
    """
    Calcula todas las métricas del dashboard.
    
    Returns:
        dict: Diccionario con todas las métricas calculadas
    """
    
    # PAI semanal
    pai_semanal = calcular_pai_semanal(ejercicios)
    
    # Peso actual
    peso_actual = peso[-1]["peso"] if peso else None
    
    # VO2max MEDIDO
    vo2max = vo2max_medido[-1]["vo2max"] if vo2max_medido else None
    
    # TSB actual
    tsb_dict = calcular_tsb(ejercicios) if ejercicios else {"tsb": 0, "ctl": 0, "atl": 0}
    tsb_actual = tsb_dict.get("tsb", 0) if isinstance(tsb_dict, dict) else tsb_dict
    
    # SUEÑO - Agrupar por DÍA primero
    promedio_sueno_horas = None
    if sueno:
        sueno_por_dia = defaultdict(float)
        for s in sueno:
            try:
                fecha = datetime.fromisoformat(s["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
                sueno_por_dia[fecha] += s.get("duracion", 0)
            except:
                continue
        
        fechas_ordenadas = sorted(sueno_por_dia.keys())[-7:]
        if fechas_ordenadas:
            total_minutos = sum(sueno_por_dia[f] for f in fechas_ordenadas)
            promedio_sueno_horas = (total_minutos / len(fechas_ordenadas)) / 60
    
    # SpO2 promedio
    spo2_promedio = None
    if spo2:
        spo2_recientes = spo2[-7:] if len(spo2) >= 7 else spo2
        spo2_promedio = sum(s.get("porcentaje", 0) for s in spo2_recientes) / len(spo2_recientes)
    
    # Grasa corporal actual
    grasa_actual = grasa_corporal[-1]["porcentaje"] if grasa_corporal else None
    
    # Masa muscular actual
    masa_muscular_actual = masa_muscular[-1]["masa_kg"] if masa_muscular else None
    logger.info(f"🔍 DEBUG Masa Muscular: masa_muscular_actual = {masa_muscular_actual}")
    if masa_muscular:
        logger.info(f"   Último registro: {masa_muscular[-1]}")
    else:
        logger.warning("   ⚠️ No hay datos de masa muscular en cache")
    
    # FC en reposo promedio
    fc_reposo_promedio = None
    if fc_reposo:
        fc_recientes = fc_reposo[-7:] if len(fc_reposo) >= 7 else fc_reposo
        fc_reposo_promedio = sum(fc.get("bpm", 0) for fc in fc_recientes) / len(fc_recientes)
    
    # PASOS - Tomar MÁXIMO por día (Samsung guarda valores acumulados)
    pasos_promedio = None
    if pasos:
        logger.info(f"🚶 DEBUG Pasos: Total registros en cache: {len(pasos)}")
        
        pasos_por_dia = defaultdict(list)
        for p in pasos:
            try:
                fecha = datetime.fromisoformat(p["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
                pasos_por_dia[fecha].append(p.get("pasos", 0))
            except:
                continue
        
        fechas_ordenadas = sorted(pasos_por_dia.keys())[-7:]
        if fechas_ordenadas:
            logger.info("📊 Pasos por día (últimos 7 DÍAS - MÁXIMO del día):")
            total_pasos = 0
            for f in fechas_ordenadas:
                pasos_dia = max(pasos_por_dia[f])
                total_pasos += pasos_dia
                logger.info(f"   - {f}: {pasos_dia:,} pasos (de {len(pasos_por_dia[f])} registros)")
            
            pasos_promedio = total_pasos / len(fechas_ordenadas)
            logger.info(f"📈 Pasos promedio calculado: {pasos_promedio:,.0f} pasos/día (últimos {len(fechas_ordenadas)} días)")
        else:
            logger.warning("⚠️ No se pudieron agrupar pasos por día")
    else:
        logger.warning("⚠️ NO hay datos de pasos en el cache")
    
    # Presión arterial promedio
    presion_sistolica = None
    presion_diastolica = None
    if presion_arterial:
        presion_recientes = presion_arterial[-7:] if len(presion_arterial) >= 7 else presion_arterial
        presion_sistolica = sum(p.get("sistolica", 0) for p in presion_recientes) / len(presion_recientes)
        presion_diastolica = sum(p.get("diastolica", 0) for p in presion_recientes) / len(presion_recientes)
    
    # PROMEDIOS DE 7 DÍAS para Healthspan Index (largo plazo)
    peso_promedio_7d = None
    if peso:
        peso_recientes = peso[-7:] if len(peso) >= 7 else peso
        peso_promedio_7d = sum(p.get("peso", 0) for p in peso_recientes) / len(peso_recientes)
    
    grasa_promedio_7d = None
    if grasa_corporal:
        grasa_recientes = grasa_corporal[-7:] if len(grasa_corporal) >= 7 else grasa_corporal
        grasa_promedio_7d = sum(g.get("porcentaje", 0) for g in grasa_recientes) / len(grasa_recientes)
    
    masa_muscular_promedio_7d = None
    if masa_muscular:
        masa_recientes = masa_muscular[-7:] if len(masa_muscular) >= 7 else masa_muscular
        masa_muscular_promedio_7d = sum(m.get("masa_kg", 0) for m in masa_recientes) / len(masa_recientes)
    
    tsb_promedio_7d = tsb_actual
    
    # Score de longevidad
    score_longevidad = calcular_score_longevidad(
        peso_actual, pai_semanal, vo2max, promedio_sueno_horas
    )
    
    # Recomendaciones
    recomendaciones = generar_recomendaciones(
        peso_actual, pai_semanal, promedio_sueno_horas
    )
    
    # HEALTHSPAN INDEX - Usa promedios de 7 días (largo plazo)
    metricas_base = {
        "pai_semanal": pai_semanal,
        "peso_promedio_7d": peso_promedio_7d,
        "vo2max": vo2max,
        "tsb_promedio_7d": tsb_promedio_7d,
        "promedio_sueno": promedio_sueno_horas,
        "spo2_promedio": spo2_promedio,
        "grasa_promedio_7d": grasa_promedio_7d,
        "masa_muscular_promedio_7d": masa_muscular_promedio_7d,
        "fc_reposo_promedio": fc_reposo_promedio,
        "pasos_promedio": pasos_promedio,
        "presion_sistolica": presion_sistolica,
        "presion_diastolica": presion_diastolica,
    }
    
    healthspan_data = calcular_healthspan_index(metricas_base)
    
    return {
        **metricas_base,
        # Valores actuales para cards individuales
        "peso_actual": peso_actual,
        "grasa_actual": grasa_actual,
        "masa_muscular_actual": masa_muscular_actual,
        "tsb_actual": tsb_actual,
        # Otros datos
        "tsb_dict": tsb_dict,
        "score_longevidad": score_longevidad,
        "recomendaciones": recomendaciones,
        "healthspan_data": healthspan_data
    }
