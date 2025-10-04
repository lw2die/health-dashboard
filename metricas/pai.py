#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cálculo de PAI (Personal Activity Intelligence) semanal
Usa ventana móvil de 7 días
"""

from datetime import datetime, timedelta
from collections import defaultdict
from config import PAI_VENTANA_DIAS, GRAFICOS_DIAS_HISTORICO
from utils.logger import logger


def calcular_pai_semanal(ejercicios):
    """
    Calcula PAI semanal con ventana móvil de 7 días desde fecha actual.
    Muestra desglose de entrenamientos incluidos en la ventana.
    
    Args:
        ejercicios (list): Lista de entrenamientos
    
    Returns:
        float: PAI total de los últimos 7 días
    """
    fecha_actual = datetime.now().date()
    fecha_inicio = fecha_actual - timedelta(days=PAI_VENTANA_DIAS - 1)
    
    logger.info("=" * 50)
    logger.info(f"CÁLCULO PAI SEMANAL - Fecha actual: {fecha_actual}")
    logger.info(f"Ventana de {PAI_VENTANA_DIAS} días: {fecha_inicio} a {fecha_actual}")
    
    pai_total = 0
    entrenamientos_ventana = []
    
    for e in ejercicios:
        try:
            fecha_entrenamiento = datetime.fromisoformat(
                e["fecha"].replace("Z", "+00:00")
            ).date()
            
            if fecha_inicio <= fecha_entrenamiento <= fecha_actual:
                pai_total += e.get("pai", 0)
                entrenamientos_ventana.append(e)
                logger.info(
                    f"  {fecha_entrenamiento}: {e['tipo']} - "
                    f"PAI={e.get('pai', 0):.1f}, FC={e.get('fc_promedio')} bpm, "
                    f"{e.get('duracion')} min"
                )
        except:
            continue
    
    logger.info("")
    logger.info(f"PAI TOTAL SEMANAL: {pai_total:.1f}")
    logger.info(f"Entrenamientos en ventana: {len(entrenamientos_ventana)}")
    logger.info("=" * 50)
    
    return round(pai_total, 1)


def preparar_datos_pai_historico(ejercicios):
    """
    Prepara datos de PAI semanal histórico para gráficos.
    Calcula ventana móvil de 7 días para los últimos N días.
    
    Args:
        ejercicios (list): Lista de entrenamientos
    
    Returns:
        dict: {"fechas": [...], "valores": [...]}
    """
    fecha_actual = datetime.now().date()
    pai_diario = defaultdict(float)
    
    # Primero calcular PAI por día
    for e in ejercicios:
        try:
            fecha = datetime.fromisoformat(
                e["fecha"].replace("Z", "+00:00")
            ).date()
            pai_diario[fecha] += e.get("pai", 0)
        except:
            continue
    
    # Calcular PAI semanal móvil para cada día
    fechas = []
    valores = []
    
    for i in range(GRAFICOS_DIAS_HISTORICO - 1, -1, -1):
        fecha = fecha_actual - timedelta(days=i)
        
        # Sumar PAI de los últimos 7 días desde esta fecha
        pai_semana = 0
        for j in range(PAI_VENTANA_DIAS):
            fecha_ventana = fecha - timedelta(days=j)
            pai_semana += pai_diario.get(fecha_ventana, 0)
        
        fechas.append(fecha.isoformat())
        valores.append(round(pai_semana, 1))
    
    return {"fechas": fechas, "valores": valores}