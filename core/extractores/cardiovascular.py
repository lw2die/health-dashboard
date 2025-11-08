#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extractor de métricas cardiovasculares - VERSIÓN CON RECORD_ID
FC reposo desde heart_rate_changes (horario nocturno), presión, VO2max, FC continua
✅ AGREGA record_id a cada registro
"""

from datetime import datetime
from utils.logger import logger
from core.utils_procesador import reportar_por_fuente


def procesar_fc_reposo(datos, cache, nombre_archivo):
    """
    Extrae FC en REPOSO desde heart_rate_changes en horario nocturno (22:00-06:00)
    Ya NO usa resting_heart_rate_records/changes
    ✅ CON RECORD_ID
    """
    fc_data = None
    
    # Buscar en heart_rate_changes
    if "heart_rate_changes" in datos and "data" in datos["heart_rate_changes"]:
        fc_data = datos["heart_rate_changes"]["data"]
    elif "heart_rate_records" in datos and "data" in datos["heart_rate_records"]:
        fc_data = datos["heart_rate_records"]["data"]
    
    if not fc_data:
        return False
    
    count_antes = len(cache.get("fc_reposo", []))
    
    # ✅ Filtrar solo horario nocturno (22:00 - 06:00) para FC reposo
    for fc in fc_data:
        try:
            start_time = datetime.fromisoformat(fc.get("start_time", "").replace("Z", "+00:00"))
            hora = start_time.hour
            
            # Solo horario nocturno
            if hora >= 22 or hora < 6:
                # Usar min_bpm si está disponible, sino avg_bpm
                bpm_reposo = fc.get("min_bpm", fc.get("avg_bpm", 0))
                
                cache["fc_reposo"].append({
                    "record_id": fc.get("record_id"),        # ✅ NUEVO
                    "timestamp": fc.get("start_time"),       # ✅ NUEVO
                    "fecha": fc.get("start_time"),           # mantener por compatibilidad
                    "bpm": bpm_reposo,
                    "fuente": fc.get("source", "Desconocido")
                })
        except Exception as ex:
            logger.warning(f"Error procesando FC reposo: {ex}")
    
    agregados = len(cache['fc_reposo']) - count_antes
    if agregados > 0:
        logger.info(f"  → FC en reposo agregada: {agregados} (desde heart_rate horario nocturno)")
        reportar_por_fuente(cache['fc_reposo'][-agregados:], "FC Reposo", "bpm")
        return True
    
    return False


def procesar_presion_arterial(datos, cache, nombre_archivo):
    """Extrae datos de presión arterial del JSON con RECORD_ID"""
    presion_data = None
    
    if "blood_pressure_records" in datos and "data" in datos["blood_pressure_records"]:
        presion_data = datos["blood_pressure_records"]["data"]
    elif "blood_pressure_changes" in datos and "data" in datos["blood_pressure_changes"]:
        presion_data = datos["blood_pressure_changes"]["data"]
    
    if not presion_data:
        return False
    
    count_antes = len(cache.get("presion_arterial", []))
    
    for p in presion_data:
        cache["presion_arterial"].append({
            "record_id": p.get("record_id"),         # ✅ NUEVO
            "timestamp": p.get("timestamp"),         # ✅ NUEVO
            "fecha": p.get("timestamp"),             # mantener por compatibilidad
            "sistolica": p.get("systolic_mmhg", 0),
            "diastolica": p.get("diastolic_mmhg", 0),
            "fuente": p.get("source", "Desconocido")
        })
    
    agregados = len(cache['presion_arterial']) - count_antes
    if agregados > 0:
        logger.info(f"  → Presión arterial agregada: {agregados}")
        reportar_por_fuente(cache['presion_arterial'][-agregados:], "Presión Arterial")
    return agregados > 0


def procesar_vo2max(datos, cache, nombre_archivo):
    """Extrae datos de VO2max medido del JSON con RECORD_ID"""
    vo2_data = None
    
    if "vo2_max_records" in datos and "data" in datos["vo2_max_records"]:
        vo2_data = datos["vo2_max_records"]["data"]
    elif "vo2max_changes" in datos and "data" in datos["vo2max_changes"]:
        vo2_data = datos["vo2max_changes"]["data"]
    
    if not vo2_data:
        return False
    
    count_antes = len(cache.get("vo2max", []))
    
    for v in vo2_data:
        cache["vo2max"].append({
            "record_id": v.get("record_id"),                              # ✅ NUEVO
            "timestamp": v.get("timestamp"),                              # ✅ NUEVO
            "fecha": v.get("timestamp"),                                  # mantener por compatibilidad
            "vo2max": v.get("vo2_max_ml_per_min_per_kg") or v.get("vo2_max") or v.get("vo2max") or 0,
            "metodo": v.get("measurement_method", "Desconocido"),
            "fuente": v.get("source", "Desconocido")
        })
    
    agregados = len(cache['vo2max']) - count_antes
    if agregados > 0:
        logger.info(f"  → VO2max registros agregados: {agregados}")
        reportar_por_fuente(cache['vo2max'][-agregados:], "VO2max", "vo2max")
    return agregados > 0


def procesar_frecuencia_cardiaca(datos, cache, nombre_archivo):
    """
    Extrae datos de frecuencia cardíaca continua del JSON (agregada por día)
    Procesa TODOS los registros y los agrupa por día
    ✅ CON RECORD_ID (usa el primero del día)
    """
    fc_data = None
    
    if "heart_rate_records" in datos and "data" in datos["heart_rate_records"]:
        fc_data = datos["heart_rate_records"]["data"]
    elif "heart_rate_changes" in datos and "data" in datos["heart_rate_changes"]:
        fc_data = datos["heart_rate_changes"]["data"]
    
    if not fc_data:
        return False
    
    count_antes = len(cache.get("frecuencia_cardiaca", []))
    
    # Agrupar por día - TODOS los registros
    por_dia = {}
    
    for fc in fc_data:
        try:
            start_time = datetime.fromisoformat(fc.get("start_time", "").replace("Z", "+00:00"))
            dia = start_time.strftime("%Y-%m-%d")
            
            if dia not in por_dia:
                por_dia[dia] = {
                    "record_id": fc.get("record_id"),        # ✅ NUEVO - primer record_id del día
                    "timestamp": fc.get("start_time"),       # ✅ NUEVO
                    "fecha": fc.get("start_time"),
                    "bpm_min": 999,
                    "bpm_max": 0,
                    "bpm_suma": 0,
                    "count": 0,
                    "fuente": fc.get("source", "Desconocido")
                }
            
            # Usar avg_bpm, min_bpm, max_bpm si están disponibles
            bpm_avg = fc.get("avg_bpm", fc.get("bpm", 0))
            bpm_min = fc.get("min_bpm", bpm_avg)
            bpm_max = fc.get("max_bpm", bpm_avg)
            
            por_dia[dia]["bpm_min"] = min(por_dia[dia]["bpm_min"], bpm_min)
            por_dia[dia]["bpm_max"] = max(por_dia[dia]["bpm_max"], bpm_max)
            por_dia[dia]["bpm_suma"] += bpm_avg
            por_dia[dia]["count"] += 1
        
        except Exception as ex:
            logger.warning(f"Error procesando FC continua: {ex}")
    
    for dia_data in por_dia.values():
        cache["frecuencia_cardiaca"].append({
            "record_id": dia_data["record_id"],              # ✅ NUEVO
            "timestamp": dia_data["timestamp"],              # ✅ NUEVO
            "fecha": dia_data["fecha"],                      # mantener por compatibilidad
            "bpm_min": dia_data["bpm_min"],
            "bpm_max": dia_data["bpm_max"],
            "bpm_promedio": dia_data["bpm_suma"] / dia_data["count"] if dia_data["count"] > 0 else 0,
            "fuente": dia_data["fuente"]
        })
    
    agregados = len(cache['frecuencia_cardiaca']) - count_antes
    if agregados > 0:
        logger.info(f"  → Frecuencia cardíaca agregada: {agregados} días")
        reportar_por_fuente(cache['frecuencia_cardiaca'][-agregados:], "Frecuencia Cardíaca")
        return True
    
    return False