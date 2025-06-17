"""
ANALIZADOR COMPLETO DE RESULTADOS DEL MODELO POLICIAL
Muestra información detallada sobre la optimización y asignaciones
"""

import pandas as pd
import numpy as np
from collections import defaultdict
import re

def cargar_datos():
    """Carga todos los datos necesarios para el análisis"""
    try:
        # Cargar resultados
        variables_df = pd.read_excel("resultados/variables_activas.xlsx")
        resumen_df = pd.read_excel("resultados/resumen_diario_recursos.xlsx")
        
        # Cargar datos base
        zonas_df = pd.read_csv("data/zonas.csv")
        vehiculos_df = pd.read_csv("data/vehiculos.csv")
        carabineros_df = pd.read_csv("data/carabineros.csv")
        tipos_delitos_df = pd.read_csv("data/tipos_delitos.csv")
        
        return variables_df, resumen_df, zonas_df, vehiculos_df, carabineros_df, tipos_delitos_df
    except Exception as e:
        print(f"❌ Error cargando datos: {e}")
        return None, None, None, None, None, None

def extraer_configuracion_modelo(variables_df):
    """Extrae la configuración utilizada en el modelo"""
    print("🔧 CONFIGURACIÓN DEL MODELO")
    print("="*50)
    
    # Extraer zonas utilizadas
    zonas_usadas = set()
    dias_usados = set()
    vehiculos_usados = set()
    turnos_usados = set()
    
    for _, row in variables_df.iterrows():
        var_name = row['variable']
        
        if var_name.startswith('x['):  # x[p,z,m,t]
            match = re.search(r'x\[(\d+),(\d+),(\d+),(\d+)\]', var_name)
            if match:
                p, z, m, t = map(int, match.groups())
                vehiculos_usados.add(p)
                zonas_usadas.add(z)
                turnos_usados.add(m)
                dias_usados.add(t)
    
    print(f"📊 Zonas utilizadas: {len(zonas_usadas)} → {sorted(zonas_usadas)}")
    print(f"📅 Días planificados: {len(dias_usados)} → {min(dias_usados)} a {max(dias_usados)}")
    print(f"🚗 Vehículos en uso: {len(vehiculos_usados)} de {vehiculos_usados}")
    print(f"⏰ Turnos: {len(turnos_usados)} → {sorted(turnos_usados)} (1=Mañana, 2=Tarde, 3=Noche)")
    
    return zonas_usadas, dias_usados, vehiculos_usados, turnos_usados

def mapear_zonas_nombres(zonas_usadas, zonas_df):
    """Mapea IDs de zonas a nombres"""
    zona_nombres = {}
    for zona_id in zonas_usadas:
        zona_row = zonas_df[zonas_df['id_zona'] == zona_id]
        if not zona_row.empty:
            zona_nombres[zona_id] = zona_row.iloc[0]['nombre_zona']
        else:
            zona_nombres[zona_id] = f"Zona {zona_id}"
    
    print(f"\n🏙️ ZONAS SELECCIONADAS:")
    for zona_id in sorted(zonas_usadas):
        print(f"   • ID {zona_id}: {zona_nombres[zona_id]}")
    
    return zona_nombres

def analizar_parametros_usados(variables_df):
    """Analiza los parámetros y valores utilizados"""
    print(f"\n📈 PARÁMETROS DEL MODELO")
    print("="*50)
    
    # Analizar valores de variables de peligrosidad
    u_vars = variables_df[variables_df['variable'].str.startswith('u[')]
    zeta_vars = variables_df[variables_df['variable'].str.startswith('zeta[')]
    
    if not u_vars.empty:
        print(f"🎯 Peligrosidad (u):")
        print(f"   • Promedio: {u_vars['valor'].mean():.6f}")
        print(f"   • Máximo: {u_vars['valor'].max():.6f}")
        print(f"   • Mínimo: {u_vars['valor'].min():.6f}")
    
    if not zeta_vars.empty:
        print(f"⚠️  Déficits (zeta):")
        print(f"   • Promedio: {zeta_vars['valor'].mean():.6f}")
        print(f"   • Máximo: {zeta_vars['valor'].max():.6f}")
        print(f"   • Total déficit: {zeta_vars['valor'].sum():.6f}")
    
    # Función objetivo total
    funcion_objetivo = u_vars['valor'].sum() if not u_vars.empty else 0
    print(f"\n🎯 FUNCIÓN OBJETIVO: {funcion_objetivo:.6f}")
    print("   (Suma total de peligrosidad - MENOR es MEJOR)")

