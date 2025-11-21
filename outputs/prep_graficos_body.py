#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preparadores de Gráficos - Composición Corporal
Prepara datos para gráficos de peso, grasa, masa muscular, masa ósea, masa agua, TMB
"""

from datetime import datetime, timedelta

def _calcular_regresion_lineal(fechas_str, valores, unidad="kg"):
    """
    Calcula regresión lineal genérica.
    Retorna puntos de la línea y texto descriptivo.
    """
    n = len(valores)
    if n < 2: return None

    # Convertir a timestamps
    timestamps = []
    for f in fechas_str:
        try:
            # Intentamos formatos comunes
            try:
                dt = datetime.strptime(f, "%Y-%m-%d")
            except:
                dt = datetime.strptime(f, "%Y-%m-%d %H:%M")
            timestamps.append(dt.timestamp())
        except:
            return None

    # Medias
    mean_x = sum(timestamps) / n
    mean_y = sum(valores) / n

    # Pendiente (m) y Ordenada (b)
    numerador = sum((timestamps[i] - mean_x) * (valores[i] - mean_y) for i in range(n))
    denominador = sum((timestamps[i] - mean_x) ** 2 for i in range(n))

    if denominador == 0: return None

    m = numerador / denominador
    b = mean_y - (m * mean_x)

    # Puntos línea (Inicio y Fin)
    y_start = (m * timestamps[0]) + b
    y_end = (m * timestamps[-1]) + b

    # Cambio semanal (m * segundos_semana)
    cambio_semanal = m * 604800
    
    # Umbral de sensibilidad para decir "Estable"
    umbral = 0.05 if unidad == "%" else 0.1
    
    if cambio_semanal < -umbral:
        icono, estado = "📉", "Bajando"
    elif cambio_semanal > umbral:
        icono, estado = "📈", "Subiendo"
    else:
        icono, estado = "➡️", "Estable"

    # Formateo del texto
    texto = f"{icono} {estado} {abs(cambio_semanal):.2f} {unidad}/sem"

    return {
        "linea_x": [fechas_str[0], fechas_str[-1]],
        "linea_y": [y_start, y_end],
        "texto": texto
    }


def preparar_datos_peso_deduplicado(peso_data, dias=90):
    """
    Prepara datos de peso DEDUPLICADOS y calcula TENDENCIA.
    """
    if not peso_data:
        return {"fechas": [], "valores": [], "tendencia": None}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    
    # Ordenar
    datos_ordenados = sorted(peso_data, key=lambda x: x.get("fecha", ""))
    
    recientes = [
        p for p in datos_ordenados
        if datetime.fromisoformat(p["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    # Deduplicar por día
    por_dia = {}
    for p in recientes:
        fecha = datetime.fromisoformat(p["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        if fecha not in por_dia:
            por_dia[fecha] = []
        por_dia[fecha].append(p["peso"])
    
    fechas = sorted(por_dia.keys())
    valores = [sum(por_dia[f]) / len(por_dia[f]) for f in fechas]
    
    # Calcular tendencia
    tendencia = None
    if len(valores) >= 3:
        tendencia = _calcular_regresion_lineal(fechas, valores, unidad="kg")
    
    return {"fechas": fechas, "valores": valores, "tendencia": tendencia}


def preparar_datos_metrica_corporal(datos, campo, dias=90):
    """
    Prepara datos de métricas corporales (Grasa, Músculo, etc.)
    Calcula tendencia automáticamente.
    """
    if not datos:
        return {"fechas": [], "valores": [], "tendencia": None}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    
    # Ordenar
    datos_ordenados = sorted(datos, key=lambda x: x.get("fecha", ""))
    
    recientes = [
        d for d in datos_ordenados
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
    
    # Determinar unidad para la tendencia
    unidad = "%" if "porcentaje" in campo else "kg"
    
    tendencia = None
    if len(valores) >= 3:
        tendencia = _calcular_regresion_lineal(fechas, valores, unidad=unidad)
    
    return {"fechas": fechas, "valores": valores, "tendencia": tendencia}


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