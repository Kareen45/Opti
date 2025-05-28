# Conjuntos reducidos
C = [0, 1]         # carabineros
P = [0]            # patrullas
E = [0]            # estaciones
V = ["peaton"]     # tipo de patrullas
Z = [0]            # zonas
T = [0]            # días
M = [0]            # turnos
D = [0]            # tipos de delitos

# Parámetros
q = {0: 2, 1: 2}  # experiencia
I = {(0, 0): 0.5}  # incidencia delito
IDD = {0: 4}       # daño del delito

O = {(0, "peaton", 0): 100}
N = {(0, "peaton"): 1}
C_e = {0: 2}
P_e = {0: 1000}
r = {("peaton", 0): 1}
w = {(0, 0, "peaton"): 1}
zeta = {0: 1}
beta = {(0, 0): 1, (1, 0): 1}
R_v = {"peaton": 2}

parametros_ejemplo = {
    "C": C, "P": P, "E": E, "V": V, "Z": Z, "T": T, "M": M, "D": D,
    "q": q, "I": I, "IDD": IDD, "O": O, "N": N, "C_e": C_e, "P_e": P_e,
    "r": r, "w": w, "zeta": zeta, "beta": beta, "R_v": R_v
}

# Aquí se van a cargar luego los datos para convertirlos en diccionarios y agregarlos al modelo