def analizar_recursos_por_dia(variables_df, dias_usados, zona_nombres):
    """Analiza recursos utilizados por día y zona"""
    print(f"\n📊 RECURSOS POR DÍA Y ZONA")
    print("="*50)
    
    # Crear estructura de datos
    recursos_dia = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    # recursos_dia[dia][zona][tipo] = cantidad
    
    for _, row in variables_df.iterrows():
        var_name = row['variable']
        valor = row['valor']
        
        if var_name.startswith('x['):  # Patrullas por zona
            match = re.search(r'x\[(\d+),(\d+),(\d+),(\d+)\]', var_name)
            if match:
                p, z, m, t = map(int, match.groups())
                recursos_dia[t][z]['patrullas'] += 1
        
        elif var_name.startswith('y['):  # Carabineros
            match = re.search(r'y\[(\d+),(\d+),(\d+),(\d+)\]', var_name)
            if match:
                c, p, m, t = map(int, match.groups())
                # Necesitamos saber a qué zona está asignado el vehículo p en el día t
                # Esto requiere cruzar con las variables x
                recursos_dia[t]['total']['carabineros'] += 1
        
        elif var_name.startswith('phi['):  # Vehículos activos
            match = re.search(r'phi\[(\d+),(\d+)\]', var_name)
            if match:
                p, t = map(int, match.groups())
                recursos_dia[t]['total']['vehiculos'] += 1
    
    # Mostrar TODOS los días
    print(f"📅 DISTRIBUCIÓN COMPLETA ({len(dias_usados)} DÍAS):")
    
    # Crear tabla resumen
    print(f"\n{'DÍA':<4} {'ESTACIÓN':<10} {'LA FLORIDA':<10} {'MAIPÚ':<8} {'PROVIDENCIA':<12} {'SANTIAGO':<9} {'VEH':<4} {'CARB':<5}")
    print("-" * 70)
    
    for dia in sorted(dias_usados):
        # Extraer patrullas por zona
        ec = recursos_dia[dia][4]['patrullas']  # Estación Central
        lf = recursos_dia[dia][8]['patrullas']  # La Florida
        ma = recursos_dia[dia][17]['patrullas'] # Maipú
        pr = recursos_dia[dia][21]['patrullas'] # Providencia
        sa = recursos_dia[dia][30]['patrullas'] # Santiago
        
        # Totales
        veh = recursos_dia[dia]['total'].get('vehiculos', 0)
        carb = recursos_dia[dia]['total'].get('carabineros', 0)
        
        print(f"{dia:<4} {ec:<10} {lf:<10} {ma:<8} {pr:<12} {sa:<9} {veh:<4} {carb:<5}")
    
    # Mostrar resumen estadístico por zona
    print(f"\n📊 RESUMEN ESTADÍSTICO POR ZONA:")
    
    # Calcular estadísticas por zona
    stats_zonas = {}
    for zona_id, zona_name in zona_nombres.items():
        patrullas_zona = []
        for dia in sorted(dias_usados):
            patrullas = recursos_dia[dia][zona_id]['patrullas']
            patrullas_zona.append(patrullas)
        
        if patrullas_zona:
            stats_zonas[zona_name] = {
                'promedio': sum(patrullas_zona) / len(patrullas_zona),
                'maximo': max(patrullas_zona),
                'minimo': min(patrullas_zona),
                'total': sum(patrullas_zona)
            }
    
    for zona, stats in stats_zonas.items():
        print(f"   • {zona}: Promedio={stats['promedio']:.1f}, Min={stats['minimo']}, Max={stats['maximo']}, Total={stats['total']}")
    
    # Mostrar tendencias temporales
    print(f"\n📈 TENDENCIAS TEMPORALES:")
    
    # Calcular totales por día
    totales_diarios = []
    for dia in sorted(dias_usados):
        total_patrullas = sum(recursos_dia[dia][zona]['patrullas'] for zona in [4, 8, 17, 21, 30])
        vehiculos = recursos_dia[dia]['total'].get('vehiculos', 0)
        carabineros = recursos_dia[dia]['total'].get('carabineros', 0)
        totales_diarios.append((dia, total_patrullas, vehiculos, carabineros))
    
    if totales_diarios:
        print("   📊 Primeros 10 días vs Últimos 10 días:")
        
        primeros_10 = totales_diarios[:10]
        ultimos_10 = totales_diarios[-10:]
        
        prom_pat_inicio = sum(x[1] for x in primeros_10) / len(primeros_10)
        prom_pat_final = sum(x[1] for x in ultimos_10) / len(ultimos_10)
        
        prom_veh_inicio = sum(x[2] for x in primeros_10) / len(primeros_10)
        prom_veh_final = sum(x[2] for x in ultimos_10) / len(ultimos_10)
        
        print(f"      • Patrullas: Inicio={prom_pat_inicio:.1f}, Final={prom_pat_final:.1f} (Δ={prom_pat_final-prom_pat_inicio:+.1f})")
        print(f"      • Vehículos: Inicio={prom_veh_inicio:.1f}, Final={prom_veh_final:.1f} (Δ={prom_veh_final-prom_veh_inicio:+.1f})")

