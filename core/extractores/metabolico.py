#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extractor de métricas metabólicas
Glucosa, tasa metabólica basal, calorías totales
"""

from utils.logger import logger
from core.utils_procesador import reportar_por_fuente


def procesar_glucosa(datos, cache, nombre_archivo):
    """
    Extrae datos de glucosa en sangre del JSON.
    CORREGIDO: Convierte mmol/L a mg/dL
    """
    glucosa_data = None
    
    if "blood_glucose_records" in datos and "data" in datos["blood_glucose_records"]:
        glucosa_data = datos["blood_glucose_records"]["data"]
    elif "blood_glucose_changes" in datos and "data" in datos["blood_glucose_changes"]:
        glucosa_data = datos["blood_glucose_changes"]["data"]
    
    if not glucosa_data:
        return False
    
    count_antes = len(cache.get("glucosa", []))
    
    for g in glucosa_data:
        # ✅ CORRECCIÓN: El valor viene en mmol/L
        mmol_l = g.get("glucose_mmol_per_l", 0)
        
        # Convertir mmol/L a mg/dL (multiplicar por 18)
        mg_dl = mmol_l * 18.0 if mmol_l else 0
        
        cache["glucosa"].append({
            "fecha": g.get("timestamp"),
            "nivel_mg_dl": round(mg_dl, 1),  # ✅ Valor convertido a mg/dL
            "tipo_muestra": g.get("specimen_source", "Desconocido"),
            "relacion_comida": g.get("meal_type", "Desconocido"),
            "fuente": g.get("source", "Desconocido")
        })
    
    agregados = len(cache['glucosa']) - count_antes
    if agregados > 0:
        logger.info(f"  → Glucosa agregada: {agregados}")
        reportar_por_fuente(cache['glucosa'][-agregados:], "Glucosa", "nivel_mg_dl")
        return True
    
    return False


def procesar_tasa_metabolica_basal(datos, cache, nombre_archivo):
    """
    Extrae datos de tasa metabólica basal (BMR) del JSON.
    CORREGIDO: Campo real es kcal_per_day
    """
    bmr_data = None
    
    if "basal_metabolic_rate_records" in datos and "data" in datos["basal_metabolic_rate_records"]:
        bmr_data = datos["basal_metabolic_rate_records"]["data"]
    elif "basal_metabolic_rate_changes" in datos and "data" in datos["basal_metabolic_rate_changes"]:
        bmr_data = datos["basal_metabolic_rate_changes"]["data"]
    
    if not bmr_data:
        return False
    
    count_antes = len(cache.get("tasa_metabolica", []))
    
    for bmr in bmr_data:
        # ✅ CORRECCIÓN: Campo real es kcal_per_day
        kcal = bmr.get("kcal_per_day", 0)
        
        cache["tasa_metabolica"].append({
            "fecha": bmr.get("timestamp"),
            "kcal_dia": round(kcal, 1),  # ✅ Valor real
            "fuente": bmr.get("source", "Desconocido")
        })
    
    agregados = len(cache['tasa_metabolica']) - count_antes
    if agregados > 0:
        logger.info(f"  → Tasa metabólica basal agregada: {agregados}")
        reportar_por_fuente(cache['tasa_metabolica'][-agregados:], "BMR", "kcal_dia")
        return True
    
    return False


def procesar_calorias_totales(datos, cache, nombre_archivo):
    """Extrae datos de calorías totales del JSON"""
    calorias_data = None
    
    if "total_calories_burned_records" in datos and "data" in datos["total_calories_burned_records"]:
        calorias_data = datos["total_calories_burned_records"]["data"]
    elif "total_calories_changes" in datos and "data" in datos["total_calories_changes"]:
        calorias_data = datos["total_calories_changes"]["data"]
    
    if not calorias_data:
        return False
    
    count_antes = len(cache.get("calorias_totales", []))
    
    for c in calorias_data:
        cache["calorias_totales"].append({
            "fecha": c.get("start_time"),
            "calorias": c.get("energy_kcal", 0),
            "fuente": c.get("source", "Desconocido")
        })
    
    agregados = len(cache['calorias_totales']) - count_antes
    if agregados > 0:
        logger.info(f"  → Calorías totales agregadas: {agregados}")
        reportar_por_fuente(cache['calorias_totales'][-agregados:], "Calorías Totales", "calorias")
        return True
    
    return False