#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extractor de métricas biométricas - VERSIÓN CORREGIDA
Peso, grasa corporal, masa muscular, masa agua, masa ósea
CON VALIDACIÓN DE PESO (rechaza valores absurdos >200kg o <30kg)
"""

from utils.logger import logger
from core.utils_procesador import reportar_por_fuente


def procesar_peso(datos, cache):
    """Extrae datos de peso del JSON CON VALIDACIÓN y DEDUPLICACIÓN POR DÍA"""
    from datetime import datetime
    
    peso_data = None
    
    if "weight_records" in datos and "data" in datos["weight_records"]:
        peso_data = datos["weight_records"]["data"]
    elif "weight_changes" in datos and "data" in datos["weight_changes"]:
        peso_data = datos["weight_changes"]["data"]
    
    if not peso_data:
        return False
    
    count_antes = len(cache["peso"])
    rechazados = 0
    
    # ✅ Agrupar por DÍA y promediar ANTES de agregar al cache
    por_dia = {}
    
    for p in peso_data:
        peso_kg = p.get("weight_kg", 0)
        timestamp = p.get("timestamp")
        
        # ✅ VALIDACIÓN: Rechazar pesos absurdos
        if peso_kg < 30 or peso_kg > 200:
            logger.warning(f"⚠️ Peso RECHAZADO (fuera de rango 30-200kg): {peso_kg:.1f} kg")
            rechazados += 1
            continue
        
        # Agrupar por día
        try:
            dia = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).strftime("%Y-%m-%d")
            if dia not in por_dia:
                por_dia[dia] = {"pesos": [], "timestamp_primero": timestamp}
            por_dia[dia]["pesos"].append(peso_kg)
        except Exception as ex:
            logger.warning(f"Error procesando fecha peso: {ex}")
            rechazados += 1
    
    # ✅ DEDUPLICAR con días ya existentes en cache
    dias_existentes = {
        datetime.fromisoformat(p["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        for p in cache["peso"]
    }
    
    # Agregar solo 1 registro por día (promedio)
    for dia, data in por_dia.items():
        if dia in dias_existentes:
            rechazados += len(data["pesos"])
            continue
        
        peso_promedio = sum(data["pesos"]) / len(data["pesos"])
        cache["peso"].append({
            "fecha": data["timestamp_primero"],
            "peso": peso_promedio
        })
    
    agregados = len(cache['peso']) - count_antes
    if agregados > 0:
        logger.info(f"  → Pesos agregados: {agregados} días (rechazados: {rechazados})")
    return agregados > 0


def procesar_grasa_corporal(datos, cache, nombre_archivo):
    """Extrae datos de grasa corporal % del JSON"""
    grasa_data = None
    
    if "body_fat_records" in datos and "data" in datos["body_fat_records"]:
        grasa_data = datos["body_fat_records"]["data"]
    elif "body_fat_changes" in datos and "data" in datos["body_fat_changes"]:
        grasa_data = datos["body_fat_changes"]["data"]
    
    if not grasa_data:
        return False
    
    count_antes = len(cache.get("grasa_corporal", []))
    
    for g in grasa_data:
        cache["grasa_corporal"].append({
            "fecha": g.get("timestamp"),
            "porcentaje": g.get("percentage", 0),
            "fuente": g.get("source", "Desconocido")
        })
    
    agregados = len(cache['grasa_corporal']) - count_antes
    logger.info(f"  → Grasa corporal agregada: {agregados}")
    if agregados > 0:
        reportar_por_fuente(cache['grasa_corporal'][-agregados:], "Grasa Corporal")
    return True


def procesar_masa_muscular(datos, cache, nombre_archivo):
    """Extrae datos de masa muscular (lean body mass) del JSON"""
    masa_data = None
    
    if "lean_body_mass_records" in datos and "data" in datos["lean_body_mass_records"]:
        masa_data = datos["lean_body_mass_records"]["data"]
    elif "lean_body_mass_changes" in datos and "data" in datos["lean_body_mass_changes"]:
        masa_data = datos["lean_body_mass_changes"]["data"]
    
    if not masa_data:
        return False
    
    count_antes = len(cache.get("masa_muscular", []))
    
    for m in masa_data:
        cache["masa_muscular"].append({
            "fecha": m.get("timestamp"),
            "masa_kg": m.get("mass_kg", 0),
            "fuente": m.get("source", "Desconocido")
        })
    
    agregados = len(cache['masa_muscular']) - count_antes
    logger.info(f"  → Masa muscular agregada: {agregados}")
    if agregados > 0:
        reportar_por_fuente(cache['masa_muscular'][-agregados:], "Masa Muscular", "masa_kg")
    return True


def procesar_masa_agua(datos, cache, nombre_archivo):
    """Extrae datos de masa de agua corporal del JSON"""
    agua_data = None
    
    if "body_water_mass_records" in datos and "data" in datos["body_water_mass_records"]:
        agua_data = datos["body_water_mass_records"]["data"]
    elif "body_water_mass_changes" in datos and "data" in datos["body_water_mass_changes"]:
        agua_data = datos["body_water_mass_changes"]["data"]
    
    if not agua_data:
        return False
    
    count_antes = len(cache.get("masa_agua", []))
    
    for a in agua_data:
        cache["masa_agua"].append({
            "fecha": a.get("timestamp"),
            "masa_kg": a.get("mass_kg", 0),
            "fuente": a.get("source", "Desconocido")
        })
    
    agregados = len(cache['masa_agua']) - count_antes
    logger.info(f"  → Masa de agua agregada: {agregados}")
    if agregados > 0:
        reportar_por_fuente(cache['masa_agua'][-agregados:], "Masa de Agua", "masa_kg")
    return True


def procesar_masa_osea(datos, cache, nombre_archivo):
    """Extrae datos de masa ósea del JSON"""
    hueso_data = None
    
    if "bone_mass_records" in datos and "data" in datos["bone_mass_records"]:
        hueso_data = datos["bone_mass_records"]["data"]
    elif "bone_mass_changes" in datos and "data" in datos["bone_mass_changes"]:
        hueso_data = datos["bone_mass_changes"]["data"]
    
    if not hueso_data:
        return False
    
    count_antes = len(cache.get("masa_osea", []))
    
    for h in hueso_data:
        cache["masa_osea"].append({
            "fecha": h.get("timestamp"),
            "masa_kg": h.get("mass_kg", 0),
            "fuente": h.get("source", "Desconocido")
        })
    
    agregados = len(cache['masa_osea']) - count_antes
    logger.info(f"  → Masa ósea agregada: {agregados}")
    if agregados > 0:
        reportar_por_fuente(cache['masa_osea'][-agregados:], "Masa Ósea", "masa_kg")
    return True