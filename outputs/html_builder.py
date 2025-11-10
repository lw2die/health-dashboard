#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML Builder - Constructor principal del dashboard
Orquesta todos los módulos para generar el HTML completo
"""

from datetime import datetime, timedelta
from outputs.html_css import generar_css
from outputs.html_sections import generar_healthspan_hero, generar_seccion_nutrition, generar_seccion_logs
from outputs.js_helpers import generar_config_base, generar_funciones_logs
from outputs.js_fitness import generar_js_fitness
from outputs.js_body import generar_js_body
from outputs.js_cardio import generar_js_cardio
from outputs.js_activity import generar_js_activity
from outputs.js_nutrition import generar_js_nutrition
from outputs.js_other import generar_js_other


def _obtener_hora_argentina():
    """Retorna la hora actual en Argentina (UTC-3)"""
    return datetime.utcnow() - timedelta(hours=3)


def generar_javascript(datos_graficos, circulo_data=None):
    """
    ✅ MODIFICADO: Ahora recibe circulo_data
    Genera todo el JavaScript para los gráficos.
    Llama a todos los módulos JS especializados.
    """
    js = generar_config_base()
    js += generar_js_fitness(datos_graficos)
    js += generar_js_body(datos_graficos)
    js += generar_js_cardio(datos_graficos)
    js += generar_js_activity(datos_graficos)
    js += generar_js_other(datos_graficos)
    js += generar_funciones_logs()
    js += generar_js_nutrition(datos_graficos, circulo_data)
    
    return js


def construir_html_completo(html_laboratorio, cards_html, entrenamientos_html, 
                           recomendaciones_html, datos_graficos, 
                           logs_html_content="", resumen_ejecucion=None, 
                           healthspan_data=None, plan_accion_html="", 
                           circulo_data=None):
    """
    ✅ MODIFICADO: Ahora recibe circulo_data en lugar de nutrition_data
    Construye el HTML completo del dashboard.
    Es el orquestador principal que combina todos los componentes.
    """
    
    # Generar componentes HTML
    healthspan_hero = generar_healthspan_hero(healthspan_data) if healthspan_data else ""
    seccion_nutrition = generar_seccion_nutrition(circulo_data, datos_graficos) if circulo_data else ""
    seccion_logs = generar_seccion_logs(logs_html_content, resumen_ejecucion)
    
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard de Salud - HealthConnect</title>
        <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
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
            
            {seccion_nutrition}
            
            <div class="training-section">
                <h2>🏃 Entrenamientos Recientes</h2>
                {entrenamientos_html}
            </div>
            
            <div class="recommendations-section">
                <h2>💡 Recomendaciones</h2>
                {recomendaciones_html}
            </div>
            
            {seccion_logs}
        </div>
        
        <script>
            {generar_javascript(datos_graficos, circulo_data)}
        </script>
    </body>
    </html>
    """