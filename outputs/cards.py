#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generación de cards (tarjetas métricas) para el dashboard
Todas las funciones _generar_card_* están aquí
"""

from config import (
    COLOR_EXCELENTE, COLOR_BUENO, COLOR_MALO,
    PAI_OBJETIVO_SEMANAL, PESO_OBJETIVO, TSB_OPTIMO_MIN, TSB_OPTIMO_MAX
)


def generar_card_pai(metricas):
    """Card PAI Semanal"""
    pai = metricas.get("pai_semanal", 0)
    
    if pai >= PAI_OBJETIVO_SEMANAL:
        color = COLOR_EXCELENTE
        estado = "Óptimo"
    elif pai >= 50:
        color = COLOR_BUENO
        estado = "Bueno"
    else:
        color = COLOR_MALO
        estado = "Bajo"
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">PAI Semanal</div>
        <div class="metric-value" style="color: {color};">{pai:.0f}</div>
        <div class="metric-detail">{estado} (Objetivo: {PAI_OBJETIVO_SEMANAL})</div>
    </div>
    """


def generar_card_peso(metricas):
    """Card Peso Actual"""
    peso = metricas.get("peso_actual")
    
    if peso is None:
        return f"""
        <div class="metric-card">
            <div class="metric-label">Peso Actual</div>
            <div class="metric-value" style="color: #8b949e;">Sin datos</div>
        </div>
        """
    
    diferencia = peso - PESO_OBJETIVO
    if abs(diferencia) <= 2:
        color = COLOR_EXCELENTE
        estado = "En objetivo"
    elif abs(diferencia) <= 5:
        color = COLOR_BUENO
        estado = "Cerca"
    else:
        color = COLOR_MALO
        estado = "Lejos"
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">Peso Actual</div>
        <div class="metric-value" style="color: {color};">{peso:.1f} kg</div>
        <div class="metric-detail">{estado} ({diferencia:+.1f} kg)</div>
    </div>
    """


def generar_card_vo2max(metricas):
    """Card VO2max MEDIDO"""
    vo2max = metricas.get("vo2max")
    
    if vo2max is None:
        return f"""
        <div class="metric-card">
            <div class="metric-label">VO2max (Medido)</div>
            <div class="metric-value" style="color: #8b949e;">Sin datos</div>
        </div>
        """
    
    if vo2max >= 40:
        color = COLOR_EXCELENTE
        estado = "Excelente"
    elif vo2max >= 35:
        color = COLOR_BUENO
        estado = "Bueno"
    else:
        color = COLOR_MALO
        estado = "Por debajo"
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">VO2max (Medido)</div>
        <div class="metric-value" style="color: {color};">{vo2max:.1f}</div>
        <div class="metric-detail">{estado}</div>
    </div>
    """


def generar_card_tsb(metricas):
    """Card TSB con CTL/ATL"""
    tsb = metricas.get("tsb_actual")
    tsb_dict = metricas.get("tsb_dict", {})
    
    if tsb is None:
        return f"""
        <div class="metric-card">
            <div class="metric-label">TSB Actual</div>
            <div class="metric-value" style="color: #8b949e;">Sin datos</div>
        </div>
        """
    
    if TSB_OPTIMO_MIN <= tsb <= TSB_OPTIMO_MAX:
        color = COLOR_EXCELENTE
        estado = "Forma óptima"
    elif -20 < tsb < TSB_OPTIMO_MIN:
        color = COLOR_BUENO
        estado = "Neutral"
    else:
        color = COLOR_MALO
        estado = "Fatiga" if tsb < -20 else "Sobreentrenamiento"
    
    ctl = tsb_dict.get("ctl", 0)
    atl = tsb_dict.get("atl", 0)
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">TSB Actual</div>
        <div class="metric-value" style="color: {color};">{tsb:.1f}</div>
        <div class="metric-detail">{estado}</div>
        <div class="metric-detail" style="font-size: 0.8em; color: #8b949e;">CTL: {ctl:.1f} | ATL: {atl:.1f}</div>
    </div>
    """


def generar_card_sueno(metricas):
    """Card Sueño promedio"""
    sueno = metricas.get("promedio_sueno")
    
    if sueno is None:
        return f"""
        <div class="metric-card">
            <div class="metric-label">Sueño (7 días)</div>
            <div class="metric-value" style="color: #8b949e;">Sin datos</div>
        </div>
        """
    
    if sueno >= 7:
        color = COLOR_EXCELENTE
        estado = "Óptimo"
    elif sueno >= 6:
        color = COLOR_BUENO
        estado = "Aceptable"
    else:
        color = COLOR_MALO
        estado = "Insuficiente"
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">Sueño (7 días)</div>
        <div class="metric-value" style="color: {color};">{sueno:.1f}h</div>
        <div class="metric-detail">{estado}</div>
    </div>
    """


