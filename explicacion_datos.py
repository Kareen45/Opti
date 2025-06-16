import pandas as pd
import os
from parametros import cargar_parametros

def explicar_datos():
    """
    Explicación completa de la naturaleza de los datos en el proyecto
    """
    
    print("="*80)
    print("       EXPLICACIÓN COMPLETA DE LOS DATOS DEL PROYECTO")
    print("="*80)
    
    print("\n1. DATOS DE ENTRADA (Carpeta 'data/')")
    print("-"*50)
    
    # 1. ZONAS
    try:
        zonas_df = pd.read_csv("data/zonas.csv")
        print(f"\nA) ZONAS GEOGRÁFICAS (zonas.csv)")
        print(f"   - Propósito: Define las {len(zonas_df)} comunas de Santiago")
        print(f"   - Información: Compatibilidad con tipos de vehículos")
        print(f"   - Campos: {list(zonas_df.columns)}")
        print(f"   - Ejemplo: Zona 0 (Cerrillos) - Compatible con moto, caballo, furgón")
        print(f"   - Uso en modelo: Determina qué vehículos pueden patrullar cada zona")
        
        # Mostrar algunas zonas específicas
        print(f"\n   - MUESTRA DE ZONAS INCLUIDAS:")
        for i, row in zonas_df.head(8).iterrows():
            nombre = row['nombre_zona']
            compatibles = []
            if row['compatible_moto']: compatibles.append('moto')
            if row['compatible_bici']: compatibles.append('bici') 
            if row['compatible_caballo']: compatibles.append('caballo')
            if row['compatible_auto']: compatibles.append('auto')
            if row['compatible_furgon']: compatibles.append('furgón')
            print(f"     * Zona {i}: {nombre} → {', '.join(compatibles) if compatibles else 'sin vehículos'}")
    except Exception as e:
        print(f"   Error leyendo zonas: {e}")
    
    # 2. DELITOS CON VALORES ESPECÍFICOS
    try:
        delitos_df = pd.read_csv("data/tipos_delitos.csv")
        incidencias_df = pd.read_csv("data/incidencia_delito.csv")
        print(f"\nB) CRIMINALIDAD")
        print(f"   - tipos_delitos.csv: {len(delitos_df)} tipos de delitos")
        print(f"     * Campos: {list(delitos_df.columns)}")
        print(f"     * Factor 'idd': Peso de peligrosidad (1.0 = más grave)")
        
        print(f"\n   - TIPOS DE DELITOS Y SUS PESOS:")
        for _, row in delitos_df.iterrows():
            print(f"     * {row['nombre_delito']}: peso = {row['idd']:.3f}")
        
        print(f"\n   - incidencia_delito.csv: {len(incidencias_df)} registros")
        print(f"     * Campos: {list(incidencias_df.columns)}")
        print(f"     * Datos: Probabilidad de cada delito en cada zona")
        
        # Mostrar zonas con mayor criminalidad
        criminalidad_por_zona = incidencias_df.groupby('id_zona')['incidencia'].sum().sort_values(ascending=False)
        print(f"\n   - ZONAS CON MAYOR CRIMINALIDAD TOTAL:")
        for i, (zona_id, total_incidencia) in enumerate(criminalidad_por_zona.head(5).items()):
            zona_nombre = zonas_df[zonas_df['id_zona'] == zona_id]['nombre_zona'].iloc[0]
            print(f"     {i+1}. Zona {zona_id} ({zona_nombre}): {total_incidencia:.3f}")
        
        print(f"\n   - Uso: Calcula peligrosidad inicial u[z,t] para cada zona")
    except Exception as e:
        print(f"   Error leyendo delitos: {e}")
    
    # 3. CARABINEROS
    try:
        carabineros_df = pd.read_csv("data/carabineros.csv")
        print(f"\nC) RECURSOS HUMANOS (carabineros.csv)")
        print(f"   - Total: {len(carabineros_df)} carabineros")
        print(f"   - Campos: {list(carabineros_df.columns)}")
        print(f"   - Experiencia: Rango {carabineros_df['experiencia'].min()}-{carabineros_df['experiencia'].max()} años")
        print(f"   - Distribución por estación: {carabineros_df['id_estacion'].nunique()} estaciones")
        print(f"   - Uso: Restricción R3 requiere experiencia mínima por patrulla")
        
        exp_stats = carabineros_df['experiencia'].value_counts().sort_index()
        print(f"   - DISTRIBUCIÓN DE EXPERIENCIA:")
        for exp, count in exp_stats.items():
            porcentaje = (count / len(carabineros_df)) * 100
            print(f"     * {exp} años: {count} carabineros ({porcentaje:.1f}%)")
    except Exception as e:
        print(f"   Error leyendo carabineros: {e}")
    
    # 4. VEHÍCULOS
    try:
        vehiculos_df = pd.read_csv("data/vehiculos.csv")
        print(f"\nD) FLOTA VEHICULAR (vehiculos.csv)")
        print(f"   - Total: {len(vehiculos_df)} vehículos")
        print(f"   - Campos: {list(vehiculos_df.columns)}")
        
        if 'tipo_vehiculo' in vehiculos_df.columns:
            tipos = vehiculos_df['tipo_vehiculo'].value_counts()
            print(f"   - TIPOS DISPONIBLES:")
            for tipo, count in tipos.items():
                porcentaje = (count / len(vehiculos_df)) * 100
                print(f"     * {tipo}: {count} unidades ({porcentaje:.1f}%)")
        
        print(f"   - Uso: Variables x[p,z,m,t] asignan vehículo p a zona z")
    except Exception as e:
        print(f"   Error leyendo vehículos: {e}")
    
    # 5. COMISARÍAS
    try:
        comisarias_df = pd.read_csv("data/comisarias.csv")
        print(f"\nE) ESTACIONES DE TRABAJO (comisarias.csv)")
        print(f"   - Total: {len(comisarias_df)} comisarías")
        print(f"   - Campos: {list(comisarias_df.columns)}")
        if 'presupuesto_anual' in comisarias_df.columns:
            presup_stats = comisarias_df['presupuesto_anual'].describe()
            print(f"   - ESTADÍSTICAS PRESUPUESTARIAS:")
            print(f"     * Promedio: ${presup_stats['mean']:,.0f}")
            print(f"     * Mediana: ${presup_stats['50%']:,.0f}")
            print(f"     * Rango: ${presup_stats['min']:,.0f} - ${presup_stats['max']:,.0f}")
            print(f"     * Desviación estándar: ${presup_stats['std']:,.0f}")
        print(f"   - Uso: Restricción R11 limita gasto por estación")
    except Exception as e:
        print(f"   Error leyendo comisarías: {e}")
    
    # 6. COSTOS
    try:
        costos_df = pd.read_csv("data/costos_diarios.csv")
        print(f"\nF) COSTOS OPERACIONALES (costos_diarios.csv)")
        print(f"   - Registros: {len(costos_df)}")
        print(f"   - Campos: {list(costos_df.columns)}")
        
        # Mostrar estadísticas de costos por tipo de vehículo
        print(f"   - COSTOS PROMEDIO POR TIPO DE VEHÍCULO:")
        for col in costos_df.columns:
            if col.startswith('Costo_uso_'):
                tipo = col.replace('Costo_uso_', '').capitalize()
                promedio = costos_df[col].mean()
                print(f"     * {tipo}: ${promedio:,.0f}/día")
        
        print(f"   - Uso: Calcula costo diario de cada patrulla para R11")
    except Exception as e:
        print(f"   Error leyendo costos: {e}")
    
    print("\n\n2. PARÁMETROS DEL MODELO UTILIZADOS")
    print("-"*50)
    
    # Cargar parámetros actuales
    try:
        # Cargar parámetros del modelo de 5 zonas
        params = cargar_parametros(modo_testing="cinco_zonas", horizonte="mensual")
        
        print(f"\nA) CONFIGURACIÓN ACTUAL:")
        print(f"   - Modo: 5 zonas + 30 días")
        print(f"   - Zonas utilizadas: {len(params['Z'])} de 32 total")
        print(f"   - Carabineros: {len(params['C'])} de 1320 total")
        print(f"   - Vehículos: {len(params['P'])} de 977 total")
        print(f"   - Turnos por día: {len(params['M'])}")
        print(f"   - Días de simulación: {len(params['T'])}")
        
        print(f"\nB) PARÁMETROS CLAVE:")
        print(f"   - λ (lambda): {params['lambda']:.2f} - Sensibilidad aumento peligrosidad")
        print(f"   - κ (kappa): {params['kappa']:.1f} - Patrullas mínimas requeridas por zona-turno")
        print(f"   - Γ (Gamma): {params['Gamma']:.1f} - Factor de decaimiento de peligrosidad")
        # mu no existe en los parámetros, es un valor fijo
        print(f"   - Experiencia mínima: 2.0 años promedio por patrulla (restricción R3)")
        
        print(f"\nC) PELIGROSIDAD INICIAL POR ZONA:")
        zonas_nombres = {0: "Cerrillos", 1: "Cerro Navia", 2: "Conchalí", 3: "El Bosque", 4: "Estación Central"}
        for z in params['Z']:
            nombre = zonas_nombres.get(z, f"Zona {z}")
            peligrosidad = params['zeta'][z]  # zeta es la peligrosidad inicial
            print(f"   - {nombre}: u[{z},0] = {peligrosidad:.4f}")
        
    except Exception as e:
        print(f"   Error cargando parámetros: {e}")
    
    print("\n\n3. DATOS DE SALIDA (Carpeta 'resultados/')")
    print("-"*50)
    
    # RESULTADOS CON VALORES ESPECÍFICOS
    try:
        if os.path.exists("resultados/variables_activas.xlsx"):
            variables_df = pd.read_excel("resultados/variables_activas.xlsx")
            print(f"\nA) VARIABLES ACTIVAS (variables_activas.xlsx)")
            print(f"   - Registros: {len(variables_df)} variables con valor > 0")
            print(f"   - Campos: {list(variables_df.columns)}")
            print(f"   - Contenido: Solución óptima del modelo")
            
            # Analizar tipos de variables
            tipos_vars = {}
            for _, row in variables_df.iterrows():
                var_name = row['variable']
                if var_name.startswith('x['):
                    tipos_vars['x'] = tipos_vars.get('x', 0) + 1
                elif var_name.startswith('y['):
                    tipos_vars['y'] = tipos_vars.get('y', 0) + 1
                elif var_name.startswith('phi['):
                    tipos_vars['phi'] = tipos_vars.get('phi', 0) + 1
                elif var_name.startswith('u['):
                    tipos_vars['u'] = tipos_vars.get('u', 0) + 1
                elif var_name.startswith('zeta['):
                    tipos_vars['zeta'] = tipos_vars.get('zeta', 0) + 1
            
            print(f"\n   - DISTRIBUCIÓN POR TIPO:")
            for tipo, count in tipos_vars.items():
                descripcion = {
                    'x': 'Asignaciones patrulla-zona',
                    'y': 'Asignaciones carabinero-patrulla', 
                    'phi': 'Activaciones de vehículo',
                    'u': 'Peligrosidad por zona',
                    'zeta': 'Déficit de cobertura'
                }
                print(f"     * {tipo}: {count} variables ({descripcion.get(tipo, 'Desconocido')})")
            
            # Interpretación detallada de variables X
            print(f"\n   - ASIGNACIONES PATRULLA-ZONA (variables x):")
            x_vars = variables_df[variables_df['variable'].str.startswith('x[')]
            zonas_asignaciones = {}
            turnos_nombres = {1: "Mañana", 2: "Tarde", 3: "Noche"}
            zonas_nombres = {0: "Cerrillos", 1: "Cerro Navia", 2: "Conchalí", 3: "El Bosque", 4: "Estación Central"}
            
            for _, row in x_vars.head(10).iterrows():
                var_name = row['variable']
                valor = row['valor']
                parts = var_name[2:-1].split(',')
                p, z, m, t = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
                zona_nombre = zonas_nombres.get(z, f"Zona {z}")
                turno_nombre = turnos_nombres.get(m, f"Turno {m}")
                print(f"     * Vehículo {p} → {zona_nombre}, {turno_nombre}, Día {t}")
                
                if z not in zonas_asignaciones:
                    zonas_asignaciones[z] = 0
                zonas_asignaciones[z] += 1
            
            print(f"\n   - RESUMEN POR ZONA:")
            for zona_id, count in sorted(zonas_asignaciones.items()):
                zona_nombre = zonas_nombres.get(zona_id, f"Zona {zona_id}")
                print(f"     * {zona_nombre}: {count} asignaciones de patrulla")
            
            # Variables Y (carabineros)
            print(f"\n   - ASIGNACIONES CARABINERO-PATRULLA (variables y):")
            y_vars = variables_df[variables_df['variable'].str.startswith('y[')]
            vehiculos_tripulacion = {}
            
            for _, row in y_vars.head(10).iterrows():
                var_name = row['variable']
                valor = row['valor']
                parts = var_name[2:-1].split(',')
                c, p, m, t = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
                turno_nombre = turnos_nombres.get(m, f"Turno {m}")
                print(f"     * Carabinero {c} → Vehículo {p}, {turno_nombre}, Día {t}")
                
                if p not in vehiculos_tripulacion:
                    vehiculos_tripulacion[p] = set()
                vehiculos_tripulacion[p].add(c)
            
            print(f"\n   - TRIPULACIÓN POR VEHÍCULO:")
            for vehiculo, carabineros in sorted(vehiculos_tripulacion.items()):
                print(f"     * Vehículo {vehiculo}: {len(carabineros)} carabineros")
            
            # Variables PHI (activaciones)
            print(f"\n   - ACTIVACIONES DE VEHÍCULOS (variables phi):")
            phi_vars = variables_df[variables_df['variable'].str.startswith('phi[')]
            for _, row in phi_vars.iterrows():
                var_name = row['variable']
                valor = row['valor']
                parts = var_name[4:-1].split(',')
                p, t = int(parts[0]), int(parts[1])
                print(f"     * Vehículo {p} activo en Día {t}")
            
            # Variables U (peligrosidad)
            u_vars = variables_df[variables_df['variable'].str.startswith('u[')]
            if len(u_vars) > 0:
                print(f"\n   - PELIGROSIDAD FINAL (variables u):")
                for _, row in u_vars.iterrows():
                    var_name = row['variable']
                    valor = row['valor']
                    parts = var_name[2:-1].split(',')
                    z, t = int(parts[0]), int(parts[1])
                    zona_nombre = zonas_nombres.get(z, f"Zona {z}")
                    print(f"     * {zona_nombre} día {t}: u[{z},{t}] = {valor:.6f}")
            
            # Variables ZETA (déficits)
            zeta_vars = variables_df[variables_df['variable'].str.startswith('zeta[')]
            if len(zeta_vars) > 0:
                print(f"\n   - DÉFICITS DE COBERTURA (variables zeta):")
                for _, row in zeta_vars.iterrows():
                    var_name = row['variable']
                    valor = row['valor']
                    parts = var_name[5:-1].split(',')
                    z, t = int(parts[0]), int(parts[1])
                    zona_nombre = zonas_nombres.get(z, f"Zona {z}")
                    print(f"     * {zona_nombre} día {t}: zeta[{z},{t}] = {valor:.6f}")
            else:
                print(f"\n   - DÉFICITS DE COBERTURA: NINGUNO (todas las zonas cubiertas)")
        
        if os.path.exists("resultados/resumen_diario_recursos.xlsx"):
            resumen_df = pd.read_excel("resultados/resumen_diario_recursos.xlsx")
            print(f"\nB) RESUMEN DIARIO (resumen_diario_recursos.xlsx)")
            print(f"   - Registros: {len(resumen_df)} días")
            print(f"   - Campos: {list(resumen_df.columns)}")
            print(f"   - Contenido: Agregación diaria de recursos utilizados")
            if len(resumen_df) > 0:
                print(f"\n   - MÉTRICAS DEL DÍA 1:")
                for col in resumen_df.columns:
                    if col != 'dia':
                        valor = resumen_df.iloc[0][col]
                        print(f"     * {col}: {valor}")
    except Exception as e:
        print(f"   Error leyendo resultados: {e}")
    
    print("\n\n4. FLUJO DE DATOS EN EL MODELO")
    print("-"*50)
    
    print("""
   ENTRADA → PROCESAMIENTO → SALIDA
   
   zonas.csv ────┐
   delitos.csv ──┤
   carabineros.csv ─┤──→ MODELO DE ──→ variables_activas.xlsx
   vehiculos.csv ──┤    OPTIMIZACIÓN    resumen_diario.xlsx
   comisarias.csv ─┤    (Gurobi)
   costos.csv ────┘
   
   TRANSFORMACIONES CLAVE:
   1. incidencia_delito.csv → peligrosidad inicial u[z,1] 
   2. Compatibilidades → restricciones de asignación
   3. Experiencia → restricción R3 de calidad
   4. Presupuestos → restricción R11 de costos
   5. Solución → asignaciones concretas de patrullas
   """)
    
    print("\n\n5. CÓMO INTERPRETAR LOS RESULTADOS")
    print("-"*50)
    
    print("""
   VARIABLES DE DECISIÓN:
   • x[p,z,m,t] = 1: Vehículo p patrulla zona z en turno m del día t
   • y[c,p,m,t] = 1: Carabinero c asignado a vehículo p en turno m del día t  
   • phi[p,t] = 1: Vehículo p está activo en día t
   • u[z,t]: Nivel de peligrosidad en zona z al final del día t
   • zeta[z,t]: Déficit de cobertura en zona z en día t
   
   TURNOS:
   • m=1: Mañana (08:00-16:00)
   • m=2: Tarde (16:00-00:00)  
   • m=3: Noche (00:00-08:00)
   
   MÉTRICAS CLAVE:
   • Función objetivo = Σ u[z,t]: Peligrosidad total acumulada
   • Variables activas: Asignaciones concretas realizadas
   • Recursos utilizados: Vehículos y carabineros empleados
   """)
    
    print("\n\n6. ARCHIVOS RECOMENDADOS PARA ANÁLISIS DETALLADO")
    print("-"*50)
    
    print("""
   PARA ENTENDER EL PROBLEMA:
   📁 data/incidencia_delito.csv → Ver criminalidad por zona
   📁 data/tipos_delitos.csv → Entender gravedad de delitos
   📁 data/zonas.csv → Conocer restricciones geográficas
   
   PARA ANALIZAR SOLUCIONES:
   📊 resultados/variables_activas.xlsx → Solución completa
   📊 resultados/resumen_diario_recursos.xlsx → Agregados diarios
   
   PARA ANÁLISIS AVANZADO:
   🐍 analisis_zonas_simple.py → Patrones por zona
   🐍 analisis_resultados.py → Evolución temporal
   🐍 diagnostico.py → Validación de parámetros
   """)

if __name__ == "__main__":
    explicar_datos() 