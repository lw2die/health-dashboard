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


def generar_card_glucemia(metricas):
    """Card Glucemia - Ayunas y Postprandial (7 días)"""
    ayunas = metricas.get("glucemia_ayunas")
    postprandial = metricas.get("glucemia_postprandial")
    
    if ayunas is None and postprandial is None:
        return f"""
        <div class="metric-card">
            <div class="metric-label">🩸 Glucemia (7d)</div>
            <div class="metric-value" style="color: #8b949e;">Sin datos</div>
        </div>
        """
    
    # Colores para ayunas (normal: 70-100 mg/dL)
    if ayunas:
        if 70 <= ayunas <= 100:
            color_ayunas = COLOR_EXCELENTE
            estado_ayunas = "Normal"
        elif 100 < ayunas <= 125:
            color_ayunas = COLOR_BUENO
            estado_ayunas = "Prediabetes"
        else:
            color_ayunas = COLOR_MALO
            estado_ayunas = "Elevada"
    else:
        color_ayunas = "#8b949e"
        estado_ayunas = "Sin datos"
    
    # Colores para postprandial (normal: <140 mg/dL a las 2h)
    if postprandial:
        if postprandial < 140:
            color_post = COLOR_EXCELENTE
            estado_post = "Normal"
        elif 140 <= postprandial < 200:
            color_post = COLOR_BUENO
            estado_post = "Prediabetes"
        else:
            color_post = COLOR_MALO
            estado_post = "Elevada"
    else:
        color_post = "#8b949e"
        estado_post = "Sin datos"
    
    ayunas_texto = f"{ayunas:.0f}" if ayunas else "---"
    post_texto = f"{postprandial:.0f}" if postprandial else "---"
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">🩸 Glucemia (7d)</div>
        <div class="metric-value" style="color: {color_ayunas}; font-size: 1.5em;">{ayunas_texto}</div>
        <div class="metric-detail" style="color: {color_ayunas}; font-weight: 600;">Ayunas: {estado_ayunas}</div>
        <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(139, 148, 158, 0.2);">
            <div class="metric-value" style="color: {color_post}; font-size: 1.3em;">{post_texto}</div>
            <div class="metric-detail" style="color: {color_post}; font-weight: 600;">Postprandial: {estado_post}</div>
        </div>
    </div>
    """


def generar_card_gmi(metricas):
    """Card GMI (Glucose Management Indicator) - 90 días"""
    gmi = metricas.get("gmi")
    glucosa_prom = metricas.get("gmi_glucosa_promedio")
    num_mediciones = metricas.get("gmi_num_mediciones", 0)
    
    if gmi is None:
        return f"""
        <div class="metric-card">
            <div class="metric-label">📈 GMI Estimado</div>
            <div class="metric-value" style="color: #8b949e;">Sin datos</div>
            <div class="metric-detail" style="font-size: 0.75em; color: #8b949e;">Requiere mediciones de glucosa</div>
        </div>
        """
    
    # Colores según niveles de HbA1c/GMI
    # <5.7% = Normal, 5.7-6.4% = Prediabetes, ≥6.5% = Diabetes
    if gmi < 5.7:
        color = COLOR_EXCELENTE
        estado = "Normal"
    elif gmi < 6.5:
        color = COLOR_BUENO
        estado = "Prediabetes"
    else:
        color = COLOR_MALO
        estado = "Diabetes"
    
    glucosa_texto = f"{glucosa_prom:.0f}" if glucosa_prom else "---"
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">📈 GMI Estimado (90d)</div>
        <div class="metric-value" style="color: {color};">{gmi:.1f}%</div>
        <div class="metric-detail" style="color: {color}; font-weight: 600;">{estado}</div>
        <div class="metric-detail" style="font-size: 0.8em; color: #8b949e; margin-top: 5px;">
            Glucosa prom: {glucosa_texto} mg/dL
        </div>
        <div class="metric-detail" style="font-size: 0.75em; color: #8b949e;">
            ⚠️ {num_mediciones} mediciones (estimación aproximada)
        </div>
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