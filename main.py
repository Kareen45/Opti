from gurobipy import *
from modelo import construir_modelo
from parametros import cargar_parametros

if __name__ == "__main__":
    parametros = cargar_parametros()
    modelo = construir_modelo(parametros)
    modelo.optimize()

    # Mostrar resultados
    if modelo.status == GRB.OPTIMAL:
        print("\n✅ Solución óptima encontrada:")
        for var in modelo.getVars():
            if var.X > 1e-5:  # Evita mostrar ceros por tolerancia
                print(f"{var.VarName} = {var.X}")

        print(f"\n🎯 Valor óptimo de la función objetivo: {modelo.ObjVal}")
    else:
        print("\n❌ No se encontró solución óptima.")
