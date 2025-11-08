#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Procesador Principal (MODULAR)
Orquesta todos los extractores de métricas
✅ VERSIÓN CON NUTRITION + DELETIONS
"""

import os
import json
from pathlib import Path
from config import INPUT_DIR, ARCHIVO_PREFIX, ARCHIVO_EXTENSION
from utils.logger import logger

# Importar extractores modulares
from core.extractores.ejercicios import procesar_ejercicios
from core.extractores.biometricos import (
    procesar_peso, procesar_grasa_corporal, procesar_masa_muscular,
    procesar_masa_agua, procesar_masa_osea
)
from core.extractores.cardiovascular import (
    procesar_fc_reposo, procesar_presion_arterial, procesar_vo2max,
    procesar_frecuencia_cardiaca
)
from core.extractores.metabolico import (
    procesar_glucosa, procesar_tasa_metabolica_basal, procesar_nutrition  # ✅ NUEVO
)
from core.extractores.actividad import (
    procesar_distancia, procesar_calorias_totales
)
from core.extractores.pasos_spo2 import (
    procesar_pasos, procesar_saturacion_oxigeno
)
from core.extractores.sueno import procesar_sueno


def procesar_deletions(cache, datos):
    """
    ✅ NUEVA FUNCIÓN: Procesa deletions del JSON y borra registros del cache.
    
    Busca en datos["deletions"]["record_ids"] y elimina esos registros
    de TODAS las secciones del cache que tengan record_id.
    
    Args:
        cache (dict): Cache de datos
        datos (dict): Datos del JSON con posible sección "deletions"
    
    Returns:
        int: Cantidad de registros borrados
    """
    if "deletions" not in datos:
        return 0
    
    deletions = datos.get("deletions", {})
    record_ids = deletions.get("record_ids", [])
    
    if not record_ids:
        return 0
    
    logger.info(f"  🗑️  Procesando {len(record_ids)} deletions...")
    
    borrados_total = 0
    
    # Lista de TODAS las secciones del cache que pueden tener record_id
    secciones = [
        "ejercicio", "peso", "sueno", "grasa_corporal", "fc_reposo", 
        "vo2max", "masa_muscular", "spo2", "pasos", "presion_arterial",
        "distancia", "calorias_totales", "frecuencia_cardiaca", "glucosa",
        "tasa_metabolica", "masa_agua", "masa_osea", "nutrition"
    ]
    
    # Buscar y borrar en cada sección
    for seccion in secciones:
        if seccion not in cache:
            continue
        
        antes = len(cache[seccion])
        
        # Filtrar: mantener solo los que NO están en record_ids
        cache[seccion] = [
            registro for registro in cache[seccion]
            if registro.get("record_id") not in record_ids and 
               registro.get("session_id") not in record_ids  # para ejercicios y sueño
        ]
        
        despues = len(cache[seccion])
        borrados = antes - despues
        
        if borrados > 0:
            borrados_total += borrados
            logger.info(f"     • {seccion}: {borrados} registros borrados")
    
    if borrados_total > 0:
        logger.info(f"  ✅ Total borrados del cache: {borrados_total}")
    else:
        logger.info(f"  ℹ️  No se encontraron registros para borrar")
    
    return borrados_total


def obtener_archivos_pendientes(archivos_procesados):
    """Obtiene lista de archivos JSON pendientes de procesar"""
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
    Procesa un JSON de HealthConnect y extrae TODAS las métricas.
    Orquesta todos los extractores modulares.
    ✅ VERSIÓN CON NUTRITION + DELETIONS
    
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
    
    # ═══════════════════════════════════════════════════════════════════════
    # PASO 1: PROCESAR DELETIONS PRIMERO (borrar registros obsoletos)
    # ═══════════════════════════════════════════════════════════════════════
    procesar_deletions(cache, datos)
    
    # ═══════════════════════════════════════════════════════════════════════
    # PASO 2: PROCESAR TODAS LAS MÉTRICAS - Llamar a cada extractor modular
    # ═══════════════════════════════════════════════════════════════════════
    
    # Ejercicio
    if procesar_ejercicios(datos, cache, nombre_archivo):
        campos_detectados.append("ejercicio")
    
    # Biométricos
    if procesar_peso(datos, cache):
        campos_detectados.append("peso")
    
    if procesar_grasa_corporal(datos, cache, nombre_archivo):
        campos_detectados.append("grasa_corporal")
    
    if procesar_masa_muscular(datos, cache, nombre_archivo):
        campos_detectados.append("masa_muscular")
    
    if procesar_masa_agua(datos, cache, nombre_archivo):
        campos_detectados.append("masa_agua")
    
    if procesar_masa_osea(datos, cache, nombre_archivo):
        campos_detectados.append("masa_osea")
    
    # Cardiovascular
    if procesar_fc_reposo(datos, cache, nombre_archivo):
        campos_detectados.append("fc_reposo")
    
    if procesar_presion_arterial(datos, cache, nombre_archivo):
        campos_detectados.append("presion_arterial")
    
    if procesar_vo2max(datos, cache, nombre_archivo):
        campos_detectados.append("vo2max")
    
    if procesar_frecuencia_cardiaca(datos, cache, nombre_archivo):
        campos_detectados.append("frecuencia_cardiaca")
    
    # Metabólico
    if procesar_glucosa(datos, cache, nombre_archivo):
        campos_detectados.append("glucosa")
    
    if procesar_tasa_metabolica_basal(datos, cache, nombre_archivo):
        campos_detectados.append("tasa_metabolica")
    
    # ✅ NUEVO - Nutrición
    if procesar_nutrition(datos, cache, nombre_archivo):
        campos_detectados.append("nutrition")
    
    # Actividad
    if procesar_pasos(datos, cache, nombre_archivo):
        campos_detectados.append("pasos")
    
    if procesar_distancia(datos, cache, nombre_archivo):
        campos_detectados.append("distancia")
    
    if procesar_calorias_totales(datos, cache, nombre_archivo):
        campos_detectados.append("calorias_totales")
    
    if procesar_saturacion_oxigeno(datos, cache, nombre_archivo):
        campos_detectados.append("spo2")
    
    # Sueño
    if procesar_sueno(datos, cache):
        campos_detectados.append("sueno")
    
    if not campos_detectados:
        logger.warning(f"  ⚠️  No se detectaron campos conocidos en {nombre_archivo}")
    
    return campos_detectados


def mover_archivo_procesado(nombre_archivo):
    """Mueve archivo JSON procesado a subcarpeta 'procesados'"""
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