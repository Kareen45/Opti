from gurobipy import Model, GRB, quicksum

def construir_modelo(parametros):
    # Desempaquetar parámetros y conjuntos
    C, P, E, V, Z, T, M, D = parametros["C"], parametros["P"], parametros["E"], parametros["V"], parametros["Z"], parametros["T"], parametros["M"], parametros["D"]
    q, I, IDD = parametros["q"], parametros["I"], parametros["IDD"]
    O, N, C_e, P_e = parametros["O"], parametros["N"], parametros["C_e"], parametros["P_e"]
    r, w, zeta, beta, R_v = parametros["r"], parametros["w"], parametros["zeta"], parametros["beta"], parametros["R_v"]

    model = Model("Patrullaje Preventivo")
    model.setParam("OutputFlag", 1)

    # Variables de decisión
    x = model.addVars(P, V, Z, M, T, vtype=GRB.BINARY, name="x")
    y = model.addVars(C, P, M, T, vtype=GRB.BINARY, name="y")
    phi = model.addVars(P, V, T, vtype=GRB.BINARY, name="phi")

    # Función objetivo
    model.setObjective(
        quicksum(x[p, v, z, m, t] * sum(I[d, z] * IDD[d] for d in D)
                 for p in P for v in V for z in Z for m in M for t in T),
        GRB.MAXIMIZE
    )

    # R1: Un turno máximo diario por carabinero
    model.addConstrs(
        (quicksum(y[c, p, m, t] for p in P for m in M) <= 1
         for c in C for t in T),
        name="R1_turno_max"
    )

    # R2: Carabineros disponibles por estación
    model.addConstrs(
        (quicksum(beta[c, e] * y[c, p, m, t] for c in C for p in P) <= C_e[e]
         for e in E for m in M for t in T),
        name="R2_lim_carabineros_estacion"
    )

    # R3: Solo carabineros de su estación
    model.addConstrs(
        (y[c, p, m, t] <= quicksum(beta[c, e] * w.get((p, e, v), 0) for e in E for v in V)
         for c in C for p in P for m in M for t in T),
        name="R3_zona_carabinero"
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

    # R7: Asignación mínima por peligrosidad
    model.addConstrs(
        (quicksum(x[p, v, z, m, t] for p in P for v in V) >= 4 * zeta[z] + (1 + zeta[z])
         for z in Z for m in M for t in T),
        name="R7_min_peligrosidad"
    )

    # R8: Límite patrullas disponibles
    model.addConstrs(
        (quicksum(w.get((p, e, v), 0) * x[p, v, z, m, t] for p in P for z in Z) <= N.get((e, v), 0)
         for e in E for v in V for m in M for t in T),
        name="R8_patru_disponibles"
    )

    # R9: Asignación única de patrulla por turno
    model.addConstrs(
        (quicksum(x[p, v, z, m, t] for z in Z) <= 1
         for p in P for v in V for m in M for t in T),
        name="R9_una_zona_por_turno"
    )

    # R10: Activación de phi
    model.addConstrs(
        (quicksum(x[p, v, z, m, t] for z in Z for m in M) <= phi[p, v, t]
         for p in P for v in V for t in T),
        name="R10_phi_activado"
    )

    model.addConstrs(
        (phi[p, v, t] <= quicksum(x[p, v, z, m, t] for z in Z for m in M)
         for p in P for v in V for t in T),
        name="R10_phi_vinculo"
    )

    # R11: Presupuesto por estación
    model.addConstrs(
        (quicksum(phi[p, v, t] * O[p, v, t] * w.get((p, e, v), 0)
                  for p in P for v in V for t in T) <= P_e[e]
         for e in E),
        name="R11_presupuesto"
    )

    # R12: Compatibilidad patrulla-zona
    model.addConstrs(
        (x[p, v, z, m, t] <= r[v, z]
         for p in P for v in V for z in Z for m in M for t in T),
        name="R12_compatibilidad"
    )

    return model
