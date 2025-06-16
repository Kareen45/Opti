from gurobipy import *
from parametros import cargar_parametros

def test_modelo_simple():
    """
    Prueba un modelo simplificado para encontrar el problema
    """
    
    print("🔬 TEST DE MODELO SIMPLIFICADO")
    print("="*40)
    
    # Cargar parámetros
    parametros = cargar_parametros(modo_testing=True, horizonte="testing")  # Solo 7 días
    
    C = parametros["C"][:5]  # Solo 5 carabineros
    P = parametros["P"][:3]  # Solo 3 vehículos
    Z = parametros["Z"]      # 1 zona
    T = parametros["T"][:3]  # Solo 3 días
    M = parametros["M"][:1]  # Solo 1 turno
    
    print(f"📊 Datos simplificados:")
    print(f"   • Carabineros: {len(C)}")
    print(f"   • Vehículos: {len(P)}")
    print(f"   • Zonas: {len(Z)}")
    print(f"   • Días: {len(T)}")
    print(f"   • Turnos: {len(M)}")
    
    # Crear modelo
    model = Model("test_simple")
    model.setParam("OutputFlag", 1)
    
    # Variables principales
    print("\n🔨 Creando variables...")
    x = model.addVars(P, Z, M, T, vtype=GRB.BINARY, name="x")
    y = model.addVars(C, P, M, T, vtype=GRB.BINARY, name="y")
    
    print(f"   • Variables x: {len(P) * len(Z) * len(M) * len(T)}")
    print(f"   • Variables y: {len(C) * len(P) * len(M) * len(T)}")
    
    # Restricciones básicas
    print("\n⚙️  Agregando restricciones básicas...")
    
    # R1: Cada carabinero máximo 1 turno por día
    for c in C:
        for t in T:
            model.addConstr(
                sum(y[c,p,m,t] for p in P for m in M) <= 1,
                name=f"R1_c{c}_t{t}"
            )
    
    # R4: Cada vehículo máximo 1 zona por turno
    for p in P:
        for m in M:
            for t in T:
                model.addConstr(
                    sum(x[p,z,m,t] for z in Z) <= 1,
                    name=f"R4_p{p}_m{m}_t{t}"
                )
    
    # R6: Carabineros solo en vehículos activos
    for c in C:
        for p in P:
            for m in M:
                for t in T:
                    model.addConstr(
                        y[c,p,m,t] <= sum(x[p,z,m,t] for z in Z),
                        name=f"R6_c{c}_p{p}_m{m}_t{t}"
                    )
    
    # R7: Al menos 1 carabinero por vehículo activo
    for p in P:
        for m in M:
            for t in T:
                model.addConstr(
                    sum(x[p,z,m,t] for z in Z) <= sum(y[c,p,m,t] for c in C),
                    name=f"R7_p{p}_m{m}_t{t}"
                )
    
    # Función objetivo simple: minimizar uso total
    model.setObjective(
        sum(x[p,z,m,t] for p in P for z in Z for m in M for t in T),
        GRB.MINIMIZE
    )
    
    print(f"\n📊 Estadísticas del modelo:")
    print(f"   • Variables: {model.NumVars}")
    print(f"   • Restricciones: {model.NumConstrs}")
    
    # Resolver
    print("\n🚀 Resolviendo...")
    model.optimize()
    
    if model.Status == GRB.OPTIMAL:
        print("✅ SOLUCIÓN ÓPTIMA ENCONTRADA")
        print(f"   • Valor objetivo: {model.ObjVal}")
        
        # Contar variables activas
        activas = 0
        for var in model.getVars():
            if var.X > 1e-10:
                activas += 1
                if activas <= 10:  # Mostrar primeras 10
                    print(f"      {var.VarName} = {var.X}")
        
        print(f"   • Variables activas: {activas}/{model.NumVars}")
        
        if activas == 0:
            print("   ⚠️  TODAS LAS VARIABLES SON 0 - PROBLEMA CONFIRMADO")
        
    elif model.Status == GRB.INFEASIBLE:
        print("❌ MODELO INFACTIBLE")
        model.computeIIS()
        model.write("debug_infeasible.ilp")
        print("   • Archivo IIS guardado: debug_infeasible.ilp")
        
    else:
        print(f"❓ ESTADO DESCONOCIDO: {model.Status}")

if __name__ == "__main__":
    test_modelo_simple() 