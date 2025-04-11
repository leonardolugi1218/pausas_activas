# src/exercise_timer.py
from PyQt5.QtCore import QTimer, QObject, pyqtSignal

class ExerciseTimer(QObject):
    time_updated = pyqtSignal(int)  # Tiempo restante en segundos
    timer_finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.remaining_time = 0
        self.is_running = False
    
    def start(self, duration):
        """Iniciar temporizador con duración en segundos"""
        self.remaining_time = duration
        self.is_running = True
        self.timer.start(1000)  # Actualizar cada segundo
        self.time_updated.emit(self.remaining_time)
    
    def stop(self):
        """Detener temporizador"""
        self.timer.stop()
        self.is_running = False
    
    def update_time(self):
        """Actualizar tiempo restante"""
        self.remaining_time -= 1
        self.time_updated.emit(self.remaining_time)
        
        if self.remaining_time <= 0:
            self.stop()
            self.timer_finished.emit()
    
    def get_remaining_time(self):
        """Obtener tiempo restante"""
        return self.remaining_time
    
    def format_time(self, seconds):
        """Formatear segundos a MM:SS"""
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"