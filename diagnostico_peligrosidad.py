import pandas as pd
import re
from collections import defaultdict

def diagnosticar_peligrosidad():
    """
    Diagnóstico específico del comportamiento de peligrosidad día a día
    """
    
    print("="*60)
    print("    DIAGNÓSTICO: ¿POR QUÉ SOLO 1 DÍA?")
    print("="*60)
    
    try:
        # Cargar variables activas
        df = pd.read_excel('resultados/variables_activas.xlsx')
        
        print("\n1. ANÁLISIS DE DÍAS CON ACTIVIDAD")
        print("-"*40)
        
        # Extraer días de todas las variables
        dias_por_tipo = defaultdict(set)
        
        for _, row in df.iterrows():
            var_name = row['variable']
            
            # Extraer día según el tipo de variable
            if var_name.startswith('x['):  # x[p,z,m,t]
                match = re.search(r'x\[\d+,\d+,\d+,(\d+)\]', var_name)
                if match:
                    dia = int(match.group(1))
                    dias_por_tipo['x (patrulla-zona)'].add(dia)
            
            elif var_name.startswith('y['):  # y[c,p,m,t]
                match = re.search(r'y\[\d+,\d+,\d+,(\d+)\]', var_name)
                if match:
                    dia = int(match.group(1))
                    dias_por_tipo['y (carabinero-patrulla)'].add(dia)
            
            elif var_name.startswith('phi['):  # phi[p,t]
                match = re.search(r'phi\[\d+,(\d+)\]', var_name)
                if match:
                    dia = int(match.group(1))
                    dias_por_tipo['phi (activación vehículo)'].add(dia)
            
            elif var_name.startswith('u['):  # u[z,t]
                match = re.search(r'u\[\d+,(\d+)\]', var_name)
                if match:
                    dia = int(match.group(1))
                    dias_por_tipo['u (peligrosidad)'].add(dia)
            
            elif var_name.startswith('zeta['):  # zeta[z,t]
                match = re.search(r'zeta\[\d+,(\d+)\]', var_name)
                if match:
                    dia = int(match.group(1))
                    dias_por_tipo['zeta (déficit)'].add(dia)
        
        # Mostrar días por tipo de variable
        todos_los_dias = set()
        for tipo, dias in dias_por_tipo.items():
            dias_ordenados = sorted(list(dias))
            todos_los_dias.update(dias)
            print(f"• {tipo}: días {dias_ordenados}")
            print(f"  Total: {len(dias)} días")
        
        print(f"\nRESUMEN: {len(todos_los_dias)} días únicos con actividad")
        print(f"Días: {sorted(list(todos_los_dias))}")
        
        print("\n2. ANÁLISIS DETALLADO POR DÍA")
        print("-"*40)
        
        # Contar variables por día
        conteo_por_dia = defaultdict(lambda: defaultdict(int))
        
        for _, row in df.iterrows():
            var_name = row['variable']
            valor = row['valor']
            
            # Determinar tipo y día
            if var_name.startswith('x['):
                match = re.search(r'x\[\d+,\d+,\d+,(\d+)\]', var_name)
                if match:
                    dia = int(match.group(1))
                    conteo_por_dia[dia]['asignaciones_patrulla'] += 1
            
            elif var_name.startswith('y['):
                match = re.search(r'y\[\d+,\d+,\d+,(\d+)\]', var_name)
                if match:
                    dia = int(match.group(1))
                    conteo_por_dia[dia]['asignaciones_carabinero'] += 1
            
            elif var_name.startswith('phi['):
                match = re.search(r'phi\[\d+,(\d+)\]', var_name)
                if match:
                    dia = int(match.group(1))
                    conteo_por_dia[dia]['activaciones_vehiculo'] += 1
            
            elif var_name.startswith('u['):
                match = re.search(r'u\[\d+,(\d+)\]', var_name)
                if match:
                    dia = int(match.group(1))
                    conteo_por_dia[dia]['peligrosidad_final'] += 1
                    # Mostrar valor de peligrosidad
                    zona_match = re.search(r'u\[(\d+),\d+\]', var_name)
                    if zona_match:
                        zona = int(zona_match.group(1))
                        print(f"    u[{zona},{dia}] = {valor:.6f}")
        
        # Mostrar conteo por día
        for dia in sorted(conteo_por_dia.keys()):
            counts = conteo_por_dia[dia]
            print(f"\nDía {dia}:")
            for tipo, count in counts.items():
                print(f"  • {tipo}: {count}")
        
        print("\n3. INTERPRETACIÓN DEL PROBLEMA")
        print("-"*40)
        
        if len(todos_los_dias) == 1 and 1 in todos_los_dias:
            print("PROBLEMA CONFIRMADO: Solo actividad en día 1")
            print("\nPOSIBLES CAUSAS:")
            print("1. kappa muy alto: El modelo satisface requerimientos desde día 1")
            print("2. lambda muy bajo: Poca sensibilidad a aumento de peligrosidad")
            print("3. Recursos excesivos vs. demanda de 5 zonas")
            print("4. Peligrosidad inicial muy baja")
            print("5. Factor Gamma permite decaimiento muy rápido")
            
            print("\nSOLUCIONES RECOMENDADAS:")
            print("• Reducir kappa de 12.0 a 5.0-8.0")
            print("• Incrementar lambda de 0.3 a 0.5-0.8") 
            print("• Verificar Gamma para que no sea demasiado alto")
            print("• Añadir 'crimen dinámico' que aparezca cada día")
            
        elif len(todos_los_dias) > 1:
            print("MODELO DINÁMICO: Actividad en múltiples días")
            print(f"Días activos: {sorted(list(todos_los_dias))}")
            
        else:
            print("CASO INESPERADO: Revisar datos")
        
        print("\n4. VERIFICACIÓN DE RESTRICCIONES TEMPORALES")
        print("-"*40)
        
        # Buscar variables u[z,t] para ver evolución de peligrosidad
        u_vars = df[df['variable'].str.startswith('u[')]
        if len(u_vars) > 0:
            print("Variables de peligrosidad encontradas:")
            for _, row in u_vars.iterrows():
                var_name = row['variable']
                valor = row['valor']
                print(f"  {var_name} = {valor:.6f}")
        else:
            print("NO se encontraron variables u[z,t] (peligrosidad)")
            print("Esto significa que el modelo NO está guardando la evolución de peligrosidad")
            print("El problema podría estar en main.py al guardar resultados")
        
        # Buscar variables zeta[z,t] para déficits
        zeta_vars = df[df['variable'].str.startswith('zeta[')]
        if len(zeta_vars) > 0:
            print("\nVariables de déficit encontradas:")
            for _, row in zeta_vars.iterrows():
                var_name = row['variable']
                valor = row['valor']
                print(f"  {var_name} = {valor:.6f}")
        else:
            print("\nNO hay déficits (zeta = 0 en todas las zonas/días)")
        
        print("\n5. CONCLUSIÓN")
        print("-"*40)
        
        if len(todos_los_dias) == 1:
            print("El modelo está funcionando 'demasiado bien':")
            print("• Encuentra una configuración óptima en día 1")
            print("• Esta configuración mantiene peligrosidad = 0 por 30 días")
            print("• Matemáticamente correcto, pero poco realista")
            print("\nPara mayor realismo, considera:")
            print("• Modelo con criminalidad dinámica")
            print("• Parámetros más restrictivos")
            print("• Más zonas o menos recursos")
            
    except Exception as e:
        print(f"Error durante diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnosticar_peligrosidad() 