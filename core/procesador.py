#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Procesamiento de archivos JSON de HealthConnect
Extrae datos de ejercicio, peso y sueño
"""

import os
import json
from datetime import datetime
from config import INPUT_DIR, ARCHIVO_PREFIX, ARCHIVO_EXTENSION, FC_REPOSO, FC_MAX, EDAD
from utils.logger import logger


def _traducir_tipo_ejercicio(tipo_id):
    """
    Traduce el código numérico de tipo de ejercicio al nombre.
    Basado en los códigos de HealthConnect/Samsung Health.
    """
    if tipo_id is None:
        return "Desconocido"
    
    tipos = {
        13: "Badminton",
        56: "Baseball",
        57: "Basketball",
        58: "Biathlon",
        59: "Calisthenics",
        60: "Cricket",
        61: "Dancing",
        62: "Elliptical",
        63: "Fencing",
        64: "Football (American)",
        65: "Football (Soccer)",
        66: "Frisbee",
        67: "Golf",
        68: "Guided Breathing",
        69: "Gymnastics",
        70: "Handball",
        71: "HIIT",
        72: "Hiking",
        73: "Ice Hockey",
        74: "Swimming",
        75: "Ice Skating",
        76: "Martial Arts",
        77: "Paddling",
        78: "Paragliding",
        79: "Walking",
        80: "Pilates",
        81: "Racquetball",
        82: "Rock Climbing",
        83: "Roller Hockey",
        84: "Rowing",
        85: "Running",
        86: "Sailing",
        87: "Scuba Diving",
        88: "Skating",
        89: "Skiing",
        90: "Snowboarding",
        91: "Snowshoeing",
        92: "Softball",
        93: "Squash",
        94: "Stair Climbing",
        95: "Strength Training",
        96: "Stretching",
        97: "Surfing",
        98: "Table Tennis",
        99: "Tennis",
        100: "Volleyball",
        101: "Water Polo",
        102: "Weightlifting",
        103: "Wheelchair",
        104: "Yoga",
    }
    
    return tipos.get(tipo_id, f"Otro ({tipo_id})")


def obtener_archivos_pendientes(archivos_procesados):
    """
    Obtiene lista de archivos JSON pendientes de procesar.
    
    Args:
        archivos_procesados (list): Lista de archivos ya procesados
    
    Returns:
        list: Archivos nuevos por procesar
    """
    try:
        archivos_json = sorted([
            f for f in os.listdir(INPUT_DIR)
            if f.startswith(ARCHIVO_PREFIX) and f.endswith(ARCHIVO_EXTENSION)
        ])
    except Exception as e:
        logger.error(f"Error listando archivos: {e}")
        return []
    
    archivos_nuevos = [f for f in archivos_json if f not in archivos_procesados]
    
    logger.info(f"Total archivos JSON encontrados: {len(archivos_json)}")
    logger.info(f"Archivos ya procesados: {len(archivos_procesados)}")
    logger.info(f"Archivos nuevos a procesar: {len(archivos_nuevos)}")
    
    return archivos_nuevos


def procesar_archivo(ruta, cache):
    """
    Procesa un JSON de HealthConnect y extrae ejercicio, peso, sueño.
    
    Args:
        ruta (str): Ruta completa al archivo JSON
        cache (dict): Cache donde agregar los datos
    
    Returns:
        list: Campos detectados en el archivo
    """
    campos_detectados = []
    nombre_archivo = os.path.basename(ruta)
    
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        logger.info(f"Procesando archivo: {nombre_archivo}")
        logger.info(f"Claves raíz del JSON: {list(datos.keys())}")
        
    except Exception as e:
        logger.error(f"Error leyendo {ruta}: {e}")
        return campos_detectados
    
    # Procesar cada tipo de dato (pasando nombre_archivo para logging)
    if _procesar_ejercicios(datos, cache, nombre_archivo):
        campos_detectados.append("ejercicio")
    
    if _procesar_peso(datos, cache):
        campos_detectados.append("peso")
    
    if _procesar_sueno(datos, cache):
        campos_detectados.append("sueno")
    
    if not campos_detectados:
        logger.warning(f"  ⚠ No se detectaron campos conocidos en {nombre_archivo}")
    
    return campos_detectados


def _procesar_ejercicios(datos, cache, nombre_archivo):
    """
    Extrae datos de ejercicio del JSON.
    Soporta formatos FULL (exercise_sessions) y DIFF (exercise_changes).
    """
    ejercicios_data = None
    
    # Formato FULL: "exercise_sessions"
    if "exercise_sessions" in datos and "data" in datos["exercise_sessions"]:
        ejercicios_data = datos["exercise_sessions"]["data"]
    # Formato AUTO_DIFF: "exercise_changes"
    elif "exercise_changes" in datos and "data" in datos["exercise_changes"]:
        ejercicios_data = datos["exercise_changes"]["data"]
    
    if not ejercicios_data:
        return False
    
    count_antes = len(cache["ejercicio"])
    
    for e in ejercicios_data:
        entrada = {
            "fecha": e.get("start_time"),
            "tipo": e.get("exercise_type_name") or _traducir_tipo_ejercicio(e.get("exercise_type")),
            "duracion": e.get("duration_minutes", 0),
            "calorias": e.get("calories_burned", 0),
            "distancia": e.get("distance_meters", 0),
            "fc_promedio": e.get("avg_heart_rate"),  # Cambié: ya no pone 0 por defecto
            "fc_max": e.get("max_heart_rate", 0),
            "pasos": e.get("total_steps", 0)
        }
        
        # Log si FC es None o 0
        if entrada["fc_promedio"] is None or entrada["fc_promedio"] == 0:
            logger.warning(
                f"⚠️ FC NULA/CERO en [{nombre_archivo}] - "
                f"Tipo: {entrada['tipo']}, Duración: {entrada['duracion']} min, "
                f"Fecha: {entrada['fecha'][:10] if entrada['fecha'] else 'N/A'}"
            )
        
        # Calcular PAI y zona FC
        entrada["pai"] = _calcular_pai(entrada["fc_promedio"], entrada["duracion"])
        entrada["zona"] = _clasificar_zona_fc(entrada["fc_promedio"])
        
        cache["ejercicio"].append(entrada)
    
    logger.info(f"  → Ejercicios agregados: {len(cache['ejercicio']) - count_antes}")
    return True
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
            "tipo": e.get("exercise_type_name", "Desconocido"),
            "duracion": e.get("duration_minutes", 0),
            "calorias": e.get("calories_burned", 0),
            "distancia": e.get("distance_meters", 0),
            "fc_promedio": e.get("avg_heart_rate", 0),
            "fc_max": e.get("max_heart_rate", 0),
            "pasos": e.get("total_steps", 0)
        }
        
        # Calcular PAI y zona FC
        entrada["pai"] = _calcular_pai(entrada["fc_promedio"], entrada["duracion"])
        entrada["zona"] = _clasificar_zona_fc(entrada["fc_promedio"])
        
        cache["ejercicio"].append(entrada)
    
    logger.info(f"  → Ejercicios agregados: {len(cache['ejercicio']) - count_antes}")
    return True


def _procesar_peso(datos, cache):
    """
    Extrae datos de peso del JSON.
    Soporta formatos FULL (weight_records) y DIFF (weight_changes).
    """
    peso_data = None
    
    # Formato FULL
    if "weight_records" in datos and "data" in datos["weight_records"]:
        peso_data = datos["weight_records"]["data"]
    # Formato DIFF
    elif "weight_changes" in datos and "data" in datos["weight_changes"]:
        peso_data = datos["weight_changes"]["data"]
    
    if not peso_data:
        return False
    
    count_antes = len(cache["peso"])
    
    for p in peso_data:
        cache["peso"].append({
            "fecha": p.get("timestamp"),
            "peso": p.get("weight_kg", 0)
        })
    
    logger.info(f"  → Pesos agregados: {len(cache['peso']) - count_antes}")
    return True


def _procesar_sueno(datos, cache):
    """
    Extrae datos de sueño del JSON.
    Soporta formatos FULL (sleep_sessions) y DIFF (sleep_changes).
    """
    sueno_data = None
    
    # Formato FULL
    if "sleep_sessions" in datos and "data" in datos["sleep_sessions"]:
        sueno_data = datos["sleep_sessions"]["data"]
    # Formato DIFF
    elif "sleep_changes" in datos and "data" in datos["sleep_changes"]:
        sueno_data = datos["sleep_changes"]["data"]
    
    if not sueno_data:
        return False
    
    count_antes = len(cache["sueno"])
    
    for s in sueno_data:
        fases = s.get("stages", [])
        
        # Calcular duración total y profundo
        duracion_total = 0
        duracion_profundo = 0
        
        for f in fases:
            start = datetime.fromisoformat(f["start_time"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(f["end_time"].replace("Z", "+00:00"))
            duracion_minutos = (end - start).total_seconds() / 60
            
            duracion_total += duracion_minutos
            
            # stage_type 5 = Deep sleep
            if f.get("stage_type") == 5:
                duracion_profundo += duracion_minutos
        
        cache["sueno"].append({
            "fecha": s.get("start_time"),
            "duracion": duracion_total,
            "profundo": duracion_profundo,
            "porcentaje_profundo": round(
                (duracion_profundo / duracion_total * 100) if duracion_total > 0 else 0,
                1
            )
        })
    
    logger.info(f"  → Registros de sueño agregados: {len(cache['sueno']) - count_antes}")
    return True


def _calcular_pai(fc_promedio, duracion_min):
    """
    Calcula PAI (Personal Activity Intelligence).
    PAI = (intensidad_relativa^2 * duración) * factor_edad
    """
    # Validar que fc_promedio no sea None o 0
    if fc_promedio is None or fc_promedio <= 0:
        return 0.0
    
    if fc_promedio <= FC_REPOSO:
        return 0.0
    
    rango_fc = FC_MAX - FC_REPOSO
    intensidad = (fc_promedio - FC_REPOSO) / rango_fc
    
    factor_edad = 1 + (EDAD - 45) * 0.01
    pai = (intensidad ** 2) * duracion_min * factor_edad
    
    return round(pai, 1)


def _clasificar_zona_fc(fc_promedio):
    """
    Clasifica zona de entrenamiento según FC.
    """
    # Manejar caso de FC None o inválida
    if fc_promedio is None or fc_promedio <= 0:
        return "Sin FC"
    
    from config import ZONAS_FC
    
    porcentaje = fc_promedio / FC_MAX
    
    if porcentaje < ZONAS_FC["aerobico"][0]:
        return "Recuperación"
    elif porcentaje < ZONAS_FC["tempo"][0]:
        return "Aeróbico"
    elif porcentaje < ZONAS_FC["umbral"][0]:
        return "Tempo"
    elif porcentaje < ZONAS_FC["vo2max"][0]:
        return "Umbral"
    else:
        return "VO2max"


def mover_archivo_procesado(nombre_archivo):
    """
    Mueve archivo JSON procesado a subcarpeta 'procesados'.
    """
    try:
        carpeta_procesados = INPUT_DIR / "procesados"
        carpeta_procesados.mkdir(exist_ok=True)
        
        origen = INPUT_DIR / nombre_archivo
        destino = carpeta_procesados / nombre_archivo
        
        if origen.exists():
            origen.rename(destino)
            logger.info(f"  ✓ Archivo movido a: procesados/{nombre_archivo}")
    except Exception as e:
        logger.warning(f"  No se pudo mover {nombre_archivo}: {e}")