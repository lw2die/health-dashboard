#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Procesador Principal (MODULAR)
Orquesta todos los extractores de métricas
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
    procesar_glucosa, procesar_tasa_metabolica_basal
)
from core.extractores.actividad import (
    procesar_distancia, procesar_calorias_totales
)
from core.extractores.pasos_spo2 import (
    procesar_pasos, procesar_saturacion_oxigeno
)
from core.extractores.sueno import procesar_sueno


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
    # PROCESAR TODAS LAS MÉTRICAS - Llamar a cada extractor modular
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

    if procesar_calorias_totales(datos, cache, nombre_archivo):
        campos_detectados.append("calorias_totales")

    # Actividad
    if procesar_pasos(datos, cache, nombre_archivo):
        campos_detectados.append("pasos")

    if procesar_distancia(datos, cache, nombre_archivo):
        campos_detectados.append("distancia")

    if procesar_saturacion_oxigeno(datos, cache, nombre_archivo):
        campos_detectados.append("spo2")

    # Sueño
    if procesar_sueno(datos, cache):
        campos_detectados.append("sueno")

    if not campos_detectados:
        logger.warning(f"  ⚠  No se detectaron campos conocidos en {nombre_archivo}")

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


def detectar_deletions(datos, nombre_archivo):
    """Detecta si el JSON tiene deletions y alerta"""
    deletions = datos.get("deletions", {})
    count = deletions.get("count", 0)
    
    if count > 0:
        logger.warning("⚠️" * 40)
        logger.warning(f"⚠️  DELETIONS DETECTADAS: {count} registros borrados en {nombre_archivo}")
        record_ids = deletions.get('record_ids', [])
        logger.warning(f"⚠️  IDs: {record_ids[:10]}")  # Solo primeros 10
        logger.warning("⚠️  ACCIÓN REQUERIDA: Implementar procesamiento de deletions")
        logger.warning("⚠️" * 40)
    
    return count
