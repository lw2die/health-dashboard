#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSS del Dashboard - Estilos completos
Define todos los estilos para el tema oscuro del dashboard
"""


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

        /* ═══════════════════════════════════════ */
        /* NUTRITION CARDS */
        /* ═══════════════════════════════════════ */
        
        .nutrition-section {
            background: linear-gradient(135deg, #2d1b3d 0%, #3d2b4d 100%);
            border: 2px solid #b392f0;
            border-radius: 12px;
            padding: 30px;
            margin: 30px 0;
        }
        
        .nutrition-section h2 {
            color: #d2a8ff;
            text-align: center;
            margin-bottom: 25px;
        }
        
        .nutrition-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .nutrition-card {
            background: rgba(139, 92, 246, 0.1);
            border: 1px solid #b392f0;
            border-radius: 8px;
            padding: 20px;
        }
        
        .nutrition-card h3 {
            color: #d2a8ff;
            font-size: 1.1em;
            margin-bottom: 15px;
        }
        
        .macro-bar {
            display: flex;
            align-items: center;
            margin: 10px 0;
        }
        
        .macro-label {
            min-width: 120px;
            color: #c9d1d9;
            font-size: 0.95em;
        }
        
        .macro-value {
            margin-left: auto;
            color: #d2a8ff;
            font-weight: bold;
        }
        
        .deficit-positive {
            color: #3fb950 !important;
        }
        
        .deficit-negative {
            color: #f85149 !important;
        }
        
        .deficit-neutral {
            color: #ffa657 !important;
        }
    </style>
    """
