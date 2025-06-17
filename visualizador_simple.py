"""
🚔 VISUALIZADOR SIMPLE - MODELO DE PATRULLAJE PREVENTIVO
Genera reportes y tablas usando solo pandas (sin gráficos)
"""

import pandas as pd
import numpy as np
import re
from collections import defaultdict
import os

def cargar_datos():
    """Cargar todos los datos necesarios"""
    try:
        # Resultados del modelo
        variables_df = pd.read_excel("resultados/variables_activas.xlsx")
        resumen_df = pd.read_excel("resultados/resumen_diario_recursos.xlsx")
        
        # Datos base
        zonas_df = pd.read_csv("data/zonas.csv")
        vehiculos_df = pd.read_csv("data/vehiculos.csv")
        
        print("✅ Datos cargados exitosamente:")
        print(f"   • Variables activas: {len(variables_df):,}")
        print(f"   • Días de resumen: {len(resumen_df)}")
        print(f"   • Zonas disponibles: {len(zonas_df)}")
        print(f"   • Vehículos totales: {len(vehiculos_df)}")
        
        return variables_df, resumen_df, zonas_df, vehiculos_df
        
    except Exception as e:
        print(f"❌ Error cargando datos: {e}")
        print("💡 Asegúrate de ejecutar 'python main.py' primero")
        return None, None, None, None

def procesar_datos(variables_df, zonas_df):
    """Procesar datos para análisis"""
    # Extraer información de variables
    zonas_utilizadas = set()
    dias_utilizados = set()
    vehiculos_utilizados = set()

    for _, row in variables_df.iterrows():
        var_name = row['variable']
        if var_name.startswith('x['):  # x[p,z,m,t]
            match = re.search(r'x\[(\d+),(\d+),(\d+),(\d+)\]', var_name)
            if match:
                p, z, m, t = map(int, match.groups())
                zonas_utilizadas.add(z)
                dias_utilizados.add(t)
                vehiculos_utilizados.add(p)

    # Crear mapeo de nombres
    zona_nombres = {}
    for zona_id in zonas_utilizadas:
        zona_row = zonas_df[zonas_df['id_zona'] == zona_id]
        if not zona_row.empty:
            zona_nombres[zona_id] = zona_row.iloc[0]['nombre_zona']
        else:
            zona_nombres[zona_id] = f"Zona {zona_id}"

    tipos_vehiculos = {1: "Peatón", 2: "Moto", 3: "Bicicleta", 4: "Caballo", 5: "Auto", 6: "Furgón"}

    print(f"\n🏙️ Zonas procesadas: {len(zonas_utilizadas)}")
    print(f"📅 Días procesados: {len(dias_utilizados)}")
    print(f"🚗 Vehículos procesados: {len(vehiculos_utilizados)}")
    
    return zonas_utilizadas, dias_utilizados, vehiculos_utilizados, zona_nombres, tipos_vehiculos

def crear_tabla_patrullas(variables_df, zonas_utilizadas, dias_utilizados, zona_nombres):
    """Crear tabla de distribución de patrullas"""
    print("\n📊 TABLA DE DISTRIBUCIÓN DE PATRULLAS POR ZONA Y DÍA")
    print("="*80)
    
    # Crear matriz de patrullas
    patrullas_matriz = defaultdict(lambda: defaultdict(int))
    
    for _, row in variables_df.iterrows():
        var_name = row['variable']
        if var_name.startswith('x['):
            match = re.search(r'x\[(\d+),(\d+),(\d+),(\d+)\]', var_name)
            if match:
                p, z, m, t = map(int, match.groups())
                patrullas_matriz[t][z] += 1

    # Convertir a DataFrame
    dias_sorted = sorted(dias_utilizados)
    zonas_sorted = sorted(zonas_utilizadas)
    
    tabla_data = []
    for dia in dias_sorted:
        fila = {'Día': dia}
        total_dia = 0
        for zona in zonas_sorted:
            patrullas = patrullas_matriz[dia][zona]
            fila[zona_nombres[zona]] = patrullas
            total_dia += patrullas
        fila['Total_Día'] = total_dia
        tabla_data.append(fila)

    tabla_df = pd.DataFrame(tabla_data)
    
    # Agregar fila de totales
    totales = {'Día': 'TOTAL'}
    for zona in zonas_sorted:
        total_zona = sum(patrullas_matriz[dia][zona] for dia in dias_sorted)
        totales[zona_nombres[zona]] = total_zona
    totales['Total_Día'] = sum(totales[col] for col in totales if col not in ['Día', 'Total_Día'])
    
    # Crear DataFrame de totales y concatenar
    totales_df = pd.DataFrame([totales])
    tabla_completa = pd.concat([tabla_df, totales_df], ignore_index=True)
    
    # Mostrar tabla (primeros 10 días + total)
    print("📅 PRIMEROS 10 DÍAS + TOTALES:")
    display_df = pd.concat([tabla_df.head(10), totales_df])
    print(display_df.to_string(index=False))
    
    if len(tabla_df) > 10:
        print(f"\n💡 Tabla completa tiene {len(tabla_df)} días. Mostrando solo primeros 10 + total.")
    
    # Guardar tabla completa
    os.makedirs("resultados/tablas", exist_ok=True)
    tabla_completa.to_excel("resultados/tablas/distribucion_patrullas.xlsx", index=False)
    print(f"\n💾 Tabla completa guardada: resultados/tablas/distribucion_patrullas.xlsx")
    
    return tabla_df, totales

