from gurobipy import *
from modelo import construir_modelo, resolver_modelo
from parametros import cargar_parametros

if __name__ == "__main__":
    print("🚔 Iniciando optimización de patrullaje preventivo...")
    
    # Cargar parámetros
    print("📊 Cargando parámetros...")
    parametros = cargar_parametros()
    
    # Construir modelo
    print("🔧 Construyendo modelo...")
    modelo = construir_modelo(parametros)
    
    # Resolver modelo
    print("⚡ Resolviendo modelo...")
    exito = resolver_modelo(modelo)
    
    if exito:
        print("\n📋 Mostrando variables con valores no nulos:")
        count = 0
        for var in modelo.getVars():
            if var.X > 1e-5:  # Evita mostrar ceros por tolerancia
                print(f"{var.VarName} = {var.X}")
                count += 1
                if count > 50:  # Limitar output para modelos grandes
                    print("... (mostrando solo las primeras 50 variables)")
                    break
    else:
        print("\n❌ No se pudo resolver el modelo satisfactoriamente.")
