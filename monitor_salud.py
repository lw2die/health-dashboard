#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor de Longevidad v4.0 - Sistema Integral de Salud
Script principal - orquesta todos los módulos

ESTRATEGIA: SIN LIMPIEZA
- Permisos configurados en Health Connect para evitar duplicados en origen
- Reporte por fuente para monitorear y detectar apps problemáticas
"""

import sys
import time
from datetime import datetime

# Imports de módulos propios
from config import INTERVALO_MINUTOS
from utils.logger import logger
from core.cache import cargar_cache, guardar_cache, obtener_archivos_procesados, marcar_archivo_procesado
from core.procesador import obtener_archivos_pendientes, procesar_archivo, mover_archivo_procesado
# from core.limpieza import validar_y_limpiar_ejercicios  # DESACTIVADO - sin duplicados en origen
from metricas.pai import calcular_pai_semanal
from metricas.fitness import calcular_vo2max
from metricas.score import calcular_score_longevidad
from outputs.dashboard import generar_dashboard
from outputs.github import publicar_github


def procesar_datos_nuevos():
    """
    Procesa archivos JSON nuevos y actualiza el cache.
    Aplica estrategia de limpieza según tipo de archivo (FULL/DIFF).
    """
    # Cargar cache existente
    cache = cargar_cache()
    
    # LIMPIEZA DESACTIVADA - datos ya vienen limpios desde Health Connect
    # (permisos configurados para evitar duplicados en origen)
    
    # Obtener archivos pendientes
    archivos_procesados = obtener_archivos_procesados(cache)
    archivos_nuevos = obtener_archivos_pendientes(archivos_procesados)
    
    if not archivos_nuevos:
        logger.info("No hay archivos nuevos para procesar.")
        return cache
    
    logger.info(f"Archivos nuevos encontrados: {archivos_nuevos}")
    
    # Procesar cada archivo
    for archivo in archivos_nuevos:
        es_full = "FULL" in archivo.upper()
        es_diff = "DIFF" in archivo.upper()
        
        tipo_archivo = "FULL" if es_full else ("DIFF" if es_diff else "UNKNOWN")
        logger.info(f"→ Procesando [{tipo_archivo}]: {archivo}")
        
        # Procesar archivo
        from config import INPUT_DIR
        import os
        campos = procesar_archivo(os.path.join(INPUT_DIR, archivo), cache)
        
        if campos:
            logger.info(f"  Campos detectados: {', '.join(campos)}")
        else:
            logger.warning(f"  ⚠ No se detectaron campos en {archivo}")
        
        # LIMPIEZA DESACTIVADA - datos limpios desde origen
        logger.info(f"  ✓ Archivo procesado sin limpieza (datos confiables)")
        
        # Marcar como procesado y mover archivo
        marcar_archivo_procesado(cache, archivo)
        mover_archivo_procesado(archivo)
    
    # Guardar cache actualizado
    guardar_cache(cache)
    
    return cache


def mostrar_resumen(cache):
    """
    Muestra resumen de métricas en consola.
    🤫 Llama a calcular_pai_semanal en modo SILENCIOSO (sin logs)
    """
    ejercicios = cache.get("ejercicio", [])
    peso = cache.get("peso", [])
    
    # Corrección de seguridad: Usar .get() o [0] con validación en la lógica de su proyecto
    # Asumo que su lógica interna ya extrae el peso actual correctamente.
    peso_actual = peso[-1]["peso"] if peso and peso[-1].get("peso") is not None else None
    
    # 🤫 LLAMADA SILENCIOSA - No imprime logs
    pai_semanal = calcular_pai_semanal(ejercicios, silencioso=True)
    vo2max = calcular_vo2max(ejercicios)
    
    # Aseguramos que la función reciba el peso actual (o None)
    score = calcular_score_longevidad(peso_actual, pai_semanal, vo2max, 0)
    
    from config import PESO_OBJETIVO, PAI_OBJETIVO_SEMANAL
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("RESUMEN DE MÉTRICAS")
    logger.info("=" * 80)
    logger.info(f"Score Longevidad: {score}/100")
    logger.info(f"PAI Semanal: {pai_semanal:.1f} (objetivo ≥{PAI_OBJETIVO_SEMANAL})")
    logger.info(f"VO2max: {vo2max} ml/kg/min")
    logger.info(f"Peso: {peso_actual:.1f} kg (objetivo {PESO_OBJETIVO})" if peso_actual is not None else f"Peso: Dato no disponible (objetivo {PESO_OBJETIVO})")
    logger.info(f"Total entrenamientos únicos: {len(ejercicios)}")
    logger.info("=" * 80)


def ciclo_principal():
    """
    Ejecuta un ciclo completo:
    1. Procesar datos nuevos
    2. Generar dashboard
    3. Publicar a GitHub
    4. Mostrar resumen
    """
    logger.info("=" * 80)
    logger.info("PROCESAMIENTO - Monitor de Longevidad v4.0 [REPORTE POR FUENTE]")
    logger.info("=" * 80)
    
    try:
        # Procesar datos
        cache = procesar_datos_nuevos()
        
        # Generar dashboard
        generar_dashboard(cache)
        
        # Publicar a GitHub
        publicar_github()
        
        # Mostrar resumen
        mostrar_resumen(cache)
        
    except Exception as e:
        logger.error(f"Error en ciclo principal: {str(e)}")
        raise


def main():
    """
    Punto de entrada principal - Ejecuta un ciclo de monitoreo y termina.
    """
    logger.info("")
    logger.info("=" * 80)
    logger.info("MONITOR DE LONGEVIDAD v4.0 - SIN LOOP DE CRON")
    logger.info("=" * 80)
    logger.info("Configuración: SIN LIMPIEZA - datos limpios desde origen")
    logger.info("Ejecución: Un ciclo, controlado por Crontab de Ubuntu.")
    logger.info("=" * 80)
    logger.info("")
    
    try:
        ciclo_principal()
            
    except Exception as e:
        logger.error(f"Fallo en la ejecución principal: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()