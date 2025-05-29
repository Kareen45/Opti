# Opti

carabineros.csv: id_carabinero,experiencia,estacion

vehiculos.csv: id_vehiculo,tipo,estacion

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

compatibilidad_vehiculo_zona.csv: tipo_vehiculo,id_zona,compatible

costo_vehiculo.csv: id_vehiculo,tipo_vehiculo,dia,costo

presupuesto_estacion.csv: estacion,presupuesto

max_patrullas.csv: estacion,tipo_vehiculo,max_pat

capacidad_vehiculo.csv: tipo_vehiculo,capacidad

zeta_inicial.csv: id_zona,dia,zeta




