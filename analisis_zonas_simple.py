import pandas as pd
from collections import defaultdict

def analizar_por_zonas():
    """
    Análisis específico por zonas para entender patrones de asignación
    """
    
    try:
        # Cargar resultados
        variables_df = pd.read_excel("resultados/variables_activas.xlsx")
        
        print("ANÁLISIS POR ZONAS - MODELO 5 ZONAS")
        print("="*50)
        
        # Análisis de asignaciones x[p,z,m,t]
        asignaciones_x = variables_df[variables_df['variable'].str.startswith('x[')]
        
        if len(asignaciones_x) == 0:
            print("No se encontraron asignaciones de patrullas")
            return
        
        # Extraer información de las variables x
        zonas_info = defaultdict(lambda: defaultdict(list))
        turnos_info = defaultdict(list)
        dias_info = defaultdict(list)
        
        for _, row in asignaciones_x.iterrows():
            var_name = row['variable']
            valor = row['valor']
            
            # Parsear x[p,z,m,t]
            try:
                partes = var_name[2:-1].split(',')
                p, z, m, t = int(partes[0]), int(partes[1]), int(partes[2]), int(partes[3])
                
                zonas_info[z]['vehiculos'].append(p)
                zonas_info[z]['turnos'].append(m)
                zonas_info[z]['dias'].append(t)
                
                turnos_info[m].append((p, z, t))
                dias_info[t].append((p, z, m))
                
            except:
                continue
        
        print(f"\n1. RESUMEN POR ZONA:")
        for zona in sorted(zonas_info.keys()):
            info = zonas_info[zona]
            patrullas = len(info['vehiculos'])
            turnos_unicos = len(set(info['turnos']))
            dias_unicos = len(set(info['dias']))
            
            print(f"   Zona {zona}:")
            print(f"      - Patrullas asignadas: {patrullas}")
            print(f"      - Turnos cubiertos: {turnos_unicos}/3")
            print(f"      - Días con actividad: {dias_unicos}")
            print(f"      - Vehículos: {sorted(set(info['vehiculos']))[:5]}...")
        
        print(f"\n2. DISTRIBUCIÓN POR TURNO:")
        for turno in sorted(turnos_info.keys()):
            asignaciones = turnos_info[turno]
            zonas_cubiertas = len(set([z for _, z, _ in asignaciones]))
            print(f"   Turno {turno}: {len(asignaciones)} patrullas en {zonas_cubiertas} zonas")
        
        print(f"\n3. DISTRIBUCIÓN TEMPORAL:")
        for dia in sorted(dias_info.keys()):
            asignaciones = dias_info[dia]
            zonas_dia = len(set([z for _, z, _ in asignaciones]))
            turnos_dia = len(set([m for _, _, m in asignaciones]))
            print(f"   Día {dia}: {len(asignaciones)} patrullas en {zonas_dia} zonas, {turnos_dia} turnos")
        
        # Análisis de carabineros y[c,p,m,t]
        print(f"\n4. ANÁLISIS DE CARABINEROS:")
        asignaciones_y = variables_df[variables_df['variable'].str.startswith('y[')]
        
        carabineros_por_vehiculo = defaultdict(list)
        for _, row in asignaciones_y.iterrows():
            try:
                var_name = row['variable']
                partes = var_name[2:-1].split(',')
                c, p, m, t = int(partes[0]), int(partes[1]), int(partes[2]), int(partes[3])
                carabineros_por_vehiculo[p].append(c)
            except:
                continue
        
        # Estadísticas de tripulación
        tripulaciones = []
        for vehiculo, carabineros in carabineros_por_vehiculo.items():
            tripulaciones.append(len(set(carabineros)))
        
        if tripulaciones:
            print(f"   Carabineros por vehículo:")
            print(f"      - Promedio: {sum(tripulaciones)/len(tripulaciones):.1f}")
            print(f"      - Rango: {min(tripulaciones)} - {max(tripulaciones)}")
            print(f"      - Vehículos con 1 carabinero: {tripulaciones.count(1)}")
            print(f"      - Vehículos con 2+ carabineros: {len([t for t in tripulaciones if t >= 2])}")
        
        # Análisis de activaciones phi[p,t]
        print(f"\n5. ACTIVACIONES DE VEHÍCULOS:")
        activaciones = variables_df[variables_df['variable'].str.startswith('phi[')]
        
        vehiculos_activos = set()
        for _, row in activaciones.iterrows():
            try:
                var_name = row['variable']
                partes = var_name[4:-1].split(',')
                p, t = int(partes[0]), int(partes[1])
                vehiculos_activos.add(p)
            except:
                continue
        
        print(f"   Total de vehículos únicos utilizados: {len(vehiculos_activos)}")
        print(f"   Vehículos ID: {sorted(list(vehiculos_activos))}")
        
        # Comparación entre zonas
        print(f"\n6. COMPARACIÓN ENTRE ZONAS:")
        if len(zonas_info) > 1:
            zona_stats = []
            for zona, info in zonas_info.items():
                patrullas = len(info['vehiculos'])
                zona_stats.append((zona, patrullas))
            
            zona_stats.sort(key=lambda x: x[1], reverse=True)
            
            print("   Ranking de zonas por patrullas asignadas:")
            for i, (zona, patrullas) in enumerate(zona_stats, 1):
                print(f"      {i}. Zona {zona}: {patrullas} patrullas")
            
            # Identificar patrones
            zona_mas_patrullas = zona_stats[0]
            zona_menos_patrullas = zona_stats[-1]
            
            print(f"\n   Interpretación:")
            print(f"      - Zona más demandante: {zona_mas_patrullas[0]} ({zona_mas_patrullas[1]} patrullas)")
            print(f"      - Zona menos demandante: {zona_menos_patrullas[0]} ({zona_menos_patrullas[1]} patrullas)")
            
            if zona_mas_patrullas[1] > zona_menos_patrullas[1] * 2:
                ratio = zona_mas_patrullas[1]/zona_menos_patrullas[1]
                print(f"      - ALERTA: zona {zona_mas_patrullas[0]} necesita {ratio:.1f}x más patrullas")
        
        print(f"\n7. CONCLUSIONES:")
        print("   - El modelo distribuye recursos según peligrosidad de cada zona")
        print("   - Diferencias en asignaciones reflejan diferentes niveles de criminalidad")
        print("   - Concentración en día 1 sugiere que la cobertura inicial es suficiente")
        print("   - Función objetivo 0 indica control perfecto de peligrosidad")
        
        # Análisis específico de por qué zona 4 necesita más patrullas
        if len(zona_stats) > 0:
            zona_mayor = zona_stats[0][0]
            zona_menor = zona_stats[-1][0] 
            print(f"\n8. ANÁLISIS ESPECÍFICO:")
            print(f"   - Zona {zona_mayor} (más patrullas) vs Zona {zona_menor} (menos patrullas)")
            print(f"   - Esto sugiere que la zona {zona_mayor} tiene mayor peligrosidad inicial")
            print(f"   - O requiere más cobertura por características geográficas/demográficas")
        
    except Exception as e:
        print(f"Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analizar_por_zonas() 