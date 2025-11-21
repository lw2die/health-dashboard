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
    pai = metricas.get("pai_semanal", 0)
    if pai >= PAI_OBJETIVO_SEMANAL: color, estado = COLOR_EXCELENTE, "Óptimo"
    elif pai >= 50: color, estado = COLOR_BUENO, "Bueno"
    else: color, estado = COLOR_MALO, "Bajo"
    return f'<div class="metric-card"><div class="metric-label">PAI Semanal</div><div class="metric-value" style="color: {color};">{pai:.0f}</div><div class="metric-detail">{estado} (Objetivo: {PAI_OBJETIVO_SEMANAL})</div></div>'


def generar_card_peso(metricas):
    peso = metricas.get("peso_actual")
    if peso is None: return '<div class="metric-card"><div class="metric-label">Peso Actual</div><div class="metric-value" style="color: #8b949e;">Sin datos</div></div>'
    diff = peso - PESO_OBJETIVO
    if abs(diff) <= 2: color, estado = COLOR_EXCELENTE, "En objetivo"
    elif abs(diff) <= 5: color, estado = COLOR_BUENO, "Cerca"
    else: color, estado = COLOR_MALO, "Lejos"
    return f'<div class="metric-card"><div class="metric-label">Peso Actual</div><div class="metric-value" style="color: {color};">{peso:.1f} kg</div><div class="metric-detail">{estado} ({diff:+.1f} kg)</div></div>'


def generar_card_vo2max(metricas):
    vo2 = metricas.get("vo2max")
    if vo2 is None: return '<div class="metric-card"><div class="metric-label">VO2max (Medido)</div><div class="metric-value" style="color: #8b949e;">Sin datos</div></div>'
    if vo2 >= 40: color, estado = COLOR_EXCELENTE, "Excelente"
    elif vo2 >= 35: color, estado = COLOR_BUENO, "Bueno"
    else: color, estado = COLOR_MALO, "Bajo"
    return f'<div class="metric-card"><div class="metric-label">VO2max (Medido)</div><div class="metric-value" style="color: {color};">{vo2:.1f}</div><div class="metric-detail">{estado}</div></div>'


def generar_card_tsb(metricas):
    tsb = metricas.get("tsb_actual")
    tsb_dict = metricas.get("tsb_dict", {})
    if tsb is None: return '<div class="metric-card"><div class="metric-label">TSB Actual</div><div class="metric-value" style="color: #8b949e;">Sin datos</div></div>'
    if TSB_OPTIMO_MIN <= tsb <= TSB_OPTIMO_MAX: color, estado = COLOR_EXCELENTE, "Forma óptima"
    elif -20 < tsb < TSB_OPTIMO_MIN: color, estado = COLOR_BUENO, "Neutral"
    else: color, estado = COLOR_MALO, "Fatiga" if tsb < -20 else "Sobreentreno"
    return f'<div class="metric-card"><div class="metric-label">TSB Actual</div><div class="metric-value" style="color: {color};">{tsb:.1f}</div><div class="metric-detail">{estado}</div><div class="metric-detail" style="font-size: 0.8em; color: #8b949e;">CTL: {tsb_dict.get("ctl",0):.1f} | ATL: {tsb_dict.get("atl",0):.1f}</div></div>'


def generar_card_sueno(metricas):
    sueno = metricas.get("promedio_sueno")
    if sueno is None: return '<div class="metric-card"><div class="metric-label">Sueño (7 días)</div><div class="metric-value" style="color: #8b949e;">Sin datos</div></div>'
    if sueno >= 7: color, estado = COLOR_EXCELENTE, "Óptimo"
    elif sueno >= 6: color, estado = COLOR_BUENO, "Aceptable"
    else: color, estado = COLOR_MALO, "Insuficiente"
    return f'<div class="metric-card"><div class="metric-label">Sueño (7 días)</div><div class="metric-value" style="color: {color};">{sueno:.1f}h</div><div class="metric-detail">{estado}</div></div>'


def generar_card_spo2(metricas):
    spo2 = metricas.get("spo2_promedio")
    if spo2 is None: return '<div class="metric-card"><div class="metric-label">SpO2 (7 días)</div><div class="metric-value" style="color: #8b949e;">Sin datos</div></div>'
    if spo2 >= 95: color, estado = COLOR_EXCELENTE, "Normal"
    elif spo2 >= 90: color, estado = COLOR_BUENO, "Aceptable"
    else: color, estado = COLOR_MALO, "Bajo"
    return f'<div class="metric-card"><div class="metric-label">SpO2 (7 días)</div><div class="metric-value" style="color: {color};">{spo2:.1f}%</div><div class="metric-detail">{estado}</div></div>'


def generar_card_grasa(metricas):
    grasa = metricas.get("grasa_actual")
    if grasa is None: return '<div class="metric-card"><div class="metric-label">Grasa Corporal</div><div class="metric-value" style="color: #8b949e;">Sin datos</div></div>'
    if grasa < 18: color, estado = COLOR_EXCELENTE, "Bajo"
    elif grasa < 25: color, estado = COLOR_BUENO, "Normal"
    else: color, estado = COLOR_MALO, "Alto"
    return f'<div class="metric-card"><div class="metric-label">Grasa Corporal</div><div class="metric-value" style="color: {color};">{grasa:.1f}%</div><div class="metric-detail">{estado}</div></div>'