def generar_card_spo2(metricas):
    """Card SpO2"""
    spo2 = metricas.get("spo2_promedio")
    
    if spo2 is None:
        return f"""
        <div class="metric-card">
            <div class="metric-label">SpO2 (7 días)</div>
            <div class="metric-value" style="color: #8b949e;">Sin datos</div>
        </div>
        """
    
    if spo2 >= 95:
        color = COLOR_EXCELENTE
        estado = "Normal"
    elif spo2 >= 90:
        color = COLOR_BUENO
        estado = "Aceptable"
    else:
        color = COLOR_MALO
        estado = "Bajo"
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">SpO2 (7 días)</div>
        <div class="metric-value" style="color: {color};">{spo2:.1f}%</div>
        <div class="metric-detail">{estado}</div>
    </div>
    """


def generar_card_grasa(metricas):
    """Card Grasa Corporal"""
    grasa = metricas.get("grasa_actual")
    
    if grasa is None:
        return f"""
        <div class="metric-card">
            <div class="metric-label">Grasa Corporal</div>
            <div class="metric-value" style="color: #8b949e;">Sin datos</div>
        </div>
        """
    
    if grasa < 15:
        color = COLOR_EXCELENTE
        estado = "Bajo"
    elif grasa < 20:
        color = COLOR_BUENO
        estado = "Normal"
    else:
        color = COLOR_MALO
        estado = "Alto"
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">Grasa Corporal</div>
        <div class="metric-value" style="color: {color};">{grasa:.1f}%</div>
        <div class="metric-detail">{estado}</div>
    </div>
    """


def generar_card_masa_muscular(metricas):
    """Card Masa Muscular"""
    masa = metricas.get("masa_muscular_actual")
    
    if masa is None:
        return f"""
        <div class="metric-card">
            <div class="metric-label">Masa Muscular</div>
            <div class="metric-value" style="color: #8b949e;">Sin datos</div>
        </div>
        """
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">Masa Muscular</div>
        <div class="metric-value" style="color: {COLOR_BUENO};">{masa:.1f} kg</div>
    </div>
    """


def generar_card_fc_reposo(metricas):
    """Card FC en Reposo"""
    fc = metricas.get("fc_reposo_promedio")
    
    if fc is None:
        return f"""
        <div class="metric-card">
            <div class="metric-label">FC Reposo (7d)</div>
            <div class="metric-value" style="color: #8b949e;">Sin datos</div>
        </div>
        """
    
    if fc < 60:
        color = COLOR_EXCELENTE
        estado = "Excelente"
    elif fc < 70:
        color = COLOR_BUENO
        estado = "Bueno"
    else:
        color = COLOR_MALO
        estado = "Elevado"
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">FC Reposo (7d)</div>
        <div class="metric-value" style="color: {color};">{fc:.0f} bpm</div>
        <div class="metric-detail">{estado}</div>
    </div>
    """


def generar_card_pasos(metricas):
    """Card Pasos Diarios"""
    pasos = metricas.get("pasos_promedio")
    
    if pasos is None:
        return f"""
        <div class="metric-card">
            <div class="metric-label">Pasos (7d)</div>
            <div class="metric-value" style="color: #8b949e;">Sin datos</div>
        </div>
        """
    
    if pasos >= 10000:
        color = COLOR_EXCELENTE
        estado = "Excelente"
    elif pasos >= 7000:
        color = COLOR_BUENO
        estado = "Bueno"
    else:
        color = COLOR_MALO
        estado = "Bajo"
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">Pasos (7d)</div>
        <div class="metric-value" style="color: {color};">{pasos:,.0f}</div>
        <div class="metric-detail">{estado}</div>
    </div>
    """


def generar_card_presion(metricas):
    """Card Presión Arterial"""
    sistolica = metricas.get("presion_sistolica")
    diastolica = metricas.get("presion_diastolica")
    
    if sistolica is None or diastolica is None:
        return f"""
        <div class="metric-card">
            <div class="metric-label">Presión (7d)</div>
            <div class="metric-value" style="color: #8b949e;">Sin datos</div>
        </div>
        """
    
    if sistolica < 120 and diastolica < 80:
        color = COLOR_EXCELENTE
        estado = "Normal"
    elif sistolica < 130 and diastolica < 85:
        color = COLOR_BUENO
        estado = "Elevada"
    else:
        color = COLOR_MALO
        estado = "Alta"
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">Presión (7d)</div>
        <div class="metric-value" style="color: {color};">{sistolica:.0f}/{diastolica:.0f}</div>
        <div class="metric-detail">{estado}</div>
    </div>
    """


def generar_card_score(metricas):
    """Card Score Longevidad"""
    score = metricas.get("score_longevidad", 0)
    
    if score >= 85:
        color = COLOR_EXCELENTE
        estado = "Excelente"
    elif score >= 70:
        color = COLOR_BUENO
        estado = "Bueno"
    else:
        color = COLOR_MALO
        estado = "Mejora"
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">Score Longevidad</div>
        <div class="metric-value" style="color: {color};">{score:.0f}/100</div>
        <div class="metric-detail">{estado}</div>
    </div>
    """