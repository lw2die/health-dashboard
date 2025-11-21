#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JavaScript - Gráficos Cardiovasculares
Genera código JS para FC reposo, FC diurna, presión arterial y SpO2
"""

from outputs.js_helpers import tiene_datos


def generar_grafico_fc_reposo(datos_graficos):
    """Genera JavaScript para el gráfico de FC en reposo con TENDENCIA"""
    datos = datos_graficos.get('fc_reposo', {})
    
    if tiene_datos(datos):
        fechas = datos.get('fechas', [])
        valores = datos.get('valores', [])
        tendencia = datos.get('tendencia')
        
        traces_js = f"""
            {{
                x: {fechas},
                y: {valores},
                type: 'scatter',
                mode: 'lines+markers',
                name: 'FC Reposo',
                line: {{ color: '#f85149', width: 2 }},
                marker: {{ size: 6 }}
            }}
        """
        
        layout_extra = ""
        if tendencia:
            traces_js += f""",
            {{
                x: {tendencia['linea_x']},
                y: {tendencia['linea_y']},
                type: 'scatter',
                mode: 'lines',
                name: 'Tendencia',
                line: {{ color: '#c9d1d9', width: 2, dash: 'dot' }},
                hoverinfo: 'skip'
            }}
            """
            
            # Texto con negrita usando HTML tags, no atributo 'weight'
            layout_extra = f"""
            annotations: [{{
                xref: 'paper', yref: 'paper',
                x: 0.05, y: 0.95,
                xanchor: 'left', yanchor: 'top',
                text: '<b>{tendencia['texto']}</b>',
                showarrow: false,
                font: {{ color: '#c9d1d9', size: 12 }},
                bgcolor: 'rgba(22, 27, 34, 0.8)',
                bordercolor: '#30363d',
                borderwidth: 1,
                borderpad: 4
            }}],
            """

        return f"""
        // FC Reposo con Tendencia
        Plotly.newPlot('fc-reposo-chart', [
            {traces_js}
        ], {{
            ...layout_config,
            yaxis: {{ title: 'FC (bpm)', gridcolor: '#30363d' }},
            xaxis: {{ gridcolor: '#30363d' }},
            {layout_extra}
        }});
        """
    else:
        return """
        document.getElementById('fc-reposo-chart').innerHTML = '<div class="chart-empty">Sin datos de FC reposo</div>';
        """


def generar_grafico_fc_diurna(datos_graficos):
    """Genera JavaScript para el gráfico de FC diurna continua"""
    if tiene_datos(datos_graficos.get('frecuencia_cardiaca', {})):
        return f"""
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
        return """
        document.getElementById('fc-diurna-chart').innerHTML = '<div class="chart-empty">Sin datos de FC diurna</div>';
        """


def generar_grafico_presion_arterial(datos_graficos):
    """Genera JavaScript para el gráfico de presión arterial"""
    if tiene_datos(datos_graficos.get('presion_arterial', {})):
        return f"""
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
        return """
        document.getElementById('presion-chart').innerHTML = '<div class="chart-empty">Sin datos de presión arterial</div>';
        """


def generar_grafico_spo2(datos_graficos):
    """Genera JavaScript para el gráfico de SpO2"""
    if tiene_datos(datos_graficos.get('spo2', {})):
        return f"""
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
        return """
        document.getElementById('spo2-chart').innerHTML = '<div class="chart-empty">Sin datos de SpO2</div>';
        """


def generar_js_cardio(datos_graficos):
    """Función principal que genera todo el JS cardiovascular"""
    js = ""
    js += generar_grafico_fc_reposo(datos_graficos)
    js += generar_grafico_fc_diurna(datos_graficos)
    js += generar_grafico_presion_arterial(datos_graficos)
    js += generar_grafico_spo2(datos_graficos)
    return js