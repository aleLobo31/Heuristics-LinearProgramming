# Defino los conjuntos de mi problema
set BUSES;
set TALLERES;
set SLOTS;

# Defino los parámetros de mi problema
param DISPONIBILIDAD_SLOT{k in SLOTS, j in TALLERES} binary;
param PASAJEROS_COMPARTIDOS{i in BUSES, j in BUSES};

# Defino las variables de mi problema
var x{i in BUSES, j in TALLERES, k in SLOTS} binary;
var y{i in BUSES, j in BUSES, k in SLOTS: i < j} binary;
var z{i in BUSES, k in SLOTS} binary;

# Defino la función objetivo
minimize SATISFACCION_PERDIDA:
sum{i in BUSES, j in BUSES, k in SLOTS: i < j} (PASAJEROS_COMPARTIDOS[i, j] * y[i, j, k]);

# Cada bus debe estar asignado a exactamente un slot de algún taller
s.t. UN_BUS_UN_SLOT{i in BUSES}:
sum{j in TALLERES, k in SLOTS} x[i, j, k] = 1;

# Disponibilidad de slots en talleres, incluye capacidad máxima de cada franja
s.t. DISPONIBILIDAD_CAPACIDAD_SLOTS{j in TALLERES, k in SLOTS}:
sum{i in BUSES} x[i, j, k] <= DISPONIBILIDAD_SLOT[k, j];

# Variable binaria auxiliar para capturar si un bus i está asignado a una franja k
s.t. DEFINICION_Z{i in BUSES, k in SLOTS}:
 z[i, k] = sum{j in TALLERES} x[i, j, k];

# Restricciones de simultaneidad entre buses que comparten pasajeros
s.t. DEFINICION_Y3{i in BUSES, j in BUSES, k in SLOTS: i < j}:
 y[i, j, k] >= z[i, k] + z[j, k] - 1;

solve;

# Imprimo los resultados
printf("**************** RESULTADOS ****************\n");
printf "Satisfacción Perdida Óptima: %f\n", SATISFACCION_PERDIDA;
printf "Número de variables de decisión: %d\n",
card(BUSES) * card(TALLERES) * card(SLOTS) +
 (card(BUSES) * (card(BUSES) - 1) / 2) * card(SLOTS) +
card(BUSES) * card(SLOTS);
printf "Número de restricciones: %d\n",
card(BUSES) +
card(TALLERES) * card(SLOTS) +
card(BUSES) * card(SLOTS) +
3 * (card(BUSES) * (card(BUSES) - 1) / 2) * card(SLOTS);

printf "\n=== ASIGNACIÓN DE BUSES ===\n";
printf "Bus → Taller, Franja\n";
display {i in BUSES, j in TALLERES, k in SLOTS: x[i, j, k] = 1} x[i, j, k];


printf "\n=== BUSES CONFLICTIVOS ===\n";
printf "Bus i, Bus j, Franja\n";
display {i in BUSES, j in BUSES, k in SLOTS: i < j and y[i, j, k] = 1} y[i, j, k];
printf("********************************************\n");

end;