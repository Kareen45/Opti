import pandas as pd

def cargar_parametros(modo_testing=True, horizonte="mensual"):
    """
    Cargar parámetros del modelo
    
    Args:
        modo_testing: Si True, reduce drasticamente el tamaño
        horizonte: "testing" (7 días), "semanal" (7 días), "mensual" (30 días), "completo" (365 días)
    """
    # Cargar zonas (Z)
    zonas_df = pd.read_csv("data/zonas.csv")
    Z = zonas_df["id_zona"].tolist()
    
    if modo_testing == True or modo_testing == "diez_zonas" or modo_testing == "cinco_zonas":
        # MODO TESTING/5 ZONAS/10 ZONAS: Usar zonas representativas por peligrosidad
        if modo_testing == True:
            Z = Z[:1]  # Solo 1 zona para testing
            print(f"🧪 MODO TESTING: Usando solo {len(Z)} zona(s)")
        elif modo_testing == "cinco_zonas":
            # Top 5 más peligrosas: Santiago, Maipú, La Florida, Providencia, Estación Central
            Z = [30, 17, 8, 21, 4]
            print(f"📊 MODO 5 ZONAS: Usando {len(Z)} zonas más peligrosas: Santiago, Maipú, La Florida, Providencia, Estación Central")
        else:  # diez_zonas
            # 10 comunas balanceadas: 3 alta + 4 media + 3 baja peligrosidad
            Z = [30, 17, 8, 23, 24, 28, 26, 31, 0, 15]
            print(f"📊 MODO 10 ZONAS: Usando {len(Z)} zonas balanceadas (alta/media/baja peligrosidad)")

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
    
    if modo_testing == True or modo_testing == "diez_zonas" or modo_testing == "cinco_zonas":
        # MODO TESTING/5 ZONAS/10 ZONAS: Reducir carabineros
        if modo_testing == True:
            C = C[:100]  # Solo 100 carabineros para testing
            print(f"🧪 MODO TESTING: Usando solo {len(C)} carabineros")
        elif modo_testing == "cinco_zonas":
            C = C[:200]  # Carabineros para 5 zonas
            print(f"📊 MODO 5 ZONAS: Usando {len(C)} carabineros")
        else:  # diez_zonas
            C = C[:300]  # Más carabineros para 10 zonas
            print(f"📊 MODO 10 ZONAS: Usando {len(C)} carabineros")
        q = {c: q[c] for c in C}
        beta = {(c, e): v for (c, e), v in beta.items() if c in C}

    # Cargar vehículos/patrullas
    vehiculos_df = pd.read_csv("data/vehiculos.csv")
    P = vehiculos_df["id"].tolist()
    
    if modo_testing == True or modo_testing == "diez_zonas" or modo_testing == "cinco_zonas":
        # MODO TESTING/5 ZONAS/10 ZONAS: Reducir vehículos
        if modo_testing == True:
            P = P[:50]  # Solo 50 vehículos para testing
            print(f"🧪 MODO TESTING: Usando solo {len(P)} vehículos")
        elif modo_testing == "cinco_zonas":
            P = P[:120]  # Vehículos para 5 zonas
            print(f"📊 MODO 5 ZONAS: Usando {len(P)} vehículos")
        else:  # diez_zonas
            P = P[:200]  # Más vehículos para 10 zonas
            print(f"📊 MODO 10 ZONAS: Usando {len(P)} vehículos")
        vehiculos_df = vehiculos_df[vehiculos_df["id"].isin(P)]

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
        if modo_testing == True or modo_testing == "diez_zonas" or modo_testing == "cinco_zonas":
            # En modo testing/5 zonas/10 zonas, aumentar presupuesto para evitar infactibilidad
            if modo_testing == True:
                multiplicador = 10
            elif modo_testing == "cinco_zonas":
                multiplicador = 7
            else:  # diez_zonas
                multiplicador = 5
            P_e[estacion_id] = row["presupuesto_anual"] * multiplicador
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

    # Peligrosidad inicial zeta[z,1] para cada zona SIN normalizar por Gamma
    # Esto hace que zonas más peligrosas requieran proporcionalmente más patrullas
    zeta = {}
    for z in Z:
        total = 0
        for d in D:
            incidencia = I.get((d, z), 0)   # Puede ser 0 si no hay datos para (d,z)
            daño = IDD.get(d, 0)            # Índice de daño del delito
            total += incidencia * daño
        # NO normalizar por Gamma - usar valor absoluto para reflejar peligrosidad real
        zeta[z] = max(total, 0.05)  # Mínimo 0.05 para evitar zonas con 0 peligrosidad

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
    lambda_ = 0.6  # Mayor sensibilidad al aumento de peligrosidad para modelo dinámico
    
    if modo_testing == True or modo_testing == "diez_zonas" or modo_testing == "cinco_zonas":
        # Reducir kappa para hacer el modelo más dinámico
        if modo_testing == True:
            kappa = 8.0   # Reducido para requerir más optimización diaria
        elif modo_testing == "cinco_zonas":
            kappa = 5.0   # Mucho más restrictivo para 5 zonas
        else:  # diez_zonas
            kappa = 15.0  # Para 10 zonas
    else:
        kappa = 30.0    # Muchas patrullas para modelo completo
        
    M_big = 1000   # Número muy grande para restricciones de activación

    return {
        "C": C, "P": P, "E": E, "V": V, "Z": Z, "T": T, "M": M, "D": D,
        "q": q, "I": I, "IDD": IDD, "O": O, "P_e": P_e,
        "r": r, "w": w, "zeta": zeta, "beta": beta, "R_v": R_v,
        "alpha": alpha, "Gamma": Gamma, "lambda": lambda_, "kappa": kappa, "M_big": M_big
    }
