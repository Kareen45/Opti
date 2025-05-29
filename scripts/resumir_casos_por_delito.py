import pandas as pd

# Cargar Excel
excel_path = "raw_data/delitos_original.xlsx"
xls = pd.ExcelFile(excel_path)

# Cargar zonas para filtrar solo comunas de la RM
zonas_df = pd.read_csv("data/zonas.csv")
comunas_rm = zonas_df["nombre_zona"].tolist()

# Inicializar lista para guardar resultados
resumen_delitos = []

# Iterar sobre cada hoja (excepto TOTAL_DMCS)
for sheet in xls.sheet_names:
    if sheet == "TOTAL_DMCS":
        continue

    try:
        df = pd.read_excel(xls, sheet_name=sheet, skiprows=3)
        df_rm = df[df["UNIDAD"].isin(comunas_rm)]

        # Buscar una columna que contenga "2023"
        col_2023 = next((col for col in df_rm.columns if "2023" in str(col)), None)

        if col_2023:
            total_2023 = df_rm[col_2023].sum()
        else:
            total_2023 = None
            print(f"[!] No se encontró columna para 2023 en hoja: {sheet}")
            print(df_rm.columns.tolist())  # Mostrar columnas disponibles

        resumen_delitos.append({
            "nombre_delito": sheet,
            "casos_2023": total_2023
        })

    except Exception as e:
        print(f"Error procesando hoja {sheet}: {e}")


# Convertir a DataFrame
df_resumen = pd.DataFrame(resumen_delitos)

# Mostrar ordenado por cantidad de casos
print(df_resumen.sort_values("casos_2023", ascending=False))

from sklearn.preprocessing import MinMaxScaler

# Quitar los delitos sin datos
df_resumen = df_resumen.dropna(subset=["casos_2023"])

# Asignar id_delito (en orden de frecuencia descendente)
df_resumen = df_resumen.sort_values("casos_2023", ascending=False).reset_index(drop=True)
df_resumen["id_delito"] = df_resumen.index

# Normalizar idd en rango [0.3, 1.0] según casos
scaler = MinMaxScaler(feature_range=(0.3, 1.0))
df_resumen["idd"] = scaler.fit_transform(df_resumen[["casos_2023"]])

# Reordenar columnas para guardar
df_final = df_resumen[["id_delito", "nombre_delito", "idd"]]

# Guardar archivo CSV
df_final.to_csv("data/tipos_delitos.csv", index=False)
print("\n✅ Se guardó data/tipos_delitos.csv correctamente.")
