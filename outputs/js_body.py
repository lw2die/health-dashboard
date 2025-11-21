#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JavaScript - Gráficos de Composición Corporal
Genera código JS para peso, grasa, masa muscular, masa ósea, masa de agua
"""

from config import PESO_OBJETIVO
from outputs.js_helpers import tiene_datos


def generar_grafico_peso(datos_graficos):
    """Genera JavaScript para el gráfico de peso con TENDENCIA"""
    datos = datos_graficos.get('peso', {})
    
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
                name: 'Peso',
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
            layout_extra = f"""
            annotations: [{{
                xref: 'paper', yref: 'paper',
                x: 0.05, y: 0.95,
                xanchor: 'left', yanchor: 'top',
                text: '{tendencia['texto']}',
                showarrow: false,
                font: {{ color: '#c9d1d9', size: 13, weight: 'bold' }},
                bgcolor: 'rgba(22, 27, 34, 0.8)',
                bordercolor: '#30363d',
                borderwidth: 1,
                borderpad: 6
            }}],
            """

        return f"""
        Plotly.newPlot('peso-chart', [
            {traces_js}
        ], {{
            ...layout_config,
            yaxis: {{ title: 'Peso (kg)', gridcolor: '#30363d' }},
            xaxis: {{ gridcolor: '#30363d' }},
            {layout_extra}
            shapes: [{{
                type: 'line',
                x0: 0, x1: 1, xref: 'paper',
                y0: {PESO_OBJETIVO}, y1: {PESO_OBJETIVO},
                line: {{ color: '#3fb950', width: 1, dash: 'dot' }}
            }}]
        }});
        """
    else:
        return "document.getElementById('peso-chart').innerHTML = '<div class=\"chart-empty\">Sin datos de peso</div>';"


def generar_grafico_grasa(datos_graficos):
    """Genera JavaScript para el gráfico de GRASA con TENDENCIA"""
    datos = datos_graficos.get('grasa', {})
    
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
                name: 'Grasa',
                line: {{ color: '#ffa657', width: 2 }},
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
            layout_extra = f"""
            annotations: [{{
                xref: 'paper', yref: 'paper',
                x: 0.05, y: 0.95,
                xanchor: 'left', yanchor: 'top',
                text: '{tendencia['texto']}',
                showarrow: false,
                font: {{ color: '#c9d1d9', size: 12 }},
                bgcolor: 'rgba(22, 27, 34, 0.8)',
                bordercolor: '#30363d',
                borderwidth: 1,
                borderpad: 4
            }}],
            """

        return f"""
        Plotly.newPlot('grasa-chart', [
            {traces_js}
        ], {{
            ...layout_config,
            yaxis: {{ title: 'Grasa (%)', gridcolor: '#30363d' }},
            xaxis: {{ gridcolor: '#30363d' }},
            {layout_extra}
        }});
        """
    else:
        return "document.getElementById('grasa-chart').innerHTML = '<div class=\"chart-empty\">Sin datos de grasa corporal</div>';"


def generar_grafico_masa_muscular(datos_graficos):
    """Genera JavaScript para el gráfico de MÚSCULO con TENDENCIA"""
    datos = datos_graficos.get('masa_muscular', {})
    
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
                name: 'Músculo',
                line: {{ color: '#3fb950', width: 2 }},
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
            layout_extra = f"""
            annotations: [{{
                xref: 'paper', yref: 'paper',
                x: 0.05, y: 0.95,
                xanchor: 'left', yanchor: 'top',
                text: '{tendencia['texto']}',
                showarrow: false,
                font: {{ color: '#c9d1d9', size: 12 }},
                bgcolor: 'rgba(22, 27, 34, 0.8)',
                bordercolor: '#30363d',
                borderwidth: 1,
                borderpad: 4
            }}],
            """

        return f"""
        Plotly.newPlot('masa-chart', [
            {traces_js}
        ], {{
            ...layout_config,
            yaxis: {{ title: 'Masa (kg)', gridcolor: '#30363d' }},
            xaxis: {{ gridcolor: '#30363d' }},
            {layout_extra}
        }});
        """
    else:
        return "document.getElementById('masa-chart').innerHTML = '<div class=\"chart-empty\">Sin datos de masa muscular</div>';"


def generar_grafico_masa_osea(datos_graficos):
    """Genera JavaScript para el gráfico de masa ósea"""
    if tiene_datos(datos_graficos.get('masa_osea', {})):
        return f"""
        Plotly.newPlot('masa-osea-chart', [{{
            x: {datos_graficos['masa_osea']['fechas']},
            y: {datos_graficos['masa_osea']['valores']},
            type: 'scatter', mode: 'lines+markers',
            line: {{ color: '#79c0ff', width: 2 }}
        }}], {{
            ...layout_config,
            yaxis: {{ title: 'Masa (kg)', gridcolor: '#30363d' }},
            xaxis: {{ gridcolor: '#30363d' }}
        }});
        """
    else:
        return "document.getElementById('masa-osea-chart').innerHTML = '<div class=\"chart-empty\">Sin datos de masa ósea</div>';"


def generar_grafico_masa_agua(datos_graficos):
    """Genera JavaScript para el gráfico de masa de agua"""
    if tiene_datos(datos_graficos.get('masa_agua', {})):
        return f"""
        Plotly.newPlot('masa-agua-chart', [{{
            x: {datos_graficos['masa_agua']['fechas']},
            y: {datos_graficos['masa_agua']['valores']},
            type: 'scatter', mode: 'lines+markers',
            line: {{ color: '#58a6ff', width: 2 }},
            fill: 'tozeroy', fillcolor: 'rgba(88, 166, 255, 0.1)'
        }}], {{
            ...layout_config,
            yaxis: {{ title: 'Masa (kg)', gridcolor: '#30363d' }},
            xaxis: {{ gridcolor: '#30363d' }}
        }});
        """
    else:
        return "document.getElementById('masa-agua-chart').innerHTML = '<div class=\"chart-empty\">Sin datos de masa de agua</div>';"


def generar_js_body(datos_graficos):
    """Función principal que genera todo el JS de composición corporal"""
    js = ""
    js += generar_grafico_peso(datos_graficos)
    js += generar_grafico_grasa(datos_graficos)
    js += generar_grafico_masa_muscular(datos_graficos)
    js += generar_grafico_masa_osea(datos_graficos)
    js += generar_grafico_masa_agua(datos_graficos)
    return js