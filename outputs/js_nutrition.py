#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JavaScript - Gráficos de Nutrición
Compatible con aspect-ratio y etiquetas de datos (Data Labels) internas
"""


def generar_circulo_calorias(circulo_data):
    """Genera círculo de calorías restantes"""
    if not circulo_data:
        return ""
    
    presupuesto = circulo_data.get("presupuesto", 0)
    comido = circulo_data.get("comido", 0)
    ejercicio = circulo_data.get("ejercicio", 0)
    restante = circulo_data.get("restante", 0)
    
    if restante > 0:
        color_restante = "#3fb950"
    elif restante > -200:
        color_restante = "#ffa657"
    else:
        color_restante = "#f85149"
    
    return f"""
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
                cutout: '80%',
                plugins: {{ legend: {{ display: false }}, tooltip: {{ enabled: false }} }}
            }}
        }});
        
        // Actualizar valores texto
        const restanteEl = document.getElementById('restante-valor');
        if(restanteEl) {{
            restanteEl.textContent = Math.abs({restante});
            restanteEl.style.color = '{color_restante}';
        }}
        const comidoEl = document.getElementById('comido-valor');
        if(comidoEl) comidoEl.textContent = {comido};
        const ejercicioEl = document.getElementById('ejercicio-valor');
        if(ejercicioEl) ejercicioEl.textContent = {ejercicio};
        
        // Recuperado: Actualizar presupuesto
        const presupuestoEl = document.getElementById('presupuesto-valor');
        if(presupuestoEl) presupuestoEl.textContent = {presupuesto};
        """


def generar_grafico_macros_porcentaje(circulo_data):
    """Genera los 3 círculos de macros"""
    if not circulo_data:
        return ""
    
    pct_proteinas = circulo_data.get("pct_proteinas", 0)
    pct_carbohidratos = circulo_data.get("pct_carbohidratos", 0)
    pct_grasas = circulo_data.get("pct_grasas", 0)
    
    return f"""
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
                cutout: '75%',
                plugins: {{ legend: {{ display: false }}, tooltip: {{ enabled: false }} }}
            }}
        }});
        
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
                cutout: '75%',
                plugins: {{ legend: {{ display: false }}, tooltip: {{ enabled: false }} }}
            }}
        }});
        
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
                cutout: '75%',
                plugins: {{ legend: {{ display: false }}, tooltip: {{ enabled: false }} }}
            }}
        }});
        """


def generar_grafico_presupuesto_consumo(datos_deficit):
    """Gráfico de líneas histórico"""
    if not datos_deficit or not datos_deficit.get("fechas"):
        return ""
    
    fechas = str(datos_deficit.get("fechas", [])).replace("'", '"')
    presupuesto = str(datos_deficit.get("presupuesto", []))
    comido = str(datos_deficit.get("comido", []))
    ejercicio = str(datos_deficit.get("ejercicio", []))
    
    return f"""
        new Chart(document.getElementById('presupuesto-consumo-chart'), {{
            type: 'line',
            data: {{
                labels: {fechas},
                datasets: [
                    {{
                        label: 'Presupuesto',
                        data: {presupuesto},
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: false,
                        pointRadius: 3
                    }},
                    {{
                        label: 'Comido',
                        data: {comido},
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: false,
                        pointRadius: 3
                    }},
                    {{
                        label: 'Ejercicio',
                        data: {ejercicio},
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: false,
                        pointRadius: 3
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: true, position: 'bottom', labels: {{ color: '#8b949e', boxWidth: 10, padding: 10 }} }},
                    title: {{ display: false }}
                }},
                scales: {{
                    x: {{ ticks: {{ color: '#8b949e', font: {{ size: 10 }} }}, grid: {{ color: 'rgba(139, 148, 158, 0.1)' }} }},
                    y: {{ ticks: {{ color: '#8b949e', font: {{ size: 10 }} }}, grid: {{ color: 'rgba(139, 148, 158, 0.1)' }} }}
                }},
                interaction: {{ mode: 'index', intersect: false }}
            }}
        }});
        """


def generar_graficos_comparacion_macros(macros_7d):
    """
    Gráficos circulares con plugin INLINE para dibujar porcentajes dentro
    """
    if not macros_7d:
        pct_prot_real = pct_carb_real = pct_gras_real = 0
    else:
        pct_prot_real = macros_7d.get("pct_proteinas", 0)
        pct_carb_real = macros_7d.get("pct_carbohidratos", 0)
        pct_gras_real = macros_7d.get("pct_grasas", 0)
    
    pct_carb_recom = 55
    pct_gras_recom = 25
    pct_prot_recom = 20
    
    # Definimos un plugin inline para dibujar texto
    plugin_labels = """
    {
        id: 'percentageLabels',
        afterDatasetsDraw(chart, args, options) {
            const {ctx} = chart;
            ctx.save();
            
            chart.data.datasets.forEach((dataset, i) => {
                chart.getDatasetMeta(i).data.forEach((datapoint, index) => {
                    const {x, y} = datapoint.tooltipPosition();
                    const value = dataset.data[index];
                    
                    if (value > 5) { // Solo mostrar si es > 5% para que quepa
                        ctx.font = 'bold 12px sans-serif';
                        ctx.fillStyle = '#ffffff';
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.shadowColor = 'rgba(0,0,0,0.5)';
                        ctx.shadowBlur = 4;
                        ctx.fillText(value + '%', x, y);
                    }
                });
            });
            ctx.restore();
        }
    }
    """
    
    return f"""
        // Definir plugin localmente
        const percentagePlugin = {plugin_labels};

        new Chart(document.getElementById('macros-recomendados'), {{
            type: 'pie',
            data: {{
                labels: ['Carb', 'Grasa', 'Prot'],
                datasets: [{{
                    data: [{pct_carb_recom}, {pct_gras_recom}, {pct_prot_recom}],
                    backgroundColor: ['#3b82f6', '#f59e0b', '#a855f7'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                layout: {{ padding: 10 }}
            }},
            plugins: [percentagePlugin]
        }});
        
        new Chart(document.getElementById('macros-reales'), {{
            type: 'pie',
            data: {{
                labels: ['Carb', 'Grasa', 'Prot'],
                datasets: [{{
                    data: [{pct_carb_real}, {pct_gras_real}, {pct_prot_real}],
                    backgroundColor: ['#3b82f6', '#f59e0b', '#a855f7'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                layout: {{ padding: 10 }}
            }},
            plugins: [percentagePlugin]
        }});
        """


def generar_js_nutrition(datos_graficos, circulo_data, macros_7d=None):
    """Función principal JS"""
    js = ""
    if circulo_data:
        js += generar_circulo_calorias(circulo_data)
        js += generar_grafico_macros_porcentaje(circulo_data)
    js += generar_graficos_comparacion_macros(macros_7d)
    if datos_graficos.get("deficit"):
        js += generar_grafico_presupuesto_consumo(datos_graficos["deficit"])
    return js