def analizar_distribucion_tipos_vehiculos(variables_df, vehiculos_df):
    """Analiza qué tipos de vehículos se utilizan"""
    print(f"\n🚗 TIPOS DE VEHÍCULOS UTILIZADOS")
    print("="*50)
    
    # Obtener vehículos activos
    vehiculos_activos = set()
    for _, row in variables_df.iterrows():
        var_name = row['variable']
        if var_name.startswith('x[') or var_name.startswith('phi['):
            match = re.search(r'[\[,](\d+)', var_name)
            if match:
                vehiculos_activos.add(int(match.group(1)))
    
    # Mapear a tipos
    tipos_nombres = {1: "Peatón", 2: "Moto", 3: "Bicicleta", 4: "Caballo", 5: "Auto", 6: "Furgón"}
    tipos_usados = defaultdict(int)
    
    for vehiculo_id in vehiculos_activos:
        vehiculo_row = vehiculos_df[vehiculos_df['id'] == vehiculo_id]
        if not vehiculo_row.empty:
            tipo = vehiculo_row.iloc[0]['tipo_medio']
            tipos_usados[tipo] += 1
    
    print("📊 Distribución por tipo:")
    for tipo in sorted(tipos_usados.keys()):
        nombre_tipo = tipos_nombres.get(tipo, f"Tipo {tipo}")
        cantidad = tipos_usados[tipo]
        print(f"   • {nombre_tipo}: {cantidad} vehículos utilizados")

def mostrar_estadisticas_generales(variables_df, resumen_df):
    """Muestra estadísticas generales del modelo"""
    print(f"\n📈 ESTADÍSTICAS GENERALES")
    print("="*50)
    
    # Variables por tipo
    tipos_variables = defaultdict(int)
    for _, row in variables_df.iterrows():
        tipo = row['variable'].split('[')[0]
        tipos_variables[tipo] += 1
    
    print("🔢 Variables activas por tipo:")
    for tipo, cantidad in sorted(tipos_variables.items()):
        nombres_tipo = {
            'x': 'Asignaciones patrulla-zona',
            'y': 'Asignaciones carabinero-patrulla', 
            'phi': 'Activaciones de vehículo',
            'u': 'Niveles de peligrosidad',
            'zeta': 'Déficits de cobertura'
        }
        nombre = nombres_tipo.get(tipo, tipo)
        print(f"   • {nombre}: {cantidad}")
    
    print(f"\n📊 Total variables activas: {len(variables_df):,}")
    
    if not resumen_df.empty:
        print(f"\n📅 Resumen temporal:")
        print(f"   • Días planificados: {len(resumen_df)}")
        if 'patrullas_asignadas' in resumen_df.columns:
            print(f"   • Patrullas promedio/día: {resumen_df['patrullas_asignadas'].mean():.1f}")
        if 'carabineros_asignados' in resumen_df.columns:
            print(f"   • Carabineros promedio/día: {resumen_df['carabineros_asignados'].mean():.1f}")
        if 'vehiculos_utilizados' in resumen_df.columns:
            print(f"   • Vehículos promedio/día: {resumen_df['vehiculos_utilizados'].mean():.1f}")

def main():
    """Función principal del analizador"""
    print("🔍 ANALIZADOR COMPLETO DE RESULTADOS")
    print("="*60)
    
    # Cargar datos
    variables_df, resumen_df, zonas_df, vehiculos_df, carabineros_df, tipos_delitos_df = cargar_datos()
    
    if variables_df is None:
        print("❌ No se pudieron cargar los datos. Ejecuta primero main.py")
        return
    
    print(f"✅ Datos cargados exitosamente")
    print(f"   • Variables activas: {len(variables_df):,}")
    print(f"   • Días en resumen: {len(resumen_df) if resumen_df is not None else 0}")
    
    # Análisis paso a paso
    zonas_usadas, dias_usados, vehiculos_usados, turnos_usados = extraer_configuracion_modelo(variables_df)
    zona_nombres = mapear_zonas_nombres(zonas_usadas, zonas_df)
    analizar_parametros_usados(variables_df)
    analizar_recursos_por_dia(variables_df, dias_usados, zona_nombres)
    analizar_distribucion_tipos_vehiculos(variables_df, vehiculos_df)
    mostrar_estadisticas_generales(variables_df, resumen_df)
    
    print(f"\n✅ ANÁLISIS COMPLETADO")
    print("📁 Archivos disponibles:")
    print("   • resultados/variables_activas.xlsx")
    print("   • resultados/resumen_diario_recursos.xlsx")

if __name__ == "__main__":
    main() 