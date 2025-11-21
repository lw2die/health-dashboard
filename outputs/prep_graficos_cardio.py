#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preparadores de Gráficos - Salud Cardiovascular
Prepara datos para gráficos de FC reposo, FC diurna, presión arterial, SpO2, glucosa
"""

from datetime import datetime, timedelta

def _calcular_regresion(fechas_str, valores, unidad=""):
    """Calcula regresión lineal simple."""
    n = len(valores)
    if n < 2: return None

    timestamps = []
    for f in fechas_str:
        try:
            try: dt = datetime.strptime(f, "%Y-%m-%d %H:%M")
            except: dt = datetime.strptime(f, "%Y-%m-%d")
            timestamps.append(dt.timestamp())
        except: return None

    mean_x = sum(timestamps) / n
    mean_y = sum(valores) / n

    numerador = sum((timestamps[i] - mean_x) * (valores[i] - mean_y) for i in range(n))
    denominador = sum((timestamps[i] - mean_x) ** 2 for i in range(n))

    if denominador == 0: return None

    m = numerador / denominador
    b = mean_y - (m * mean_x)

    y_start = (m * timestamps[0]) + b
    y_end = (m * timestamps[-1]) + b

    cambio_semanal = m * 604800
    if cambio_semanal > 0.1: icono, estado = "📈", "Sube"
    elif cambio_semanal < -0.1: icono, estado = "📉", "Baja"
    else: icono, estado = "➡️", "Estable"

    texto = f"{icono} {estado} {abs(cambio_semanal):.1f} {unidad}/sem"

    return {
        "linea_x": [fechas_str[0], fechas_str[-1]],
        "linea_y": [y_start, y_end],
        "texto": texto
    }


def preparar_datos_fc_reposo(fc_reposo_data, dias=30):
    if not fc_reposo_data: return {"fechas": [], "valores": [], "tendencia": None}
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [fc for fc in sorted(fc_reposo_data, key=lambda x: x.get("fecha")) if datetime.fromisoformat(fc["fecha"].replace("Z", "")).replace(tzinfo=None) >= fecha_limite]
    
    por_dia = {}
    for fc in recientes:
        fecha = datetime.fromisoformat(fc["fecha"].replace("Z", "")).strftime("%Y-%m-%d")
        por_dia.setdefault(fecha, []).append(fc["bpm"])
    
    fechas = sorted(por_dia.keys())
    valores = [sum(por_dia[f]) / len(por_dia[f]) for f in fechas]
    
    tendencia = None
    if len(valores) >= 3:
        tendencia = _calcular_regresion(fechas, valores, unidad="bpm")
    
    return {"fechas": fechas, "valores": valores, "tendencia": tendencia}


def preparar_datos_fc_diurna(fc_diurna_data, dias=30):
    if not fc_diurna_data: return {"fechas": [], "bpm_min": [], "bpm_max": [], "bpm_promedio": []}
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [fc for fc in fc_diurna_data if datetime.fromisoformat(fc["fecha"].replace("Z", "")).replace(tzinfo=None) >= fecha_limite]
    por_dia = {}
    for fc in recientes:
        fecha = datetime.fromisoformat(fc["fecha"].replace("Z", "")).strftime("%Y-%m-%d")
        entry = por_dia.setdefault(fecha, {"bpm_min": [], "bpm_max": [], "bpm_promedio": []})
        entry["bpm_min"].append(fc.get("bpm_min", 0))
        entry["bpm_max"].append(fc.get("bpm_max", 0))
        entry["bpm_promedio"].append(fc.get("bpm_promedio", 0))
    fechas = sorted(por_dia.keys())
    return {
        "fechas": fechas,
        "bpm_min": [min(por_dia[f]["bpm_min"]) for f in fechas],
        "bpm_max": [max(por_dia[f]["bpm_max"]) for f in fechas],
        "bpm_promedio": [sum(por_dia[f]["bpm_promedio"]) / len(por_dia[f]["bpm_promedio"]) for f in fechas]
    }


def preparar_datos_presion_arterial(presion_data, dias=90):
    if not presion_data: return {"fechas": [], "sistolica": [], "diastolica": []}
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [p for p in presion_data if datetime.fromisoformat(p["fecha"].replace("Z", "")).replace(tzinfo=None) >= fecha_limite]
    por_dia = {}
    for p in recientes:
        fecha = datetime.fromisoformat(p["fecha"].replace("Z", "")).strftime("%Y-%m-%d")
        entry = por_dia.setdefault(fecha, {"sistolica": [], "diastolica": []})
        entry["sistolica"].append(p.get("sistolica", 0))
        entry["diastolica"].append(p.get("diastolica", 0))
    fechas = sorted(por_dia.keys())
    return {
        "fechas": fechas,
        "sistolica": [sum(por_dia[f]["sistolica"]) / len(por_dia[f]["sistolica"]) for f in fechas],
        "diastolica": [sum(por_dia[f]["diastolica"]) / len(por_dia[f]["diastolica"]) for f in fechas]
    }


def preparar_datos_spo2(spo2_data, dias=30):
    if not spo2_data: return {"fechas": [], "valores": []}
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [s for s in spo2_data if datetime.fromisoformat(s["fecha"].replace("Z", "")).replace(tzinfo=None) >= fecha_limite]
    por_dia = {}
    for s in recientes:
        fecha = datetime.fromisoformat(s["fecha"].replace("Z", "")).strftime("%Y-%m-%d")
        por_dia.setdefault(fecha, []).append(s["porcentaje"])
    fechas = sorted(por_dia.keys())
    valores = [sum(por_dia[f]) / len(por_dia[f]) for f in fechas]
    return {"fechas": fechas, "valores": valores}


def preparar_datos_glucosa(glucosa_data, dias=90):
    """
    Prepara datos de glucosa separando Basal vs Postprandial.
    CORRECCIÓN: Fechas naive para evitar errores de comparación.
    """
    ayunas = {"fechas": [], "valores": []}
    post = {"fechas": [], "valores": []}
    tendencia = None
    
    if not glucosa_data:
        return {"ayunas": ayunas, "post": post, "tendencia": None}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    datos_ordenados = sorted(glucosa_data, key=lambda x: x.get("timestamp", x.get("fecha", "")))
    
    for g in datos_ordenados:
        try:
            ts = g.get("timestamp", g.get("fecha", ""))
            # Parseo literal y forzamos a naive (sin zona)
            dt_local = datetime.fromisoformat(ts.replace("Z", "")).replace(tzinfo=None)
            
            if dt_local < fecha_limite:
                continue
            
            valor = g.get("nivel_mg_dl", 0)
            if valor <= 0: continue
            
            fecha_str = dt_local.strftime("%Y-%m-%d %H:%M")
            relacion = g.get("relacion_comida")
            
            es_basal = False
            # 1. Regla de hora
            if dt_local.hour < 8:
                es_basal = True
            # 2. Regla de etiqueta
            elif relacion == 1 or relacion == "1":
                es_basal = True
            
            if es_basal:
                ayunas["fechas"].append(fecha_str)
                ayunas["valores"].append(valor)
            else:
                post["fechas"].append(fecha_str)
                post["valores"].append(valor)
                
        except Exception:
            continue
            
    if len(ayunas["valores"]) >= 3:
        tendencia = _calcular_regresion(ayunas["fechas"], ayunas["valores"], unidad="mg/dL")
    
    return {"ayunas": ayunas, "post": post, "tendencia": tendencia}