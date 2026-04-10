import sys
import numpy as np
import pyaudio
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QComboBox, QSlider, QLabel, QPushButton,
                             QProgressBar, QSpinBox, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont


class AudioProcessor(QThread):
    """Thread para procesar audio en tiempo real con PyAudio"""
    level_signal = pyqtSignal(float)
    
    def __init__(self, input_device=None, output_device=None, volume=1.0, buffer_ms=10):
        super().__init__()
        self.input_device = input_device
        self.output_device = output_device
        self.volume = volume
        self.buffer_ms = buffer_ms
        self.running = False
        self.stream = None
        self.pa = None
        
    def audio_callback(self, in_data, frame_count, time_info, status):
        """Callback para procesar audio en tiempo real"""
        try:
            # Convertir bytes a numpy array
            audio_data = np.frombuffer(in_data, dtype=np.float32)
            
            # Aplicar volumen
            audio_data = audio_data * self.volume
            
            # Limitar para evitar clipping
            audio_data = np.clip(audio_data, -1.0, 1.0)
            
            # Calcular nivel general (RMS)
            level = np.sqrt(np.mean(audio_data ** 2))
            self.level_signal.emit(float(level))
            
            # Retornar datos procesados
            return (audio_data.astype(np.float32).tobytes(), pyaudio.paContinue)
        except Exception as e:
            print(f"Error en callback: {e}")
            return (in_data, pyaudio.paContinue)
    
    def run(self):
        """Ejecutar stream de audio"""
        self.running = True
        RATE = 44100
        CHUNK = 2048
        CHANNELS = 2
        
        try:
            self.pa = pyaudio.PyAudio()
            
            print(f"Iniciando stream: Entrada={self.input_device}, Salida={self.output_device}")
            
            stream_created = False
            last_error = None
            
            # Intento 1: Con dispositivos especificados
            try:
                print(f"Intento 1: PyAudio Stream")
                self.stream = self.pa.open(
                    format=pyaudio.paFloat32,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=True,
                    input_device_index=self.input_device,
                    output_device_index=self.output_device,
                    frames_per_buffer=CHUNK,
                    stream_callback=self.audio_callback
                )
                stream_created = True
                print("✓ Conexión exitosa (PyAudio)")
            except Exception as e:
                last_error = e
                print(f"✗ Intento 1 falló: {e}")
            
            if not stream_created:
                print(f"✗ Error crítico: No se pudo crear stream. {last_error}")
                if self.pa:
                    self.pa.terminate()
                self.running = False
                return
            
            self.stream.start_stream()
            print("🎵 Stream iniciado correctamente - Audio siendo capturado y redirigido")
            
            # Mantener el thread activo
            while self.running and self.stream.is_active():
                self.msleep(100)
            
            self.stream.stop_stream()
            self.stream.close()
            self.pa.terminate()
            print("Stream cerrado correctamente")
                
        except Exception as e:
            print(f"Error crítico: {e}")
            if self.pa:
                self.pa.terminate()
    
    def stop(self):
        self.running = False
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
        if self.pa:
            try:
                self.pa.terminate()
            except:
                pass
        
    def update_volume(self, volume):
        self.volume = volume / 100.0
    
    def update_buffer(self, buffer_ms):
        self.buffer_ms = buffer_ms


