import pandas as pd

def cargar_parametros():
    # Cargar zonas (Z)
    zonas_df = pd.read_csv("data/zonas.csv")
    Z = zonas_df["id_zona"].tolist()

    # Cargar tipos de delitos (D, IDD)
    delitos_df = pd.read_csv("data/tipos_delitos.csv")
    D = delitos_df["id_delito"].tolist()
    IDD = dict(zip(delitos_df["id_delito"], delitos_df["idd"]))

    # Cargar incidencias (I)
    incidencia_df = pd.read_csv("data/incidencia_delito.csv")
    I = {(row["id_delito"], row["id_zona"]): row["incidencia"] for _, row in incidencia_df.iterrows()}

    # Cargar carabineros
    carab_df = pd.read_csv("data/carabineros.csv")
    C = carab_df["id_carabinero"].tolist()
    q = dict(zip(carab_df["id_carabinero"], carab_df["experiencia"]))
    beta = {(row["id_carabinero"], row["id_estacion"]): 1 for _, row in carab_df.iterrows()}

    # Cargar vehículos/patrullas
    vehiculos_df = pd.read_csv("data/vehiculos.csv")
    P = vehiculos_df["id"].tolist()

    # Conjunto de estaciones (E) y tipos de vehículos (V)
    E = sorted(carab_df["id_estacion"].unique().tolist())
    V = [1, 2, 3, 4, 5, 6]
    T = list(range(365))  # Días
    M = [1, 2, 3]  # Turnos

    # Construir alpha: a qué estación pertenece cada patrulla
    alpha = {(row["id"], row["id_estacion"]): 1 for _, row in vehiculos_df.iterrows()}

    # Construir w[p, e, v]: si la patrulla p de estación e es del tipo de vehículo v
    w = {}
    for _, row in vehiculos_df.iterrows():
        p = row["id"]
        e = row["id_estacion"]
        v = row["tipo_medio"]
        w[(p, e, v)] = 1

    # Cargar costos de uso de vehículos
    costos_df = pd.read_csv("data/costos_diarios.csv")
    O = {}
    for _, row in costos_df.iterrows():
        t = row["Dia"]
        for v, col in zip([1, 2, 3, 4, 5, 6], 
                          ["Costo_uso_peaton", "Costo_uso_moto", "Costo_uso_bici", 
                           "Costo_uso_caballo", "Costo_uso_auto", "Costo_uso_furgon"]):
            for p in P:
                O[(p, v, t)] = row[col]

    # Presupuesto por estación (ficticio, puedes ajustar con archivo si tienes)
    P_e = {e: 1000 for e in E}

    # Compatibilidad vehículo-zona (puedes cargar desde CSV más adelante)
    r = {(v, z): 1 for v in V for z in Z}

    # Peligrosidad inicial
    zeta = {(z, t): 0.5 for z in Z for t in T}

    # Capacidad máxima por tipo de vehículo
    R_v = {
        1: 1,  # peatón
        2: 1,  # moto
        3: 1,  # bici
        4: 2,  # caballo
        5: 4,  # auto
        6: 7   # furgón
    }

    # Parámetros escalares
    gamma = 1.0
    lambda_ = 0.1
    N = {(0, 0): 1}  # Puedes eliminar si no se usa en el modelo

    return {
        "C": C, "P": P, "E": E, "V": V, "Z": Z, "T": T, "M": M, "D": D,
        "q": q, "I": I, "IDD": IDD, "O": O, "N": N, "P_e": P_e,
        "r": r, "w": w, "zeta": zeta, "beta": beta, "R_v": R_v,
        "alpha": alpha, "gamma": gamma, "lambda": lambda_
    }
