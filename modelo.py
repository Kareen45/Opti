from gurobipy import Model, GRB, quicksum

def construir_modelo(parametros):
    # Desempaquetar parámetros y conjuntos
    C, P, E, V, Z, T, M, D = parametros["C"], parametros["P"], parametros["E"], parametros["V"], parametros["Z"], parametros["T"], parametros["M"], parametros["D"]
    q, I, IDD = parametros["q"], parametros["I"], parametros["IDD"]
    O, N, P_e = parametros["O"], parametros["N"], parametros["P_e"]
    r, w, zeta_init, beta, R_v = parametros["r"], parametros["w"], parametros["zeta"], parametros["beta"], parametros["R_v"]
    alpha = parametros["alpha"]
    Gamma = parametros["gamma"]
    lambda_ = parametros["lambda"]

    model = Model("Patrullaje Preventivo")
    model.setParam("OutputFlag", 1)

    # Variables de decisión
    x = model.addVars(P, V, Z, M, T, vtype=GRB.BINARY, name="x")
    y = model.addVars(C, P, M, T, vtype=GRB.BINARY, name="y")
    phi = model.addVars(P, V, T, vtype=GRB.BINARY, name="phi")
    u = model.addVars(Z, M, T, lb=0.0, vtype=GRB.CONTINUOUS, name="u")
    zeta = model.addVars(Z, T, lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name="zeta")

    # Set valores iniciales para peligrosidad
    for z in Z:
        for t in T:
            zeta[z, t].start = zeta_init.get((z, t), 0.5)

    # Función objetivo: maximizar cobertura ponderada por daño del delito
    model.setObjective(
        quicksum(x[p, v, z, m, t] * sum(I.get((d, z), 0) * IDD[d] for d in D)
                for p in P for v in V for z in Z for m in M for t in T),
        GRB.MAXIMIZE
    )


    # R1: Un turno máximo diario por carabinero
    model.addConstrs(
        (quicksum(y[c, p, m, t] for p in P for m in M) <= 1
         for c in C for t in T),
        name="R1_turno_max"
    )

    # R2: Asignación única por turno para carabinero
    model.addConstrs(
        (quicksum(y[c, p, m, t] for p in P) <= 1
        for c in C for m in M for t in T),
        name="R2_asignacion_unica"
    )

    # R3: Solo carabineros de su estación
    model.addConstrs(
    (
        y[c, p, m, t] <= sum(beta.get((c, e), 0) * alpha.get((p, e), 0) for e in E)
        for c in C for p in P for m in M for t in T
    ),
    name="R3_compatibilidad_estacion"
    )   

    # R4: Límite mínimo de carabineros por patrulla
    model.addConstrs(
        (quicksum(x[p, v, z, m, t] for z in Z) <= quicksum(y[c, p, m, t] for c in C)
         for p in P for v in V for m in M for t in T),
        name="R4_min_carabineros"
    )

    # R5: Límite máximo de carabineros por patrulla
    model.addConstrs(
        (quicksum(y[c, p, m, t] for c in C) <= R_v[v] * quicksum(x[p, v, z, m, t] for z in Z)
         for p in P for v in V for m in M for t in T),
        name="R5_max_carabineros"
    )

    # R6: Experiencia mínima por patrulla
    model.addConstrs(
        (4 * quicksum(x[p, v, z, m, t] for z in Z) <= quicksum(y[c, p, m, t] * q[c] for c in C)
         for p in P for v in V for m in M for t in T),
        name="R6_experiencia"
    )

    # R7: Cobertura mínima por zona (permite déficit u)
    model.addConstrs(
        (quicksum(x[p, v, z, m, t] for p in P for v in V) + u[z, m, t] >= 1
         for z in Z for m in M for t in T),
        name="R7_cobertura_min"
    )

    # R8: Actualización de peligrosidad
    model.addConstrs(
        (zeta[z, t+1] >= zeta[z, t] + lambda_ * u[z, m, t] * 
        (sum(I.get((d, z), 0) * IDD[d] for d in D) / Gamma)
        for z in Z for t in range(len(T)-1) for m in M),
        name="R8_peligrosidad"
    )

    # R9: Compatibilidad patrulla-zona
    model.addConstrs(
        (x[p, v, z, m, t] <= r.get((v, z), 0)
         for p in P for v in V for z in Z for m in M for t in T),
        name="R9_compatibilidad"
    )

    # R10: Asignación única por patrulla en cada turno
    model.addConstrs(
        (quicksum(x[p, v, z, m, t] for z in Z) <= 1
         for p in P for v in V for m in M for t in T),
        name="R10_asignacion_unica"
    )

    # R11: Activación de vehículo si es usado
    model.addConstrs(
        (quicksum(x[p, v, z, m, t] for z in Z for m in M) <= phi[p, v, t]
         for p in P for v in V for t in T),
        name="R11_phi_activado"
    )
    model.addConstrs(
        (phi[p, v, t] <= quicksum(x[p, v, z, m, t] for z in Z for m in M)
         for p in P for v in V for t in T),
        name="R11_phi_vinculo"
    )

    # R12: Límite presupuestario por estación
    model.addConstrs(
        (quicksum(phi[p, v, t] * O.get((p, v, t), 0) * w.get((p, e, v), 0)
                  for p in P for v in V for t in T) <= P_e[e]
         for e in E),
        name="R12_presupuesto"
    )

    return model