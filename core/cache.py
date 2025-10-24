#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestión del cache de datos de salud
Estructura JSON que almacena todos los datos procesados
"""

import json
from pathlib import Path
from config import CACHE_JSON
from utils.logger import logger


def inicializar_cache():
    """
    Inicializa estructura del cache con TODAS las métricas disponibles.
    """
    return {
        # Métricas originales
        "ejercicio": [],
        "peso": [],
        "sueno": [],
        
        # Métricas agregadas anteriormente
        "grasa_corporal": [],
        "fc_reposo": [],
        "vo2max": [],
        "masa_muscular": [],
        "spo2": [],
        "pasos": [],
        "presion_arterial": [],
        
        # ⭐ NUEVAS MÉTRICAS AGREGADAS
        "distancia": [],
        "calorias_totales": [],
        "frecuencia_cardiaca": [],
        "glucosa": [],
        "tasa_metabolica": [],
        "masa_agua": [],
        "masa_osea": [],
        
        # Metadata
        "archivos_procesados": [],
        "ultima_actualizacion": None
    }


def cargar_cache():
    """
    Carga el cache desde archivo JSON.
    Si no existe o está corrupto, inicializa uno nuevo.
    """
    try:
        if CACHE_JSON.exists():
            with open(CACHE_JSON, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            
            # Asegurar que todas las claves existan (migración automática)
            cache_nuevo = inicializar_cache()
            for key in cache_nuevo.keys():
                if key not in cache:
                    cache[key] = cache_nuevo[key]
                    logger.info(f"➕ Métrica nueva agregada al cache: {key}")
            
            logger.info(f"Cache cargado: {CACHE_JSON}")
            return cache
        else:
            logger.info("No existe cache previo. Creando nuevo...")
            return inicializar_cache()
    
    except json.JSONDecodeError:
        logger.warning("Cache corrupto. Creando nuevo...")
        return inicializar_cache()
    
    except Exception as e:
        logger.error(f"Error cargando cache: {e}")
        return inicializar_cache()


def guardar_cache(cache):
    """
    Guarda el cache en archivo JSON.
    """
    from datetime import datetime
    
    try:
        cache["ultima_actualizacion"] = datetime.now().isoformat()
        
        with open(CACHE_JSON, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Cache guardado: {CACHE_JSON}")
        
    except Exception as e:
        logger.error(f"Error guardando cache: {e}")


def obtener_archivos_procesados(cache):
    """
    Obtiene lista de archivos ya procesados.
    """
    return cache.get("archivos_procesados", [])


def marcar_archivo_procesado(cache, nombre_archivo):
    """
    Marca un archivo como procesado.
    """
    if nombre_archivo not in cache["archivos_procesados"]:
        cache["archivos_procesados"].append(nombre_archivo)


def obtener_estadisticas_cache(cache):
    """
    Retorna estadísticas del cache actual.
    """
    stats = {
        "ejercicio": len(cache.get("ejercicio", [])),
        "peso": len(cache.get("peso", [])),
        "sueno": len(cache.get("sueno", [])),
        "grasa_corporal": len(cache.get("grasa_corporal", [])),
        "fc_reposo": len(cache.get("fc_reposo", [])),
        "vo2max": len(cache.get("vo2max", [])),
        "masa_muscular": len(cache.get("masa_muscular", [])),
        "spo2": len(cache.get("spo2", [])),
        "pasos": len(cache.get("pasos", [])),
        "presion_arterial": len(cache.get("presion_arterial", [])),
        "distancia": len(cache.get("distancia", [])),
        "calorias_totales": len(cache.get("calorias_totales", [])),
        "frecuencia_cardiaca": len(cache.get("frecuencia_cardiaca", [])),
        "glucosa": len(cache.get("glucosa", [])),
        "tasa_metabolica": len(cache.get("tasa_metabolica", [])),
        "masa_agua": len(cache.get("masa_agua", [])),
        "masa_osea": len(cache.get("masa_osea", [])),
        "archivos_procesados": len(cache.get("archivos_procesados", [])),
    }
    
    return stats