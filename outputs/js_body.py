#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JavaScript - Gráficos de Composición Corporal
Genera código JS para peso, grasa, masa muscular, masa ósea, masa de agua
"""

from config import PESO_OBJETIVO
from outputs.js_helpers import tiene_datos


def generar_grafico_peso(datos_graficos):
    """Genera JavaScript para el gráfico de peso"""
    if tiene_datos(datos_graficos.get('peso', {})):
        return f"""
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
        return """
        document.getElementById('peso-chart').innerHTML = '<div class="chart-empty">Sin datos de peso</div>';
        """


def generar_grafico_grasa(datos_graficos):
    """Genera JavaScript para el gráfico de grasa corporal"""
    if tiene_datos(datos_graficos.get('grasa', {})):
        return f"""
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
        return """
        document.getElementById('grasa-chart').innerHTML = '<div class="chart-empty">Sin datos de grasa corporal</div>';
        """


def generar_grafico_masa_muscular(datos_graficos):
    """Genera JavaScript para el gráfico de masa muscular"""
    if tiene_datos(datos_graficos.get('masa_muscular', {})):
        return f"""
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
        return """
        document.getElementById('masa-chart').innerHTML = '<div class="chart-empty">Sin datos de masa muscular</div>';
        """


def generar_grafico_masa_osea(datos_graficos):
    """Genera JavaScript para el gráfico de masa ósea"""
    if tiene_datos(datos_graficos.get('masa_osea', {})):
        return f"""
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
        return """
        document.getElementById('masa-osea-chart').innerHTML = '<div class="chart-empty">Sin datos de masa ósea</div>';
        """


def generar_grafico_masa_agua(datos_graficos):
    """Genera JavaScript para el gráfico de masa de agua"""
    if tiene_datos(datos_graficos.get('masa_agua', {})):
        return f"""
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
        return """
        document.getElementById('masa-agua-chart').innerHTML = '<div class="chart-empty">Sin datos de masa de agua</div>';
        """


def generar_js_body(datos_graficos):
    """Función principal que genera todo el JS de composición corporal"""
    js = ""
    js += generar_grafico_peso(datos_graficos)
    js += generar_grafico_grasa(datos_graficos)
    js += generar_grafico_masa_muscular(datos_graficos)
    js += generar_grafico_masa_osea(datos_graficos)
    js += generar_grafico_masa_agua(datos_graficos)
    return js
