import pandas as pd

def cargar_parametros(modo_testing=True, horizonte="testing"):
    """
    Cargar parámetros del modelo
    
    Args:
        modo_testing: Si True, reduce drasticamente el tamaño
        horizonte: "testing" (7 días), "semanal" (7 días), "mensual" (30 días), "completo" (365 días)
    """
    # Cargar zonas (Z)
    zonas_df = pd.read_csv("data/zonas.csv")
    Z = zonas_df["id_zona"].tolist()
    
    if modo_testing:
        # MODO TESTING: Reducir drasticamente el tamaño
        Z = Z[:5]  # Solo 5 zonas
        print(f"🧪 MODO TESTING: Usando solo {len(Z)} zonas")

    # Cargar tipos de delitos (D, IDD)
    delitos_df = pd.read_csv("data/tipos_delitos.csv")
    D = delitos_df["id_delito"].tolist()
    IDD = dict(zip(delitos_df["id_delito"], delitos_df["idd"]))

    # Cargar incidencias (I)
    incidencia_df = pd.read_csv("data/incidencia_delito.csv")
    I = {(row["id_delito"], row["id_zona"]): row["incidencia"] 
         for _, row in incidencia_df.iterrows() 
         if row["id_zona"] in Z}  # Solo zonas seleccionadas

    # Cargar carabineros
    carab_df = pd.read_csv("data/carabineros.csv")
    C = carab_df["id_carabinero"].tolist()
    q = dict(zip(carab_df["id_carabinero"], carab_df["experiencia"]))
    beta = {(row["id_carabinero"], row["id_estacion"]): 1 for _, row in carab_df.iterrows()}
    
    if modo_testing:
        # MODO TESTING: Reducir carabineros
        C = C[:100]  # Solo 100 carabineros
        q = {c: q[c] for c in C}
        beta = {(c, e): v for (c, e), v in beta.items() if c in C}
        print(f"🧪 MODO TESTING: Usando solo {len(C)} carabineros")

    # Cargar vehículos/patrullas
    vehiculos_df = pd.read_csv("data/vehiculos.csv")
    P = vehiculos_df["id"].tolist()
    
    if modo_testing:
        # MODO TESTING: Reducir vehículos
        P = P[:50]  # Solo 50 vehículos
        vehiculos_df = vehiculos_df[vehiculos_df["id"].isin(P)]
        print(f"🧪 MODO TESTING: Usando solo {len(P)} vehículos")

    # Conjunto de estaciones (E) y tipos de vehículos (V)
    E = sorted(carab_df["id_estacion"].unique().tolist())
    V = [1, 2, 3, 4, 5, 6]
    
    # Configurar horizonte temporal
    if horizonte == "testing":
        T = list(range(1, 8))  # 7 días
        print(f"📅 HORIZONTE TESTING: {len(T)} días")
    elif horizonte == "semanal":
        T = list(range(1, 8))  # 7 días
        print(f"📅 HORIZONTE SEMANAL: {len(T)} días")
    elif horizonte == "mensual":
        T = list(range(1, 31))  # 30 días
        print(f"📅 HORIZONTE MENSUAL: {len(T)} días")
    elif horizonte == "completo":
        T = list(range(1, 366))  # 365 días
        print(f"📅 HORIZONTE COMPLETO: {len(T)} días (⚠️ PUEDE TARDAR MUCHO)")
    else:
        T = list(range(1, 8))  # Default: 7 días
        print(f"📅 HORIZONTE DEFAULT: {len(T)} días")
        
    M = [1, 2, 3]  # Turnos

    # Construir alpha: parámetro binario que indica si el vehículo p pertenece a la estación e
    alpha = {(row["id"], row["id_estacion"]): 1 
             for _, row in vehiculos_df.iterrows() 
             if row["id"] in P}

    # Construir w[p,v]: parámetro binario que indica si el vehículo p es de tipo v
    w = {}
    for _, row in vehiculos_df.iterrows():
        if row["id"] in P:
            p = row["id"]
            v = row["tipo_medio"]
            w[(p, v)] = 1

    # Cargar costos de uso de vehículos O[v,t]
    costos_df = pd.read_csv("data/costos_diarios.csv")
    O = {}
    for _, row in costos_df.iterrows():
        t = row["Dia"]
        if t in T:  # Solo días seleccionados
            costos_por_tipo = {
                1: row["Costo_uso_peaton"],
                2: row["Costo_uso_moto"], 
                3: row["Costo_uso_bici"],
                4: row["Costo_uso_caballo"], 
                5: row["Costo_uso_auto"], 
                6: row["Costo_uso_furgon"]
            }
            for v in V:
                O[(v, t)] = costos_por_tipo[v]

    # Cargar presupuesto por estación desde comisarias.csv
    comisarias_df = pd.read_csv("data/comisarias.csv")
    # Mapear IDs de comisaria (1-66) a IDs de estación (0-65)
    P_e = {}
    for _, row in comisarias_df.iterrows():
        estacion_id = row["id_comisaria"] - 1  # Convertir de 1-66 a 0-65
        if modo_testing:
            # En modo testing, aumentar presupuesto para evitar infactibilidad
            P_e[estacion_id] = row["presupuesto_anual"] * 10
        else:
            P_e[estacion_id] = row["presupuesto_anual"]

    # Compatibilidad vehículo-zona r[v,z]
    r = {}
    vehiculo_cols = {
        2: "compatible_moto",
        3: "compatible_bici",
        4: "compatible_caballo",
        5: "compatible_auto",
        6: "compatible_furgon"
    }
    for _, row in zonas_df.iterrows():
        z = row["id_zona"]
        if z in Z:  # Solo zonas seleccionadas
            for v in V:
                if v == 1:
                    r[(v, z)] = 1  # peatón compatible en todas las zonas
                else:
                    r[(v, z)] = row[vehiculo_cols[v]]

    # Calcular Gamma según la documentación: máximo de peligrosidad teórica entre todas las zonas
    Gamma = 0
    for z in Z:
        peligrosidad_zona = sum(I.get((d, z), 0) * IDD[d] for d in D)
        if peligrosidad_zona > Gamma:
            Gamma = peligrosidad_zona
    
    # Evitar división por cero
    if Gamma == 0:
        Gamma = 1.0

    # Peligrosidad inicial zeta[z,1] para cada zona
    zeta = {}
    for z in Z:
        zeta[z] = 0.5  # Valor inicial según documentación

    # Capacidad máxima por tipo de vehículo R_v
    R_v = {
        1: 1,  # peatón
        2: 1,  # moto
        3: 1,  # bici
        4: 2,  # caballo
        5: 4,  # auto
        6: 7   # furgón
    }

    # Parámetros escalares según documentación
    lambda_ = 0.1  # Sensibilidad del aumento de peligrosidad (entre 0 y 1)
    
    if modo_testing:
        kappa = 0.5    # Reducir requerimiento de patrullas en testing
    else:
        kappa = 1.0    # Parámetro que traduce peligrosidad en número de patrullas requeridas
        
    M_big = 1000   # Número muy grande para restricciones de activación

    return {
        "C": C, "P": P, "E": E, "V": V, "Z": Z, "T": T, "M": M, "D": D,
        "q": q, "I": I, "IDD": IDD, "O": O, "P_e": P_e,
        "r": r, "w": w, "zeta": zeta, "beta": beta, "R_v": R_v,
        "alpha": alpha, "Gamma": Gamma, "lambda": lambda_, "kappa": kappa, "M_big": M_big
    }
