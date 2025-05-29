from gurobipy import Model, GRB, quicksum

def construir_modelo(parametros):
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

    model = Model("Patrullaje Preventivo")
    model.setParam("OutputFlag", 1)
    model.setParam("TimeLimit", 3600)  # 1 hora máximo

    # Variables de decisión según documentación
    x = model.addVars(P, Z, M, T, vtype=GRB.BINARY, name="x")
    y = model.addVars(C, P, M, T, vtype=GRB.BINARY, name="y")
    phi = model.addVars(P, T, vtype=GRB.BINARY, name="phi")
    u = model.addVars(Z, M, T, lb=0.0, vtype=GRB.CONTINUOUS, name="u")
    zeta = model.addVars(Z, T, lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name="zeta")

    # Establecer valores iniciales de peligrosidad
    for z in Z:
        zeta[z, 1].start = zeta_init.get(z, 0.5)

    # Función objetivo: minimizar suma de peligrosidad
    model.setObjective(
        quicksum(zeta[z, t] for z in Z for t in T),
        GRB.MINIMIZE
    )

    # R1: Asignación diaria única de carabinero
    model.addConstrs(
        (quicksum(y[c, p, m, t] for p in P for m in M) <= 1
         for c in C for t in T),
        name="R1_asignacion_diaria_unica"
    )

    # R2: Compatibilidad de estaciones para carabinero y vehículo
    model.addConstrs(
        (y[c, p, m, t] <= quicksum(beta.get((c, e), 0) * alpha.get((p, e), 0) for e in E)
         for c in C for p in P for m in M for t in T),
        name="R2_compatibilidad_estacion"
    )

    # R3: Experiencia mínima por patrulla
    model.addConstrs(
        (4 * quicksum(x[p, z, m, t] for z in Z) <= quicksum(y[c, p, m, t] * q[c] for c in C)
         for p in P for m in M for t in T),
        name="R3_experiencia_minima"
    )

    # R4: Asignación única de patrulla por turno
    model.addConstrs(
        (quicksum(x[p, z, m, t] for z in Z) <= 1
         for p in P for m in M for t in T),
        name="R4_asignacion_unica_patrulla"
    )

    # R5: Compatibilidad de tipo de vehículo con zona
    model.addConstrs(
        (x[p, z, m, t] <= quicksum(w.get((p, v), 0) * r.get((v, z), 0) for v in V)
         for p in P for z in Z for m in M for t in T),
        name="R5_compatibilidad_vehiculo_zona"
    )

    # R6: Asignación carabineros a patrullas activas por turno
    model.addConstrs(
        (y[c, p, m, t] <= quicksum(x[p, z, m, t] for z in Z)
         for c in C for p in P for m in M for t in T),
        name="R6_carabineros_patrullas_activas"
    )

    # R7: Límite de carabineros por patrullas I
    model.addConstrs(
        (quicksum(x[p, z, m, t] for z in Z) <= quicksum(y[c, p, m, t] for c in C)
         for p in P for m in M for t in T),
        name="R7_limite_carabineros_I"
    )

    # R8: Límite de carabineros por patrulla II
    model.addConstrs(
        (quicksum(y[c, p, m, t] for c in C) <= 
         quicksum(R_v[v] * w.get((p, v), 0) * quicksum(x[p, z, m, t] for z in Z) for v in V)
         for p in P for m in M for t in T),
        name="R8_limite_carabineros_II"
    )

    # R9: Activación diaria de vehículo I
    model.addConstrs(
        (quicksum(x[p, z, m, t] for m in M for z in Z) <= M_big * phi[p, t]
         for p in P for t in T),
        name="R9_activacion_vehiculo_I"
    )

    # R10: Activación diaria de vehículo II
    model.addConstrs(
        (phi[p, t] <= quicksum(y[c, p, m, t] for c in C for m in M)
         for p in P for t in T),
        name="R10_activacion_vehiculo_II"
    )

    # R11: Límite presupuestario por estación
    model.addConstrs(
        (quicksum(phi[p, t] * quicksum(w.get((p, v), 0) * O.get((v, t), 0) for v in V) * alpha.get((p, e), 0)
                  for p in P for t in T) <= P_e[e]
         for e in E),
        name="R11_limite_presupuestario"
    )

    # R12: Cobertura mínima con penalización por déficit
    model.addConstrs(
        (quicksum(x[p, z, m, t] for p in P) + u[z, m, t] >= kappa * zeta[z, t-1]
         for z in Z for m in M for t in T if t > 1),
        name="R12_cobertura_minima_deficit"
    )

    # R13: Actualización de peligrosidad por déficit
    model.addConstrs(
        (zeta[z, t+1] == zeta[z, t] + lambda_ * quicksum(u[z, m, t] for m in M) * 
         (quicksum(I.get((d, z), 0) * IDD[d] for d in D) / Gamma)
         for z in Z for t in T if t < max(T)),
        name="R13_actualizacion_peligrosidad"
    )

    return model

def resolver_modelo(model):
    """Resuelve el modelo y retorna información de la solución"""
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