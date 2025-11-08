#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extractor de datos de ejercicio - VERSIÓN CON SESSION_ID Y RECORD_ID
Procesa exercise_sessions y exercise_changes
✅ AGREGA session_id, record_id, start_time, end_time
"""

from utils.logger import logger
from core.utils_procesador import (
    calcular_pai, calcular_hrtss, clasificar_zona_fc, 
    reportar_ejercicios_por_tipo, traducir_tipo_ejercicio
)


def procesar_ejercicios(datos, cache, nombre_archivo):
    """
    Extrae datos de ejercicio del JSON.
    Soporta formatos FULL (exercise_sessions) y DIFF (exercise_changes).
    ✅ CON SESSION_ID, RECORD_ID, START_TIME, END_TIME
    """
    ejercicios_data = None
    
    # Formato FULL
    if "exercise_sessions" in datos and "data" in datos["exercise_sessions"]:
        ejercicios_data = datos["exercise_sessions"]["data"]
    # Formato DIFF
    elif "exercise_changes" in datos and "data" in datos["exercise_changes"]:
        ejercicios_data = datos["exercise_changes"]["data"]
    
    if not ejercicios_data:
        return False
    
    count_antes = len(cache["ejercicio"])
    
    for e in ejercicios_data:
        # Obtener session_id (puede venir como session_id o como id en el JSON)
        session_id = e.get("session_id") or e.get("id")
        
        entrada = {
            "session_id": session_id,                                                    # ✅ NUEVO
            "record_id": session_id,                                                     # ✅ NUEVO (mismo que session_id)
            "start_time": e.get("start_time"),                                           # ✅ NUEVO
            "end_time": e.get("end_time"),                                               # ✅ NUEVO
            "fecha": e.get("start_time"),                                                # mantener por compatibilidad
            "tipo": e.get("exercise_type_name") or traducir_tipo_ejercicio(e.get("exercise_type")),
            "duracion": e.get("duration_minutes", 0),
            "calorias": e.get("calories_burned", 0),
            "distancia": e.get("distance_meters", 0),
            "fc_promedio": e.get("avg_heart_rate"),
            "fc_max": e.get("max_heart_rate", 0),
            "pasos": e.get("total_steps", 0),
            "fuente": e.get("source", "Desconocido")
        }
        
        # Log si FC es None o 0
        if entrada["fc_promedio"] is None or entrada["fc_promedio"] == 0:
            logger.warning(
                f"⚠️ FC NULA/CERO en [{nombre_archivo}] - "
                f"Tipo: {entrada['tipo']}, Duración: {entrada['duracion']} min"
            )
        
        # Calcular PAI (para métrica de salud cardiovascular)
        entrada["pai"] = calcular_pai(entrada["fc_promedio"], entrada["duracion"])
        
        # Calcular hrTSS (para métrica de carga de entrenamiento / TSB)
        entrada["hrtss"] = calcular_hrtss(entrada["fc_promedio"], entrada["duracion"])
        
        # Clasificar zona FC
        entrada["zona"] = clasificar_zona_fc(entrada["fc_promedio"])
        
        cache["ejercicio"].append(entrada)
    
    agregados = len(cache['ejercicio']) - count_antes
    if agregados > 0:
        logger.info(f"  → Ejercicios agregados: {agregados}")
        reportar_ejercicios_por_tipo(cache['ejercicio'][-agregados:])
    
    return agregados > 0