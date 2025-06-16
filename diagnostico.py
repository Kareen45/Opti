import pandas as pd
from parametros import cargar_parametros

def diagnosticar_modelo():
    """
    Diagnostica los parámetros del modelo para entender por qué la F.O. es 0
    """
    
    print("🔍 DIAGNÓSTICO DEL MODELO")
    print("="*50)
    
    # Cargar parámetros
    print("\n1️⃣ Cargando parámetros...")
    parametros = cargar_parametros(modo_testing=True, horizonte="mensual")
    
    # Extraer información clave
    Z = parametros["Z"]
    T = parametros["T"]
    zeta = parametros["zeta"]
    lambda_ = parametros["lambda"]
    kappa = parametros["kappa"]
    Gamma = parametros["Gamma"]
    I = parametros["I"]
    IDD = parametros["IDD"]
    D = parametros["D"]
    
    print(f"\n2️⃣ PARÁMETROS BÁSICOS:")
    print(f"   • Zonas: {len(Z)} (IDs: {Z})")
    print(f"   • Días: {len(T)} (del {min(T)} al {max(T)})")
    print(f"   • λ (lambda): {lambda_}")
    print(f"   • κ (kappa): {kappa}")
    print(f"   • Γ (Gamma): {Gamma}")
    
    print(f"\n3️⃣ PELIGROSIDAD INICIAL:")
    for z in Z:
        print(f"   • Zona {z}: ζ[{z},1] = {zeta[z]:.6f}")
    
    print(f"\n4️⃣ DATOS DE INCIDENCIA:")
    print("   Incidencias por delito y zona:")
    for d in D:
        for z in Z:
            incidencia = I.get((d, z), 0)
            daño = IDD.get(d, 0)
            producto = incidencia * daño
            print(f"      Delito {d}, Zona {z}: I={incidencia:.3f}, IDD={daño:.3f}, I×IDD={producto:.6f}")
    
    print(f"\n5️⃣ CÁLCULO DE GAMMA:")
    print("   Peligrosidad teórica por zona:")
    for z in Z:
        peligrosidad_teorica = sum(I.get((d, z), 0) * IDD[d] for d in D)
        print(f"      Zona {z}: {peligrosidad_teorica:.6f}")
    
    print(f"\n6️⃣ ANÁLISIS DEL PROBLEMA:")
    
    # Verificar si zeta inicial es 0
    zeta_total = sum(zeta[z] for z in Z)
    if zeta_total < 1e-10:
        print("   ⚠️  PROBLEMA: Peligrosidad inicial ≈ 0")
        print("      • Si ζ[z,1] = 0, entonces no se requieren patrullas inicialmente")
        print("      • La restricción de cobertura κ×ζ[z,t-1] ≈ 0")
        print("      • El modelo puede asignar 0 patrullas sin penalización")
        
    # Verificar datos de incidencia
    incidencias_total = sum(I.get((d, z), 0) for d in D for z in Z)
    if incidencias_total < 1e-10:
        print("   ⚠️  PROBLEMA: Datos de incidencia ≈ 0")
        print("      • Sin incidencias, no hay peligrosidad base")
        
    # Verificar IDD
    idd_total = sum(IDD[d] for d in D)
    if idd_total < 1e-10:
        print("   ⚠️  PROBLEMA: Índices de daño ≈ 0")
        
    if Gamma < 1e-10:
        print("   ⚠️  PROBLEMA: Gamma ≈ 0")
        print("      • División por cero en cálculo de zeta")
        
    print(f"\n7️⃣ REQUERIMIENTOS DE PATRULLAS:")
    for z in Z:
        requerimiento = kappa * zeta[z]
        print(f"   • Zona {z}: κ×ζ = {kappa}×{zeta[z]:.6f} = {requerimiento:.6f} patrullas")
    
    requerimiento_total = sum(kappa * zeta[z] for z in Z)
    print(f"   • TOTAL REQUERIDO: {requerimiento_total:.6f} patrullas por turno")
    
    print(f"\n8️⃣ RECURSOS DISPONIBLES:")
    C = parametros["C"]
    P = parametros["P"]
    print(f"   • Carabineros disponibles: {len(C)}")
    print(f"   • Vehículos disponibles: {len(P)}")
    print(f"   • Máximo patrullas teóricas: {min(len(C), len(P))}")
    
    if requerimiento_total > 0:
        ratio_cobertura = min(len(C), len(P)) / requerimiento_total
        print(f"   • Ratio cobertura: {ratio_cobertura:.2f} (>1 = exceso, <1 = déficit)")
    
    print(f"\n9️⃣ ANÁLISIS ESPECÍFICO DEL PROBLEMA:")
    
    if requerimiento_total > min(len(C), len(P)):
        print("   ✅ RECURSOS INSUFICIENTES - modelo debe optimizar")
        print("      • Se requieren más patrullas de las disponibles")
        print("      • El modelo debería generar déficits y peligrosidad creciente")
    elif requerimiento_total < 0.1:
        print("   ⚠️  REQUERIMIENTOS MUY BAJOS")
        print("      • Con pocos requerimientos, el modelo puede asignar 0 patrullas")
        print("      • Incrementar κ o peligrosidad inicial")
    else:
        print("   ❓ CASO INTERMEDIO")
        print("      • Analizar restricciones específicas")
    
    print(f"\n10️⃣ SOLUCIONES SUGERIDAS:")
    print("   1. Verificar archivos CSV de datos")
    print("   2. Incrementar valores de incidencia artificialmente para testing")
    print("   3. Establecer peligrosidad inicial mínima (ej. 0.1)")
    print("   4. Revisar fórmula de cálculo de zeta")
    print("   5. Usar datos reales de criminalidad")

if __name__ == "__main__":
    diagnosticar_modelo() 