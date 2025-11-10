#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JavaScript - Gráficos de Nutrición
✅ REEMPLAZADO: Círculo de calorías + Gráfico Presupuesto/Consumo (estilo Samsung Health)
"""


def generar_circulo_calorias(circulo_data):
    """
    ✅ NUEVO: Genera círculo de calorías restantes del día actual
    Estilo Samsung Health (imagen 2)
    """
    if not circulo_data:
        return ""
    
    presupuesto = circulo_data.get("presupuesto", 0)
    comido = circulo_data.get("comido", 0)
    ejercicio = circulo_data.get("ejercicio", 0)
    restante = circulo_data.get("restante", 0)
    
    # Determinar color del restante
    if restante > 0:
        color_restante = "#3fb950"  # Verde (puedes comer más)
    elif restante > -200:
        color_restante = "#ffa657"  # Naranja (casi en meta)
    else:
        color_restante = "#f85149"  # Rojo (excediste)
    
    # Preparar datos para gráfico de dona
    pct_comido = round((comido / presupuesto * 100), 1) if presupuesto > 0 else 0
    pct_restante = max(0, 100 - pct_comido)
    
    return f"""
        // ═══════════════════════════════════════════════════════════════
        // CÍRCULO DE CALORÍAS RESTANTES - Día actual
        // ═══════════════════════════════════════════════════════════════
        const circuloData = {{
            presupuesto: {presupuesto},
            comido: {comido},
            ejercicio: {ejercicio},
            restante: {restante}
        }};
        
        new Chart(document.getElementById('circulo-calorias'), {{
            type: 'doughnut',
            data: {{
                labels: ['Comido', 'Restante'],
                datasets: [{{
                    data: [{comido}, {max(0, restante)}],
                    backgroundColor: ['#ff6384', '{color_restante}'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                cutout: '75%',
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{ enabled: false }}
                }}
            }}
        }});
        
        // Actualizar valores en el HTML
        document.getElementById('restante-valor').textContent = Math.abs({restante});
        document.getElementById('restante-valor').style.color = '{color_restante}';
        document.getElementById('comido-valor').textContent = {comido};
        document.getElementById('ejercicio-valor').textContent = {ejercicio};
        document.getElementById('presupuesto-valor').textContent = {presupuesto};
        """


def generar_grafico_macros_porcentaje(circulo_data):
    """
    ✅ NUEVO: Genera los 3 círculos de macros en porcentaje
    Estilo Samsung Health (imagen 2)
    """
    if not circulo_data:
        return ""
    
    pct_proteinas = circulo_data.get("pct_proteinas", 0)
    pct_carbohidratos = circulo_data.get("pct_carbohidratos", 0)
    pct_grasas = circulo_data.get("pct_grasas", 0)
    
    proteinas_g = circulo_data.get("proteinas_g", 0)
    carbohidratos_g = circulo_data.get("carbohidratos_g", 0)
    grasas_g = circulo_data.get("grasas_g", 0)
    
    return f"""
        // ═══════════════════════════════════════════════════════════════
        // MACROS EN PORCENTAJE - 3 círculos
        // ═══════════════════════════════════════════════════════════════
        
        // Proteínas
        new Chart(document.getElementById('macro-proteinas'), {{
            type: 'doughnut',
            data: {{
                datasets: [{{
                    data: [{pct_proteinas}, {100 - pct_proteinas}],
                    backgroundColor: ['#a855f7', 'rgba(168, 85, 247, 0.1)'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {{ legend: {{ display: false }}, tooltip: {{ enabled: false }} }}
            }}
        }});
        document.getElementById('proteinas-pct').textContent = '{pct_proteinas}%';
        document.getElementById('proteinas-g').textContent = '{proteinas_g}g';
        
        // Carbohidratos
        new Chart(document.getElementById('macro-carbohidratos'), {{
            type: 'doughnut',
            data: {{
                datasets: [{{
                    data: [{pct_carbohidratos}, {100 - pct_carbohidratos}],
                    backgroundColor: ['#3b82f6', 'rgba(59, 130, 246, 0.1)'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {{ legend: {{ display: false }}, tooltip: {{ enabled: false }} }}
            }}
        }});
        document.getElementById('carbohidratos-pct').textContent = '{pct_carbohidratos}%';
        document.getElementById('carbohidratos-g').textContent = '{carbohidratos_g}g';
        
        // Grasas
        new Chart(document.getElementById('macro-grasas'), {{
            type: 'doughnut',
            data: {{
                datasets: [{{
                    data: [{pct_grasas}, {100 - pct_grasas}],
                    backgroundColor: ['#f59e0b', 'rgba(245, 158, 11, 0.1)'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {{ legend: {{ display: false }}, tooltip: {{ enabled: false }} }}
            }}
        }});
        document.getElementById('grasas-pct').textContent = '{pct_grasas}%';
        document.getElementById('grasas-g').textContent = '{grasas_g}g';
        """


def generar_grafico_presupuesto_consumo(datos_deficit):
    """
    ✅ NUEVO: Gráfico de 14 días con 3 líneas
    Estilo Samsung Health (imagen 3): Presupuesto vs Comido vs Ejercicio
    """
    if not datos_deficit or not datos_deficit.get("fechas"):
        return ""
    
    fechas = datos_deficit.get("fechas", [])
    presupuesto = datos_deficit.get("presupuesto", [])
    comido = datos_deficit.get("comido", [])
    ejercicio = datos_deficit.get("ejercicio", [])
    
    # Convertir listas Python a formato JavaScript
    fechas_js = str(fechas).replace("'", '"')
    presupuesto_js = str(presupuesto)
    comido_js = str(comido)
    ejercicio_js = str(ejercicio)
    
    return f"""
        // ═══════════════════════════════════════════════════════════════
        // GRÁFICO PRESUPUESTO Y CONSUMO - 14 días
        // ═══════════════════════════════════════════════════════════════
        new Chart(document.getElementById('presupuesto-consumo-chart'), {{
            type: 'line',
            data: {{
                labels: {fechas_js},
                datasets: [
                    {{
                        label: 'Presupuesto',
                        data: {presupuesto_js},
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: false,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }},
                    {{
                        label: 'Comido',
                        data: {comido_js},
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: false,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }},
                    {{
                        label: 'Ejercicio',
                        data: {ejercicio_js},
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: false,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ 
                        display: true, 
                        position: 'bottom',
                        labels: {{ 
                            color: '#c9d1d9',
                            usePointStyle: true,
                            padding: 15,
                            font: {{ size: 12 }}
                        }}
                    }},
                    title: {{ 
                        display: true, 
                        text: 'Presupuesto y Consumo', 
                        color: '#79c0ff', 
                        font: {{ size: 16 }},
                        padding: 20
                    }}
                }},
                scales: {{
                    x: {{ 
                        ticks: {{ color: '#8b949e' }}, 
                        grid: {{ color: 'rgba(139, 148, 158, 0.1)' }}
                    }},
                    y: {{ 
                        ticks: {{ color: '#8b949e' }}, 
                        grid: {{ color: 'rgba(139, 148, 158, 0.1)' }},
                        title: {{ 
                            display: true, 
                            text: 'Calorías (kcal)', 
                            color: '#8b949e' 
                        }}
                    }}
                }},
                interaction: {{
                    mode: 'index',
                    intersect: false
                }}
            }}
        }});
        """


def generar_js_nutrition(datos_graficos, circulo_data):
    """
    ✅ FUNCIÓN PRINCIPAL: Genera todo el JS de nutrición
    """
    js = ""
    
    # Círculo de calorías restantes
    if circulo_data:
        js += generar_circulo_calorias(circulo_data)
        js += generar_grafico_macros_porcentaje(circulo_data)
    
    # Gráfico de presupuesto y consumo
    if datos_graficos.get("deficit"):
        js += generar_grafico_presupuesto_consumo(datos_graficos["deficit"])
    
    return js