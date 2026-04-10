import sys
import numpy as np
import sounddevice as sd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QComboBox, QSlider, QLabel, QPushButton,
                             QProgressBar, QSpinBox, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont


class AudioProcessor(QThread):
    """Thread para procesar audio en tiempo real"""
    level_signal = pyqtSignal(float)
    
    def __init__(self, input_device=None, output_device=None, volume=1.0, buffer_ms=10):
        super().__init__()
        self.input_device = input_device
        self.output_device = output_device
        self.volume = volume
        self.buffer_ms = buffer_ms
        self.running = False
        self.stream = None
        
    def audio_callback(self, indata, outdata, frames, time, status):
        """Callback para procesar audio en tiempo real"""
        if status:
            print(f"Estado: {status}")
        
        try:
            # Obtener número de canales
            input_channels = indata.shape[1]
            output_channels = outdata.shape[1]
            
            # Copiar y procesar audio
            for out_ch in range(output_channels):
                # Reutilizar canales si necesario
                in_ch = out_ch % input_channels if input_channels > 0 else 0
                
                audio_data = indata[:, in_ch].copy()
                audio_data = audio_data * self.volume
                audio_data = np.clip(audio_data, -1.0, 1.0)
                outdata[:, out_ch] = audio_data
            
            # Calcular nivel (RMS)
            level = np.sqrt(np.mean(indata ** 2))
            self.level_signal.emit(float(level))
            
        except Exception as e:
            print(f"Error en callback: {e}")
        
    def run(self):
        """Ejecutar stream de audio"""
        self.running = True
        RATE = 44100
        
        try:
            input_info = sd.query_devices(self.input_device)
            output_info = sd.query_devices(self.output_device)
            
            # Forzar al menos 2 canales incluso si reporta 0
            input_channels = max(2, int(input_info['max_input_channels']))
            output_channels = max(1, int(output_info['max_output_channels']))
            
            print(f"\n{'='*60}")
            print(f"🎵 INICIANDO AUDIO REPEATER")
            print(f"{'='*60}")
            print(f"📥 ENTRADA: [{self.input_device}] {input_info['name'].strip()}")
            print(f"             Canales: {input_channels}, SR: {int(input_info['default_samplerate'])} Hz")
            print(f"📤 SALIDA:  [{self.output_device}] {output_info['name'].strip()}")
            print(f"             Canales: {output_channels}, SR: {int(output_info['default_samplerate'])} Hz")
            print(f"{'='*60}\n")
            
            self.stream = sd.Stream(
                device=(self.input_device, self.output_device),
                samplerate=RATE,
                channels=(input_channels, output_channels),
                callback=self.audio_callback,
                latency='low',
                blocksize=int(RATE * self.buffer_ms / 1000)
            )
            
            self.stream.start()
            print("✓ Stream activo - Capturando y transmitiendo audio...\n")
            
            while self.running and self.stream.active:
                self.msleep(100)
            
            self.stream.stop()
            self.stream.close()
            print("\n✓ Stream cerrado correctamente\n")
                
        except Exception as e:
            print(f"\n✗ ERROR: {e}\n")
    
    def stop(self):
        self.running = False
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except:
                pass
        
    def update_volume(self, volume):
        self.volume = volume / 100.0


