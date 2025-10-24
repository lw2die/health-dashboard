#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Limpieza y validación de datos de ejercicio
Elimina duplicados manteniendo 1 sesión por día
"""

from utils.logger import logger


def validar_y_limpiar_ejercicios(ejercicios):
    """
    VERSIÓN AGRESIVA: Mantiene solo 1 entrenamiento por día.
    
    Criterio de selección:
    - El de mayor duración
    - Si duración similar (±2 min), el de mayor PAI
    
    Args:
        ejercicios (list): Lista de entrenamientos
    
    Returns:
        list: Lista de entrenamientos sin duplicados
    """
    logger.info("Validando y limpiando datos de ejercicio (1 sesión/día)...")
    
    if not ejercicios:
        return ejercicios
    
    # Agrupar por fecha (sin hora)
    por_fecha = {}
    for e in ejercicios:
        fecha_str = e.get("fecha", "")[:10]  # YYYY-MM-DD
        if fecha_str not in por_fecha:
            por_fecha[fecha_str] = []
        por_fecha[fecha_str].append(e)
    
    # Detectar días con PAI anormalmente alto ANTES de limpiar
    _detectar_pai_anormal(por_fecha)
    
    # Mantener solo el mejor entrenamiento por día
    limpiados = []
    eliminados = 0
    
    for fecha, entrenamientos_dia in sorted(por_fecha.items()):
        if len(entrenamientos_dia) == 1:
            # Solo hay 1 entrenamiento ese día
            limpiados.append(entrenamientos_dia[0])
        else:
            # Múltiples entrenamientos → elegir el mejor
            mejor = _seleccionar_mejor_entrenamiento(entrenamientos_dia)
            limpiados.append(mejor)
            eliminados += len(entrenamientos_dia) - 1
            
            _log_limpieza_dia(fecha, entrenamientos_dia, mejor)
    
    if eliminados > 0:
        _log_resumen_limpieza(eliminados, len(limpiados), len(ejercicios))
    
    return limpiados


def _detectar_pai_anormal(por_fecha):
    """
    Detecta días con PAI anormalmente alto (>100).
    """
    for fecha, entrenamientos_dia in por_fecha.items():
        pai_total = sum(e.get("pai", 0) for e in entrenamientos_dia)
        if pai_total > 100:
            logger.warning(
                f"PAI ANORMALMENTE ALTO el {fecha}: {pai_total:.1f} "
                f"(total {len(entrenamientos_dia)} entrenamientos)"
            )


def _seleccionar_mejor_entrenamiento(entrenamientos):
    """
    Selecciona el mejor entrenamiento según duración y PAI.
    
    Criterio: mayor duración, y si empate, mayor PAI
    """
    return max(
        entrenamientos,
        key=lambda e: (e.get("duracion", 0), e.get("pai", 0))
    )


def _log_limpieza_dia(fecha, todos, mejor):
    """
    Registra en log qué entrenamientos se mantienen y cuáles se eliminan.
    """
    logger.warning(
        f"MÚLTIPLES ENTRENAMIENTOS el {fecha} ({len(todos)} sesiones) "
        f"→ manteniendo solo:"
    )
    logger.warning(
        f"  ✓ MANTENER: {mejor.get('tipo')} - {mejor.get('duracion')} min, "
        f"FC {mejor.get('fc_promedio')} bpm, PAI {mejor.get('pai', 0):.1f}"
    )
    
    for e in todos:
        if e != mejor:
            logger.warning(
                f"  ✗ ELIMINAR: {e.get('tipo')} - {e.get('duracion')} min, "
                f"FC {e.get('fc_promedio')} bpm, PAI {e.get('pai', 0):.1f}"
            )


def _log_resumen_limpieza(eliminados, finales, originales):
    """
    Muestra resumen de la limpieza realizada.
    """
    logger.warning("")
    logger.warning("=" * 70)
    logger.warning(f"RESUMEN LIMPIEZA: Se eliminaron {eliminados} entrenamientos duplicados")
    logger.warning(f"Entrenamientos únicos: {finales} (de {originales} originales)")
    logger.warning("=" * 70)
    logger.warning("")


def limpiar_metricas_corporales(cache):
    """
    Limpia duplicados de métricas corporales (1 registro por día).
    """
    eliminados = 0
    
    for metrica in ["spo2", "grasa_corporal", "masa_muscular", "vo2max", "fc_reposo"]:
        if metrica not in cache:
            continue
        
        datos = cache[metrica]
        if not datos:
            continue
        
        # Agrupar por fecha (YYYY-MM-DD)
        por_fecha = {}
        for d in datos:
            fecha_str = d.get("fecha", "")[:10]
            if fecha_str not in por_fecha:
                por_fecha[fecha_str] = []
            por_fecha[fecha_str].append(d)
        
        # Mantener solo el primero de cada día
        limpiados = []
        for fecha in sorted(por_fecha.keys()):
            limpiados.append(por_fecha[fecha][0])
            eliminados += len(por_fecha[fecha]) - 1
        
        cache[metrica] = limpiados
    
    if eliminados > 0:
        logger.info(f"Métricas corporales: {eliminados} duplicados eliminados")
    
    return eliminados