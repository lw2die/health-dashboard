#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preparación de datos para gráficos de Plotly
"""

from datetime import datetime
from config import PESO_OBJETIVO


def preparar_datos_peso(peso):
    """
    Prepara datos de peso para gráfico.
    
    Args:
        peso (list): Lista de registros de peso
    
    Returns:
        dict: {"fechas": [...], "valores": [...], "objetivo": float}
    """
    fechas = []
    valores = []
    
    for p in peso:
        try:
            fecha = datetime.fromisoformat(p["fecha"].replace("Z", "+00:00"))
            fechas.append(fecha.strftime("%Y-%m-%d"))
            valores.append(p["peso"])
        except:
            continue
    
    return {
        "fechas": fechas,
        "valores": valores,
        "objetivo": PESO_OBJETIVO
    }