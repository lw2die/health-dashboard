from config import INPUT_DIR, PROCESADOS_DIR
import os

print("INPUT_DIR =", INPUT_DIR)
print("PROCESADOS_DIR =", PROCESADOS_DIR)

print("\nArchivos encontrados en INPUT_DIR:")
try:
    for f in os.listdir(INPUT_DIR):
        print("  ", f)
except Exception as e:
    print("  ERROR leyendo carpeta:", e)
