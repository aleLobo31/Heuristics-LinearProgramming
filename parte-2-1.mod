# Defino los conjuntos de mi problema
set BUSES; # En mi problema puede haber m buses
set SLOTS; # En mi problema puede haber n slots

# Defino los parámetros de mi problema
param COSTE_ASIGNACION;
param COSTE_OPORTUNIDAD;
param DISTANCIAS{i in BUSES};
param PASAJEROS{i in BUSES};

# Defino las variables de mi problema
var c{i in BUSES, j in SLOTS} binary; # Variable de asignación

# Defino la función objetivo
minimize COSTE_TOTAL:
    sum{i in BUSES, j in SLOTS} (c[i,j] * DISTANCIAS[i] * COSTE_ASIGNACION + (1 - c[i,j]) * PASAJEROS[i] * COSTE_OPORTUNIDAD);

# Defino las restricciones de mi problema
s.t. UN_SLOT_POR_BUS{j in SLOTS}:
    sum{i in BUSES} c[i,j] = 1; # Para cada slot j compruebo que la suma de todas las variable de asignación sea = 1

# Resuelvo el modelo
solve;

# Imprimo los resultados
printf "Coste Total Óptimo: %f\n", COSTE_TOTAL;
printf "Número de variables de decisión: %d\n", card(BUSES) * card(SLOTS);
printf "Número de restricciones: %d\n", card(SLOTS);

end;