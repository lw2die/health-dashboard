#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extractor de métricas de actividad física
Distancia recorrida y calorías totales quemadas
"""

from datetime import datetime
from utils.logger import logger
from core.utils_procesador import reportar_por_fuente


def procesar_distancia(datos, cache, nombre_archivo):
    """
    Extrae datos de distancia recorrida del JSON.
    Soporta formatos FULL (distance_records) y DIFF (distance_changes).
    Agrupa por día automáticamente.
    """
    distancia_data = None
    
    if "distance_records" in datos and "data" in datos["distance_records"]:
        distancia_data = datos["distance_records"]["data"]
    elif "distance_changes" in datos and "data" in datos["distance_changes"]:
        distancia_data = datos["distance_changes"]["data"]
    
    if not distancia_data:
        return False
    
    count_antes = len(cache.get("distancia", []))
    
    # Agrupar por día para evitar múltiples registros
    por_dia = {}
    
    for d in distancia_data:
        try:
            start_time = datetime.fromisoformat(d.get("start_time", "").replace("Z", "+00:00"))
            dia = start_time.strftime("%Y-%m-%d")
            
            if dia not in por_dia:
                por_dia[dia] = {
                    "fecha": d.get("start_time"),
                    "distancia_total": 0,
                    "fuente": d.get("source", "Desconocido")
                }
            
            # Sumar distancia en metros y convertir a km
            distancia_m = d.get("distance_meters", 0)
            por_dia[dia]["distancia_total"] += distancia_m / 1000  # Convertir a km
        
        except Exception as ex:
            logger.warning(f"Error procesando distancia: {ex}")
    
    # Agregar al cache
    for dia_data in por_dia.values():
        cache["distancia"].append({
            "fecha": dia_data["fecha"],
            "distancia_km": round(dia_data["distancia_total"], 2),
            "fuente": dia_data["fuente"]
        })
    
    agregados = len(cache['distancia']) - count_antes
    if agregados > 0:
        logger.info(f"  → Distancia agregada: {agregados} días")
        reportar_por_fuente(cache['distancia'][-agregados:], "Distancia", "distancia_km")
        return True
    
    return False


def procesar_calorias_totales(datos, cache, nombre_archivo):
    """
    Extrae datos de calorías totales del JSON.
    Soporta formatos FULL (total_calories_records) y DIFF (total_calories_changes).
    Agrupa por día automáticamente.
    """
    calorias_data = None
    
    if "total_calories_records" in datos and "data" in datos["total_calories_records"]:
        calorias_data = datos["total_calories_records"]["data"]
    elif "total_calories_changes" in datos and "data" in datos["total_calories_changes"]:
        calorias_data = datos["total_calories_changes"]["data"]
    
    if not calorias_data:
        return False
    
    count_antes = len(cache.get("calorias_totales", []))
    
    # Agrupar por día para evitar múltiples registros
    por_dia = {}
    
    for c in calorias_data:
        try:
            start_time = datetime.fromisoformat(c.get("start_time", "").replace("Z", "+00:00"))
            dia = start_time.strftime("%Y-%m-%d")
            
            if dia not in por_dia:
                por_dia[dia] = {
                    "fecha": c.get("start_time"),
                    "energia_total": 0,
                    "fuente": c.get("source", "Desconocido")
                }
            
            # Sumar calorías
            energia_kcal = c.get("energy_kcal", 0)
            por_dia[dia]["energia_total"] += energia_kcal
        
        except Exception as ex:
            logger.warning(f"Error procesando calorías: {ex}")
    
    # Agregar al cache
    for dia_data in por_dia.values():
        cache["calorias_totales"].append({
            "fecha": dia_data["fecha"],
            "energia_kcal": round(dia_data["energia_total"], 0),
            "fuente": dia_data["fuente"]
        })
    
    agregados = len(cache['calorias_totales']) - count_antes
    if agregados > 0:
        logger.info(f"  → Calorías totales agregadas: {agregados} días")
        reportar_por_fuente(cache['calorias_totales'][-agregados:], "Calorías Totales", "energia_kcal")
        return True
    
    return False