class AudioRepeaterApp(QMainWindow):
    """Aplicación Audio Repeater Pro con PyAudio/WASAPI"""
    
    def __init__(self):
        super().__init__()
        self.audio_processor = None
        self.pa = pyaudio.PyAudio()
        self.init_ui()
        
    def init_ui(self):
        """Inicializar interfaz de usuario"""
        self.setWindowTitle('Audio Repeater Pro')
        self.setGeometry(100, 100, 500, 450)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 11px;
            }
            QComboBox, QSpinBox {
                background-color: #3c3c3c;
                color: #e0e0e0;
                border: 1px solid #555;
                padding: 5px;
                font-size: 11px;
            }
            QSlider::groove:horizontal {
                background: #3c3c3c;
                height: 6px;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                width: 12px;
                margin: -3px 0;
            }
            QPushButton {
                background-color: #464646;
                color: #e0e0e0;
                border: 1px solid #555;
                padding: 8px 20px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555;
            }
            QPushButton:pressed {
                background-color: #4CAF50;
            }
        """)
        
        # Widget principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # ===== INPUT DEVICE =====
        input_layout = QHBoxLayout()
        input_label = QLabel('Input Device')
        input_label.setMinimumWidth(120)
        self.input_combo = QComboBox()
        self.load_input_devices()
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_combo, 1)
        main_layout.addLayout(input_layout)
        
        # ===== OUTPUT DEVICE =====
        output_layout = QHBoxLayout()
        output_label = QLabel('Output Device')
        output_label.setMinimumWidth(120)
        self.output_combo = QComboBox()
        self.load_output_devices()
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_combo, 1)
        
        # Botón de advertencia
        self.warning_btn = QPushButton('⚠')
        self.warning_btn.setMaximumWidth(30)
        self.warning_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: #000;
            }
        """)
        output_layout.addWidget(self.warning_btn)
        main_layout.addLayout(output_layout)
        
        # ===== STREAM FORMAT =====
        format_layout = QHBoxLayout()
        format_label = QLabel('Stream Format')
        format_label.setMinimumWidth(120)
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            'Direct Streaming',
            'PCM 16-bit',
            'PCM 24-bit',
            'PCM 32-bit'
        ])
        format_info = QLabel('44.1kHz 2Ch 32Bit')
        format_info.setStyleSheet("color: #888; font-size: 9px;")
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo, 1)
        format_layout.addWidget(format_info)
        main_layout.addLayout(format_layout)
        
        # ===== STREAM BUFFER =====
        buffer_layout = QHBoxLayout()
        buffer_label = QLabel('Stream Buffer')
        buffer_label.setMinimumWidth(120)
        self.buffer_spin = QSpinBox()
        self.buffer_spin.setMinimum(5)
        self.buffer_spin.setMaximum(500)
        self.buffer_spin.setValue(10)
        self.buffer_spin.setSuffix(' Milliseconds')
        self.buffer_spin.valueChanged.connect(self.on_buffer_changed)
        
        process_btn = QPushButton('☑ Process Audio')
        process_btn.setMaximumWidth(120)
        buffer_layout.addWidget(buffer_label)
        buffer_layout.addWidget(self.buffer_spin, 1)
        buffer_layout.addWidget(process_btn)
        main_layout.addLayout(buffer_layout)
        
        # ===== STREAM GAIN (VOLUMEN) =====
        gain_layout = QHBoxLayout()
        gain_label = QLabel('Stream Gain')
        gain_label.setMinimumWidth(120)
        self.gain_slider = QSlider(Qt.Horizontal)
        self.gain_slider.setMinimum(0)
        self.gain_slider.setMaximum(200)
        self.gain_slider.setValue(100)
        self.gain_slider.setTickPosition(QSlider.TicksBelow)
        self.gain_slider.setTickInterval(10)
        self.gain_slider.valueChanged.connect(self.on_gain_changed)
        
        self.gain_label_value = QLabel('100 %')
        self.gain_label_value.setMinimumWidth(40)
        gain_layout.addWidget(gain_label)
        gain_layout.addWidget(self.gain_slider, 1)
        gain_layout.addWidget(self.gain_label_value)
        main_layout.addLayout(gain_layout)
        
        # ===== STREAM LEVEL (VISUALIZADOR) =====
        level_label = QLabel('Stream Level')
        level_label.setMinimumWidth(120)
        main_layout.addWidget(level_label)
        
        self.level_bar = QProgressBar()
        self.level_bar.setMinimum(0)
        self.level_bar.setMaximum(100)
        self.level_bar.setValue(0)
        self.level_bar.setMaximumHeight(20)
        self.level_bar.setStyleSheet("""
            QProgressBar {
                background-color: #3c3c3c;
                border: 1px solid #555;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        main_layout.addWidget(self.level_bar)
        
        # ===== STREAM FX =====
        fx_layout = QHBoxLayout()
        fx_label = QLabel('Stream FX')
        fx_label.setMinimumWidth(120)
        
        self.fx_chain_btn = QPushButton('☑ FX Chain')
        self.fx_chain_btn.setMaximumWidth(100)
        
        self.bypass_btn = QPushButton('☐ Bypass FX Chain')
        self.bypass_btn.setMaximumWidth(150)
        
        fx_layout.addWidget(fx_label)
        fx_layout.addWidget(self.fx_chain_btn)
        fx_layout.addWidget(self.bypass_btn)
        fx_layout.addStretch()
        main_layout.addLayout(fx_layout)
        
        # Espacio
        main_layout.addStretch()
        
        # ===== BOTONES DE CONTROL =====
        button_layout = QHBoxLayout()
        
        self.about_button = QPushButton('About')
        self.about_button.setMaximumWidth(100)
        
        self.start_button = QPushButton('Start')
        self.start_button.setMinimumHeight(40)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.start_button.clicked.connect(self.toggle_audio)
        
        button_layout.addWidget(self.about_button)
        button_layout.addStretch()
        button_layout.addWidget(self.start_button)
        main_layout.addLayout(button_layout)
        
        central_widget.setLayout(main_layout)
        
        # Timer para actualizar nivel cuando está parado
        self.level_timer = QTimer()
        self.level_timer.timeout.connect(self.animate_level)
        self.level_decay = 0
    
    def load_input_devices(self):
        """Cargar dispositivos de entrada usando PyAudio (WASAPI en Windows)"""
        self.input_combo.clear()
        self.input_devices_map = {}
        
        device_count = self.pa.get_device_count()
        
        for i in range(device_count):
            device = self.pa.get_device_info_by_index(i)
            
            # Solo mostrar dispositivos que tengan entrada o sean "Realtek Digital"
            if device['maxInputChannels'] > 0 or 'Realtek Digital' in device['name']:
                device_name = device['name'].strip()
                display_name = f"[{i}] {device_name}"
                
                # Marcar especiales
                if 'Realtek Digital Output' in device_name:
                    display_name += " [CAPTURA DIGITAL]"
                elif 'Mezcla' in device_name or 'Stereo Mix' in device_name:
                    display_name += " [LOOPBACK]"
                elif 'Qobuz' in device_name:
                    display_name += " [QOBUZ]"
                
                self.input_combo.addItem(display_name, userData=i)
                self.input_devices_map[i] = device
        
        if self.input_combo.count() == 0:
            self.input_combo.addItem("No hay dispositivos de entrada", userData=-1)
    
    def load_output_devices(self):
        """Cargar dispositivos de salida usando PyAudio (WASAPI en Windows)"""
        self.output_combo.clear()
        self.output_devices_map = {}
        
        device_count = self.pa.get_device_count()
        realtek_audio_index = None
        qobuz_index = None
        
        for i in range(device_count):
            device = self.pa.get_device_info_by_index(i)
            
            if device['maxOutputChannels'] > 0:
                device_name = device['name'].strip()
                display_name = f"[{i}] {device_name}"
                
                # Marcar especiales
                if 'Realtek(R) Audio' in device_name and device['maxOutputChannels'] >= 2:
                    if realtek_audio_index is None:
                        display_name += " [SALIDA PRINCIPAL]"
                        realtek_audio_index = i
                
                if 'Qobuz' in device_name:
                    display_name += " [QOBUZ]"
                    if qobuz_index is None:
                        qobuz_index = i
                
                self.output_combo.addItem(display_name, userData=i)
                self.output_devices_map[i] = device
        
        # Seleccionar por defecto
        if realtek_audio_index is not None:
            self.output_combo.setCurrentIndex(self.output_combo.findData(realtek_audio_index))
        elif qobuz_index is not None:
            self.output_combo.setCurrentIndex(self.output_combo.findData(qobuz_index))
        
        if self.output_combo.count() == 0:
            self.output_combo.addItem("No hay dispositivos de salida", userData=-1)
    
    def on_gain_changed(self, value):
        """Actualizar ganancia"""
        self.gain_label_value.setText(f'{value} %')
        if self.audio_processor:
            self.audio_processor.update_volume(value)
    
    def on_buffer_changed(self, value):
        """Actualizar buffer"""
        if self.audio_processor:
            self.audio_processor.update_buffer(value)
    
    def animate_level(self):
        """Animar descenso del nivel cuando está parado"""
        self.level_decay -= 5
        if self.level_decay < 0:
            self.level_decay = 0
        self.level_bar.setValue(int(self.level_decay))
    
    def on_level_updated(self, level):
        """Actualizar barra de nivel"""
        db = 20 * np.log10(level + 0.0001)
        db = np.clip(db, -60, 0)
        normalized = (db + 60) / 60 * 100
        self.level_decay = normalized
        self.level_bar.setValue(int(normalized))
    
    def toggle_audio(self):
        """Iniciar/Detener clonación"""
        if self.audio_processor is None or not self.audio_processor.isRunning():
            # Iniciar
            input_device = self.input_combo.currentData()
            output_device = self.output_combo.currentData()
            
            # Validar
            if input_device is None or input_device < 0:
                QMessageBox.warning(self, "Error", "Selecciona un dispositivo de entrada válido")
                return
            if output_device is None or output_device < 0:
                QMessageBox.warning(self, "Error", "Selecciona un dispositivo de salida válido")
                return
            
            buffer_ms = self.buffer_spin.value()
            gain = self.gain_slider.value()
            
            print(f"Iniciando: Input={input_device}, Output={output_device}")
            
            self.audio_processor = AudioProcessor(
                input_device, 
                output_device, 
                gain / 100.0,
                buffer_ms
            )
            self.audio_processor.level_signal.connect(self.on_level_updated)
            self.audio_processor.start()
            
            self.start_button.setText('Stop')
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #da190b;
                }
            """)
            self.input_combo.setEnabled(False)
            self.output_combo.setEnabled(False)
            self.level_timer.start(50)
        else:
            # Detener
            if self.audio_processor:
                self.audio_processor.stop()
                self.audio_processor.wait()
                self.audio_processor = None
            
            self.start_button.setText('Start')
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            self.input_combo.setEnabled(True)
            self.output_combo.setEnabled(True)
            self.level_timer.stop()
    
    def closeEvent(self, event):
        """Limpiar al cerrar"""
        if self.audio_processor:
            self.audio_processor.stop()
            self.audio_processor.wait()
        self.level_timer.stop()
        self.pa.terminate()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AudioRepeaterApp()
    window.show()
    sys.exit(app.exec_())
