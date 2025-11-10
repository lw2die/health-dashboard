#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JavaScript - Gráficos de Fitness
Genera código JS para PAI y TSB (CTL/ATL)
"""

from config import PAI_OBJETIVO_SEMANAL
from outputs.js_helpers import tiene_datos


def generar_grafico_pai(datos_graficos):
    """Genera JavaScript para el gráfico de PAI (diario + ventana móvil 7 días)"""
    if tiene_datos(datos_graficos.get('pai', {})):
        return f"""
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
        return """
        document.getElementById('pai-chart').innerHTML = '<div class="chart-empty">Sin datos de PAI</div>';
        """


def generar_grafico_tsb(datos_graficos):
    """Genera JavaScript para el gráfico de TSB + CTL + ATL"""
    if tiene_datos(datos_graficos.get('tsb', {})):
        return f"""
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
        return """
        document.getElementById('tsb-chart').innerHTML = '<div class="chart-empty">Sin datos de TSB</div>';
        """


def generar_js_fitness(datos_graficos):
    """Función principal que genera todo el JS de fitness"""
    js = ""
    js += generar_grafico_pai(datos_graficos)
    js += generar_grafico_tsb(datos_graficos)
    return js
