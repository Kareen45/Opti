from gurobipy import *
from modelo import construir_modelo, resolver_modelo
from parametros import cargar_parametros
import sys

if __name__ == "__main__":
    print("🚔 Iniciando optimización de patrullaje preventivo...")
    
    # Determinar modo de ejecución
    modo_testing = True
    horizonte = "testing"
    
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
        print("🧪 MODO TESTING por defecto: Datos reducidos + 7 días (rápido y funcional)")
        print("   Opciones disponibles:")
        print("   --testing  : Datos reducidos + 7 días (~110K variables - RECOMENDADO)")
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
        
        if count == 0:
            print("⚠️  No hay variables con valores no nulos (posible problema)")
    else:
        print("\n❌ No se pudo resolver el modelo satisfactoriamente.")
