#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JavaScript - Gráficos Adicionales
Genera código JS para glucosa, tasa metabólica basal y sueño
"""

from outputs.js_helpers import tiene_datos


def generar_grafico_glucosa(datos_graficos):
    """Genera JavaScript para el gráfico de glucosa en sangre"""
    if tiene_datos(datos_graficos.get('glucosa', {})):
        return f"""
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
        return """
        document.getElementById('glucosa-chart').innerHTML = '<div class="chart-empty">Sin datos de glucosa</div>';
        """


def generar_grafico_tmb(datos_graficos):
    """Genera JavaScript para el gráfico de tasa metabólica basal"""
    if tiene_datos(datos_graficos.get('tasa_metabolica', {})):
        return f"""
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
        return """
        document.getElementById('tmb-chart').innerHTML = '<div class="chart-empty">Sin datos de tasa metabólica</div>';
        """


def generar_grafico_sueno(datos_graficos):
    """Genera JavaScript para el gráfico de sueño por fases (barras apiladas)"""
    if tiene_datos(datos_graficos.get('sueno', {})):
        sueno_data = datos_graficos['sueno']
        return f"""
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
        return """
        document.getElementById('sueno-chart').innerHTML = '<div class="chart-empty">Sin datos de sueño</div>';
        """


def generar_js_other(datos_graficos):
    """Función principal que genera todo el JS de gráficos adicionales"""
    js = ""
    js += generar_grafico_glucosa(datos_graficos)
    js += generar_grafico_tmb(datos_graficos)
    js += generar_grafico_sueno(datos_graficos)
    return js
