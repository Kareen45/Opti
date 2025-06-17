"""
SISTEMA DE OPTIMIZACIÓN DE PATRULLAJE PREVENTIVO
Versión oficial - Modelo de asignación de recursos policiales
"""

from gurobipy import *
from modelo import construir_modelo, resolver_modelo
from parametros import cargar_parametros
import sys
import pandas as pd
import os
from collections import defaultdict

def mostrar_ayuda():
    """Muestra las opciones disponibles del programa"""
    print("🚔 SISTEMA DE OPTIMIZACIÓN DE PATRULLAJE PREVENTIVO")
    print("="*55)
    print("MODOS DISPONIBLES:")
    print("  --cinco-zonas    : 5 zonas representativas + 30 días (RECOMENDADO)")
    print("  --testing        : 1 zona + 7 días (PRUEBA RÁPIDA)")
    print("\nEJEMPLOS:")
    print("  python main.py                # Modo recomendado (5 zonas + 30 días)")
    print("  python main.py --cinco-zonas  # Modo explícito")
    print("  python main.py --testing      # Prueba rápida")



def resolver_modelo_policial(modo_testing="cinco_zonas", horizonte="mensual"):
    """
    Resuelve el modelo de optimización policial
    """
    
    print("📊 Cargando parámetros...")
    parametros = cargar_parametros(modo_testing=modo_testing, horizonte=horizonte)
    
    print("🔧 Construyendo modelo...")
    modelo = construir_modelo(parametros)
    
    os.makedirs("resultados", exist_ok=True)
    print("⚡ Resolviendo modelo...")
    exito = resolver_modelo(modelo)
    
    if exito:
        print("\n📋 Procesando resultados...")

        variables_activas = []
        total_variables = 0
        variables_cero = 0

        for var in modelo.getVars():
            total_variables += 1
            if abs(var.X) < 1e-10:
                variables_cero += 1
            elif var.X > 1e-10:
                nombre = var.VarName
                valor = var.X
                variables_activas.append((nombre, valor))

        print(f"📊 Estadísticas del modelo:")
        print(f"   • Total de variables: {total_variables:,}")
        print(f"   • Variables activas: {len(variables_activas):,}")
        print(f"   • Función objetivo: {modelo.objVal:.6f}")
        
        # Guardar variables activas
        df_vars = pd.DataFrame(variables_activas, columns=["variable", "valor"])
        df_vars.to_excel("resultados/variables_activas.xlsx", index=False)
        
        # Generar resumen diario
        resumen = defaultdict(lambda: defaultdict(float))

        for nombre, valor in variables_activas:
            try:
                if nombre.startswith("x["):  # x[p,z,m,t]
                    partes = nombre[2:-1].split(",")
                    t = int(partes[3])
                    resumen[t]["patrullas_asignadas"] += 1
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
                    resumen[t]["peligrosidad_acumulada"] += valor
                elif nombre.startswith("zeta["):  # zeta[z,t]
                    partes = nombre[5:-1].split(",")
                    t = int(partes[1])
                    resumen[t]["deficit_cobertura"] += valor
            except Exception as e:
                continue  # Ignorar errores de parsing

        # Convertir resumen a DataFrame
        filas = []
        for dia in sorted(resumen):
            fila = {"dia": dia}
            fila.update(resumen[dia])
            filas.append(fila)

        df_resumen = pd.DataFrame(filas)
        df_resumen.to_excel("resultados/resumen_diario_recursos.xlsx", index=False)
        
        print("✅ Archivos guardados:")
        print("   • resultados/variables_activas.xlsx")
        print("   • resultados/resumen_diario_recursos.xlsx")
        
        print(f"\n🎯 FUNCIÓN OBJETIVO FINAL: {modelo.objVal:.6f}")
        print("   (Peligrosidad total minimizada - MENOR es MEJOR)")

    else:
        print("\n❌ No se pudo resolver el modelo satisfactoriamente.")

if __name__ == "__main__":
    print("🚔 Iniciando Sistema de Optimización de Patrullaje Preventivo...")
    
    # Configuración por defecto
    modo_testing = "cinco_zonas"
    horizonte = "mensual"
    
    # Procesar argumentos
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg == "--help" or arg == "-h":
            mostrar_ayuda()
            sys.exit(0)
        elif arg == "--cinco-zonas":
            modo_testing = "cinco_zonas"
            print("📊 MODO 5 ZONAS: 5 zonas representativas + 30 días")
        elif arg == "--testing":
            modo_testing = True
            horizonte = "testing"
            print("🧪 MODO TESTING: 1 zona + 7 días")
        else:
            print(f"❌ Argumento desconocido: {arg}")
            print("💡 Argumentos válidos: --cinco-zonas, --testing")
            mostrar_ayuda()
            sys.exit(1)
    else:
        print("📊 MODO POR DEFECTO: 5 zonas representativas + 30 días")
        print("   Ejecuta 'python main.py --help' para ver opciones")
    
    # Ejecutar optimización
    resolver_modelo_policial(modo_testing, horizonte)