def crear_ranking_comunas(tabla_df, zona_nombres):
    """Crear ranking de comunas por recursos"""
    print("\n🏆 RANKING DE COMUNAS POR RECURSOS ASIGNADOS")
    print("="*60)
    
    # Calcular totales por zona
    ranking_data = []
    total_general = 0
    
    for zona_id in sorted(zona_nombres.keys()):
        zona_name = zona_nombres[zona_id]
        if zona_name in tabla_df.columns:
            total_zona = tabla_df[zona_name].sum()
            promedio_dia = total_zona / len(tabla_df)
            total_general += total_zona
            
            ranking_data.append({
                'Comuna': zona_name,
                'Total_Patrullas': total_zona,
                'Promedio_Diario': round(promedio_dia, 1),
                'Min_Diario': tabla_df[zona_name].min(),
                'Max_Diario': tabla_df[zona_name].max()
            })
    
    ranking_df = pd.DataFrame(ranking_data)
    ranking_df = ranking_df.sort_values('Total_Patrullas', ascending=False)
    
    # Agregar porcentajes
    ranking_df['Porcentaje'] = round((ranking_df['Total_Patrullas'] / total_general) * 100, 1)
    
    print(ranking_df.to_string(index=False))
    
    # Guardar ranking
    ranking_df.to_excel("resultados/tablas/ranking_comunas.xlsx", index=False)
    print(f"\n💾 Ranking guardado: resultados/tablas/ranking_comunas.xlsx")
    
    return ranking_df

def analizar_vehiculos(vehiculos_utilizados, vehiculos_df, tipos_vehiculos):
    """Analizar distribución de vehículos"""
    print("\n🚗 ANÁLISIS DE TIPOS DE VEHÍCULOS UTILIZADOS")
    print("="*60)
    
    vehiculos_por_tipo = defaultdict(int)
    
    for vehiculo_id in vehiculos_utilizados:
        vehiculo_row = vehiculos_df[vehiculos_df['id'] == vehiculo_id]
        if not vehiculo_row.empty:
            tipo = vehiculo_row.iloc[0]['tipo_medio']
            vehiculos_por_tipo[tipo] += 1
    
    # Crear tabla de vehículos
    vehiculos_data = []
    total_utilizados = sum(vehiculos_por_tipo.values())
    
    for tipo, cantidad in vehiculos_por_tipo.items():
        nombre_tipo = tipos_vehiculos.get(tipo, f"Tipo {tipo}")
        porcentaje = (cantidad / total_utilizados) * 100
        
        vehiculos_data.append({
            'Tipo_Vehiculo': nombre_tipo,
            'Cantidad_Utilizada': cantidad,
            'Porcentaje': round(porcentaje, 1)
        })
    
    vehiculos_tabla = pd.DataFrame(vehiculos_data)
    vehiculos_tabla = vehiculos_tabla.sort_values('Cantidad_Utilizada', ascending=False)
    
    print(vehiculos_tabla.to_string(index=False))
    
    # Estadísticas adicionales
    total_disponible = len(vehiculos_df)
    eficiencia = (total_utilizados / total_disponible) * 100
    
    print(f"\n📊 ESTADÍSTICAS DE FLOTA:")
    print(f"   • Total vehículos utilizados: {total_utilizados}")
    print(f"   • Total vehículos disponibles: {total_disponible}")
    print(f"   • Eficiencia de flota: {eficiencia:.1f}%")
    
    # Guardar tabla
    vehiculos_tabla.to_excel("resultados/tablas/analisis_vehiculos.xlsx", index=False)
    print(f"\n💾 Análisis guardado: resultados/tablas/analisis_vehiculos.xlsx")
    
    return vehiculos_tabla

