#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preparadores de Gráficos - Composición Corporal
Prepara datos para gráficos de peso, grasa, masa muscular, masa ósea, masa agua, TMB
"""

from datetime import datetime, timedelta


def preparar_datos_peso_deduplicado(peso_data, dias=90):
    """
    Prepara datos de peso DEDUPLICADOS por día.
    Si hay múltiples mediciones en un día, usa el promedio.
    """
    if not peso_data:
        return {"fechas": [], "valores": []}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        p for p in peso_data
        if datetime.fromisoformat(p["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    # Deduplicar por día - promediar si hay múltiples mediciones
    por_dia = {}
    for p in recientes:
        fecha = datetime.fromisoformat(p["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        if fecha not in por_dia:
            por_dia[fecha] = []
        por_dia[fecha].append(p["peso"])
    
    fechas = sorted(por_dia.keys())
    valores = [sum(por_dia[f]) / len(por_dia[f]) for f in fechas]
    
    return {"fechas": fechas, "valores": valores}


def preparar_datos_metrica_corporal(datos, campo, dias=90):
    """Prepara datos genéricos de métricas corporales"""
    if not datos:
        return {"fechas": [], "valores": []}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        d for d in datos
        if datetime.fromisoformat(d["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    por_dia = {}
    for d in recientes:
        fecha = datetime.fromisoformat(d["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        if fecha not in por_dia:
            por_dia[fecha] = []
        por_dia[fecha].append(d.get(campo, 0))
    
    fechas = sorted(por_dia.keys())
    valores = [sum(por_dia[f]) / len(por_dia[f]) for f in fechas]
    
    return {"fechas": fechas, "valores": valores}


def preparar_datos_tasa_metabolica(tmb_data, dias=90):
    """Prepara datos de tasa metabólica basal"""
    if not tmb_data:
        return {"fechas": [], "valores": []}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        t for t in tmb_data
        if datetime.fromisoformat(t["timestamp"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    por_dia = {}
    for t in recientes:
        fecha = datetime.fromisoformat(t["timestamp"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        if fecha not in por_dia:
            por_dia[fecha] = []
        por_dia[fecha].append(t.get("kcal_dia", 0))
    
    fechas = sorted(por_dia.keys())
    valores = [sum(por_dia[f]) / len(por_dia[f]) for f in fechas]
    
    return {"fechas": fechas, "valores": valores}
