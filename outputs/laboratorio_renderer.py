#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Renderizador de sección de Laboratorio Científico
VERSIÓN CORREGIDA - Maneja None/vacíos correctamente
"""

from config import COLOR_EXCELENTE, COLOR_BUENO, COLOR_MALO


def generar_html_laboratorio(datos_laboratorio):
    """Genera HTML de la sección de laboratorio científico"""
    if not datos_laboratorio:
        return ""
    
    scores = datos_laboratorio.get("scores", {})
    longevity = datos_laboratorio.get("longevity_score", 0)
    cardio = scores.get("CardioScore", 0)
    metabolic = scores.get("MetabolicScore", 0)
    inflammation = scores.get("InflammationScore", 0)
    hormone = scores.get("HormoneScore", 0)
    
    return f"""
    <div class="laboratorio-section">
        <h2>🧬 Dashboard Científico</h2>
        <div class="scores-grid">
            <div class="score-card score-main">
                <div class="score-label">Longevity Score</div>
                <div class="score-value" style="color: {_get_color_score(longevity)};">{longevity:.1f}/100</div>
                <div class="subscore-description">Puntuación general de salud basada en análisis de laboratorio (biomarcadores sanguíneos)</div>
            </div>
            <div class="score-card">
                <div class="score-label">CardioScore</div>
                <div class="score-value" style="color: {_get_color_score(cardio)};">{cardio:.1f}</div>
                <div class="subscore-description">Colesterol total, HDL, LDL, triglicéridos y homocisteína</div>
            </div>
            <div class="score-card">
                <div class="score-label">MetabolicScore</div>
                <div class="score-value" style="color: {_get_color_score(metabolic)};">{metabolic:.1f}</div>
                <div class="subscore-description">Glucosa, HbA1c, insulina y marcadores de resistencia insulínica</div>
            </div>
            <div class="score-card">
                <div class="score-label">InflammationScore</div>
                <div class="score-value" style="color: {_get_color_score(inflammation)};">{inflammation:.1f}</div>
                <div class="subscore-description">Proteína C reactiva, ferritina y otros marcadores inflamatorios</div>
            </div>
            <div class="score-card">
                <div class="score-label">HormoneScore</div>
                <div class="score-value" style="color: {_get_color_score(hormone)};">{hormone:.1f}</div>
                <div class="subscore-description">Testosterona, vitamina D, hormonas tiroideas y cortisol</div>
            </div>
        </div>
        <div class="alertas-section">
            <h3>⚠️ Alertas</h3>
            {_generar_alertas_html(datos_laboratorio.get("alertas", []))}
        </div>
    </div>
    """


def _get_color_score(score):
    """Retorna color según el score"""
    if score >= 80:
        return COLOR_EXCELENTE
    elif score >= 60:
        return COLOR_BUENO
    else:
        return COLOR_MALO


def _generar_alertas_html(alertas):
    """Genera HTML de las alertas"""
    if not alertas:
        return "<p style='color: #8b949e;'>Sin alertas</p>"
    
    items = []
    for alerta in alertas:
        severidad = alerta.get("severidad", "INFO")
        color = "#f85149" if severidad == "CRITICA" else "#f0883e" if severidad == "ALTA" else "#d29922"
        
        items.append(f"""
        <div class="alerta-item" style="border-left: 4px solid {color};">
            <div style="font-weight: bold; color: {color};">{alerta.get("titulo", "")}</div>
            <div style="color: #c9d1d9; margin-top: 5px;">{alerta.get("descripcion", "")}</div>
        </div>
        """)
    
    return "".join(items)


def generar_tabla_entrenamientos(entrenamientos):
    """Genera tabla HTML de entrenamientos recientes - CORREGIDO"""
    from datetime import datetime
    from config import COLOR_EXCELENTE, COLOR_BUENO, COLOR_MALO
    
    if not entrenamientos:
        return "<p style='color: #8b949e;'>Sin entrenamientos</p>"
    
    filas = []
    for e in entrenamientos:
        fecha = datetime.fromisoformat(e["fecha"].replace("Z", "+00:00"))
        fecha_str = fecha.strftime("%d/%m %H:%M")
        
        # ✅ CORRECCIÓN: Manejar duracion None
        duracion = e.get('duracion', 0)
        duracion_str = f"{duracion:.0f} min" if duracion and duracion > 0 else "–"
        
        # ✅ CORRECCIÓN: Manejar fc_promedio None
        fc_promedio = e.get('fc_promedio')
        fc_str = str(int(fc_promedio)) if fc_promedio else "–"
        
        pai = e.get("pai", 0)
        pai_color = COLOR_EXCELENTE if pai > 10 else COLOR_BUENO if pai > 5 else COLOR_MALO
        
        fila = f"""
        <tr>
            <td>{fecha_str}</td>
            <td>{e['tipo']}</td>
            <td>{duracion_str}</td>
            <td>{fc_str}</td>
            <td style="color: {pai_color}; font-weight: bold;">{pai:.1f}</td>
            <td>{e.get('zona', 'N/A')}</td>
        </tr>
        """
        filas.append(fila)
    
    return f"""
    <table>
        <thead>
            <tr>
                <th>Fecha</th>
                <th>Tipo</th>
                <th>Duración</th>
                <th>FC Prom</th>
                <th>PAI</th>
                <th>Zona</th>
            </tr>
        </thead>
        <tbody>
            {"".join(filas)}
        </tbody>
    </table>
    """


def generar_recomendaciones_html(recomendaciones):
    """Genera HTML de recomendaciones"""
    if not recomendaciones:
        return "<p style='color: #8b949e;'>Sin recomendaciones</p>"
    
    items = []
    for rec in recomendaciones:
        items.append(f"<li>{rec}</li>")
    
    return f"""
    <ul class="recommendations-list">
        {"".join(items)}
    </ul>
    """