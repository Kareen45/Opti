import pandas as pd

# Cargar archivos base
xls = pd.ExcelFile("raw_data/delitos_original.xlsx")
zonas_df = pd.read_csv("data/zonas.csv")
tipos_df = pd.read_csv("data/tipos_delitos.csv")

# Preparar diccionarios para mapeo
comunas_rm = zonas_df["nombre_zona"].tolist()
nombre_to_idzona = dict(zip(zonas_df["nombre_zona"], zonas_df["id_zona"]))
nombre_to_iddelito = dict(zip(tipos_df["nombre_delito"], tipos_df["id_delito"]))

# Lista para guardar resultados
filas = []

# Procesar cada tipo de delito
for _, row in tipos_df.iterrows():
    nombre_delito = row["nombre_delito"]
    id_delito = row["id_delito"]

    try:
        df = pd.read_excel(xls, sheet_name=nombre_delito, skiprows=3)
        df_rm = df[df["UNIDAD"].isin(comunas_rm)]

        col_2023 = next((col for col in df_rm.columns if "2023" in str(col)), None)
        if col_2023 is None:
            print(f"[!] Columna 2023 no encontrada en hoja {nombre_delito}")
            continue

        total_delito = df_rm[col_2023].sum()
        if total_delito == 0:
            continue

        for _, comuna_row in df_rm.iterrows():
            comuna = comuna_row["UNIDAD"]
            id_zona = nombre_to_idzona.get(comuna)
            if id_zona is None:
                continue

            casos = comuna_row[col_2023]
            incidencia = casos / total_delito
            filas.append({
                "id_delito": id_delito,
                "id_zona": id_zona,
                "incidencia": round(incidencia, 6)
            })

    except Exception as e:
        print(f"[!] Error en hoja {nombre_delito}: {e}")

# Exportar CSV final
df_final = pd.DataFrame(filas)
df_final.to_csv("data/incidencia_delito.csv", index=False)
print("✅ Archivo 'data/incidencia_delito.csv' generado exitosamente.")
