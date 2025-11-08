#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extractor de métricas metabólicas - VERSIÓN CON RECORD_ID + NUTRITION
Glucosa, tasa metabólica basal, calorías totales, NUTRICIÓN
✅ AGREGA record_id a cada registro
✅ NUEVA función procesar_nutrition()
"""

from utils.logger import logger
from core.utils_procesador import reportar_por_fuente


def procesar_glucosa(datos, cache, nombre_archivo):
    """
    Extrae datos de glucosa en sangre del JSON.
    CORREGIDO: Convierte mmol/L a mg/dL
    ✅ CON RECORD_ID
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
            "record_id": g.get("record_id"),             # ✅ NUEVO
            "timestamp": g.get("timestamp"),             # ✅ NUEVO
            "fecha": g.get("timestamp"),                 # mantener por compatibilidad
            "nivel_mg_dl": round(mg_dl, 1),              # ✅ Valor convertido a mg/dL
            "tipo_muestra": g.get("specimen_source", "Desconocido"),
            "meal_type": g.get("meal_type", 0),          # ✅ NUEVO
            "relacion_comida": g.get("relation_to_meal", "Desconocido"),
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
    ✅ CON RECORD_ID
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
            "record_id": bmr.get("record_id"),           # ✅ NUEVO
            "timestamp": bmr.get("timestamp"),           # ✅ NUEVO
            "fecha": bmr.get("timestamp"),               # mantener por compatibilidad
            "kcal_dia": round(kcal, 1),                  # ✅ Valor real
            "fuente": bmr.get("source", "Desconocido")
        })
    
    agregados = len(cache['tasa_metabolica']) - count_antes
    if agregados > 0:
        logger.info(f"  → Tasa metabólica basal agregada: {agregados}")
        reportar_por_fuente(cache['tasa_metabolica'][-agregados:], "BMR", "kcal_dia")
        return True
    
    return False


def procesar_nutrition(datos, cache, nombre_archivo):
    """
    ✅ NUEVA FUNCIÓN: Extrae datos de nutrición del JSON.
    Procesa nutrition_records o nutrition_changes.
    
    Guarda:
    - record_id, timestamp, meal_type, name (nombre del alimento)
    - energy_kcal (calorías)
    - protein_g, carbs_g, fat_total_g (macronutrientes)
    - fiber_g, sugar_g (opcionales)
    - fuente
    """
    nutrition_data = None
    
    if "nutrition_records" in datos and "data" in datos["nutrition_records"]:
        nutrition_data = datos["nutrition_records"]["data"]
    elif "nutrition_changes" in datos and "data" in datos["nutrition_changes"]:
        nutrition_data = datos["nutrition_changes"]["data"]
    
    if not nutrition_data:
        return False
    
    count_antes = len(cache.get("nutrition", []))
    
    # Contador por tipo de comida para el log
    por_meal_type = {
        0: "Sin especificar",
        1: "Desayuno", 
        2: "Almuerzo",
        3: "Cena",
        4: "Snack"
    }
    contador_meal = {}
    
    for n in nutrition_data:
        meal_type = n.get("meal_type", 0)
        
        cache["nutrition"].append({
            "record_id": n.get("record_id"),                     # ✅ NUEVO
            "timestamp": n.get("start_time"),                    # ✅ NUEVO (nutrition usa start_time)
            "meal_type": meal_type,                              # ✅ NUEVO (0=sin especificar, 1=desayuno, 2=almuerzo, 3=cena, 4=snack)
            "name": n.get("name", "Sin nombre"),                 # ✅ NUEVO
            "energy_kcal": n.get("energy_kcal", 0),              # ✅ NUEVO
            "protein_g": n.get("protein_g", 0),                  # ✅ NUEVO
            "carbs_g": n.get("carbs_g", 0),                      # ✅ NUEVO
            "fat_total_g": n.get("fat_total_g", 0),              # ✅ NUEVO
            "fiber_g": n.get("fiber_g"),                         # ✅ NUEVO (puede ser None)
            "sugar_g": n.get("sugar_g"),                         # ✅ NUEVO (puede ser None)
            "fuente": n.get("source", "Desconocido")
        })
        
        # Contar por tipo de comida
        meal_name = por_meal_type.get(meal_type, "Otro")
        contador_meal[meal_name] = contador_meal.get(meal_name, 0) + 1
    
    agregados = len(cache['nutrition']) - count_antes
    if agregados > 0:
        logger.info(f"  → Nutrición agregada: {agregados} alimentos")
        logger.info(f"     🍽️  Por tipo de comida:")
        for meal, count in sorted(contador_meal.items()):
            logger.info(f"        • {meal}: {count} alimentos")
        return True
    
    return False