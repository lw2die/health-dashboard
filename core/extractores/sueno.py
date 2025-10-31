#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extractor de datos de sueño
Procesa sleep_sessions y sleep_changes
✅ VERSIÓN MEJORADA: Extrae todas las fases de sueño
"""

from datetime import datetime
from utils.logger import logger
from collections import defaultdict


def procesar_sueno(datos, cache):
    """
    Extrae datos de sueño del JSON.
    
    ✅ Extrae todas las fases:
    - stage_type 1 = Awake (despierto)
    - stage_type 2 = Sleep (genérico)
    - stage_type 3 = Out of bed
    - stage_type 4 = Light sleep (ligero)
    - stage_type 5 = Deep sleep (profundo)
    - stage_type 6 = REM
    """
    sueno_data = None
    
    if "sleep_sessions" in datos and "data" in datos["sleep_sessions"]:
        sueno_data = datos["sleep_sessions"]["data"]
    elif "sleep_changes" in datos and "data" in datos["sleep_changes"]:
        sueno_data = datos["sleep_changes"]["data"]
    
    if not sueno_data:
        return False
    
    count_antes = len(cache["sueno"])
    por_fuente = defaultdict(int)
    
    for s in sueno_data:
        fases = s.get("stages", [])
        fuente = s.get("source", "Desconocido")
        
        # Calcular duración por fase
        duracion_total = 0
        duracion_awake = 0
        duracion_light = 0
        duracion_deep = 0
        duracion_rem = 0
        
        for f in fases:
            start = datetime.fromisoformat(f["start_time"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(f["end_time"].replace("Z", "+00:00"))
            duracion_minutos = (end - start).total_seconds() / 60
            
            duracion_total += duracion_minutos
            
            stage_type = f.get("stage_type")
            
            # Clasificar por tipo de fase
            if stage_type == 1:  # Awake
                duracion_awake += duracion_minutos
            elif stage_type == 4:  # Light sleep
                duracion_light += duracion_minutos
            elif stage_type == 5:  # Deep sleep
                duracion_deep += duracion_minutos
            elif stage_type == 6:  # REM
                duracion_rem += duracion_minutos
        
        cache["sueno"].append({
            "fecha": s.get("start_time"),
            "duracion": duracion_total,
            "awake": duracion_awake,
            "light": duracion_light,
            "deep": duracion_deep,
            "rem": duracion_rem,
            "porcentaje_profundo": round(
                (duracion_deep / duracion_total * 100) if duracion_total > 0 else 0,
                1
            ),
            "fuente": fuente
        })
        
        por_fuente[fuente] += 1
    
    agregados = len(cache["sueno"]) - count_antes
    if agregados > 0:
        logger.info(f"  → Sueño agregado: {agregados} sesiones")
        logger.info(f"     📊 Sueño por fuente:")
        for fuente, count in sorted(por_fuente.items()):
            logger.info(f"        • {fuente}: {count} sesiones")
    
    return agregados > 0