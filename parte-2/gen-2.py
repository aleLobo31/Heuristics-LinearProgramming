#!/usr/bin/env python3
"""
Script para procesar archivo de entrada, generar archivo .dat 
y ejecutar el solver GLPSOL
"""

import sys
import subprocess
import os

MODEL_PATH = "model/parte-2-2.mod"


def read_input_file(path_input_file: str) -> dict:
    try:
        # Read input file
        with open(path_input_file, 'r') as f:
            lineas = f.readlines()
        
        # Define the matrixes where the rest of parameters are going to be stored
        shared_passengers = []
        available_slots = []

        # Aux variable to iterate through the input file
        i = 1
        
        # Extract: <n> <m> <u>
        n, m, u = map(int, lineas[0].strip().split())

        # Check n, m and u are positive
        if n <= 0 or m <= 0 or u <= 0:
            raise ValueError("n, m y u deben ser enteros positivos")

        # Extract shared_passengers matrix
        while(i <= m):
            # Extract all integer values from the line
            values = list(map(int, lineas[i].strip().split()))
            # Check shared passengers
            check_shared_passengers(values, m, i-1)
            # Add the shared passengers to the associated matrix
            shared_passengers.append(values)
            # Iterate
            i += 1
        
        # Check shared_passengers is a simetric matrix
        for row in range(0, len(shared_passengers)):
            for col in range(0, len(shared_passengers)):
                if(shared_passengers[row][col] != shared_passengers[col][row]):
                    raise ValueError("La matriz de pasajeros compartidos no es simétrica")

        # Extract available_slots matrix
        while(i != len(lineas) and lineas[i].strip() != ""):
            # Check whether there are more buses than the ones defined
            if(i - m > u):
                raise ValueError("Existen slots asignados a talleres inexistentes")
            # Extract all integer values from the line
            values = list(map(int, lineas[i].strip().split()))
            # Check available_slots
            check_available_slots(values, n)
            # Add the available slots to the associated matrix
            available_slots.append(values)
            # Iterate
            i += 1

        # Transpose available_slots matrix to match the required format
        if available_slots:
            available_slots = [list(row) for row in zip(*available_slots)]

        return {
            'n': n,
            'm': m,
            'u': u,
            'c': shared_passengers,
            'o': available_slots
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

def check_shared_passengers(values: list, m: int, curr_line: int):
    if len(values) > m:
        raise ValueError("Existen pasajeros simultáneos asignados a buses no existentes")
    if values[curr_line] != 0:
        raise ValueError("Un bus no puede tener consigo mismo pasajeros simultáneos")
    for i in range(0, len(values)):
        if values[i] < 0:
            raise ValueError("Los pasajeros compartidos no pueden ser valores negativos")
    return

def check_available_slots(values: list, n: int):
    if(len(values) > n):
        raise ValueError("El número de slots exceden su número definido")
    for i in range(0, len(values)):
        if(values[i] != 0 and values[i] != 1):
            raise ValueError("El slot definido no es una variable binaria")
    return

def generate_dat_file(data: dict, output_path: str):
    # Extract data values
    n = data['n']
    m = data['m']
    u = data['u']
    c = data['c']
    o = data['o']
    
    try:
        # Open output file or create it if doesn't exist
        with open(output_path, 'w') as f:
            # Write header
            f.write("# Problema de asignación de buses a slots de diferentes talleres\n\n")
            f.write("data;\n\n")
            
            # Define BUSES set
            f.write("set BUSES :=")
            for i in range(1, m + 1):
                f.write(f" Bus{i}")
            f.write(";\n")

            # Define TALLERES set
            f.write("set TALLERES :=")
            for j in range(1, u+1):
                f.write(f" Taller{j}")
            f.write(";\n")
            
            # Define SLOTS set
            f.write("set SLOTS :=")
            for k in range(1, n + 1):
                f.write(f" Slot{k}")
            f.write(";\n\n")
            
            # Define shared_passengers parameters:
            f.write("param PASAJEROS_COMPARTIDOS:")
            for i in range(1, m+1):
                f.write(f" Bus{i}")
            f.write(":=\n")

            for i in range(1, m+1):
                f.write(f"\tBus{i}")
                for j in range(0, len(c[i-1])):
                    f.write(f" {c[i-1][j]}")
                if(i == m):
                    f.write(";")
                f.write("\n")
            f.write("\n")
            
            # Define available_slots parameters:
            f.write("param DISPONIBILIDAD_SLOT:")
            for j in range(1, u+1):
                f.write(f" Taller{j}")
            f.write(":=\n")

            for k in range(1, n+1):
                f.write(f"\tSlot{k}")
                for j in range(0, len(o[k-1])):
                    f.write(f" {o[k-1][j]}")
                if(k == n):
                    f.write(";")
                f.write("\n")
            f.write("\n")

            # Write end of data
            f.write("end;\n")        
    except IOError as e:
        print(f"Error al escribir el archivo .dat: {e}")
        sys.exit(1)

def solve(data_path: str, output_file_path: str="logs/output_model_2_2.txt"):
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
        
        # Show output
        print(resultado.stdout)

        # Show errors if any
        if resultado.stderr:
            print("Advertencias/Errores del solver:")
            print(resultado.stderr)
        
    except subprocess.CalledProcessError as e:
        print(f"\nError al ejecutar GLPSOL:")
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("\nError: No se encontró el comando 'glpsol'")
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
    # Check that input file has .in extension
    if not path_input_file.endswith('.in'):
        print("Error: El archivo de entrada debe tener extensión .in")
        sys.exit(1)
    
    path_output_file = sys.argv[2]
    # Check that output file has .dat extension
    if not path_output_file.endswith('.dat'):
        print("Error: El archivo de salida debe tener extensión .dat")
        sys.exit(1)
    
    # Reads input file
    data = read_input_file(path_input_file)
    # print(data)

    # Generates .dat file
    generate_dat_file(data, path_output_file)
    
    # Call the solver
    solve(path_output_file)

if __name__ == "__main__":
    main()