def crear_reporte_ejecutivo(variables_df, ranking_df, vehiculos_tabla, zonas_utilizadas, dias_utilizados, vehiculos_utilizados, vehiculos_df):
    """Crear reporte ejecutivo completo"""
    print("\n" + "="*80)
    print("📋 REPORTE EJECUTIVO - MODELO DE PATRULLAJE PREVENTIVO")
    print("="*80)
    
    # Extraer función objetivo
    u_vars = variables_df[variables_df['variable'].str.startswith('u[')]
    zeta_vars = variables_df[variables_df['variable'].str.startswith('zeta[')]
    funcion_objetivo = u_vars['valor'].sum() if not u_vars.empty else 0
    deficit_total = zeta_vars['valor'].sum() if not zeta_vars.empty else 0
    
    # Métricas principales
    total_patrullas = ranking_df['Total_Patrullas'].sum()
    total_dias = len(dias_utilizados)
    total_zonas = len(zonas_utilizadas)
    promedio_diario = total_patrullas / total_dias
    total_vehiculos_utilizados = len(vehiculos_utilizados)
    eficiencia_flota = (total_vehiculos_utilizados / len(vehiculos_df)) * 100
    
    reporte_data = {
        'Métrica': [
            'Función Objetivo Óptima',
            'Déficit Total de Cobertura',
            'Período Planificado (días)',
            'Comunas Cubiertas',
            'Total Patrullas Asignadas',
            'Promedio Patrullas/Día',
            'Vehículos Utilizados',
            'Eficiencia de Flota (%)',
            'Variables Activas Totales',
            'Costo-Beneficio (Patrullas/Unidad Peligrosidad)'
        ],
        'Valor': [
            f"{funcion_objetivo:.6f}",
            f"{deficit_total:.6f}",
            total_dias,
            total_zonas,
            f"{total_patrullas:,}",
            f"{promedio_diario:.1f}",
            total_vehiculos_utilizados,
            f"{eficiencia_flota:.1f}%",
            f"{len(variables_df):,}",
            f"{(total_patrullas/funcion_objetivo):.0f}" if funcion_objetivo > 0 else "N/A"
        ]
    }
    
    reporte_df = pd.DataFrame(reporte_data)
    print("\n📊 MÉTRICAS PRINCIPALES:")
    print(reporte_df.to_string(index=False))
    
    # Top 3 comunas
    print(f"\n🏆 TOP 3 COMUNAS (más recursos):")
    top3 = ranking_df.head(3)
    for i, row in top3.iterrows():
        print(f"   {i+1}. {row['Comuna']}: {row['Total_Patrullas']} patrullas ({row['Porcentaje']}%)")
    
    # Top 3 tipos de vehículos
    print(f"\n🚗 TOP 3 TIPOS DE VEHÍCULOS:")
    top3_veh = vehiculos_tabla.head(3)
    for i, row in top3_veh.iterrows():
        print(f"   {i+1}. {row['Tipo_Vehiculo']}: {row['Cantidad_Utilizada']} unidades ({row['Porcentaje']}%)")
    
    # Guardar reporte
    reporte_df.to_excel("resultados/tablas/reporte_ejecutivo.xlsx", index=False)
    
    print(f"\n🎯 CONCLUSIONES CLAVE:")
    print(f"   • Modelo optimizado exitosamente para {total_zonas} comunas prioritarias")
    print(f"   • Plan operativo de {total_dias} días con {total_patrullas:,} asignaciones estratégicas")
    print(f"   • Utilización eficiente del {eficiencia_flota:.1f}% del parque vehicular")
    print(f"   • Función objetivo minimizada: {funcion_objetivo:.6f} (menor = mejor seguridad)")
    if deficit_total > 0:
        cobertura = ((total_zonas * total_dias - len(zeta_vars)) / (total_zonas * total_dias)) * 100
        print(f"   • Cobertura lograda: {cobertura:.1f}% (déficits mínimos en {len(zeta_vars)} casos)")
    
    print(f"\n💾 Reporte guardado: resultados/tablas/reporte_ejecutivo.xlsx")
    print("="*80)

def main():
    """Función principal"""
    print("📊 VISUALIZADOR SIMPLE - MODELO DE PATRULLAJE PREVENTIVO")
    print("="*65)
    print("💡 Genera reportes y tablas sin necesidad de librerías de gráficos")
    print("")
    
    # Cargar datos
    variables_df, resumen_df, zonas_df, vehiculos_df = cargar_datos()
    if variables_df is None:
        return
    
    # Procesar datos
    zonas_utilizadas, dias_utilizados, vehiculos_utilizados, zona_nombres, tipos_vehiculos = procesar_datos(
        variables_df, zonas_df)
    
    # Generar análisis
    tabla_df, totales = crear_tabla_patrullas(variables_df, zonas_utilizadas, dias_utilizados, zona_nombres)
    ranking_df = crear_ranking_comunas(tabla_df, zona_nombres)
    vehiculos_tabla = analizar_vehiculos(vehiculos_utilizados, vehiculos_df, tipos_vehiculos)
    crear_reporte_ejecutivo(variables_df, ranking_df, vehiculos_tabla, zonas_utilizadas, 
                           dias_utilizados, vehiculos_utilizados, vehiculos_df)
    
    print(f"\n✅ ANÁLISIS COMPLETADO EXITOSAMENTE")
    print(f"📁 Archivos generados en: resultados/tablas/")
    print(f"   • distribucion_patrullas.xlsx - Tabla completa día por día")
    print(f"   • ranking_comunas.xlsx - Ranking de comunas por recursos")
    print(f"   • analisis_vehiculos.xlsx - Distribución de tipos de vehículos")
    print(f"   • reporte_ejecutivo.xlsx - Métricas principales y conclusiones")
    print(f"\n💡 Para gráficos visuales, instala: pip install matplotlib seaborn plotly")
    print(f"    Luego ejecuta: python generar_graficos.py")

if __name__ == "__main__":
    main() 