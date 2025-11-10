#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preparadores de Gráficos - Salud Cardiovascular
Prepara datos para gráficos de FC reposo, FC diurna, presión arterial, SpO2, glucosa
"""

from datetime import datetime, timedelta


def preparar_datos_fc_reposo(fc_reposo_data, dias=30):
    """Prepara datos de FC en reposo"""
    if not fc_reposo_data:
        return {"fechas": [], "valores": []}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        fc for fc in fc_reposo_data
        if datetime.fromisoformat(fc["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    por_dia = {}
    for fc in recientes:
        fecha = datetime.fromisoformat(fc["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        if fecha not in por_dia:
            por_dia[fecha] = []
        por_dia[fecha].append(fc["bpm"])
    
    fechas = sorted(por_dia.keys())
    valores = [sum(por_dia[f]) / len(por_dia[f]) for f in fechas]
    
    return {"fechas": fechas, "valores": valores}


def preparar_datos_fc_diurna(fc_diurna_data, dias=30):
    """Prepara datos de FC diurna (continua) - min, max, promedio"""
    if not fc_diurna_data:
        return {"fechas": [], "bpm_min": [], "bpm_max": [], "bpm_promedio": []}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        fc for fc in fc_diurna_data
        if datetime.fromisoformat(fc["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    por_dia = {}
    for fc in recientes:
        fecha = datetime.fromisoformat(fc["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        if fecha not in por_dia:
            por_dia[fecha] = {
                "bpm_min": [],
                "bpm_max": [],
                "bpm_promedio": []
            }
        por_dia[fecha]["bpm_min"].append(fc.get("bpm_min", 0))
        por_dia[fecha]["bpm_max"].append(fc.get("bpm_max", 0))
        por_dia[fecha]["bpm_promedio"].append(fc.get("bpm_promedio", 0))
    
    fechas = sorted(por_dia.keys())
    bpm_min = [min(por_dia[f]["bpm_min"]) for f in fechas]
    bpm_max = [max(por_dia[f]["bpm_max"]) for f in fechas]
    bpm_promedio = [sum(por_dia[f]["bpm_promedio"]) / len(por_dia[f]["bpm_promedio"]) for f in fechas]
    
    return {
        "fechas": fechas,
        "bpm_min": bpm_min,
        "bpm_max": bpm_max,
        "bpm_promedio": bpm_promedio
    }


def preparar_datos_presion_arterial(presion_data, dias=90):
    """Prepara datos de presión arterial"""
    if not presion_data:
        return {"fechas": [], "sistolica": [], "diastolica": []}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        p for p in presion_data
        if datetime.fromisoformat(p["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    por_dia = {}
    for p in recientes:
        fecha = datetime.fromisoformat(p["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        if fecha not in por_dia:
            por_dia[fecha] = {
                "sistolica": [],
                "diastolica": []
            }
        por_dia[fecha]["sistolica"].append(p.get("sistolica", 0))
        por_dia[fecha]["diastolica"].append(p.get("diastolica", 0))
    
    fechas = sorted(por_dia.keys())
    sistolica = [sum(por_dia[f]["sistolica"]) / len(por_dia[f]["sistolica"]) for f in fechas]
    diastolica = [sum(por_dia[f]["diastolica"]) / len(por_dia[f]["diastolica"]) for f in fechas]
    
    return {
        "fechas": fechas,
        "sistolica": sistolica,
        "diastolica": diastolica
    }


def preparar_datos_spo2(spo2_data, dias=30):
    """Prepara datos de SpO2"""
    if not spo2_data:
        return {"fechas": [], "valores": []}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        s for s in spo2_data
        if datetime.fromisoformat(s["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    por_dia = {}
    for s in recientes:
        fecha = datetime.fromisoformat(s["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        if fecha not in por_dia:
            por_dia[fecha] = []
        por_dia[fecha].append(s["porcentaje"])
    
    fechas = sorted(por_dia.keys())
    valores = [sum(por_dia[f]) / len(por_dia[f]) for f in fechas]
    
    return {"fechas": fechas, "valores": valores}


def preparar_datos_glucosa(glucosa_data, dias=90):
    """Prepara datos de glucosa en sangre"""
    if not glucosa_data:
        return {"fechas": [], "valores": []}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        g for g in glucosa_data
        if datetime.fromisoformat(g["timestamp"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    por_dia = {}
    for g in recientes:
        fecha = datetime.fromisoformat(g["timestamp"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        if fecha not in por_dia:
            por_dia[fecha] = []
        por_dia[fecha].append(g.get("nivel_mg_dl", 0))
    
    fechas = sorted(por_dia.keys())
    valores = [sum(por_dia[f]) / len(por_dia[f]) for f in fechas]
    
    return {"fechas": fechas, "valores": valores}
