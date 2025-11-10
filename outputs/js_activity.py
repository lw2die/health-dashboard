#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JavaScript - Gráficos de Actividad Física
Genera código JS para pasos, distancia y calorías totales
"""

from outputs.js_helpers import tiene_datos


def generar_grafico_pasos(datos_graficos):
    """Genera JavaScript para el gráfico de pasos diarios"""
    if tiene_datos(datos_graficos.get('pasos', {})):
        return f"""
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
        return """
        document.getElementById('pasos-chart').innerHTML = '<div class="chart-empty">Sin datos de pasos</div>';
        """


def generar_grafico_distancia(datos_graficos):
    """Genera JavaScript para el gráfico de distancia recorrida"""
    if tiene_datos(datos_graficos.get('distancia', {})):
        return f"""
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
        return """
        document.getElementById('distancia-chart').innerHTML = '<div class="chart-empty">Sin datos de distancia</div>';
        """


def generar_grafico_calorias_totales(datos_graficos):
    """Genera JavaScript para el gráfico de calorías totales quemadas"""
    if tiene_datos(datos_graficos.get('calorias_totales', {})):
        return f"""
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
        return """
        document.getElementById('calorias-chart').innerHTML = '<div class="chart-empty">Sin datos de calorías</div>';
        """


def generar_js_activity(datos_graficos):
    """Función principal que genera todo el JS de actividad física"""
    js = ""
    js += generar_grafico_pasos(datos_graficos)
    js += generar_grafico_distancia(datos_graficos)
    js += generar_grafico_calorias_totales(datos_graficos)
    return js
