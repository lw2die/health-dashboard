#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generación del dashboard HTML con gráficos interactivos
"""

from datetime import datetime, timedelta
from config import (
    OUTPUT_HTML, EDAD, ALTURA_CM, FC_MAX, FC_REPOSO, PESO_OBJETIVO,
    PAI_OBJETIVO_SEMANAL, COLOR_EXCELENTE, COLOR_BUENO, COLOR_MALO,
    TSB_OPTIMO_MIN, TSB_OPTIMO_MAX
)
from metricas.pai import calcular_pai_semanal, preparar_datos_pai_historico
from metricas.fitness import calcular_vo2max, calcular_tsb, preparar_datos_tsb_historico
from metricas.score import calcular_score_longevidad, generar_recomendaciones
from outputs.graficos import preparar_datos_peso
from utils.logger import logger


def generar_dashboard(cache):
    """
    Genera dashboard HTML completo con métricas y gráficos.
    
    Args:
        cache (dict): Cache con todos los datos
    """
    logger.info("Generando dashboard HTML con gráficos...")
    
    ejercicios = cache.get("ejercicio", [])
    peso = cache.get("peso", [])
    sueno = cache.get("sueno", [])
    
    # Calcular métricas principales
    metricas = _calcular_metricas(ejercicios, peso, sueno)
    
    # Preparar datos para gráficos
    datos_graficos = {
        "pai": preparar_datos_pai_historico(ejercicios),
        "peso": preparar_datos_peso(peso),
        "tsb": preparar_datos_tsb_historico(ejercicios)
    }
    
    # Obtener entrenamientos recientes
    entrenamientos_recientes = _obtener_entrenamientos_recientes(ejercicios)
    
    # Generar HTML
    html = _generar_html(metricas, datos_graficos, entrenamientos_recientes, len(ejercicios))
    
    # Guardar archivo
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    
    logger.info(f"Dashboard generado: {OUTPUT_HTML}")


def _calcular_metricas(ejercicios, peso, sueno):
    """
    Calcula todas las métricas necesarias para el dashboard.
    """
    # PAI y fitness
    pai_semanal = calcular_pai_semanal(ejercicios)
    vo2max = calcular_vo2max(ejercicios)
    tsb = calcular_tsb(ejercicios)
    
    # Peso
    peso_actual = peso[-1]["peso"] if peso else 0
    delta_peso = peso_actual - PESO_OBJETIVO
    
    # Sueño (últimos 7 días)
    sueno_7d = [
        s for s in sueno
        if (datetime.now().replace(tzinfo=None) - 
            datetime.fromisoformat(s["fecha"].replace("Z", "+00:00")).replace(tzinfo=None)).days <= 7
    ]
    sueno_promedio = sum(s["duracion"] for s in sueno_7d) / len(sueno_7d) / 60 if sueno_7d else 0
    sueno_profundo_pct = sum(s["porcentaje_profundo"] for s in sueno_7d) / len(sueno_7d) if sueno_7d else 0
    
    # Score de longevidad
    score_longevidad = calcular_score_longevidad(peso_actual, pai_semanal, vo2max, sueno_promedio)
    
    # Recomendaciones
    recomendaciones = generar_recomendaciones(peso_actual, pai_semanal, sueno_promedio)
    recomendaciones_html = "<br><br>".join(recomendaciones) if recomendaciones else \
        "<strong>Estado Óptimo:</strong> Todas las métricas dentro de rangos saludables."
    
    # Colores
    score_color = COLOR_EXCELENTE if score_longevidad >= 80 else \
                  COLOR_BUENO if score_longevidad >= 60 else COLOR_MALO
    
    pai_color = COLOR_EXCELENTE if pai_semanal >= PAI_OBJETIVO_SEMANAL else \
                COLOR_BUENO if pai_semanal >= 75 else COLOR_MALO
    
    tsb_color = COLOR_EXCELENTE if TSB_OPTIMO_MIN < tsb["tsb"] < TSB_OPTIMO_MAX else \
                COLOR_BUENO if -20 < tsb["tsb"] < 20 else COLOR_MALO
    
    return {
        "pai_semanal": pai_semanal,
        "vo2max": vo2max,
        "tsb": tsb,
        "peso_actual": peso_actual,
        "delta_peso": delta_peso,
        "sueno_promedio": sueno_promedio,
        "sueno_profundo_pct": sueno_profundo_pct,
        "score_longevidad": score_longevidad,
        "recomendaciones_html": recomendaciones_html,
        "score_color": score_color,
        "pai_color": pai_color,
        "tsb_color": tsb_color
    }


def _obtener_entrenamientos_recientes(ejercicios, dias=7):
    """
    Obtiene entrenamientos de los últimos N días.
    """
    fecha_limite = datetime.now().replace(tzinfo=None) - timedelta(days=dias)
    recientes = [
        e for e in ejercicios
        if datetime.fromisoformat(e["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    recientes.sort(key=lambda x: x["fecha"], reverse=True)
    return recientes[:10]  # Máximo 10


def _generar_html(metricas, datos_graficos, entrenamientos_recientes, total_entrenamientos):
    """
    Genera el HTML completo del dashboard.
    """
    return f"""<!DOCTYPE html>
