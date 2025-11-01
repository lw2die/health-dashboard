#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Constructor HTML - CSS, JavaScript y estructura del dashboard
VERSIÓN CORREGIDA - Maneja gráficos vacíos
"""

from datetime import datetime, timedelta
from config import PAI_OBJETIVO_SEMANAL, PESO_OBJETIVO


def _obtener_hora_argentina():
    """Retorna la hora actual en Argentina (UTC-3)"""
    return datetime.utcnow() - timedelta(hours=3)


def generar_css():
    """Genera todo el CSS del dashboard"""
    return """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
            color: #c9d1d9;
            padding: 20px;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        h1 {
            font-size: 2.5em;
            color: #58a6ff;
            margin-bottom: 10px;
        }
        
        h2 {
            color: #58a6ff;
            margin: 30px 0 20px 0;
            font-size: 1.8em;
        }
        
        h3 {
            color: #79c0ff;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .subtitle {
            color: #8b949e;
            font-size: 1.1em;
        }
        
        /* ═══════════════════════════════════════ */
        /* HEALTHSPAN INDEX - HERO CARD */
        /* ═══════════════════════════════════════ */
        
        .healthspan-hero {
            background: linear-gradient(135deg, #1a3a52 0%, #2d5a7b 100%);
            border: 2px solid #58a6ff;
            border-radius: 16px;
            padding: 40px;
            margin-bottom: 40px;
            box-shadow: 0 8px 32px rgba(88, 166, 255, 0.4);
        }
        
        .healthspan-title {
            text-align: center;
            font-size: 1.5em;
            color: #79c0ff;
            margin-bottom: 20px;
            letter-spacing: 2px;
        }
        
        .healthspan-main-score {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .healthspan-value {
            font-size: 5em;
            font-weight: bold;
        }
        
        .healthspan-status {
            font-size: 1.3em;
            font-weight: 600;
            margin-top: 10px;
        }
        
        .healthspan-subscores {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .subscore-card {
            background: rgba(22, 27, 34, 0.6);
            border: 1px solid #30363d;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }
        
        .subscore-label {
            color: #8b949e;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        
        .subscore-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .subscore-bar {
            height: 6px;
            background: #161b22;
            border-radius: 3px;
            overflow: hidden;
        }
        
        .subscore-fill {
            height: 100%;
            transition: width 0.3s ease;
        }
        
        .subscore-description {
            color: #6e7681;
            font-size: 0.75em;
            margin-top: 10px;
            line-height: 1.3;
            font-style: italic;
        }
        
        .healthspan-description {
            color: #8b949e;
            font-size: 0.85em;
            margin-top: 5px;
            text-align: center;
            font-style: italic;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .metric-card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(88, 166, 255, 0.3);
        }
        
        .metric-label {
            color: #8b949e;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .metric-detail {
            color: #8b949e;
            font-size: 0.9em;
        }
        
        .charts-section {
            margin: 40px 0;
        }
        
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
        }
        
        .chart-container {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
        }
        
        .chart-empty {
            color: #8b949e;
            text-align: center;
            padding: 40px;
            font-style: italic;
        }
        
        .training-section, .recommendations-section {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 25px;
            margin: 30px 0;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #30363d;
        }
        
        th {
            color: #58a6ff;
            font-weight: 600;
        }
        
        tr:hover {
            background: #0d1117;
        }
        
        .recommendations-list {
            list-style: none;
            padding: 0;
        }
        
        .recommendations-list li {
            padding: 12px;
            margin: 10px 0;
            background: #0d1117;
            border-left: 3px solid #58a6ff;
            border-radius: 4px;
        }
        
        .laboratorio-section {
            background: #161b22;
            border: 2px solid #58a6ff;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 40px;
        }
        
        .scores-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .score-card {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }
        
        .score-main {
            grid-column: 1 / -1;
            border: 2px solid #58a6ff;
        }
        
        .score-label {
            color: #8b949e;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        
        .score-value {
            font-size: 2.5em;
            font-weight: bold;
        }
        
        .alertas-section {
            margin-top: 30px;
        }
        
        .alerta-item {
            background: #0d1117;
            padding: 15px;
            margin: 10px 0;
            border-radius: 6px;
        }
        
        @media (max-width: 768px) {
            .healthspan-value {
                font-size: 3.5em;
            }
            .healthspan-subscores {
                grid-template-columns: 1fr 1fr;
            }
            .charts-grid {
                grid-template-columns: 1fr;
            }
            h1 {
                font-size: 1.8em;
            }
        }
        
        /* ESTILOS PARA SECCIÓN DE LOGS */
        .logs-section {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 25px;
            margin: 30px 0;
        }
        
        .logs-summary {
            background: #0d1117;
            border-radius: 6px;
            padding: 20px;
            margin-bottom: 15px;
        }
        
        .logs-summary p {
            margin: 8px 0;
            font-size: 1.05em;
        }
        
        .logs-toggle-btn {
            background: #238636;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
            margin-top: 15px;
            transition: background 0.2s;
        }
        
        .logs-toggle-btn:hover {
            background: #2ea043;
        }
        
        .logs-toggle-btn.expanded {
            background: #da3633;
        }
        
        #logs-content {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 15px;
            max-height: 500px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            line-height: 1.4;
            white-space: pre-wrap;
            word-wrap: break-word;
            color: #c9d1d9;
        }
        
        .logs-hidden {
            display: none;
        }
        
        .log-info { color: #58a6ff; }
        .log-warning { color: #d29922; }
        .log-error { color: #f85149; }
        .log-success { color: #3fb950; }
    </style>
    """


def generar_javascript(datos_graficos):
    """Genera todo el JavaScript para los gráficos Plotly - CORREGIDO"""
    
    # ✅ Validar que cada gráfico tenga datos
    def tiene_datos(datos, campo='fechas'):
        return datos and datos.get(campo) and len(datos.get(campo, [])) > 0
    
    js = """
        const layout_config = {
            paper_bgcolor: '#0d1117',
            plot_bgcolor: '#161b22',
            font: { color: '#c9d1d9' },
            margin: { l: 40, r: 20, t: 20, b: 40 },
            showlegend: true,
            height: 300
        };
    """
    
    # PAI
    if tiene_datos(datos_graficos.get('pai', {})):
        js += f"""
        // PAI: Diario + Ventana Móvil 7 días
        const pai_diario = {{
            x: {datos_graficos['pai']['fechas']},
            y: {datos_graficos['pai']['pai_diario']},
            type: 'bar',
            name: 'PAI Diario',
            marker: {{ color: '#58a6ff' }}
        }};
        
        const pai_ventana = {{
            x: {datos_graficos['pai']['fechas']},
            y: {datos_graficos['pai']['pai_ventana_movil']},
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Ventana 7d',
            line: {{ color: '#f85149', width: 3 }},
            marker: {{ size: 8 }},
            yaxis: 'y2'
        }};
        
        Plotly.newPlot('pai-chart', [pai_diario, pai_ventana], {{
            ...layout_config,
            yaxis: {{ title: 'PAI Diario', gridcolor: '#30363d' }},
            yaxis2: {{
                title: 'PAI Acumulado 7d',
                overlaying: 'y',
                side: 'right',
                gridcolor: '#30363d'
            }},
            xaxis: {{ gridcolor: '#30363d' }},
            shapes: [{{
                type: 'line',
                x0: 0, x1: 1, xref: 'paper',
                yref: 'y2',
                y0: {PAI_OBJETIVO_SEMANAL}, y1: {PAI_OBJETIVO_SEMANAL},
                line: {{ color: '#3fb950', width: 2, dash: 'dot' }}
            }}]
        }});
        """
    else:
        js += """
        document.getElementById('pai-chart').innerHTML = '<div class="chart-empty">Sin datos de PAI</div>';
        """
    
    # Peso
    if tiene_datos(datos_graficos.get('peso', {})):
        js += f"""
        // Peso
        const peso_data = {{
            x: {datos_graficos['peso']['fechas']},
            y: {datos_graficos['peso']['valores']},
            type: 'scatter',
            mode: 'lines+markers',
            line: {{ color: '#f85149', width: 2 }},
            marker: {{ size: 6 }}
        }};
        
        Plotly.newPlot('peso-chart', [peso_data], {{
            ...layout_config,
            yaxis: {{ title: 'Peso (kg)', gridcolor: '#30363d' }},
            xaxis: {{ gridcolor: '#30363d' }},
            shapes: [{{
                type: 'line',
                x0: 0, x1: 1, xref: 'paper',
                y0: {PESO_OBJETIVO}, y1: {PESO_OBJETIVO},
                line: {{ color: '#3fb950', width: 1, dash: 'dot' }}
            }}]
        }});
        """
    else:
        js += """
        document.getElementById('peso-chart').innerHTML = '<div class="chart-empty">Sin datos de peso</div>';
        """
    
    # TSB
    if tiene_datos(datos_graficos.get('tsb', {})):
        js += f"""
        // TSB + CTL + ATL
        const tsb_data = {{
            x: {datos_graficos['tsb']['fechas']},
            y: {datos_graficos['tsb']['tsb']},
            type: 'scatter',
            mode: 'lines',
            name: 'TSB',
            fill: 'tozeroy',
            line: {{ color: '#ffa657', width: 2 }}
        }};
        
        const ctl_data = {{
            x: {datos_graficos['tsb']['fechas']},
            y: {datos_graficos['tsb']['ctl']},
            type: 'scatter',
            mode: 'lines',
            name: 'CTL (Fitness)',
            line: {{ color: '#3fb950', width: 2 }}
        }};
        
        const atl_data = {{
            x: {datos_graficos['tsb']['fechas']},
            y: {datos_graficos['tsb']['atl']},
            type: 'scatter',
            mode: 'lines',
            name: 'ATL (Fatiga)',
            line: {{ color: '#f85149', width: 2 }}
        }};
        
        Plotly.newPlot('tsb-chart', [tsb_data, ctl_data, atl_data], {{
            ...layout_config,
            yaxis: {{ title: 'Puntuación', gridcolor: '#30363d' }},
            xaxis: {{ gridcolor: '#30363d' }}
        }});
        """
    else:
        js += """
        document.getElementById('tsb-chart').innerHTML = '<div class="chart-empty">Sin datos de TSB</div>';
        """
    
    # SpO2
    if tiene_datos(datos_graficos.get('spo2', {})):
        js += f"""
        // SpO2
        Plotly.newPlot('spo2-chart', [{{
            x: {datos_graficos['spo2']['fechas']},
            y: {datos_graficos['spo2']['valores']},
            type: 'scatter',
            mode: 'lines+markers',
            line: {{ color: '#79c0ff', width: 2 }}
        }}], {{
            ...layout_config,
            yaxis: {{ title: 'SpO2 (%)', gridcolor: '#30363d' }},
            xaxis: {{ gridcolor: '#30363d' }}
        }});
        """
    else:
        js += """
        document.getElementById('spo2-chart').innerHTML = '<div class="chart-empty">Sin datos de SpO2</div>';
        """
    
    # Grasa Corporal
    if tiene_datos(datos_graficos.get('grasa', {})):
        js += f"""
        // Grasa Corporal
        Plotly.newPlot('grasa-chart', [{{
            x: {datos_graficos['grasa']['fechas']},
            y: {datos_graficos['grasa']['valores']},
            type: 'scatter',
            mode: 'lines+markers',
            line: {{ color: '#ffa657', width: 2 }}
        }}], {{
            ...layout_config,
            yaxis: {{ title: 'Grasa (%)', gridcolor: '#30363d' }},
            xaxis: {{ gridcolor: '#30363d' }}
        }});
        """
    else:
        js += """
        document.getElementById('grasa-chart').innerHTML = '<div class="chart-empty">Sin datos de grasa corporal</div>';
        """
    
    # Masa Muscular
    if tiene_datos(datos_graficos.get('masa_muscular', {})):
        js += f"""
        // Masa Muscular
        Plotly.newPlot('masa-chart', [{{
            x: {datos_graficos['masa_muscular']['fechas']},
            y: {datos_graficos['masa_muscular']['valores']},
            type: 'scatter',
            mode: 'lines+markers',
            line: {{ color: '#3fb950', width: 2 }}
        }}], {{
            ...layout_config,
            yaxis: {{ title: 'Masa (kg)', gridcolor: '#30363d' }},
            xaxis: {{ gridcolor: '#30363d' }}
        }});
        """
    else:
        js += """
        document.getElementById('masa-chart').innerHTML = '<div class="chart-empty">Sin datos de masa muscular</div>';
        """
    
    # FC Reposo
    if tiene_datos(datos_graficos.get('fc_reposo', {})):
        js += f"""
        // FC Reposo
        Plotly.newPlot('fc-reposo-chart', [{{
            x: {datos_graficos['fc_reposo']['fechas']},
            y: {datos_graficos['fc_reposo']['valores']},
            type: 'scatter',
            mode: 'lines+markers',
            line: {{ color: '#f85149', width: 2 }}
        }}], {{
            ...layout_config,
            yaxis: {{ title: 'FC (bpm)', gridcolor: '#30363d' }},
            xaxis: {{ gridcolor: '#30363d' }}
        }});
        """
    else:
        js += """
        document.getElementById('fc-reposo-chart').innerHTML = '<div class="chart-empty">Sin datos de FC reposo</div>';
        """
    
    # FC Diurna (Continua) - ✅ AGREGADO
    if tiene_datos(datos_graficos.get('frecuencia_cardiaca', {})):
        js += f"""
        // Frecuencia Cardíaca Diurna
        Plotly.newPlot('fc-diurna-chart', [
            {{
                x: {datos_graficos['frecuencia_cardiaca']['fechas']},
                y: {datos_graficos['frecuencia_cardiaca']['bpm_min']},
                type: 'scatter',
                mode: 'lines',
                name: 'Mínima',
                line: {{ color: '#58a6ff', width: 1 }},
                fill: 'tonexty'
            }},
            {{
                x: {datos_graficos['frecuencia_cardiaca']['fechas']},
                y: {datos_graficos['frecuencia_cardiaca']['bpm_promedio']},
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Promedio',
                line: {{ color: '#ffa657', width: 2 }}
            }},
            {{
                x: {datos_graficos['frecuencia_cardiaca']['fechas']},
                y: {datos_graficos['frecuencia_cardiaca']['bpm_max']},
                type: 'scatter',
                mode: 'lines',
                name: 'Máxima',
                line: {{ color: '#f85149', width: 1 }},
                fill: 'tonexty'
            }}
        ], {{
            ...layout_config,
            yaxis: {{ title: 'FC (bpm)', gridcolor: '#30363d' }},
            xaxis: {{ gridcolor: '#30363d' }}
        }});
        """
    else:
        js += """
        document.getElementById('fc-diurna-chart').innerHTML = '<div class="chart-empty">Sin datos de FC diurna</div>';
        """
    
    # Pasos
    if tiene_datos(datos_graficos.get('pasos', {})):
        js += f"""
        // Pasos
        Plotly.newPlot('pasos-chart', [{{
            x: {datos_graficos['pasos']['fechas']},
            y: {datos_graficos['pasos']['valores']},
            type: 'bar',
            marker: {{ color: '#58a6ff' }}
        }}], {{
            ...layout_config,
            yaxis: {{ title: 'Pasos', gridcolor: '#30363d' }},
            xaxis: {{ gridcolor: '#30363d' }}
        }});
        """
    else:
        js += """
        document.getElementById('pasos-chart').innerHTML = '<div class="chart-empty">Sin datos de pasos</div>';
        """
    
    # Presión Arterial
    if tiene_datos(datos_graficos.get('presion_arterial', {})):
        js += f"""
        // Presión Arterial
        Plotly.newPlot('presion-chart', [
            {{
                x: {datos_graficos['presion_arterial']['fechas']},
                y: {datos_graficos['presion_arterial']['sistolica']},
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Sistólica',
                line: {{ color: '#f85149', width: 2 }}
            }},
            {{
                x: {datos_graficos['presion_arterial']['fechas']},
                y: {datos_graficos['presion_arterial']['diastolica']},
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Diastólica',
                line: {{ color: '#58a6ff', width: 2 }}
            }}
        ], {{
            ...layout_config,
            yaxis: {{ title: 'mmHg', gridcolor: '#30363d' }},
            xaxis: {{ gridcolor: '#30363d' }}
        }});
        """
    else:
        js += """
        document.getElementById('presion-chart').innerHTML = '<div class="chart-empty">Sin datos de presión arterial</div>';
        """
    
    # Glucosa en Sangre
    if tiene_datos(datos_graficos.get('glucosa', {})):
        js += f"""
        // Glucosa en Sangre
        Plotly.newPlot('glucosa-chart', [{{
            x: {datos_graficos['glucosa']['fechas']},
            y: {datos_graficos['glucosa']['valores']},
            type: 'scatter',
            mode: 'lines+markers',
            line: {{ color: '#d29922', width: 2 }},
            marker: {{ size: 8 }}
        }}], {{
            ...layout_config,
            yaxis: {{ title: 'mg/dL', gridcolor: '#30363d' }},
            xaxis: {{ gridcolor: '#30363d' }},
            shapes: [
                {{
                    type: 'rect',
                    xref: 'paper',
                    x0: 0, x1: 1,
                    y0: 70, y1: 100,
                    fillcolor: '#3fb950',
                    opacity: 0.1,
                    line: {{ width: 0 }}
                }}
            ]
        }});
        """
    else:
        js += """
        document.getElementById('glucosa-chart').innerHTML = '<div class="chart-empty">Sin datos de glucosa</div>';
        """
    
    # Masa Ósea
    if tiene_datos(datos_graficos.get('masa_osea', {})):
        js += f"""
        // Masa Ósea
        Plotly.newPlot('masa-osea-chart', [{{
            x: {datos_graficos['masa_osea']['fechas']},
            y: {datos_graficos['masa_osea']['valores']},
            type: 'scatter',
            mode: 'lines+markers',
            line: {{ color: '#79c0ff', width: 2 }}
        }}], {{
            ...layout_config,
            yaxis: {{ title: 'Masa (kg)', gridcolor: '#30363d' }},
            xaxis: {{ gridcolor: '#30363d' }}
        }});
        """
    else:
        js += """
        document.getElementById('masa-osea-chart').innerHTML = '<div class="chart-empty">Sin datos de masa ósea</div>';
        """
    
    # Masa de Agua
    if tiene_datos(datos_graficos.get('masa_agua', {})):
        js += f"""
        // Masa de Agua Corporal
        Plotly.newPlot('masa-agua-chart', [{{
            x: {datos_graficos['masa_agua']['fechas']},
            y: {datos_graficos['masa_agua']['valores']},
            type: 'scatter',
            mode: 'lines+markers',
            line: {{ color: '#58a6ff', width: 2 }},
            fill: 'tozeroy',
            fillcolor: 'rgba(88, 166, 255, 0.1)'
        }}], {{
            ...layout_config,
            yaxis: {{ title: 'Masa (kg)', gridcolor: '#30363d' }},
            xaxis: {{ gridcolor: '#30363d' }}
        }});
        """
    else:
        js += """
        document.getElementById('masa-agua-chart').innerHTML = '<div class="chart-empty">Sin datos de masa de agua</div>';
        """
    
    # Tasa Metabólica Basal
    if tiene_datos(datos_graficos.get('tasa_metabolica', {})):
        js += f"""
        // Tasa Metabólica Basal
        Plotly.newPlot('tmb-chart', [{{
            x: {datos_graficos['tasa_metabolica']['fechas']},
            y: {datos_graficos['tasa_metabolica']['valores']},
            type: 'scatter',
            mode: 'lines+markers',
            line: {{ color: '#ffa657', width: 2 }}
        }}], {{
            ...layout_config,
            yaxis: {{ title: 'kcal/día', gridcolor: '#30363d' }},
            xaxis: {{ gridcolor: '#30363d' }}
        }});
        """
    else:
        js += """
        document.getElementById('tmb-chart').innerHTML = '<div class="chart-empty">Sin datos de tasa metabólica</div>';
        """
    
    # Distancia Recorrida
    if tiene_datos(datos_graficos.get('distancia', {})):
        js += f"""
        // Distancia Recorrida
        Plotly.newPlot('distancia-chart', [{{
            x: {datos_graficos['distancia']['fechas']},
            y: {datos_graficos['distancia']['valores']},
            type: 'bar',
            marker: {{ 
                color: '#58a6ff',
                line: {{ color: '#1f6feb', width: 1 }}
            }}
        }}], {{
            ...layout_config,
            yaxis: {{ title: 'Distancia (km)', gridcolor: '#30363d' }},
            xaxis: {{ gridcolor: '#30363d' }}
        }});
        """
    else:
        js += """
        document.getElementById('distancia-chart').innerHTML = '<div class="chart-empty">Sin datos de distancia</div>';
        """
    
    # Calorías Totales
    if tiene_datos(datos_graficos.get('calorias_totales', {})):
        js += f"""
        // Calorías Totales
        Plotly.newPlot('calorias-chart', [{{
            x: {datos_graficos['calorias_totales']['fechas']},
            y: {datos_graficos['calorias_totales']['valores']},
            type: 'bar',
            marker: {{ 
                color: '#ffa657',
                line: {{ color: '#d4a72c', width: 1 }}
            }}
        }}], {{
            ...layout_config,
            yaxis: {{ title: 'Calorías (kcal)', gridcolor: '#30363d' }},
            xaxis: {{ gridcolor: '#30363d' }}
        }});
        """
    else:
        js += """
        document.getElementById('calorias-chart').innerHTML = '<div class="chart-empty">Sin datos de calorías</div>';
        """
    
    # Gráfico de Sueño (barras apiladas por fase)
    if tiene_datos(datos_graficos.get('sueno', {})):
        sueno_data = datos_graficos['sueno']
        js += f"""
        // Gráfico de Sueño - Barras Apiladas
        Plotly.newPlot('sueno-chart', [
            {{
                x: {sueno_data['fechas']},
                y: {sueno_data['deep']},
                name: 'Profundo',
                type: 'bar',
                marker: {{ color: '#1f6feb' }}
            }},
            {{
                x: {sueno_data['fechas']},
                y: {sueno_data['light']},
                name: 'Ligero',
                type: 'bar',
                marker: {{ color: '#d29922' }}
            }},
            {{
                x: {sueno_data['fechas']},
                y: {sueno_data['rem']},
                name: 'REM',
                type: 'bar',
                marker: {{ color: '#8957e5' }}
            }},
            {{
                x: {sueno_data['fechas']},
                y: {sueno_data['awake']},
                name: 'Despierto',
                type: 'bar',
                marker: {{ color: '#f85149' }}
            }}
        ], {{
            ...layout_config,
            barmode: 'stack',
            yaxis: {{ title: 'Horas', gridcolor: '#30363d' }},
            xaxis: {{ gridcolor: '#30363d' }},
            showlegend: true,
            legend: {{ 
                orientation: 'h',
                yanchor: 'bottom',
                y: 1.02,
                xanchor: 'right',
                x: 1,
                bgcolor: 'rgba(22, 27, 34, 0.8)'
            }}
        }});
        """
    else:
        js += """
        document.getElementById('sueno-chart').innerHTML = '<div class="chart-empty">Sin datos de sueño</div>';
        """
    
    # JavaScript para logs
    js += """
    
    // FUNCIONES PARA LOGS
    function toggleLogs() {
        const logsContent = document.getElementById('logs-content');
        const toggleBtn = document.getElementById('logs-toggle-btn');
        
        if (logsContent.classList.contains('logs-hidden')) {
            logsContent.classList.remove('logs-hidden');
            toggleBtn.textContent = '▲ Ocultar logs';
            toggleBtn.classList.add('expanded');
        } else {
            logsContent.classList.add('logs-hidden');
            toggleBtn.textContent = '▼ Ver logs completos (últimas 500 líneas)';
            toggleBtn.classList.remove('expanded');
        }
    }
    
    function formatearLogs() {
        const logsContent = document.getElementById('logs-content');
        if (!logsContent) return;
        
        let html = logsContent.innerHTML;
        
        // Colorear según nivel de log
        html = html.replace(/\\[INFO\\]/g, '<span class="log-info">[INFO]</span>');
        html = html.replace(/\\[WARNING\\]/g, '<span class="log-warning">[WARNING]</span>');
        html = html.replace(/\\[ERROR\\]/g, '<span class="log-error">[ERROR]</span>');
        html = html.replace(/✅/g, '<span class="log-success">✅</span>');
        html = html.replace(/❌/g, '<span class="log-error">❌</span>');
        html = html.replace(/⚠️/g, '<span class="log-warning">⚠️</span>');
        
        logsContent.innerHTML = html;
    }
    
    // Ejecutar al cargar la página
    document.addEventListener('DOMContentLoaded', formatearLogs);
    """
    
    return js


def _generar_healthspan_hero(healthspan_data):
    """Genera el hero card de Healthspan Index"""
    if not healthspan_data:
        return ""
    
    index = healthspan_data.get("healthspan_index", 0)
    status = healthspan_data.get("status", "")
    fitness = healthspan_data.get("fitness_score", 0)
    body = healthspan_data.get("body_score", 0)
    recovery = healthspan_data.get("recovery_score", 0)
    metabolic = healthspan_data.get("metabolic_score", 0)
    functional = healthspan_data.get("functional_score", 0)
    
    # Determinar color principal
    if index >= 85:
        main_color = "#3fb950"
        status_color = "#3fb950"
    elif index >= 70:
        main_color = "#58a6ff"
        status_color = "#58a6ff"
    elif index >= 55:
        main_color = "#d29922"
        status_color = "#d29922"
    else:
        main_color = "#f85149"
        status_color = "#f85149"
    
    # Función para determinar color de subscore
    def get_subscore_color(score):
        if score >= 85:
            return "#3fb950"
        elif score >= 70:
            return "#d29922"
        else:
            return "#f85149"
    
    return f"""
    <div class="healthspan-hero">
        <div class="healthspan-title">🏆 HEALTHSPAN INDEX</div>
        <div class="healthspan-main-score">
            <div class="healthspan-value" style="color: {main_color};">{index}</div>
            <div class="healthspan-status" style="color: {status_color};">{status}</div>
            <div class="healthspan-description">Indicador de años de vida saludable basado en fitness, composición corporal y recuperación (ventana 7 días)</div>
        </div>
        
        <div class="healthspan-subscores">
            <div class="subscore-card">
                <div class="subscore-label">💪 FITNESS</div>
                <div class="subscore-value" style="color: {get_subscore_color(fitness)};">{fitness}</div>
                <div class="subscore-bar">
                    <div class="subscore-fill" style="width: {fitness}%; background: {get_subscore_color(fitness)};"></div>
                </div>
                <div class="subscore-description">PAI semanal + balance entrenamiento (TSB) + capacidad aeróbica (VO2max)</div>
            </div>
            
            <div class="subscore-card">
                <div class="subscore-label">🏋️ BODY</div>
                <div class="subscore-value" style="color: {get_subscore_color(body)};">{body}</div>
                <div class="subscore-bar">
                    <div class="subscore-fill" style="width: {body}%; background: {get_subscore_color(body)};"></div>
                </div>
                <div class="subscore-description">Peso, grasa corporal y masa muscular vs objetivos (promedio 7d)</div>
            </div>
            
            <div class="subscore-card">
                <div class="subscore-label">😴 RECOVERY</div>
                <div class="subscore-value" style="color: {get_subscore_color(recovery)};">{recovery}</div>
                <div class="subscore-bar">
                    <div class="subscore-fill" style="width: {recovery}%; background: {get_subscore_color(recovery)};"></div>
                </div>
                <div class="subscore-description">Calidad de sueño + frecuencia cardíaca en reposo + saturación de oxígeno</div>
            </div>
            
            <div class="subscore-card">
                <div class="subscore-label">🔥 METABOLIC</div>
                <div class="subscore-value" style="color: {get_subscore_color(metabolic)};">{metabolic}</div>
                <div class="subscore-bar">
                    <div class="subscore-fill" style="width: {metabolic}%; background: {get_subscore_color(metabolic)};"></div>
                </div>
                <div class="subscore-description">Presión arterial + biomarcadores de salud metabólica</div>
            </div>
            
            <div class="subscore-card">
                <div class="subscore-label">⚡ FUNCTIONAL</div>
                <div class="subscore-value" style="color: {get_subscore_color(functional)};">{functional}</div>
                <div class="subscore-bar">
                    <div class="subscore-fill" style="width: {functional}%; background: {get_subscore_color(functional)};"></div>
                </div>
                <div class="subscore-description">Pasos diarios y movilidad funcional (promedio 7d)</div>
            </div>
        </div>
    </div>
    """


def _generar_seccion_logs(logs_content, resumen):
    """Genera la sección HTML de logs"""
    if not resumen:
        return ""
    
    # Info de debug del archivo de log
    log_info = ""
    if 'log_existe' in resumen:
        if resumen.get('log_existe'):
            log_info = f"<p style='color: #8b949e; font-size: 0.9em;'>📄 Log file: {resumen.get('log_size', 0)} bytes</p>"
        else:
            log_info = "<p style='color: #f85149; font-size: 0.9em;'>⚠️ Archivo de log no encontrado</p>"
    
    return f"""
    <div class="logs-section">
        <h2>📋 Última Ejecución</h2>
        <div class="logs-summary">
            <p>✅ <strong>Fecha:</strong> {resumen.get('fecha', 'N/A')}</p>
            <p>✅ <strong>Archivos procesados:</strong> {resumen.get('archivos_procesados', 0)}</p>
            <p>✅ <strong>Total ejercicios:</strong> {resumen.get('total_ejercicios', 0)}</p>
            <p>✅ <strong>Total registros peso:</strong> {resumen.get('total_peso', 0)}</p>
            <p>✅ <strong>Total registros pasos:</strong> {resumen.get('total_pasos', 0)}</p>
            {log_info}
            <button id="logs-toggle-btn" class="logs-toggle-btn" onclick="toggleLogs()">▼ Ver logs completos (últimas 500 líneas)</button>
        </div>
        <pre id="logs-content" class="logs-hidden">{logs_content}</pre>
    </div>
    """


def construir_html_completo(html_laboratorio, cards_html, entrenamientos_html, recomendaciones_html, datos_graficos, logs_html_content="", resumen_ejecucion=None, healthspan_data=None, plan_accion_html=""):
    """Construye el HTML completo del dashboard"""
    healthspan_hero = _generar_healthspan_hero(healthspan_data) if healthspan_data else ""
    
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard de Salud - HealthConnect</title>
        <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
        {generar_css()}
    </head>
    <body>
        <div class="container">
            <header>
                <h1>📊 Dashboard de Salud</h1>
                <p class="subtitle">Última actualización: {_obtener_hora_argentina().strftime("%d/%m/%Y %H:%M")} (Argentina)</p>
            </header>
            
            {healthspan_hero}
            
            {html_laboratorio}
            
            {plan_accion_html}
            
            <div class="metrics-grid">
                {cards_html}
            </div>
            
            <div class="charts-section">
                <h2>📈 Evolución Temporal</h2>
                <div class="charts-grid">
                    <div class="chart-container">
                        <h3>PAI (Diario + Ventana Móvil 7 días)</h3>
                        <div id="pai-chart"></div>
                    </div>
                    <div class="chart-container">
                        <h3>Peso</h3>
                        <div id="peso-chart"></div>
                    </div>
                    <div class="chart-container">
                        <h3>TSB + CTL + ATL</h3>
                        <div id="tsb-chart"></div>
                    </div>
                    <div class="chart-container">
                        <h3>SpO2</h3>
                        <div id="spo2-chart"></div>
                    </div>
                    <div class="chart-container">
                        <h3>Grasa Corporal</h3>
                        <div id="grasa-chart"></div>
                    </div>
                    <div class="chart-container">
                        <h3>Masa Muscular</h3>
                        <div id="masa-chart"></div>
                    </div>
                    <div class="chart-container">
                        <h3>FC en Reposo (Nocturna)</h3>
                        <div id="fc-reposo-chart"></div>
                    </div>
                    <div class="chart-container">
                        <h3>FC Diurna (Continua)</h3>
                        <div id="fc-diurna-chart"></div>
                    </div>
                    <div class="chart-container">
                        <h3>Pasos Diarios</h3>
                        <div id="pasos-chart"></div>
                    </div>
                    <div class="chart-container">
                        <h3>Presión Arterial</h3>
                        <div id="presion-chart"></div>
                    </div>
                    <div class="chart-container">
                        <h3>Glucosa en Sangre</h3>
                        <div id="glucosa-chart"></div>
                    </div>
                    <div class="chart-container">
                        <h3>Masa Ósea</h3>
                        <div id="masa-osea-chart"></div>
                    </div>
                    <div class="chart-container">
                        <h3>Masa de Agua Corporal</h3>
                        <div id="masa-agua-chart"></div>
                    </div>
                    <div class="chart-container">
                        <h3>Tasa Metabólica Basal</h3>
                        <div id="tmb-chart"></div>
                    </div>
                    <div class="chart-container">
                        <h3>Distancia Recorrida</h3>
                        <div id="distancia-chart"></div>
                    </div>
                    <div class="chart-container">
                        <h3>Calorías Totales</h3>
                        <div id="calorias-chart"></div>
                    </div>
                    <div class="chart-container">
                        <h3>Sueño por Fases (últimos 14 días)</h3>
                        <div id="sueno-chart"></div>
                    </div>
                </div>
            </div>
            
            <div class="training-section">
                <h2>🏃 Entrenamientos Recientes</h2>
                {entrenamientos_html}
            </div>
            
            <div class="recommendations-section">
                <h2>💡 Recomendaciones</h2>
                {recomendaciones_html}
            </div>
            
            {_generar_seccion_logs(logs_html_content, resumen_ejecucion)}
        </div>
        
        <script>
            {generar_javascript(datos_graficos)}
        </script>
    </body>
    </html>
    """