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

    # Conjuntos 
    C = [0, 1]  # carabineros
    P = [0]
    E = list(range(66)) # 66 estaciones/comisarías numeradas del 0 al 65
    V = [1, 2, 3, 4, 5, 6]  # Tipo de vehículo:  1:peaton, 2:moto, 3:bici, 4:caballo, 5:auto, 6:furgón
    T = [0, 1]         # días
    M = [0]            # turnos

    # Parámetros
    q = {0: 2, 1: 2}
    gamma = 1.0
    lambda_ = 0.1
    O = {(0, 0, 0): 100}
    N = {(0, 0): 1}
    C_e = {0: 2}
    P_e = {0: 1000}
    r = {(0, z): 1 for z in Z}
    w = {(0, 0, 0): 1}
    alpha = {(0, 0): 1}
    beta = {(0, 0): 1, (1, 0): 1}
    R_v = {0: 2}
    zeta = {(z, t): 0.5 for z in Z for t in T}

    return {
        "C": C, "P": P, "E": E, "V": V, "Z": Z, "T": T, "M": M, "D": D,
        "q": q, "I": I, "IDD": IDD, "O": O, "N": N, "C_e": C_e, "P_e": P_e,
        "r": r, "w": w, "zeta": zeta, "beta": beta, "R_v": R_v,
        "alpha": alpha, "gamma": gamma, "lambda": lambda_
    }
