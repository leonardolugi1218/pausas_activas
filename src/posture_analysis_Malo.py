import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, QMutex


def create_posture_analyzer(self):
    """Crea un analizador de postura adecuado según las dependencias disponibles"""
    
    class PostureAnalyzerStub(QObject):
        """Clase interna para simular el análisis de postura"""
        posture_alert = pyqtSignal(str)
        frame_processed = pyqtSignal(np.ndarray)
        
        def __init__(self):
            super().__init__()
            self.is_running = False
            self.timer = QTimer()
            self.timer.timeout.connect(self.generate_frame)
            self.posture_states = ["good", "bad"]
            self.message = "¡Endereza tu espalda!"
        
        def start(self):
            self.is_running = True
            self.timer.start(2000)  # Actualizar cada 2 segundos
        
        def stop(self):
            self.is_running = False
            self.timer.stop()
        
        def generate_frame(self):
            """Generar un frame simulado con estado aleatorio"""
            state = random.choice(self.posture_states)
            color = (0, 255, 0) if state == "good" else (0, 0, 255)  # Verde o rojo
            
            # Crear imagen simulada
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.rectangle(frame, (100, 100), (540, 380), color, -1)
            
            # Emitir señales
            self.frame_processed.emit(frame)
            if state == "bad":
                self.posture_alert.emit(self.message)

    try:
        from posture_analysis import PostureAnalyzer
        print("Usando analizador de postura completo")
        return PostureAnalyzer()
    except ImportError:
        print("Usando simulador de postura - Dependencias no disponibles")
        return PostureAnalyzerStub()