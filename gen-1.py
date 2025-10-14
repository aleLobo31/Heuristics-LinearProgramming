#!/usr/bin/env python3
"""
Script para procesar archivo de entrada, generar archivo .dat 
y ejecutar el solver GLPSOL
"""

import sys
import subprocess
import os

MODEL_PATH = "model/parte-2-1.mod"


def read_input_file(path_input_file: str) -> dict:
    try:
        # Read input file
        with open(path_input_file, 'r') as f:
            lineas = f.readlines()
        
        # Extract: <n> <m>
        n, m = map(int, lineas[0].strip().split())
        # Extract: <k_d> <k_p>
        k_d, k_p = map(float, lineas[1].strip().split())
        # Extract: <d1, d2, ..., dm>
        distances = list(map(float, lineas[2].strip().split()))
        # Extract: <p1, p2, ..., pm>
        passengers = list(map(float, lineas[3].strip().split()))

        # Check n and m are positive
        if n <= 0 or m <= 0:
            raise ValueError("n y m deben ser enteros positivos")
        
        # Check k_d and k_p are non-negative
        if k_d < 0 or k_p < 0:
            raise ValueError("k_d y k_p deben ser números no negativos")

        # Check there is a distance to the workshop for each bus
        if len(distances) != m:
            raise ValueError(f"Se esperaban {m} distancias, se encontraron {len(distances)}")
        
        # Check all distances are non-negative
        if any(d < 0 for d in distances):
            raise ValueError("Todas las distancias deben ser números no negativos")
        
        # Check there is a passenger number for each bus
        if len(passengers) != m:
            raise ValueError(f"Se esperaban {m} pasajeros, se encontraron {len(passengers)}")
        
        # Check all passenger numbers are non-negative
        if any(p < 0 for p in passengers):
            raise ValueError("Todos los números de pasajeros deben ser números no negativos")

        return {
            'n': n,
            'm': m,
            'k_d': k_d,
            'k_p': k_p,
            'distancias': distances,
            'pasajeros': passengers
        }
    
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{path_input_file}'")
        sys.exit(1)
    except IndexError:
        print("Error: El archivo de entrada no tiene el formato correcto")
        sys.exit(1)
    except ValueError as e:
        print(f"Error al procesar el valor: {e}")
        sys.exit(1)


def generate_dat_file(data: dict, output_path: str):
    # Extract data values
    n = data['n']
    m = data['m']
    k_d = data['k_d']
    k_p = data['k_p']
    distances = data['distancias']
    passengers = data['pasajeros']
    
    try:
        # Open output file or create it if doesn't exist
        with open(output_path, 'w') as f:
            # Write header
            f.write("# Problema de asignación de buses a slots del taller\n\n")
            f.write("data;\n\n")
            
            # Define BUS set
            f.write("set BUSES :=")
            for i in range(1, m + 1):
                f.write(f" Bus{i}")
            f.write(";\n")
            
            # Define SLOT set
            f.write("set SLOTS :=")
            for j in range(1, n + 1):
                f.write(f" Slot{j}")
            f.write(";\n\n")
            
            # Define k_d y k_p parameters
            f.write(f"param COSTE_ASIGNACION := {k_d};\n")
            f.write(f"param COSTE_OPORTUNIDAD := {k_p};\n\n")
            
            # Define distances
            f.write("param DISTANCIAS :=\n")
            for i in range(1, m + 1):
                f.write(f"    Bus{i}  {distances[i-1]}")
                if i < m:
                    f.write("\n")
            f.write(";\n\n")
            
            # Define passengers
            f.write("param PASAJEROS :=\n")
            for i in range(1, m + 1):
                f.write(f"    Bus{i}  {passengers[i-1]}")
                if i < m:
                    f.write("\n")
            f.write(";\n\n")

            # Write end of data
            f.write("end;\n")        
    except IOError as e:
        print(f"Error al escribir el archivo .dat: {e}")
        sys.exit(1)


def solve(data_path: str, output_file_path: str="logs/output.txt"):
    # Check if the model file exists
    if not os.path.exists(MODEL_PATH):
        print(f"Error: No se encontró el archivo modelo '{MODEL_PATH}'")
        sys.exit(1)
    
    # Declare the command
    comando = [
        "glpsol",
        "-m", MODEL_PATH,
        "-d", data_path,
        "-o", output_file_path
    ]
    
    try:
        # Run the command
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Show output and errors if any
        print(resultado.stdout)
        if resultado.stderr:
            print("Advertencias/Errores del solver:")
            print(resultado.stderr)
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error al ejecutar GLPSOL:")
        print(e.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("\n✗ Error: No se encontró el comando 'glpsol'")
        print("Asegúrate de que GLPK esté instalado y en el PATH")
        sys.exit(1)


def main():
    """Función principal del script."""
    
    # Check the right number of arguments have been provided
    if len(sys.argv) != 3:
        print("Uso: python script.py <archivo_entrada.in> <archivo_salida.dat>\n")
        print("Ejemplo: python script.py data/entrada.in data/salida.dat")
        sys.exit(1)
    
    path_input_file = sys.argv[1]
    path_output_file = sys.argv[2]
    
    # Reads input file
    data = read_input_file(path_input_file)
    print(data)

    # Generates .dat file
    generate_dat_file(data, path_output_file)
    
    # Call the solver
    # solve(path_output_file)

if __name__ == "__main__":
    main()