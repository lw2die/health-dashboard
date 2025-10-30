#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Funciones auxiliares para el procesador
Cálculos, traducciones, reportes
"""

from collections import defaultdict
from config import FC_REPOSO, FC_MAX, EDAD, ZONAS_FC
from utils.logger import logger


def calcular_pai(fc_promedio, duracion_min):
    """
    Calcula PAI (Personal Activity Intelligence).
    PAI = (intensidad_relativa^2 * duración) * factor_edad
    """
    if fc_promedio is None or fc_promedio <= 0:
        return 0.0
    
    if fc_promedio <= FC_REPOSO:
        return 0.0
    
    rango_fc = FC_MAX - FC_REPOSO
    intensidad = (fc_promedio - FC_REPOSO) / rango_fc
    
    factor_edad = 1 + (EDAD - 45) * 0.01
    pai = (intensidad ** 2) * duracion_min * factor_edad
    
    return round(pai, 1)


def calcular_hrtss(fc_promedio, duracion_min):
    """
    Calcula hrTSS (Heart Rate Training Stress Score).
    
    hrTSS = (duración_horas) × (HR_reserve%)² × 100
    
    Donde:
        HR_reserve% = (FC_promedio - FC_reposo) / (FC_max - FC_reposo)
    
    Esta métrica se usa para calcular TSB/CTL/ATL (Training Stress Balance).
    """
    if fc_promedio is None or fc_promedio <= 0:
        return 0.0
    
    if fc_promedio <= FC_REPOSO:
        return 0.0
    
    # Calcular HR Reserve %
    rango_fc = FC_MAX - FC_REPOSO
    hr_reserve_pct = (fc_promedio - FC_REPOSO) / rango_fc
    
    # Limitar entre 0 y 1
    hr_reserve_pct = max(0.0, min(1.0, hr_reserve_pct))
    
    # Duración en horas
    duracion_horas = duracion_min / 60.0
    
    # hrTSS = duración × (HR_reserve%)² × 100
    hrtss = duracion_horas * (hr_reserve_pct ** 2) * 100
    
    return round(hrtss, 1)


def clasificar_zona_fc(fc_promedio):
    """Clasifica zona de entrenamiento según FC"""
    if fc_promedio is None or fc_promedio <= 0:
        return "Sin FC"
    
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


def traducir_tipo_ejercicio(tipo_id):
    """Traduce código numérico de tipo de ejercicio al nombre"""
    if tipo_id is None:
        return "Desconocido"
    
    tipos = {
        0: "Aparatos de Musculación",
        13: "Press Banca",
        56: "Baseball",
        57: "Basketball",
        70: "Press Banca",  # ✅ AGREGADO - código alternativo
        71: "HIIT",
        72: "Hiking",
        74: "Swimming",
        79: "Walking",
        85: "Running",
        95: "Strength Training",
        96: "Stretching",
        104: "Yoga",
    }
    
    return tipos.get(tipo_id, f"Otro ({tipo_id})")


def reportar_por_fuente(datos, nombre_metrica, campo_valor=""):
    """Agrupa datos por fuente y reporta estadísticas"""
    por_fuente = defaultdict(lambda: {"count": 0, "total": 0})
    
    for d in datos:
        fuente = d.get("fuente", d.get("source", "Desconocido"))
        
        # Simplificar nombre
        if "withings" in fuente.lower():
            fuente = "Withings"
        elif "samsung" in fuente.lower() or "shealth" in fuente.lower():
            fuente = "Samsung Health"
        elif "healthsync" in fuente.lower():
            fuente = "HealthSync"
        else:
            fuente = fuente.split(".")[-1] if "." in fuente else fuente
        
        por_fuente[fuente]["count"] += 1
        if campo_valor and campo_valor in d:
            por_fuente[fuente]["total"] += d[campo_valor]
    
    if por_fuente:
        logger.info(f"    📊 {nombre_metrica} por fuente:")
        for fuente, stats in sorted(por_fuente.items()):
            if campo_valor:
                logger.info(f"       • {fuente}: {stats['count']} registros (total: {stats['total']:.0f})")
            else:
                logger.info(f"       • {fuente}: {stats['count']} registros")


def reportar_ejercicios_por_tipo(ejercicios):
    """Reporta ejercicios agrupados por tipo"""
    por_tipo = defaultdict(lambda: {"count": 0, "duracion_total": 0})
    
    for e in ejercicios:
        tipo = e.get("tipo", "Desconocido")
        por_tipo[tipo]["count"] += 1
        duracion = e.get("duracion") or 0
        por_tipo[tipo]["duracion_total"] += duracion
    
    if por_tipo:
        logger.info(f"    📊 Ejercicios por tipo:")
        for tipo, stats in sorted(por_tipo.items(), key=lambda x: x[1]["count"], reverse=True):
            logger.info(f"       • {tipo}: {stats['count']} sesiones ({stats['duracion_total']:.0f} min)")