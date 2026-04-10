# Audio Cloner Pro 🎵

Una aplicación de escritorio para **clonar/duplicar audio** desde una entrada de audio a múltiples dispositivos de salida simultáneamente, similar a Audio Repeater Pro.

## Características

✅ **Selecciona dispositivo de entrada** - Micrófono, línea de entrada, o cualquier entrada de audio  
✅ **Múltiples salidas** - Envía audio a varios dispositivos a la vez  
✅ **Control de volumen** - Ajusta el volumen entre 0-200%  
✅ **Visualizador de audio** - Ve en tiempo real el audio que se está procesando  
✅ **Interfaz gráfica intuitiva** - Botones y controles amigables  

## Requisitos Previos

- **Python 3.8 o superior**
- **Windows 10/11**

## Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

**Nota:** Si tienes problemas con PyAudio en Windows, ejecuta:
```bash
pip install pipwin
pipwin install pyaudio
```

### 2. Ejecutar la aplicación

```bash
python audio_cloner.py
```

## Uso

1. **Selecciona dispositivo de entrada** - Elige de dónde quieres capturar el audio
2. **Marca dispositivos de salida** - Selecciona uno o más dispositivos donde reproducir (marca los checkboxes)
3. **Ajusta volumen** (opcional) - Control deslizante del 0-200%
4. **Haz clic en "INICIAR CLONACIÓN"** - El audio comenzará a fluir
5. **Observa el visualizador** - Verás en tiempo real el audio procesado
6. **Haz clic en "DETENER"** para terminar

## Solución de Problemas

### Error: "No module named 'pyaudio'"
```bash
pip install pipwin
pipwin install pyaudio
```

### No aparecen dispositivos de audio
- Verifica que ya tienes dispositivos de audio conectados en Windows
- Ve a Configuración → Sonido → Dispositivos de entrada/salida

### Error de permisos en Windows
- Ejecuta PowerShell como Administrador
- Luego instala las dependencias

## Requisitos del Sistema

- **CPU:** Procesador moderno (Intel/AMD)
- **RAM:** Mínimo 512 MB
- **Audio:** Dispositivo de entrada y salida de audio
- **SO:** Windows 10/11

## Estructura de Archivos

```
audio_cloner.py       # Aplicación principal
requirements.txt      # Dependencias de Python
README.md            # Este archivo
```

## Ejemplos de Uso

### Caso 1: Usar micrófono para múltiples altavoces
- Entrada: Micrófono
- Salida: Altavoz + Auriculares
- Resultado: Tu voz se escucha en ambos dispositivos

### Caso 2: Duplicar audio de línea auxiliar
- Entrada: Línea de entrada de audio (aux)
- Salida: Altavoz 1 + Altavoz 2 + Grabador USB
- Resultado: Audio distribuido a múltiples destinos

## Notas Técnicas

- Latencia muy baja (< 100ms típicamente)
- Procesamiento en thread separado para no bloquear la GUI
- Formato de audio: 44.1 kHz, 16-bit PCM, 2 canales (estéreo)
- Buffer: 2048 muestras por frame

## Licencia

Uso personal y comercial permitido.

---

**¿Necesitas ayuda?** Verifica que todos los dispositivos de audio estén conectados y activos antes de iniciar la aplicación.
