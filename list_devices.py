import sounddevice as sd

print("\n=== DISPOSITIVOS DE AUDIO DETECTADOS ===\n")
devices = sd.query_devices()

for i, d in enumerate(devices):
    print(f"ID: {i}")
    print(f"  Nombre: {d['name']}")
    print(f"  Canales entrada: {d['max_input_channels']}")
    print(f"  Canales salida: {d['max_output_channels']}")
    print(f"  Frecuencia: {d['default_samplerate']} Hz")
    print(f"  Latencia entrada: {d['default_low_input_latency']}")
    print(f"  Latencia salida: {d['default_low_output_latency']}")
    print()

print("\n=== DISPOSITIVO POR DEFECTO ===")
print(f"Entrada por defecto: {sd.default.device[0]}")
print(f"Salida por defecto: {sd.default.device[1]}")