<html lang='es'>
<head>
    <meta charset='UTF-8'>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Longevidad</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        {_generar_css()}
    </style>
</head>
<body>
    <div class='container'>
        {_generar_header()}
        {_generar_score_section(metricas)}
        {_generar_metrics_grid(metricas, total_entrenamientos)}
        {_generar_recomendaciones(metricas)}
        {_generar_graficos_containers()}
        {_generar_entrenamientos_recientes(entrenamientos_recientes)}
        {_generar_interpretacion()}
    </div>
    
    <script>
        {_generar_javascript(datos_graficos)}
    </script>
</body>
</html>"""


def _generar_css():
    """CSS del dashboard"""
    return """
        body {
            background: #0d1117;
            color: #c9d1d9;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }
        h1, h2, h3, h4 { margin: 0; padding-bottom: 10px; }
        .container { max-width: 1400px; margin: auto; }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .metric-card {
            background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #30363d;
            transition: transform 0.2s;
        }
        .metric-card:hover { transform: translateY(-5px); }
        .metric-card h3 { color: #58a6ff; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }
        .metric-value { font-size: 2.5em; font-weight: bold; margin: 10px 0; }
        .metric-subtitle { font-size: 0.85em; color: #8b949e; }
        .info-box {
            background: #161b22;
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
            border: 1px solid #30363d;
        }
        .info-box h3 { color: #58a6ff; margin-bottom: 15px; }
        .info-box ul { list-style-position: inside; padding: 0; margin: 10px 0; }
        .info-box li { padding: 8px 0; border-bottom: 1px solid #21262d; }
        .info-box li:last-child { border-bottom: none; }
        .chart-container { margin-top: 30px; }
        .recommendations {
            background: linear-gradient(135deg, #1f6feb 0%, #1158c7 100%);
            padding: 20px;
            border-radius: 12px;
            margin: 20px 0;
            line-height: 1.8;
        }
        header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #1f6feb 0%, #1158c7 100%);
            border-radius: 12px;
        }
        .score-grande {
            font-size: 4em;
            font-weight: bold;
            margin: 20px 0;
        }
    """


def _generar_header():
    """Header del dashboard"""
    return f"""
        <header>
            <h1>Dashboard de Longevidad Integral</h1>
            <p style="margin: 5px 0;">Última actualización: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p style="font-size: 0.9em; margin: 0;">Edad: {EDAD} años | Altura: {ALTURA_CM} cm | FC Max: {FC_MAX} bpm | FC Reposo: {FC_REPOSO} bpm</p>
        </header>
    """


def _generar_score_section(metricas):
    """Sección del score principal"""
    return f"""
        <div style="text-align: center; background: #161b22; padding: 30px; border-radius: 12px; margin-bottom: 20px;">
            <h2>Score de Longevidad</h2>
            <div class='score-grande' style="color: {metricas['score_color']}">{metricas['score_longevidad']}</div>
            <p style="color: #8b949e;">Basado en composición corporal, fitness, sueño y balance de entrenamiento</p>
        </div>
    """


def _generar_metrics_grid(metricas, total_entrenamientos):
    """Grid de métricas principales"""
    return f"""
        <div class='metrics-grid'>
            <div class='metric-card'>
                <h3>PAI Semanal</h3>
                <div class='metric-value' style="color: {metricas['pai_color']}">{metricas['pai_semanal']}</div>
                <div class='metric-subtitle'>Objetivo: ≥{PAI_OBJETIVO_SEMANAL}/semana</div>
            </div>
            
            <div class='metric-card'>
                <h3>Peso Actual</h3>
                <div class='metric-value'>{metricas['peso_actual']:.1f} kg</div>
                <div class='metric-subtitle'>Objetivo: {PESO_OBJETIVO} kg ({'+' if metricas['delta_peso'] > 0 else ''}{metricas['delta_peso']:.1f} kg)</div>
            </div>
            
            <div class='metric-card'>
                <h3>VO2max</h3>
                <div class='metric-value'>{metricas['vo2max']}</div>
                <div class='metric-subtitle'>ml/kg/min (Promedio)</div>
            </div>
            
            <div class='metric-card'>
                <h3>TSB (Balance)</h3>
                <div class='metric-value' style="color: {metricas['tsb_color']}">{metricas['tsb']['tsb']}</div>
                <div class='metric-subtitle'>CTL: {metricas['tsb']['ctl']} | ATL: {metricas['tsb']['atl']}</div>
            </div>
            
            <div class='metric-card'>
                <h3>Sueño (7d)</h3>
                <div class='metric-value'>{metricas['sueno_promedio']:.1f}h</div>
                <div class='metric-subtitle'>Profundo: {metricas['sueno_profundo_pct']:.1f}%</div>
            </div>
            
            <div class='metric-card'>
                <h3>Entrenamientos</h3>
                <div class='metric-value'>{total_entrenamientos}</div>
                <div class='metric-subtitle'>Total registrados</div>
            </div>
        </div>
    """


def _generar_recomendaciones(metricas):
    """Sección de recomendaciones"""
    return f"""
        <div class='recommendations'>
            <h3>Recomendaciones Priorizadas para Optimizar Longevidad</h3>
            <div style="margin-top: 15px;">{metricas['recomendaciones_html']}</div>
        </div>
    """


def _generar_graficos_containers():
    """Contenedores para los gráficos"""
    return """
        <div class='chart-container'>
            <div id="pai-chart" style="height:400px;"></div>
        </div>
        
        <div class='chart-container'>
            <div id="peso-chart" style="height:400px;"></div>
        </div>
        
        <div class='chart-container'>
            <div id="tsb-chart" style="height:400px;"></div>
        </div>
    """


def _generar_entrenamientos_recientes(entrenamientos):
    """Lista de entrenamientos recientes"""
    items = ''.join([
        f"""<li>
            <strong>{datetime.fromisoformat(e["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")}:</strong> 
            {e["tipo"]} - {e["duracion"]} min 
            (FC: {e["fc_promedio"]} bpm, PAI: {e["pai"]:.1f}, Zona: {e["zona"]})
        </li>"""
        for e in entrenamientos
    ])
    
    return f"""
        <div class="info-box">
            <h3>Entrenamientos Recientes (Últimos 7 días)</h3>
            <ul>{items}</ul>
        </div>
    """


def _generar_interpretacion():
    """Sección de interpretación del score"""
    return """
        <div class="info-box">
            <h3>Interpretación del Score de Longevidad</h3>
            <p>El score combina las métricas más importantes para healthspan:</p>
            <ul>
                <li><strong>80-100:</strong> Excelente. Estás en el camino óptimo para longevidad.</li>
                <li><strong>60-79:</strong> Bueno. Hay áreas específicas que mejorar (ver recomendaciones).</li>
                <li><strong>&lt;60:</strong> Necesita atención. Las recomendaciones son prioritarias.</li>
            </ul>
            <p><strong>Componentes del Score:</strong></p>
            <ul>
                <li>Composición Corporal (40%): Peso y % grasa cerca de objetivos</li>
                <li>Fitness Cardiovascular (30%): VO2max y PAI semanal</li>
                <li>Sueño (20%): Cantidad y calidad de descanso</li>
                <li>Balance Entrenamiento (10%): TSB óptimo para evitar lesiones</li>
            </ul>
        </div>
    """


def _generar_javascript(datos_graficos):
    """JavaScript para los gráficos de Plotly"""
    return f"""
        const layout = {{
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: {{ color: '#c9d1d9', family: 'Arial' }},
            xaxis: {{ gridcolor: '#30363d' }},
            yaxis: {{ gridcolor: '#30363d' }},
            margin: {{ l: 60, r: 40, t: 60, b: 60 }}
        }};
        
        // Gráfico PAI Semanal
        Plotly.newPlot('pai-chart', [
            {{
                x: {datos_graficos["pai"]["fechas"]},
                y: {datos_graficos["pai"]["valores"]},
                type: 'scatter',
                mode: 'lines+markers',
                name: 'PAI Semanal',
                fill: 'tozeroy',
                line: {{ color: '#58a6ff', width: 3 }},
                marker: {{ 
                    size: 8,
                    color: {datos_graficos["pai"]["valores"]}.map(v => v >= {PAI_OBJETIVO_SEMANAL} ? '{COLOR_EXCELENTE}' : v >= 75 ? '{COLOR_BUENO}' : '{COLOR_MALO}')
                }}
            }},
            {{
                x: {datos_graficos["pai"]["fechas"]},
                y: Array({len(datos_graficos["pai"]["fechas"])}).fill({PAI_OBJETIVO_SEMANAL}),
                type: 'scatter',
                mode: 'lines',
                name: 'Objetivo ({PAI_OBJETIVO_SEMANAL})',
                line: {{ color: '{COLOR_EXCELENTE}', dash: 'dash', width: 2 }}
            }}
        ], {{
            ...layout,
            title: 'PAI Semanal (ventana móvil 7 días) - Últimos 30 días',
            yaxis: {{ ...layout.yaxis, title: 'PAI Acumulado (7 días)' }},
            showlegend: true
        }});
        
        // Gráfico Peso
        Plotly.newPlot('peso-chart', [
            {{
                x: {datos_graficos["peso"]["fechas"]},
                y: {datos_graficos["peso"]["valores"]},
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Peso',
                line: {{ color: '#58a6ff', width: 3 }},
                marker: {{ size: 8 }}
            }},
            {{
                x: {datos_graficos["peso"]["fechas"]},
                y: Array({len(datos_graficos["peso"]["fechas"])}).fill({datos_graficos["peso"]["objetivo"]}),
                type: 'scatter',
                mode: 'lines',
                name: 'Objetivo',
                line: {{ color: '{COLOR_EXCELENTE}', dash: 'dash', width: 2 }}
            }}
        ], {{
            ...layout,
            title: 'Evolución del Peso',
            yaxis: {{ ...layout.yaxis, title: 'Peso (kg)' }}
        }});
        
        // Gráfico TSB
        Plotly.newPlot('tsb-chart', [
            {{
                x: {datos_graficos["tsb"]["fechas"]},
                y: {datos_graficos["tsb"]["tsb"]},
                type: 'scatter',
                mode: 'lines',
                name: 'TSB',
                fill: 'tozeroy',
                line: {{ color: '#ffbb28', width: 3 }}
            }},
            {{
                x: {datos_graficos["tsb"]["fechas"]},
                y: {datos_graficos["tsb"]["ctl"]},
                type: 'scatter',
                mode: 'lines',
                name: 'CTL (Fitness)',
                line: {{ color: '{COLOR_EXCELENTE}', width: 2 }}
            }},
            {{
                x: {datos_graficos["tsb"]["fechas"]},
                y: {datos_graficos["tsb"]["atl"]},
                type: 'scatter',
                mode: 'lines',
                name: 'ATL (Fatiga)',
                line: {{ color: '{COLOR_MALO}', width: 2 }}
            }}
        ], {{
            ...layout,
            title: 'Balance de Entrenamiento (TSB)',
            yaxis: {{ ...layout.yaxis, title: 'Puntuación' }}
        }});
    """