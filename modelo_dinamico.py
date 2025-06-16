"""
Modelo de optimización con criminalidad dinámica
Este modelo añade nuevo crimen cada día para mayor realismo
"""

import gurobipy as gp
from gurobipy import GRB

def construir_modelo_dinamico(params):
    """
    Construye el modelo con criminalidad dinámica
    """
    
    # Extraer parámetros
    C = params["C"]
    P = params["P"] 
    E = params["E"]
    V = params["V"]
    Z = params["Z"]
    T = params["T"]
    M = params["M"]
    
    # Crear modelo
    model = gp.Model("patrullaje_dinamico")
    
    # Variables de decisión (igual que antes)
    x = model.addVars(P, Z, M, T, vtype=GRB.BINARY, name="x")
    y = model.addVars(C, P, M, T, vtype=GRB.BINARY, name="y") 
    phi = model.addVars(P, T, vtype=GRB.BINARY, name="phi")
    u = model.addVars(Z, T, vtype=GRB.CONTINUOUS, name="u")
    zeta = model.addVars(Z, T, vtype=GRB.CONTINUOUS, name="zeta")
    
    # Función objetivo (minimizar peligrosidad total)
    model.setObjective(gp.quicksum(u[z,t] for z in Z for t in T), GRB.MINIMIZE)
    
    # RESTRICCIONES DINÁMICAS MEJORADAS
    
    # R13 modificada: Actualización de peligrosidad CON NUEVO CRIMEN DIARIO
    for z in Z:
        for t in T:
            if t == 1:
                # Día 1: peligrosidad inicial
                peligrosidad_inicial = params["zeta"][z]
                cobertura = gp.quicksum(x[p,z,m,t] for p in P for m in M)
                model.addConstr(
                    u[z,t] == peligrosidad_inicial + params["lambda"] * zeta[z,t] - params["Gamma"] * cobertura,
                    name=f"R13_inicial_{z}_{t}"
                )
            else:
                # Días 2+: peligrosidad anterior + NUEVO CRIMEN + déficit - cobertura
                nuevo_crimen = 0.1 * params["zeta"][z]  # 10% de criminalidad nueva cada día
                cobertura = gp.quicksum(x[p,z,m,t] for p in P for m in M)
                model.addConstr(
                    u[z,t] == u[z,t-1] + nuevo_crimen + params["lambda"] * zeta[z,t] - params["Gamma"] * cobertura,
                    name=f"R13_dinamica_{z}_{t}"
                )
    
    # R12 modificada: Cobertura mínima MÁS ESTRICTA cada día
    for z in Z:
        for t in T:
            cobertura_total = gp.quicksum(x[p,z,m,t] for p in P for m in M)
            # Incrementar requerimiento gradualmente con el tiempo
            kappa_dinamico = params["kappa"] * (1 + 0.02 * (t-1))  # +2% cada día
            model.addConstr(
                cobertura_total + zeta[z,t] >= kappa_dinamico, 
                name=f"R12_dinamica_{z}_{t}"
            )
    
    # Resto de restricciones igual que modelo original...
    # (R1-R11 se mantienen igual)
    
    return model, x, y, phi, u, zeta

if __name__ == "__main__":
    print("Modelo dinámico creado")
    print("Este modelo incluye:")
    print("• Nuevo crimen que aparece cada día (10% de peligrosidad inicial)")
    print("• Requerimientos de cobertura que aumentan con el tiempo") 
    print("• Peligrosidad que evoluciona día a día") 