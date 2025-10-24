#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extractor de datos de ejercicio
Procesa exercise_sessions y exercise_changes
"""

from utils.logger import logger
from core.utils_procesador import (
    calcular_pai, clasificar_zona_fc, reportar_ejercicios_por_tipo,
    traducir_tipo_ejercicio
)


def procesar_ejercicios(datos, cache, nombre_archivo):
    """
    Extrae datos de ejercicio del JSON.
    Soporta formatos FULL (exercise_sessions) y DIFF (exercise_changes).
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
        entrada = {
            "fecha": e.get("start_time"),
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
        
        # Calcular PAI y zona FC
        entrada["pai"] = calcular_pai(entrada["fc_promedio"], entrada["duracion"])
        entrada["zona"] = clasificar_zona_fc(entrada["fc_promedio"])
        
        cache["ejercicio"].append(entrada)
    
    agregados = len(cache['ejercicio']) - count_antes
    logger.info(f"  → Ejercicios agregados: {agregados}")
    if agregados > 0:
        reportar_ejercicios_por_tipo(cache['ejercicio'][-agregados:])
    
    return True