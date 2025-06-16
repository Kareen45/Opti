from gurobipy import Model, GRB, quicksum

def construir_modelo(parametros):
    print("🔧 Iniciando construcción del modelo...")
    
    # Desempaquetar parámetros y conjuntos
    C, P, E, V, Z, T, M, D = parametros["C"], parametros["P"], parametros["E"], parametros["V"], parametros["Z"], parametros["T"], parametros["M"], parametros["D"]
    q, I, IDD = parametros["q"], parametros["I"], parametros["IDD"]
    O, P_e = parametros["O"], parametros["P_e"]
    r, w, zeta_init, beta, R_v = parametros["r"], parametros["w"], parametros["zeta"], parametros["beta"], parametros["R_v"]
    alpha = parametros["alpha"]
    Gamma = parametros["Gamma"]
    lambda_ = parametros["lambda"]
    kappa = parametros["kappa"]
    M_big = parametros["M_big"]

    print(f"📊 Tamaños de conjuntos: C={len(C)}, P={len(P)}, E={len(E)}, Z={len(Z)}, T={len(T)}")
    print(f"📊 Variables estimadas: {len(P)*len(Z)*len(M)*len(T) + len(C)*len(P)*len(M)*len(T)} aprox.")

    model = Model("Patrullaje Preventivo")
    # logs
    model.setParam("OutputFlag", 1)         
    model.setParam("LogToConsole", 1)       # Asegura que imprime en consola
    model.setParam("DisplayInterval", 10)   # Muestra progreso cada 10s

    model.setParam("TimeLimit", 1800)  # 30 min máximo según requisitos del proyecto
    
    # Configuraciones para reducir uso de memoria
    model.setParam("NodefileStart", 0.5)  # Usar disco cuando memoria > 0.5 GB
    model.setParam("MemLimit", 8)  # Límite de memoria en GB
    model.setParam("Presolve", 2)  # Presolve agresivo para reducir variables

    print("✅ Creando variables de decisión...")
    # Variables de decisión según documentación
    x = model.addVars(P, Z, M, T, vtype=GRB.BINARY, name="x")
    print(f"   ✓ Variable x: {len(P)*len(Z)*len(M)*len(T)} variables binarias")
    
    y = model.addVars(C, P, M, T, vtype=GRB.BINARY, name="y")
    print(f"   ✓ Variable y: {len(C)*len(P)*len(M)*len(T)} variables binarias")
    
    phi = model.addVars(P, T, vtype=GRB.BINARY, name="phi")
    print(f"   ✓ Variable phi: {len(P)*len(T)} variables binarias")
    
    u = model.addVars(Z, M, T, lb=0.0, vtype=GRB.CONTINUOUS, name="u")
    print(f"   ✓ Variable u: {len(Z)*len(M)*len(T)} variables continuas")
    
    zeta = model.addVars(Z, T, lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name="zeta")
    print(f"   ✓ Variable zeta: {len(Z)*len(T)} variables continuas")

    # Establecer valores iniciales de peligrosidad
    print("✅ Estableciendo valores iniciales...")
    for z in Z:
        zeta[z, 1].start = zeta_init.get(z, 0.5)

    # Función objetivo: minimizar suma de peligrosidad
    print("✅ Definiendo función objetivo...")
    model.setObjective(
        quicksum(zeta[z, t] for z in Z for t in T),
        GRB.MINIMIZE
    )

    print("✅ Agregando restricciones...")
    
    # R1: Asignación diaria única de carabinero
    print("   🔄 R1: Asignación diaria única...")
    model.addConstrs(
        (quicksum(y[c, p, m, t] for p in P for m in M) <= 1
         for c in C for t in T),
        name="R1_asignacion_diaria_unica"
    )

    # R2: Compatibilidad de estaciones para carabinero y vehículo
    print("   🔄 R2: Compatibilidad estaciones...")
    model.addConstrs(
        (y[c, p, m, t] <= quicksum(beta.get((c, e), 0) * alpha.get((p, e), 0) for e in E)
         for c in C for p in P for m in M for t in T),
        name="R2_compatibilidad_estacion"
    )

    # R3: Experiencia mínima por patrulla
    print("   🔄 R3: Experiencia mínima...")
    model.addConstrs(
        (4 * quicksum(x[p, z, m, t] for z in Z) <= quicksum(y[c, p, m, t] * q[c] for c in C)
         for p in P for m in M for t in T),
        name="R3_experiencia_minima"
    )

    # R4: Asignación única de patrulla por turno
    print("   🔄 R4: Asignación única patrulla...")
    model.addConstrs(
        (quicksum(x[p, z, m, t] for z in Z) <= 1
         for p in P for m in M for t in T),
        name="R4_asignacion_unica_patrulla"
    )

    # R5: Compatibilidad de tipo de vehículo con zona
    print("   🔄 R5: Compatibilidad vehículo-zona...")
    model.addConstrs(
        (x[p, z, m, t] <= quicksum(w.get((p, v), 0) * r.get((v, z), 0) for v in V)
         for p in P for z in Z for m in M for t in T),
        name="R5_compatibilidad_vehiculo_zona"
    )

    # R6: Asignación carabineros a patrullas activas por turno
    print("   🔄 R6: Carabineros a patrullas activas...")
    model.addConstrs(
        (y[c, p, m, t] <= quicksum(x[p, z, m, t] for z in Z)
         for c in C for p in P for m in M for t in T),
        name="R6_carabineros_patrullas_activas"
    )

    # R7: Límite de carabineros por patrullas I
    print("   🔄 R7: Límite carabineros I...")
    model.addConstrs(
        (quicksum(x[p, z, m, t] for z in Z) <= quicksum(y[c, p, m, t] for c in C)
         for p in P for m in M for t in T),
        name="R7_limite_carabineros_I"
    )

    # R8: Límite de carabineros por patrulla II
    print("   🔄 R8: Límite carabineros II...")
    model.addConstrs(
        (quicksum(y[c, p, m, t] for c in C) <= 
         quicksum(R_v[v] * w.get((p, v), 0) * quicksum(x[p, z, m, t] for z in Z) for v in V)
         for p in P for m in M for t in T),
        name="R8_limite_carabineros_II"
    )

    # R9: Activación diaria de vehículo I
    print("   🔄 R9: Activación vehículo I...")
    model.addConstrs(
        (quicksum(x[p, z, m, t] for m in M for z in Z) <= M_big * phi[p, t]
         for p in P for t in T),
        name="R9_activacion_vehiculo_I"
    )

    # R10: Activación diaria de vehículo II
    print("   🔄 R10: Activación vehículo II...")
    model.addConstrs(
        (phi[p, t] <= quicksum(y[c, p, m, t] for c in C for m in M)
         for p in P for t in T),
        name="R10_activacion_vehiculo_II"
    )

    # R11: Límite presupuestario por estación
    print("   🔄 R11: Límite presupuestario...")
    model.addConstrs(
        (quicksum(phi[p, t] * quicksum(w.get((p, v), 0) * O.get((v, t), 0) for v in V) * alpha.get((p, e), 0)
                  for p in P for t in T) <= P_e[e]
         for e in E),
        name="R11_limite_presupuestario"
    )

    # R12: Cobertura mínima DIARIA OBLIGATORIA - TODOS LOS DÍAS
    print("   🔄 R12: Cobertura mínima...")
    
    # CAMBIO CLAVE: Requerir patrullaje mínimo CADA DÍA independientemente de peligrosidad
    # Esto asegura que el modelo genere un plan mensual real
    model.addConstrs(
        (quicksum(x[p, z, m, t] for p in P for m in M) >= kappa
         for z in Z for t in T),
        name="R12_patrullaje_diario_obligatorio"
    )

    # R13: Actualización de peligrosidad CON CRIMINALIDAD BASE DIARIA
    print("   🔄 R13: Actualización peligrosidad...")
    
    # Para el primer día, usar peligrosidad inicial
    for z in Z:
        peligrosidad_base = quicksum(I.get((d, z), 0) * IDD[d] for d in D)
        cobertura_total = quicksum(x[p, z, m, 1] for p in P for m in M)
        model.addConstr(
            zeta[z, 1] == zeta_init[z] + lambda_ * peligrosidad_base - Gamma * cobertura_total/10,
            name=f"R13_inicial_{z}"
        )
    
    # Para días posteriores: criminalidad base diaria + evolución de peligrosidad
    for z in Z:
        for t in T:
            if t > 1:
                # CRIMINALIDAD BASE: Cada día aparece 20% de la criminalidad inicial
                criminalidad_diaria = 0.2 * quicksum(I.get((d, z), 0) * IDD[d] for d in D)
                cobertura_total = quicksum(x[p, z, m, t] for p in P for m in M)
                
                model.addConstr(
                    zeta[z, t] == zeta[z, t-1] + criminalidad_diaria + lambda_ * quicksum(u[z, m, t-1] for m in M) - Gamma * cobertura_total/10,
                    name=f"R13_dinamica_{z}_{t}"
                )
    
    # Restricción adicional: Déficit siempre positivo (nunca perfectamente 0)
    model.addConstrs(
        (u[z, m, t] >= 0.01 * zeta_init[z] - quicksum(x[p, z, m, t] for p in P)
         for z in Z for m in M for t in T),
        name="R14_deficit_minimo"
    )

    print("✅ Modelo construido exitosamente!")
    print(f"📊 Total variables: {model.NumVars}")
    print(f"📊 Total restricciones: {model.NumConstrs}")
    return model

def resolver_modelo(model):
    """Resuelve el modelo y retorna información de la solución"""
    print("🚀 Llamando a model.optimize()...")
    model.optimize()
    
    if model.status == GRB.OPTIMAL:
        print(f"Solución óptima encontrada!")
        print(f"Valor objetivo: {model.ObjVal:.2f}")
        print(f"Tiempo de ejecución: {model.Runtime:.2f} segundos")
        print(f"Variables: {model.NumVars}, Restricciones: {model.NumConstrs}")
        return True
    elif model.status == GRB.TIME_LIMIT:
        print(f"Tiempo límite alcanzado. Mejor solución: {model.ObjVal:.2f}")
        return False
    else:
        print(f"No se encontró solución óptima. Status: {model.status}")
        return False