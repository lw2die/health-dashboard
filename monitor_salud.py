#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor de Longevidad v4.0 - Sistema Integral de Salud
Script principal - orquesta todos los módulos

ESTRATEGIA DE LIMPIEZA:
- Archivos FULL: limpieza agresiva (1 sesión/día, elimina duplicados)
- Archivos DIFF: sin limpieza (datos ya validados por la app)
"""

import sys
import time
from datetime import datetime

# Imports de módulos propios
from config import INTERVALO_MINUTOS
from utils.logger import logger
from core.cache import cargar_cache, guardar_cache, obtener_archivos_procesados, marcar_archivo_procesado
from core.procesador import obtener_archivos_pendientes, procesar_archivo, mover_archivo_procesado
from core.limpieza import validar_y_limpiar_ejercicios
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
    
    # Limpieza inicial (solo la primera vez)
    if len(cache.get("ejercicio", [])) > 0 and len(cache.get("procesados", [])) <= 1:
        ejercicios_originales = len(cache["ejercicio"])
        cache["ejercicio"] = validar_y_limpiar_ejercicios(cache["ejercicio"])
        ejercicios_limpiados = len(cache["ejercicio"])
        
        if ejercicios_originales != ejercicios_limpiados:
            logger.info(
                f"Limpieza inicial: {ejercicios_originales} → {ejercicios_limpiados} "
                f"entrenamientos (-{ejercicios_originales - ejercicios_limpiados} duplicados)"
            )
            guardar_cache(cache)
    
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
        
        # Limpiar duplicados solo si es archivo FULL
        if es_full and "ejercicio" in campos:
            ejercicios_antes = len(cache["ejercicio"])
            cache["ejercicio"] = validar_y_limpiar_ejercicios(cache["ejercicio"])
            ejercicios_despues = len(cache["ejercicio"])
            
            if ejercicios_antes != ejercicios_despues:
                logger.info(
                    f"  Limpieza FULL: {ejercicios_antes} → {ejercicios_despues} "
                    f"(-{ejercicios_antes - ejercicios_despues} duplicados)"
                )
        elif es_diff:
            logger.info("  ✓ DIFF procesado sin limpieza (datos confiables)")
        
        # Marcar como procesado y mover archivo
        marcar_archivo_procesado(cache, archivo)
        mover_archivo_procesado(archivo)
    
    # Guardar cache actualizado
    guardar_cache(cache)
    
    return cache


def mostrar_resumen(cache):
    """
    Muestra resumen de métricas en consola.
    """
    ejercicios = cache.get("ejercicio", [])
    peso = cache.get("peso", [])
    
    peso_actual = peso[-1]["peso"] if peso else 0
    pai_semanal = calcular_pai_semanal(ejercicios)
    vo2max = calcular_vo2max(ejercicios)
    score = calcular_score_longevidad(peso_actual, pai_semanal, vo2max, 0)
    
    from config import PESO_OBJETIVO, PAI_OBJETIVO_SEMANAL
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("RESUMEN DE MÉTRICAS")
    logger.info("=" * 80)
    logger.info(f"Score Longevidad: {score}/100")
    logger.info(f"PAI Semanal: {pai_semanal:.1f} (objetivo ≥{PAI_OBJETIVO_SEMANAL})")
    logger.info(f"VO2max: {vo2max} ml/kg/min")
    logger.info(f"Peso: {peso_actual:.1f} kg (objetivo {PESO_OBJETIVO})")
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
    logger.info("PROCESAMIENTO - Monitor de Longevidad v4.0 [MODO HÍBRIDO]")
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
    Punto de entrada principal con loop de monitoreo.
    Ejecuta cada N minutos (configurado en config.py).
    """
    logger.info("")
    logger.info("=" * 80)
    logger.info("MONITOR DE LONGEVIDAD v4.0 - MODO HÍBRIDO [MODULAR]")
    logger.info("=" * 80)
    logger.info("Configuración: FULL=limpieza agresiva | DIFF=sin limpieza")
    logger.info(f"Intervalo: cada {INTERVALO_MINUTOS} minutos")
    logger.info("Presiona Ctrl+C para detener.")
    logger.info("=" * 80)
    logger.info("")
    
    try:
        while True:
            ciclo_principal()
            
            # Countdown timer
            segundos_espera = INTERVALO_MINUTOS * 60
            for remaining in range(segundos_espera, 0, -1):
                mins, secs = divmod(remaining, 60)
                barra = "█" * 50
                sys.stdout.write(
                    f"\r{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [INFO] - "
                    f"[{barra}] {mins:02d}:{secs:02d} → Próxima ejecución"
                )
                sys.stdout.flush()
                time.sleep(1)
            
            print()  # Nueva línea después del countdown
            
    except KeyboardInterrupt:
        logger.info("")
        logger.info("=" * 80)
        logger.info("Monitor detenido por el usuario.")
        logger.info("=" * 80)
        sys.exit(0)


if __name__ == "__main__":
    main()