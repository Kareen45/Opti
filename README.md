# Opti

✅carabineros.csv: id_carabinero,experiencia,id_estacion
- 20 carabineros x cada comisaría (son 66)
- Se usan 1320 carabineros en total

✅comisarias.csv: id_comisaria,id_zona,numero_carabineros,numero_motos,numero_bicis,numero_caballos,numero_autos,numero_furgon,presupuesto_anual
- 

✅zonas.csv: id_zona, nombre_zona
- Corresponden a las comunas de Santiago

✅tipos_delitos.csv: id_delito,nombre_delito,idd
- Se usó el pdf de frecuencia de casos policiales
- Se usó la librería pandas para leer solo las filas relacionadas a la región metropolitana en base a zonas.csv
- Idd es un valor entre 0.3 y 1, que indica qué tan grave o importante es un delito
- Se usó el escalamiento min-max de la librería scikit-learn

✅incidencia_delito.csv: id_delito,id_zona,incidencia
- Se usó el pdf de frecuencia de casos policiales
- Para cada comuna se guardan los casos por delito
- El índice de incidencia se calcula dividiendo los casos del delito x en los casos totales

costos_diarios.csv: Dia,Costo_uso_peaton,Costo_uso_moto,Costo_uso_bici,Costo_uso_caballo,Costo_uso_auto,Costo_uso_furgon

vehiculos.csv: id,tipo_medio,id_estacion


