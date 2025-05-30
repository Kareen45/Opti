from gurobipy import *
from modelo import construir_modelo, resolver_modelo
from parametros import cargar_parametros
import sys
import pandas as pd
import os
from collections import defaultdict

if __name__ == "__main__":
    print("🚔 Iniciando optimización de patrullaje preventivo...")
    
    # Determinar modo de ejecución
    modo_testing = False
    horizonte = "mensual"
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--testing":
            modo_testing = True
            horizonte = "testing"
            print("🧪 MODO TESTING: Datos reducidos + 7 días")
        elif sys.argv[1] == "--semanal":
            modo_testing = False
            horizonte = "semanal"
            print("📅 MODO SEMANAL: Todos los datos + 7 días (⚠️ PUEDE TARDAR MUCHO)")
        elif sys.argv[1] == "--mensual":
            horizonte = "mensual"
            print("📅 MODO MENSUAL: Todos los datos + 30 días (⚠️ MUY LENTO)")
        elif sys.argv[1] == "--completo":
            horizonte = "completo"
            print("🔥 MODO COMPLETO: Todos los datos + 365 días (⚠️ PUEDE TARDAR HORAS)")
    else:
        print("📅 MODO MENSUAL por defecto: Todos los datos + 30 días")
        print("   Opciones disponibles:")
        print("   --testing  : Datos reducidos + 7 días (~110K variables - RÁPIDO)")
        print("   --semanal  : Todos los datos + 7 días (~27M variables - LENTO)")
        print("   --mensual  : Todos los datos + 30 días (~115M variables - MUY LENTO)")
        print("   --completo : Todos los datos + 365 días (~1.4B variables - EXTREMO)")
    
    # Cargar parámetros
    print("📊 Cargando parámetros...")
    parametros = cargar_parametros(modo_testing=modo_testing, horizonte=horizonte)
    
    # Construir modelo
    print("🔧 Construyendo modelo...")
    modelo = construir_modelo(parametros)
    
    # Resolver modelo
    os.makedirs("resultados", exist_ok=True)
    print("⚡ Resolviendo modelo...")
    exito = resolver_modelo(modelo)
    
    if exito:
        print("\n📋 Guardando variables activas...")

        variables_activas = []

        for var in modelo.getVars():
            if var.X > 1e-5:
                nombre = var.VarName
                valor = var.X
                variables_activas.append((nombre, valor))

        # Guardar todas las variables activas en Excel
        df_vars = pd.DataFrame(variables_activas, columns=["variable", "valor"])
        df_vars.to_excel("resultados/variables_activas.xlsx", index=False)
        print("✅ Guardado: resultados/variables_activas.xlsx")

        # Inicializar resumen diario
        resumen = defaultdict(lambda: defaultdict(float))  # resumen[dia][recurso] = total

        for nombre, valor in variables_activas:
            try:
                if nombre.startswith("x["):  # x[p,z,m,t]
                    partes = nombre[2:-1].split(",")
                    t = int(partes[3])
                    resumen[t]["patrullas_asignadas"] += 1  # es binaria
                elif nombre.startswith("y["):  # y[c,p,m,t]
                    partes = nombre[2:-1].split(",")
                    t = int(partes[3])
                    resumen[t]["carabineros_asignados"] += 1
                elif nombre.startswith("phi["):  # phi[p,t]
                    partes = nombre[4:-1].split(",")
                    t = int(partes[1])
                    resumen[t]["vehiculos_utilizados"] += 1
                elif nombre.startswith("u["):  # u[z,m,t]
                    partes = nombre[2:-1].split(",")
                    t = int(partes[2])
                    resumen[t]["deficit_patrullas"] += valor
                elif nombre.startswith("zeta["):  # zeta[z,t]
                    partes = nombre[5:-1].split(",")
                    t = int(partes[1])
                    resumen[t]["nivel_peligrosidad"] += valor  # se suma por zona
            except Exception as e:
                print(f"[!] No se pudo procesar {nombre}: {e}")

        # Convertir resumen a DataFrame
        filas = []
        for dia in sorted(resumen):
            fila = {"dia": dia}
            fila.update(resumen[dia])
            filas.append(fila)

        df_resumen = pd.DataFrame(filas)
        df_resumen.to_excel("resultados/resumen_diario_recursos.xlsx", index=False)
        print("✅ Guardado: resultados/resumen_diario_recursos.xlsx")

        # Mostrar por consola las primeras 50 variables
        print("\n🔍 Primeras 50 variables activas:")
        for i, (nombre, valor) in enumerate(variables_activas[:50]):
            print(f"{nombre} = {valor}")
        if len(variables_activas) > 50:
            print("... (mostrando solo las primeras 50 variables)")

    else:
        print("\n❌ No se pudo resolver el modelo satisfactoriamente.")
