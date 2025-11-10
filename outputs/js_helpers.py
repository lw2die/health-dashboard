#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JavaScript Helpers - Configuración base y funciones auxiliares
Parte del sistema modular de generación de gráficos
"""


def tiene_datos(datos, campo='fechas'):
    """
    Valida que un diccionario de datos tenga el campo especificado con contenido.
    Usado antes de renderizar cada gráfico.
    """
    return datos and datos.get(campo) and len(datos.get(campo, [])) > 0


def generar_config_base():
    """
    Genera la configuración base de Plotly que se reutiliza en todos los gráficos.
    Define colores del tema oscuro y márgenes estándar.
    """
    return """
        const layout_config = {
            paper_bgcolor: '#0d1117',
            plot_bgcolor: '#161b22',
            font: { color: '#c9d1d9' },
            margin: { l: 40, r: 20, t: 20, b: 40 },
            showlegend: true,
            height: 300
        };
    """


def generar_funciones_logs():
    """
    Genera las funciones JavaScript para toggle de logs y formateo.
    """
    return """
    
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
