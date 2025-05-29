# Opti - Modelo de Optimización de Patrullaje Preventivo

Este proyecto implementa un modelo de optimización para la asignación de patrullas de carabineros en la ciudad de Santiago, con el objetivo de minimizar la peligrosidad total considerando la evolución dinámica del riesgo en cada zona.

## Descripción de Archivos CSV

### carabineros.csv
**Estructura:** `id_carabinero,experiencia,id_estacion`
- **Propósito:** Define el conjunto C de carabineros disponibles
- **Contenido:** 20 carabineros por cada comisaría (66 comisarías = 1320 carabineros total)
- **Parámetros del modelo:**
  - `q[c]`: Experiencia en años del carabinero c
  - `β[c,e]`: Parámetro binario que indica si el carabinero c pertenece a la estación e
- **Uso en restricciones:** R1 (asignación única), R2 (compatibilidad estación), R3 (experiencia mínima)

### comisarias.csv
**Estructura:** `id_comisaria,id_zona,numero_carabineros,numero_motos,numero_bicis,numero_caballos,numero_autos,numero_furgon,presupuesto_anual`
- **Propósito:** Define las estaciones (conjunto E) y sus recursos disponibles
- **Parámetros del modelo:**
  - `P_e[e]`: Presupuesto anual para la estación e
- **Uso en restricciones:** R11 (límite presupuestario por estación)

### zonas.csv
**Estructura:** `id_zona,nombre_zona,compatible_moto,compatible_bici,compatible_caballo,compatible_auto,compatible_furgon`
- **Propósito:** Define el conjunto Z de zonas (comunas de Santiago) y compatibilidad con tipos de vehículos
- **Parámetros del modelo:**
  - `r[v,z]`: Parámetro binario que indica si vehículos tipo v pueden operar en zona z
- **Uso en restricciones:** R5 (compatibilidad tipo de vehículo con zona)
- **Nota:** Peatones (tipo 1) son compatibles con todas las zonas por defecto

### tipos_delitos.csv
**Estructura:** `id_delito,nombre_delito,idd`
- **Propósito:** Define el conjunto D de familias de delitos y su índice de daño
- **Fuente:** PDF de frecuencia de casos policiales de la Región Metropolitana
- **Parámetros del modelo:**
  - `IDD[d]`: Índice de daño del delito familia d (escalado entre 0.3 y 1 usando min-max)
- **Uso en modelo:** Cálculo de Γ (normalización) y actualización de peligrosidad (R13)

### incidencia_delito.csv
**Estructura:** `id_delito,id_zona,incidencia`
- **Propósito:** Define la tasa de incidencia de cada tipo de delito en cada zona
- **Fuente:** PDF de frecuencia de casos policiales procesado por comuna
- **Parámetros del modelo:**
  - `I[d,z]`: Tasa de incidencia del delito d en zona z (casos del delito / casos totales)
- **Uso en modelo:** Cálculo de Γ y evolución de peligrosidad (R13)

### costos_diarios.csv
**Estructura:** `Dia,Costo_uso_peaton,Costo_uso_moto,Costo_uso_bici,Costo_uso_caballo,Costo_uso_auto,Costo_uso_furgon`
- **Propósito:** Define los costos operacionales diarios por tipo de vehículo
- **Parámetros del modelo:**
  - `O[v,t]`: Costo diario por uso de vehículo tipo v el día t
- **Uso en restricciones:** R11 (límite presupuestario por estación)

### vehiculos.csv
**Estructura:** `id,tipo_medio,id_estacion`
- **Propósito:** Define el conjunto P de vehículos disponibles y sus características
- **Parámetros del modelo:**
  - `w[p,v]`: Parámetro binario que indica si vehículo p es de tipo v
  - `α[p,e]`: Parámetro binario que indica si vehículo p pertenece a estación e
- **Uso en restricciones:** R2 (compatibilidad estación), R5 (compatibilidad zona), R8 (capacidad), R11 (presupuesto)

## Parámetros Adicionales del Modelo

- **Γ (Gamma):** Valor máximo de peligrosidad teórica calculado como `max_z(∑_d I[d,z] × IDD[d])`
- **λ (lambda):** Sensibilidad del aumento de peligrosidad (0.1 por defecto)
- **κ (kappa):** Factor de conversión peligrosidad → patrullas requeridas (1.0 por defecto)
- **R_v:** Capacidad máxima por tipo de vehículo (peatón:1, moto:1, bici:1, caballo:2, auto:4, furgón:7)

## Estructura del Modelo

El modelo minimiza la suma total de peligrosidad `∑∑ζ[z,t]` sujeto a 13 restricciones que incluyen:
- Asignación única de carabineros y vehículos
- Compatibilidad entre estaciones, vehículos y zonas  
- Experiencia mínima y capacidad máxima por patrulla
- Cobertura mínima proporcional a peligrosidad
- Evolución dinámica de peligrosidad por déficit de cobertura
- Límites presupuestarios por estación


