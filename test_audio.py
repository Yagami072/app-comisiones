import sounddevice as sd
import numpy as np

print("=== PRUEBA DE AUDIO ===\n")

# Testear con Línea de entrada (ID 12) -> Speakers (ID 13)
INPUT_ID = 12  # Línea de entrada
OUTPUT_ID = 13  # Speakers

print(f"Input: ID {INPUT_ID} - {sd.query_devices(INPUT_ID)['name']}")
print(f"Output: ID {OUTPUT_ID} - {sd.query_devices(OUTPUT_ID)['name']}\n")

RATE = 44100
CHANNELS = 2
DURATION = 3

print("Escuchando 3 segundos de entrada y reproduciéndolo en salida...")

def callback(indata, outdata, frames, time, status):
    if status:
        print(f"Estado: {status}")
    # Copiar entrada a salida
    outdata[:] = indata
    # Mostrar nivel
    level = np.sqrt(np.mean(indata ** 2))
    print(f"Nivel: {level:.4f}", end='\r')

try:
    with sd.Stream(device=(INPUT_ID, OUTPUT_ID), 
                   samplerate=RATE, 
                   channels=CHANNELS,
                   callback=callback,
                   latency='low'):
        sd.sleep(DURATION * 1000)
    print("\n✓ Prueba completada exitosamente")
except Exception as e:
    print(f"\n✗ Error: {e}")
