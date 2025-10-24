#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extractor de pasos y saturación de oxígeno
"""

from datetime import datetime
from utils.logger import logger
from core.utils_procesador import reportar_por_fuente


def procesar_pasos(datos, cache, nombre_archivo):
    """
    Extrae datos de pasos del JSON.
    Soporta formatos FULL (steps_records) y DIFF (steps_changes).
    Agrupa por día automáticamente.
    """
    pasos_data = None
    
    if "steps_records" in datos and "data" in datos["steps_records"]:
        pasos_data = datos["steps_records"]["data"]
    elif "steps_changes" in datos and "data" in datos["steps_changes"]:
        pasos_data = datos["steps_changes"]["data"]
    
    if not pasos_data:
        return False
    
    count_antes = len(cache.get("pasos", []))
    
    # Agrupar por día + fuente
    por_dia_fuente = {}
    
    for p in pasos_data:
        try:
            fecha = datetime.fromisoformat(p.get("start_time", "").replace("Z", "+00:00"))
            dia = fecha.strftime("%Y-%m-%d")
            fuente = p.get("source", "Desconocido")
            
            clave = f"{dia}|{fuente}"
            
            if clave not in por_dia_fuente:
                por_dia_fuente[clave] = {
                    "fecha": p.get("start_time"),
                    "pasos": 0,
                    "fuente": fuente
                }
            
            por_dia_fuente[clave]["pasos"] += p.get("count", 0)
        
        except Exception as ex:
            logger.warning(f"Error procesando pasos: {ex}")
    
    # Agregar al cache
    for registro in por_dia_fuente.values():
        cache["pasos"].append(registro)
    
    agregados = len(cache["pasos"]) - count_antes
    if agregados > 0:
        logger.info(f"  → Pasos agregados: {agregados}")
        reportar_por_fuente(cache["pasos"][-agregados:], "Pasos", "pasos")
        return True
    
    return False


def procesar_saturacion_oxigeno(datos, cache, nombre_archivo):
    """
    Extrae datos de saturación de oxígeno (SpO2) del JSON.
    Soporta formatos FULL (oxygen_saturation_records) y DIFF (oxygen_saturation_changes).
    """
    spo2_data = None
    
    if "oxygen_saturation_records" in datos and "data" in datos["oxygen_saturation_records"]:
        spo2_data = datos["oxygen_saturation_records"]["data"]
    elif "oxygen_saturation_changes" in datos and "data" in datos["oxygen_saturation_changes"]:
        spo2_data = datos["oxygen_saturation_changes"]["data"]
    
    if not spo2_data:
        return False
    
    count_antes = len(cache.get("spo2", []))
    
    for s in spo2_data:
        cache["spo2"].append({
            "fecha": s.get("timestamp"),
            "porcentaje": s.get("percentage", 0),
            "fuente": s.get("source", "Desconocido")
        })
    
    agregados = len(cache['spo2']) - count_antes
    if agregados > 0:
        logger.info(f"  → SpO2 agregado: {agregados}")
        reportar_por_fuente(cache['spo2'][-agregados:], "SpO2", "porcentaje")
        return True
    
    return False