class AudioRepeaterApp(QMainWindow):
    """Aplicación Audio Repeater Pro"""
    
    def __init__(self):
        super().__init__()
        self.audio_processor = None
        self.init_ui()
        
    def init_ui(self):
        """Inicializar interfaz"""
        self.setWindowTitle('Audio Repeater Pro')
        self.setGeometry(100, 100, 550, 450)
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
                font-size: 10px;
            }
            QSlider::groove:horizontal {
                background: #3c3c3c;
                height: 6px;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                width: 12px;
            }
            QPushButton {
                background-color: #464646;
                color: #e0e0e0;
                border: 1px solid #555;
                padding: 8px 20px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # INPUT
        input_layout = QHBoxLayout()
        input_label = QLabel('Input Device')
        input_label.setMinimumWidth(120)
        self.input_combo = QComboBox()
        self.load_input_devices()
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_combo, 1)
        main_layout.addLayout(input_layout)
        
        # OUTPUT
        output_layout = QHBoxLayout()
        output_label = QLabel('Output Device')
        output_label.setMinimumWidth(120)
        self.output_combo = QComboBox()
        self.load_output_devices()
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_combo, 1)
        main_layout.addLayout(output_layout)
        
        # FORMAT
        format_layout = QHBoxLayout()
        format_label = QLabel('Stream Format')
        format_label.setMinimumWidth(120)
        self.format_combo = QComboBox()
        self.format_combo.addItems(['Direct Streaming', 'PCM 16-bit', 'PCM 24-bit', 'PCM 32-bit'])
        format_info = QLabel('44.1kHz 2Ch 32Bit')
        format_info.setStyleSheet("color: #888; font-size: 9px;")
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo, 1)
        format_layout.addWidget(format_info)
        main_layout.addLayout(format_layout)
        
        # BUFFER
        buffer_layout = QHBoxLayout()
        buffer_label = QLabel('Buffer')
        buffer_label.setMinimumWidth(120)
        self.buffer_spin = QSpinBox()
        self.buffer_spin.setMinimum(5)
        self.buffer_spin.setMaximum(500)
        self.buffer_spin.setValue(10)
        self.buffer_spin.setSuffix(' ms')
        buffer_layout.addWidget(buffer_label)
        buffer_layout.addWidget(self.buffer_spin, 1)
        main_layout.addLayout(buffer_layout)
        
        # GAIN
        gain_layout = QHBoxLayout()
        gain_label = QLabel('Gain')
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
        
        # LEVEL
        level_label = QLabel('Level')
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
        
        main_layout.addStretch()
        
        # BUTTONS
        button_layout = QHBoxLayout()
        
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
        """)
        self.start_button.clicked.connect(self.toggle_audio)
        
        button_layout.addStretch()
        button_layout.addWidget(self.start_button)
        main_layout.addLayout(button_layout)
        
        central_widget.setLayout(main_layout)
        
        self.level_timer = QTimer()
        self.level_timer.timeout.connect(self.animate_level)
        self.level_decay = 0
    
    def load_input_devices(self):
        """Cargar dispositivos - priorizando Realtek Digital Output"""
        self.input_combo.clear()
        devices = sd.query_devices()
        
        realtek_digital_index = None
        
        for i in range(len(devices)):
            name = devices[i]['name'].strip()
            
            # Buscar Realtek Digital Output PRIMERO
            if 'Realtek Digital Output' in name:
                display_name = f"[{i}] {name} ← ENTRADA PRINCIPAL"
                self.input_combo.addItem(display_name, userData=i)
                if realtek_digital_index is None:
                    realtek_digital_index = i
            # Luego agregar otros dispositivos con entrada
            elif devices[i]['max_input_channels'] > 0:
                display_name = f"[{i}] {name}"
                self.input_combo.addItem(display_name, userData=i)
        
        # Preseleccionar Realtek Digital Output si existe
        if realtek_digital_index is not None:
            self.input_combo.setCurrentIndex(self.input_combo.findData(realtek_digital_index))
    
    def load_output_devices(self):
        """Cargar SOLO dispositivos reales de salida"""
        self.output_combo.clear()
        devices = sd.query_devices()
        
        realtek_index = None
        
        for i in range(len(devices)):
            if devices[i]['max_output_channels'] > 0:
                name = devices[i]['name'].strip()
                display_name = f"[{i}] {name}"
                
                # Marcar Realtek principal
                if 'Realtek(R) Audio' in name and realtek_index is None:
                    display_name += " ← Salida Principal"
                    realtek_index = i
                
                self.output_combo.addItem(display_name, userData=i)
        
        # Preseleccionar Realtek si existe
        if realtek_index is not None:
            self.output_combo.setCurrentIndex(self.output_combo.findData(realtek_index))
    
    def on_gain_changed(self, value):
        self.gain_label_value.setText(f'{value} %')
        if self.audio_processor:
            self.audio_processor.update_volume(value)
    
    def animate_level(self):
        self.level_decay -= 5
        if self.level_decay < 0:
            self.level_decay = 0
        self.level_bar.setValue(int(self.level_decay))
    
    def on_level_updated(self, level):
        db = 20 * np.log10(level + 0.0001)
        db = np.clip(db, -60, 0)
        normalized = (db + 60) / 60 * 100
        self.level_decay = normalized
        self.level_bar.setValue(int(normalized))
    
    def toggle_audio(self):
        if self.audio_processor is None or not self.audio_processor.isRunning():
            input_device = self.input_combo.currentData()
            output_device = self.output_combo.currentData()
            
            if input_device is None or output_device is None:
                QMessageBox.warning(self, "Error", "Selecciona dispositivos válidos")
                return
            
            gain = self.gain_slider.value()
            buffer_ms = self.buffer_spin.value()
            
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
            """)
            self.input_combo.setEnabled(False)
            self.output_combo.setEnabled(False)
            self.level_timer.start(50)
        else:
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
            """)
            self.input_combo.setEnabled(True)
            self.output_combo.setEnabled(True)
            self.level_timer.stop()
    
    def closeEvent(self, event):
        if self.audio_processor:
            self.audio_processor.stop()
            self.audio_processor.wait()
        self.level_timer.stop()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AudioRepeaterApp()
    window.show()
    sys.exit(app.exec_())
