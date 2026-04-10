import sounddevice as sd

print("=== TODAS LAS SALIDAS DE AUDIO ===\n")

devices = sd.query_devices()

salidas = []
for i, device in enumerate(devices):
    if device['max_output_channels'] > 0:
        salidas.append(i)
        print(f"ID: {i:2d} | {device['name'][:60]:60s} | Canales: {device['max_output_channels']}")

print(f"\n✓ Total de salidas detectadas: {len(salidas)}")
