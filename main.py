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
    modo_testing = True  # Cambio por defecto a True para usar solo 1 zona
    horizonte = "mensual"
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--testing":
            modo_testing = True
            horizonte = "testing"
            print("🧪 MODO TESTING: Datos reducidos + 7 días")
        elif sys.argv[1] == "--diez-zonas":
            modo_testing = "diez_zonas"  # Nuevo modo especial
            horizonte = "mensual"
            print("📊 MODO 10 ZONAS: 10 zonas + 30 días (~medio millón variables)")
        elif sys.argv[1] == "--cinco-zonas":
            modo_testing = "cinco_zonas"  # Nuevo modo intermedio
            horizonte = "mensual"
            print("📊 MODO 5 ZONAS: 5 zonas + 30 días (~250K variables - INTERMEDIO)")
        elif sys.argv[1] == "--semanal":
            modo_testing = False
            horizonte = "semanal"
            print("📅 MODO SEMANAL: Todos los datos + 7 días (⚠️ PUEDE TARDAR MUCHO)")
        elif sys.argv[1] == "--mensual":
            modo_testing = False  # Mensual completo con todas las zonas
            horizonte = "mensual"
            print("📅 MODO MENSUAL: Todos los datos + 30 días (⚠️ MUY LENTO)")
        elif sys.argv[1] == "--completo":
            modo_testing = False
            horizonte = "completo"
            print("🔥 MODO COMPLETO: Todos los datos + 365 días (⚠️ PUEDE TARDAR HORAS)")
    else:
        print("📅 MODO TESTING MENSUAL por defecto: 1 zona + 30 días")
        print("   Opciones disponibles:")
        print("   --testing    : 1 zona + 7 días (~3K variables - MUY RÁPIDO)")
        print("   --cinco-zonas: 5 zonas + 30 días (~250K variables - INTERMEDIO)")
        print("   --diez-zonas : 10 zonas + 30 días (~500K variables - RÁPIDO)")
        print("   --semanal    : Todas las zonas + 7 días (~27M variables - LENTO)")
        print("   --mensual    : Todas las zonas + 30 días (~115M variables - MUY LENTO)")
        print("   --completo   : Todas las zonas + 365 días (~1.4B variables - EXTREMO)")
    
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
        total_variables = 0
        variables_cero = 0

        for var in modelo.getVars():
            total_variables += 1
            if abs(var.X) < 1e-10:
                variables_cero += 1
            elif var.X > 1e-10:  # Bajo el umbral de 1e-5 a 1e-10
                nombre = var.VarName
                valor = var.X
                variables_activas.append((nombre, valor))

        print(f"📊 Estadísticas de variables:")
        print(f"   • Total de variables: {total_variables}")
        print(f"   • Variables = 0: {variables_cero}")
        print(f"   • Variables activas (>{1e-10}): {len(variables_activas)}")
        
        # Si no hay variables activas, mostrar algunas variables con valores más pequeños
        if len(variables_activas) == 0:
            print("⚠️  No hay variables activas. Mostrando variables con valores más altos:")
            variables_no_cero = []
            for var in modelo.getVars():
                if var.X != 0:
                    variables_no_cero.append((var.VarName, var.X))
            
            # Ordenar por valor absoluto descendente
            variables_no_cero.sort(key=lambda x: abs(x[1]), reverse=True)
            
            for i, (nombre, valor) in enumerate(variables_no_cero[:20]):
                print(f"      {nombre} = {valor}")
            
            # Usar un umbral aún más bajo
            variables_activas = [(n, v) for n, v in variables_no_cero if abs(v) > 1e-15]
            print(f"   • Usando umbral 1e-15: {len(variables_activas)} variables")

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