def generar_card_masa_muscular(metricas):
    masa = metricas.get("masa_muscular_actual")
    if masa is None: return '<div class="metric-card"><div class="metric-label">Masa Muscular</div><div class="metric-value" style="color: #8b949e;">Sin datos</div></div>'
    return f'<div class="metric-card"><div class="metric-label">Masa Muscular</div><div class="metric-value" style="color: {COLOR_BUENO};">{masa:.1f} kg</div></div>'


def generar_card_fc_reposo(metricas):
    fc = metricas.get("fc_reposo_promedio")
    if fc is None: return '<div class="metric-card"><div class="metric-label">FC Reposo (7d)</div><div class="metric-value" style="color: #8b949e;">Sin datos</div></div>'
    if fc < 60: color, estado = COLOR_EXCELENTE, "Excelente"
    elif fc < 70: color, estado = COLOR_BUENO, "Bueno"
    else: color, estado = COLOR_MALO, "Elevado"
    return f'<div class="metric-card"><div class="metric-label">FC Reposo (7d)</div><div class="metric-value" style="color: {color};">{fc:.0f} bpm</div><div class="metric-detail">{estado}</div></div>'


def generar_card_pasos(metricas):
    pasos = metricas.get("pasos_promedio")
    if pasos is None: return '<div class="metric-card"><div class="metric-label">Pasos (7d)</div><div class="metric-value" style="color: #8b949e;">Sin datos</div></div>'
    if pasos >= 10000: color, estado = COLOR_EXCELENTE, "Excelente"
    elif pasos >= 7000: color, estado = COLOR_BUENO, "Bueno"
    else: color, estado = COLOR_MALO, "Bajo"
    return f'<div class="metric-card"><div class="metric-label">Pasos (7d)</div><div class="metric-value" style="color: {color};">{pasos:,.0f}</div><div class="metric-detail">{estado}</div></div>'


def generar_card_presion(metricas):
    sis = metricas.get("presion_sistolica")
    dias = metricas.get("presion_diastolica")
    if sis is None: return '<div class="metric-card"><div class="metric-label">Presión (7d)</div><div class="metric-value" style="color: #8b949e;">Sin datos</div></div>'
    if sis < 120 and dias < 80: color, estado = COLOR_EXCELENTE, "Normal"
    elif sis < 130 and dias < 85: color, estado = COLOR_BUENO, "Elevada"
    else: color, estado = COLOR_MALO, "Alta"
    return f'<div class="metric-card"><div class="metric-label">Presión (7d)</div><div class="metric-value" style="color: {color};">{sis:.0f}/{dias:.0f}</div><div class="metric-detail">{estado}</div></div>'


def generar_card_glucemia(metricas):
    ayunas = metricas.get("glucemia_ayunas")
    post = metricas.get("glucemia_postprandial")
    if ayunas is None and post is None: return '<div class="metric-card"><div class="metric-label">🩸 Glucemia (7d)</div><div class="metric-value" style="color: #8b949e;">Sin datos</div></div>'
    
    txt_ayunas, col_ayunas = (f"{ayunas:.0f}", COLOR_EXCELENTE if ayunas < 100 else COLOR_BUENO if ayunas < 126 else COLOR_MALO) if ayunas else ("--", "#8b949e")
    txt_post, col_post = (f"{post:.0f}", COLOR_EXCELENTE if post < 140 else COLOR_BUENO if post < 200 else COLOR_MALO) if post else ("--", "#8b949e")
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">🩸 Glucemia (7d)</div>
        <div class="metric-value" style="color: {col_ayunas}; font-size: 1.5em;">{txt_ayunas}</div>
        <div class="metric-detail" style="color: {col_ayunas}; font-weight: 600;">Ayunas</div>
        <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(139, 148, 158, 0.2);">
            <div class="metric-value" style="color: {col_post}; font-size: 1.3em;">{txt_post}</div>
            <div class="metric-detail" style="color: {col_post}; font-weight: 600;">Postprandial</div>
        </div>
    </div>
    """


def generar_card_hba1c(metricas):
    """Card HbA1c Estimada (fórmula ADAG)"""
    a1c = metricas.get("hba1c")
    glucosa_prom = metricas.get("hba1c_glucosa_promedio")
    
    if a1c is None:
        return '<div class="metric-card"><div class="metric-label">HbA1c Estimada</div><div class="metric-value" style="color: #8b949e;">Sin datos</div></div>'
    
    if a1c < 5.7: color, estado = COLOR_EXCELENTE, "Normal"
    elif a1c < 6.5: color, estado = COLOR_BUENO, "Prediabetes"
    else: color, estado = COLOR_MALO, "Diabetes"
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">HbA1c Estimada (90d)</div>
        <div class="metric-value" style="color: {color};">{a1c:.1f}%</div>
        <div class="metric-detail" style="color: {color}; font-weight: 600;">{estado}</div>
        <div class="metric-detail" style="font-size: 0.8em; color: #8b949e; margin-top: 5px;">
            Gluc. prom: {glucosa_prom} mg/dL
        </div>
    </div>
    """


def generar_card_score(metricas):
    score = metricas.get("score_longevidad", 0)
    if score >= 85: color, estado = COLOR_EXCELENTE, "Excelente"
    elif score >= 70: color, estado = COLOR_BUENO, "Bueno"
    else: color, estado = COLOR_MALO, "Mejora"
    return f'<div class="metric-card"><div class="metric-label">Score Longevidad</div><div class="metric-value" style="color: {color};">{score:.0f}/100</div><div class="metric-detail">{estado}</div></div>'