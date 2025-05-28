from modelo import construir_modelo
from data.parametros import parametros_ejemplo

if __name__ == "__main__":
    modelo = construir_modelo(parametros_ejemplo)
    modelo.optimize()
