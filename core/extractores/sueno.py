#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extractor de datos de sueño - VERSIÓN COMPLETA CON RECORD_ID Y STAGES
Procesa sleep_sessions y sleep_changes
✅ AGREGA: session_id, record_id, start_time, end_time, zone_offset, stages array
✅ MANTIENE: awake, light, deep, rem por compatibilidad
"""

from datetime import datetime
from utils.logger import logger
from collections import defaultdict


def procesar_sueno(datos, cache):
    """
    Extrae datos de sueño del JSON.
    
    ✅ VERSIÓN COMPLETA:
    - session_id, record_id (identificadores únicos)
    - start_time, end_time, start_zone_offset, end_zone_offset
    - stages array completo con todas las fases
    - awake, light, deep, rem (campos planos por compatibilidad)
    - duration_minutes, stages_count
    
    Fases de sueño:
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
        # ✅ NUEVOS CAMPOS - Identificadores y tiempos
        session_id = s.get("session_id") or s.get("id")
        start_time = s.get("start_time")
        end_time = s.get("end_time")
        start_zone_offset = s.get("start_zone_offset")
        end_zone_offset = s.get("end_zone_offset")
        duration_minutes = s.get("duration_minutes", 0)
        
        fases = s.get("stages", [])
        stages_count = len(fases)
        fuente = s.get("source", "Desconocido")
        
        # ✅ NUEVO - Construir array de stages completo
        stages_array = []
        
        # Calcular duración por fase (mantener lógica existente)
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
            
            # ✅ NUEVO - Agregar a stages array
            stage_name = "unknown"
            if stage_type == 1:
                stage_name = "awake"
                duracion_awake += duracion_minutos
            elif stage_type == 2:
                stage_name = "sleep"
            elif stage_type == 3:
                stage_name = "out_of_bed"
            elif stage_type == 4:
                stage_name = "light"
                duracion_light += duracion_minutos
            elif stage_type == 5:
                stage_name = "deep"
                duracion_deep += duracion_minutos
            elif stage_type == 6:
                stage_name = "rem"
                duracion_rem += duracion_minutos
            
            stages_array.append({
                "stage": stage_name,
                "stage_type": stage_type,
                "start_time": f["start_time"],
                "end_time": f["end_time"],
                "duration_minutes": round(duracion_minutos, 1)
            })
        
        # Si duration_minutes viene del JSON, usarlo; sino usar el calculado
        if duration_minutes == 0:
            duration_minutes = duracion_total
        
        cache["sueno"].append({
            # ✅ NUEVOS CAMPOS - Identificadores
            "session_id": session_id,                        # ✅ NUEVO
            "record_id": session_id,                         # ✅ NUEVO (mismo que session_id)
            
            # ✅ NUEVOS CAMPOS - Tiempos y zona horaria
            "start_time": start_time,                        # ✅ NUEVO
            "end_time": end_time,                            # ✅ NUEVO
            "start_zone_offset": start_zone_offset,          # ✅ NUEVO
            "end_zone_offset": end_zone_offset,              # ✅ NUEVO
            
            # ✅ NUEVOS CAMPOS - Stages array y conteo
            "stages": stages_array,                          # ✅ NUEVO - Array completo
            "stages_count": stages_count,                    # ✅ NUEVO
            
            # Campos existentes (por compatibilidad)
            "fecha": start_time,                             # mantener por compatibilidad
            "duracion": duration_minutes,
            "awake": duracion_awake,
            "light": duracion_light,
            "deep": duracion_deep,
            "rem": duracion_rem,
            "porcentaje_profundo": round(
                (duracion_deep / duration_minutes * 100) if duration_minutes > 0 else 0,
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