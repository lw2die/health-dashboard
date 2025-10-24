#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestión del cache de datos (cache_datos.json)
Maneja lectura, escritura y estructura del cache
"""

import json
import os
from config import CACHE_JSON
from utils.logger import logger


def cargar_cache():
    """
    Carga el cache desde disco. Si no existe, crea uno nuevo.
    
    Returns:
        dict: Cache con estructura completa incluyendo nuevas métricas
    """
    if os.path.exists(CACHE_JSON):
        try:
            with open(CACHE_JSON, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            logger.info(f"Cache cargado: {len(cache.get('ejercicio', []))} ejercicios, "
                       f"{len(cache.get('peso', []))} pesos, "
                       f"{len(cache.get('sueno', []))} registros de sueño")
            
            # Log de nuevas métricas si existen
            if cache.get('grasa_corporal'):
                logger.info(f"  + {len(cache['grasa_corporal'])} registros de grasa corporal")
            if cache.get('fc_reposo'):
                logger.info(f"  + {len(cache['fc_reposo'])} registros de FC en reposo")
            if cache.get('vo2max'):
                logger.info(f"  + {len(cache['vo2max'])} registros de VO2max")
            if cache.get('masa_muscular'):
                logger.info(f"  + {len(cache['masa_muscular'])} registros de masa muscular")
            if cache.get('spo2'):
                logger.info(f"  + {len(cache['spo2'])} registros de SpO2")
            if cache.get('pasos'):
                logger.info(f"  + {len(cache['pasos'])} registros de Pasos")
                
        except Exception as e:
            logger.error(f"Error leyendo cache: {e}. Creando cache nuevo.")
            cache = _crear_cache_vacio()
    else:
        logger.info("Cache no existe. Creando cache nuevo.")
        cache = _crear_cache_vacio()
    
    # Asegurar que todas las claves existen (incluyendo nuevas métricas)
    cache.setdefault("ejercicio", [])
    cache.setdefault("peso", [])
    cache.setdefault("sueno", [])
    cache.setdefault("procesados", [])
    
    # ⭐ Nuevas métricas
    cache.setdefault("grasa_corporal", [])
    cache.setdefault("fc_reposo", [])
    cache.setdefault("vo2max", [])
    cache.setdefault("masa_muscular", [])
    cache.setdefault("spo2", [])
    cache.setdefault("pasos", [])
    
    return cache


def guardar_cache(cache):
    """
    Guarda el cache en disco.
    
    Args:
        cache (dict): Cache a guardar
    """
    try:
        with open(CACHE_JSON, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        logger.info(f"Cache guardado: {CACHE_JSON}")
    except Exception as e:
        logger.error(f"Error guardando cache: {e}")
        raise


def _crear_cache_vacio():
    """
    Crea estructura de cache vacía con todas las métricas.
    
    Returns:
        dict: Cache vacío con estructura estándar + nuevas métricas
    """
    return {
        "ejercicio": [],
        "peso": [],
        "sueno": [],
        "procesados": [],
        # ⭐ Nuevas métricas agregadas
        "grasa_corporal": [],
        "fc_reposo": [],
        "vo2max": [],
        "masa_muscular": [],
        "spo2": [],
        "pasos": []
    }


def obtener_archivos_procesados(cache):
    """
    Retorna lista de archivos ya procesados.
    
    Args:
        cache (dict): Cache actual
    
    Returns:
        list: Lista de nombres de archivo procesados
    """
    return cache.get("procesados", [])


def marcar_archivo_procesado(cache, nombre_archivo):
    """
    Marca un archivo como procesado en el cache.
    
    Args:
        cache (dict): Cache actual
        nombre_archivo (str): Nombre del archivo procesado
    """
    if "procesados" not in cache:
        cache["procesados"] = []
    
    if nombre_archivo not in cache["procesados"]:
        cache["procesados"].append(nombre_archivo)
        logger.info(f"Archivo marcado como procesado: {nombre_archivo}")