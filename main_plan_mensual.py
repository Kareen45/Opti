"""
Generador de Plan Mensual - Resuelve día por día para asegurar actividad diaria
"""

from parametros import cargar_parametros
from modelo import construir_modelo, resolver_modelo
import pandas as pd
import sys

def generar_plan_mensual(modo_testing="cinco_zonas"):
    """
    Genera un plan mensual resolviendo múltiples problemas de corto plazo
    """
    
    print("🗓️ GENERANDO PLAN MENSUAL REAL")
    print("="*50)
    
    # Cargar parámetros base
    params = cargar_parametros(modo_testing=modo_testing, horizonte="testing")  # 7 días por iteración
    
    plan_completo = []
    dias_totales = 30
    
    for semana in range(1, 5):  # 4 semanas
        print(f"\n📅 SEMANA {semana} (días {(semana-1)*7 + 1} a {semana*7})")
        
        # Ajustar días para esta semana
        params["T"] = list(range((semana-1)*7 + 1, semana*7 + 1))
        
        # Incrementar ligeramente la peligrosidad cada semana (criminalidad acumulada)
        factor_aumento = 1.0 + 0.1 * (semana - 1)  # 10% más cada semana
        for z in params["Z"]:
            params["zeta"][z] = params["zeta"][z] * factor_aumento
        
        print(f"   🎯 Resolviendo días {params['T']}")
        print(f"   📈 Factor criminalidad: {factor_aumento:.2f}")
        
        # Construir y resolver modelo para esta semana
        try:
            model = construir_modelo(params)
            exito = resolver_modelo(model)
            
            if exito:
                # Extraer variables activas de esta semana
                variables_semana = []
                for var in model.getVars():
                    if var.X > 1e-6:  # Variable activa
                        variables_semana.append({
                            'semana': semana,
                            'variable': var.VarName,
                            'valor': var.X
                        })
                
                plan_completo.extend(variables_semana)
                print(f"   ✅ Semana {semana}: {len(variables_semana)} asignaciones")
            
            else:
                print(f"   ❌ Error en semana {semana}")
                
        except Exception as e:
            print(f"   ❌ Error en semana {semana}: {e}")
            continue
    
    # Guardar plan completo
    if plan_completo:
        df_plan = pd.DataFrame(plan_completo)
        df_plan.to_excel("resultados/plan_mensual_completo.xlsx", index=False)
        
        print(f"\n📊 RESUMEN DEL PLAN MENSUAL:")
        print(f"   • Total asignaciones: {len(plan_completo)}")
        print(f"   • Semanas completadas: {df_plan['semana'].nunique()}")
        
        # Análisis por semana
        for semana in df_plan['semana'].unique():
            count = len(df_plan[df_plan['semana'] == semana])
            print(f"   • Semana {semana}: {count} asignaciones")
        
        print(f"\n✅ Plan guardado en: resultados/plan_mensual_completo.xlsx")
        
        # Generar resumen diario
        generar_resumen_diario(df_plan)
        
    else:
        print("❌ No se pudo generar el plan mensual")

def generar_resumen_diario(df_plan):
    """
    Genera un resumen día por día del plan mensual
    """
    
    resumen_diario = []
    
    # Extraer información por día
    for _, row in df_plan.iterrows():
        var_name = row['variable']
        semana = row['semana']
        
        # Extraer día de la variable
        if 'x[' in var_name:  # x[p,z,m,t]
            import re
            match = re.search(r'x\[\d+,\d+,\d+,(\d+)\]', var_name)
            if match:
                dia = int(match.group(1))
                resumen_diario.append({
                    'dia': dia,
                    'semana': semana,
                    'tipo': 'patrulla',
                    'variable': var_name
                })
    
    if resumen_diario:
        df_resumen = pd.DataFrame(resumen_diario)
        
        # Contar por día
        conteo_diario = df_resumen.groupby('dia').size().reset_index(columns=['asignaciones'])
        conteo_diario.to_excel("resultados/resumen_diario_plan_mensual.xlsx", index=False)
        
        print(f"✅ Resumen diario guardado en: resultados/resumen_diario_plan_mensual.xlsx")

if __name__ == "__main__":
    modo = "cinco_zonas"
    if len(sys.argv) > 1:
        if sys.argv[1] == "--testing":
            modo = True
        elif sys.argv[1] == "--cinco-zonas":
            modo = "cinco_zonas"
    
    generar_plan_mensual(modo) 