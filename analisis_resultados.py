import pandas as pd
from collections import defaultdict

def analizar_resultados():
    """
    Analiza los resultados del modelo de patrullaje preventivo
    con foco en la evolución temporal de las variables de decisión
    """
    
    try:
        # Cargar resultados
        print("📊 Cargando archivos de resultados...")
        variables_df = pd.read_excel("resultados/variables_activas.xlsx")
        resumen_df = pd.read_excel("resultados/resumen_diario_recursos.xlsx")
        
        print(f"✅ Variables cargadas: {len(variables_df)} filas")
        print(f"✅ Resumen cargado: {len(resumen_df)} filas")
        print(f"📋 Columnas en resumen: {list(resumen_df.columns)}")
        
        print("\n📊 ANÁLISIS DETALLADO DE RESULTADOS")
        print("="*50)
        
        # 1. Análisis general
        print("\n1️⃣ RESUMEN GENERAL:")
        print(f"   • Total de variables activas: {len(variables_df)}")
        
        if len(resumen_df) > 0 and 'dia' in resumen_df.columns:
            print(f"   • Días analizados: {resumen_df['dia'].max()}")
        else:
            print(f"   • Estructura del resumen: {resumen_df.head()}")
        
        # 2. Evolución temporal de recursos (si existe)
        print("\n2️⃣ EVOLUCIÓN TEMPORAL DE RECURSOS:")
        
        cols_interes = ['patrullas_asignadas', 'carabineros_asignados', 'vehiculos_utilizados']
        for col in cols_interes:
            if col in resumen_df.columns:
                promedio = resumen_df[col].mean()
                variacion = resumen_df[col].std()
                print(f"   • {col}: Promedio={promedio:.1f}, Desv.Est={variacion:.2f}")
            else:
                print(f"   • {col}: No encontrada")
        
        # 3. Análisis de peligrosidad
        print("\n3️⃣ EVOLUCIÓN DE PELIGROSIDAD:")
        if 'nivel_peligrosidad' in resumen_df.columns and len(resumen_df) > 0:
            peligrosidad_inicial = resumen_df['nivel_peligrosidad'].iloc[0]
            peligrosidad_final = resumen_df['nivel_peligrosidad'].iloc[-1] 
            print(f"   • Peligrosidad inicial: {peligrosidad_inicial:.3f}")
            print(f"   • Peligrosidad final: {peligrosidad_final:.3f}")
            print(f"   • Reducción: {((peligrosidad_inicial - peligrosidad_final)/max(peligrosidad_inicial, 1e-6))*100:.1f}%")
        else:
            print("   • No hay datos de peligrosidad o resumen vacío")
        
        # 4. Análisis por tipo de variable
        print("\n4️⃣ DISTRIBUCIÓN DE VARIABLES ACTIVAS:")
        tipos_vars = defaultdict(int)
        
        if len(variables_df) > 0:
            for _, row in variables_df.iterrows():
                var_name = str(row['variable'])
                if var_name.startswith('x['):
                    tipos_vars['Asignaciones patrulla-zona'] += 1
                elif var_name.startswith('y['):
                    tipos_vars['Asignaciones carabinero-patrulla'] += 1
                elif var_name.startswith('phi['):
                    tipos_vars['Activaciones de vehículo'] += 1
                elif var_name.startswith('zeta['):
                    tipos_vars['Niveles de peligrosidad'] += 1
                elif var_name.startswith('u['):
                    tipos_vars['Déficits de cobertura'] += 1
        
        for tipo, cantidad in tipos_vars.items():
            print(f"   • {tipo}: {cantidad}")
        
        if len(tipos_vars) == 0:
            print("   • No se encontraron variables activas o hay un problema con el formato")
        
        # 5. Análisis de déficits
        if len(variables_df) > 0:
            deficits = variables_df[variables_df['variable'].str.startswith('u[')]
            if not deficits.empty:
                print(f"\n5️⃣ ANÁLISIS DE DÉFICITS:")
                print(f"   • Total de déficits registrados: {len(deficits)}")
                print(f"   • Valor promedio de déficit: {deficits['valor'].mean():.3f}")
                print(f"   • Máximo déficit: {deficits['valor'].max():.3f}")
            else:
                print(f"\n5️⃣ ANÁLISIS DE DÉFICITS:")
                print("   • No se registraron déficits (todas las zonas cubiertas)")
        
        # 6. Verificar F.O. = 0
        print("\n6️⃣ INTERPRETACIÓN - FUNCIÓN OBJETIVO:")
        
        if 'nivel_peligrosidad' in resumen_df.columns:
            peligrosidad_total = resumen_df['nivel_peligrosidad'].sum()
        else:
            # Calcular desde variables zeta
            zetas = variables_df[variables_df['variable'].str.startswith('zeta[')]
            peligrosidad_total = zetas['valor'].sum() if len(zetas) > 0 else 0
        
        print(f"   • Peligrosidad total acumulada: {peligrosidad_total:.6f}")
        
        if peligrosidad_total < 1e-6:
            print("   ⚠️  PROBLEMA IDENTIFICADO: Función objetivo ≈ 0")
            print("      • El modelo logra reducir completamente la peligrosidad")
            print("      • Esto puede ser poco realista en escenarios reales")
            print("      • CAUSAS POSIBLES:")
            print("        - λ = 0.1 es muy bajo (poca sensibilidad al déficit)")
            print("        - κ = 0.5 es muy bajo (pocos patrullas requeridas)")
            print("        - Solo 1 zona facilita la cobertura completa")
            print("        - Muchos recursos disponibles vs. pocas zonas")
        
        # 7. Mostrar variables de ejemplo
        if len(variables_df) > 0:
            print("\n7️⃣ MUESTRA DE VARIABLES ACTIVAS:")
            print("   Primeras 10 variables:")
            for i, (_, row) in enumerate(variables_df.head(10).iterrows()):
                print(f"      {row['variable']} = {row['valor']}")
        
        print("\n8️⃣ RECOMENDACIONES:")
        print("   1. Probar con --diez-zonas para mayor complejidad")
        print("   2. Incrementar λ de 0.1 a 0.3-0.5")
        print("   3. Incrementar κ de 0.5 a 1.0-2.0")
        print("   4. Verificar datos de incidencia inicial")
        
        print("\n✅ Análisis completado")
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analizar_resultados() 