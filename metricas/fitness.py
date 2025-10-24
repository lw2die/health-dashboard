#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Métricas de fitness cardiovascular - VERSIÓN FINAL
Usa EWMA (Exponential Weighted Moving Average) como TrainingPeaks/Strava
"""

from datetime import datetime, timedelta
from collections import defaultdict
from config import (
    FC_MAX, FC_REPOSO, EDAD,
    TSB_CTL_DIAS, TSB_ATL_DIAS,
    GRAFICOS_DIAS_HISTORICO
)


def calcular_vo2max(ejercicios):
    """Estima VO2max usando la fórmula de Firstbeat."""
    fecha_limite = datetime.now().replace(tzinfo=None) - timedelta(days=30)
    
    entrenamientos_relevantes = []
    
    for e in ejercicios:
        try:
            fecha_e = datetime.fromisoformat(
                e["fecha"].replace("Z", "+00:00")
            ).replace(tzinfo=None)
            fc = e.get("fc_promedio", 0)
            duracion = e.get("duracion", 0)
            
            if fecha_e >= fecha_limite and fc > (FC_MAX * 0.80) and duracion >= 10:
                entrenamientos_relevantes.append(e)
        except:
            continue
    
    if not entrenamientos_relevantes:
        for e in ejercicios:
            try:
                fecha_e = datetime.fromisoformat(
                    e["fecha"].replace("Z", "+00:00")
                ).replace(tzinfo=None)
                if fecha_e >= fecha_limite and e.get("fc_promedio", 0) > 0:
                    entrenamientos_relevantes.append(e)
            except:
                continue
    
    if not entrenamientos_relevantes:
        return 0
    
    vo2max_base = 15.3 * (FC_MAX / FC_REPOSO)
    factor_edad = 1 - ((EDAD - 25) * 0.01) if EDAD > 25 else 1
    vo2max_ajustado = vo2max_base * factor_edad
    
    fc_promedio_entrenamientos = sum(
        e["fc_promedio"] for e in entrenamientos_relevantes
    ) / len(entrenamientos_relevantes)
    factor_intensidad = fc_promedio_entrenamientos / FC_MAX
    
    vo2max_final = vo2max_ajustado * (0.85 + (factor_intensidad * 0.15))
    
    return round(vo2max_final, 1)


def _agrupar_pai_por_dia(ejercicios):
    """Agrupa PAI total por día."""
    pai_por_dia = defaultdict(float)
    
    for e in ejercicios:
        try:
            fecha = datetime.fromisoformat(
                e["fecha"].replace("Z", "+00:00")
            ).date()
            pai_por_dia[fecha] += e.get("pai", 0)
        except:
            continue
    
    return pai_por_dia


def calcular_tsb(ejercicios):
    """
    Calcula TSB usando EWMA (como TrainingPeaks).
    
    ✅ FÓRMULA CORRECTA:
    - CTL_hoy = CTL_ayer * (1 - 1/42) + PAI_hoy * (1/42)
    - ATL_hoy = ATL_ayer * (1 - 1/7) + PAI_hoy * (1/7)
    - TSB = CTL - ATL
    
    Returns:
        dict: {"tsb": float, "ctl": float, "atl": float}
    """
    if not ejercicios:
        return {"tsb": 0, "ctl": 0, "atl": 0}
    
    pai_por_dia = _agrupar_pai_por_dia(ejercicios)
    
    # Ordenar fechas
    todas_fechas = sorted(pai_por_dia.keys())
    if not todas_fechas:
        return {"tsb": 0, "ctl": 0, "atl": 0}
    
    # Constantes EWMA
    k_ctl = 1.0 / TSB_CTL_DIAS  # 1/42 = 0.0238
    k_atl = 1.0 / TSB_ATL_DIAS  # 1/7 = 0.1429
    
    ctl = 0
    atl = 0
    
    # Calcular EWMA día por día desde el primer entrenamiento
    fecha_actual = datetime.now().date()
    fecha_inicio = todas_fechas[0]
    
    for dias in range((fecha_actual - fecha_inicio).days + 1):
        fecha = fecha_inicio + timedelta(days=dias)
        pai_hoy = pai_por_dia.get(fecha, 0)
        
        # EWMA: nueva = antigua * (1 - k) + valor_hoy * k
        ctl = ctl * (1 - k_ctl) + pai_hoy * k_ctl
        atl = atl * (1 - k_atl) + pai_hoy * k_atl
    
    tsb = ctl - atl
    
    return {
        "tsb": round(tsb, 1),
        "ctl": round(ctl, 1),
        "atl": round(atl, 1)
    }


def preparar_datos_tsb_historico(ejercicios):
    """
    Prepara datos históricos de TSB para gráficos usando EWMA.
    
    ✅ FÓRMULA CORRECTA aplicada día por día
    """
    if not ejercicios:
        return {
            "fechas": [],
            "tsb": [],
            "ctl": [],
            "atl": []
        }
    
    pai_por_dia = _agrupar_pai_por_dia(ejercicios)
    
    todas_fechas = sorted(pai_por_dia.keys())
    if not todas_fechas:
        return {
            "fechas": [],
            "tsb": [],
            "ctl": [],
            "atl": []
        }
    
    # Constantes EWMA
    k_ctl = 1.0 / TSB_CTL_DIAS
    k_atl = 1.0 / TSB_ATL_DIAS
    
    fecha_actual = datetime.now().date()
    fecha_inicio = max(
        todas_fechas[0],
        fecha_actual - timedelta(days=GRAFICOS_DIAS_HISTORICO)
    )
    
    fechas = []
    valores_tsb = []
    valores_ctl = []
    valores_atl = []
    
    ctl = 0
    atl = 0
    
    # Calcular EWMA desde el inicio hasta hoy
    # Pero solo guardar los últimos GRAFICOS_DIAS_HISTORICO días
    fecha_inicio_total = todas_fechas[0]
    
    for dias in range((fecha_actual - fecha_inicio_total).days + 1):
        fecha = fecha_inicio_total + timedelta(days=dias)
        pai_hoy = pai_por_dia.get(fecha, 0)
        
        # Actualizar EWMA
        ctl = ctl * (1 - k_ctl) + pai_hoy * k_ctl
        atl = atl * (1 - k_atl) + pai_hoy * k_atl
        tsb = ctl - atl
        
        # Solo guardar si está en la ventana de gráfico
        if fecha >= fecha_inicio:
            fechas.append(fecha.isoformat())
            valores_tsb.append(round(tsb, 1))
            valores_ctl.append(round(ctl, 1))
            valores_atl.append(round(atl, 1))
    
    return {
        "fechas": fechas,
        "tsb": valores_tsb,
        "ctl": valores_ctl,
        "atl": valores_atl
    }