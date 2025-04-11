# src/scheduler.py
import time
from threading import Thread
from datetime import datetime, timedelta
from PyQt5.QtCore import QObject, pyqtSignal
import schedule
from utils import load_config

class ExerciseScheduler(QObject):
    exercise_time = pyqtSignal(str)  # Señal para indicar que es hora de un ejercicio
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.running = False
        self.thread = None
        self.update_intervals()
    
    def update_intervals(self):
        """Actualizar los intervalos de trabajo y descanso"""
        self.work_interval = int(self.config.get("DEFAULT", "work_interval"))
        self.break_interval = int(self.config.get("DEFAULT", "break_interval"))
        
        # Limpiar programación anterior
        schedule.clear()
        
        # Programar pausas cada X minutos
        schedule.every(self.work_interval).minutes.do(
            self.trigger_exercise, 
            exercise_type="stretch"
        )
    
    def update_config(self, config):
        """Actualizar configuración"""
        self.config = config
        self.update_intervals()
    
    def trigger_exercise(self, exercise_type):
        """Emitir señal para realizar ejercicio"""
        self.exercise_time.emit(exercise_type)
    
    def run_scheduler(self):
        """Ejecutar el planificador en un hilo"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def start(self):
        """Iniciar el planificador"""
        if not self.running:
            self.running = True
            self.thread = Thread(target=self.run_scheduler, daemon=True)
            self.thread.start()
    
    def stop(self):
        """Detener el planificador"""
        self.running = False
        if self.thread is not None:
            self.thread.join()