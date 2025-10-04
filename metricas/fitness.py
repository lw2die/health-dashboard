#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Métricas de fitness cardiovascular:
- VO2max (capacidad aeróbica)
- TSB (Training Stress Balance)
"""

from datetime import datetime, timedelta
from config import (
    FC_MAX, FC_REPOSO, EDAD,
    TSB_CTL_DIAS, TSB_ATL_DIAS,
    GRAFICOS_DIAS_HISTORICO
)


def calcular_vo2max(ejercicios):
    """
    Estima VO2max usando la fórmula de Firstbeat basada en FC de reserva.
    
    VO2max = 15.3 × (FC_max / FC_reposo)
    
    Para mayor precisión, usa entrenamientos de zona umbral/VO2max
    (FC > 80% de FC_max) de los últimos 30 días.
    
    Args:
        ejercicios (list): Lista de entrenamientos
    
    Returns:
        float: VO2max estimado en ml/kg/min
    """
    fecha_limite = datetime.now().replace(tzinfo=None) - timedelta(days=30)
    
    entrenamientos_relevantes = []
    
    # Filtrar entrenamientos de alta intensidad
    for e in ejercicios:
        try:
            fecha_e = datetime.fromisoformat(
                e["fecha"].replace("Z", "+00:00")
            ).replace(tzinfo=None)
            fc = e.get("fc_promedio", 0)
            duracion = e.get("duracion", 0)
            
            # Últimos 30 días, FC > 80% FC_max, duración > 10 min
            if fecha_e >= fecha_limite and fc > (FC_MAX * 0.80) and duracion >= 10:
                entrenamientos_relevantes.append(e)
        except:
            continue
    
    # Si no hay entrenamientos de alta intensidad, usar todos
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
    
    # Fórmula de Firstbeat
    vo2max_base = 15.3 * (FC_MAX / FC_REPOSO)
    
    # Ajuste por edad (declina ~1% por año después de 25)
    factor_edad = 1 - ((EDAD - 25) * 0.01) if EDAD > 25 else 1
    vo2max_ajustado = vo2max_base * factor_edad
    
    # Ajuste por intensidad promedio
    fc_promedio_entrenamientos = sum(
        e["fc_promedio"] for e in entrenamientos_relevantes
    ) / len(entrenamientos_relevantes)
    factor_intensidad = fc_promedio_entrenamientos / FC_MAX
    
    vo2max_final = vo2max_ajustado * (0.85 + (factor_intensidad * 0.15))
    
    return round(vo2max_final, 1)


def calcular_tsb(ejercicios):
    """
    Calcula Training Stress Balance (TSB) para prevenir sobreentrenamiento.
    
    TSB = CTL - ATL
    - CTL (Chronic Training Load): promedio 42 días (fitness largo plazo)
    - ATL (Acute Training Load): promedio 7 días (fatiga aguda)
    
    Args:
        ejercicios (list): Lista de entrenamientos
    
    Returns:
        dict: {"tsb": float, "ctl": float, "atl": float}
    """
    fecha_actual = datetime.now().date()
    
    ctl_dias = [fecha_actual - timedelta(days=i) for i in range(TSB_CTL_DIAS)]
    atl_dias = [fecha_actual - timedelta(days=i) for i in range(TSB_ATL_DIAS)]
    
    ctl_total = 0
    atl_total = 0
    
    for e in ejercicios:
        try:
            fecha = datetime.fromisoformat(
                e["fecha"].replace("Z", "+00:00")
            ).date()
            
            if fecha in ctl_dias:
                ctl_total += e.get("pai", 0)
            if fecha in atl_dias:
                atl_total += e.get("pai", 0)
        except:
            continue
    
    ctl = ctl_total / TSB_CTL_DIAS
    atl = atl_total / TSB_ATL_DIAS
    tsb = ctl - atl
    
    return {
        "tsb": round(tsb, 1),
        "ctl": round(ctl, 1),
        "atl": round(atl, 1)
    }


def preparar_datos_tsb_historico(ejercicios):
    """
    Prepara datos históricos de TSB para gráficos.
    
    Args:
        ejercicios (list): Lista de entrenamientos
    
    Returns:
        dict: {"fechas": [...], "tsb": [...], "ctl": [...], "atl": [...]}
    """
    fecha_actual = datetime.now().date()
    fechas = []
    valores_tsb = []
    valores_ctl = []
    valores_atl = []
    
    for i in range(GRAFICOS_DIAS_HISTORICO - 1, -1, -1):
        fecha = fecha_actual - timedelta(days=i)
        
        # Calcular CTL y ATL para esta fecha
        ctl_dias = [fecha - timedelta(days=j) for j in range(TSB_CTL_DIAS)]
        atl_dias = [fecha - timedelta(days=j) for j in range(TSB_ATL_DIAS)]
        
        ctl_total = sum(
            e.get("pai", 0) for e in ejercicios
            if datetime.fromisoformat(
                e["fecha"].replace("Z", "+00:00")
            ).date() in ctl_dias
        )
        atl_total = sum(
            e.get("pai", 0) for e in ejercicios
            if datetime.fromisoformat(
                e["fecha"].replace("Z", "+00:00")
            ).date() in atl_dias
        )
        
        ctl = ctl_total / TSB_CTL_DIAS
        atl = atl_total / TSB_ATL_DIAS
        tsb_val = ctl - atl
        
        fechas.append(fecha.isoformat())
        valores_tsb.append(round(tsb_val, 1))
        valores_ctl.append(round(ctl, 1))
        valores_atl.append(round(atl, 1))
    
    return {
        "fechas": fechas,
        "tsb": valores_tsb,
        "ctl": valores_ctl,
        "atl": valores_atl
    }