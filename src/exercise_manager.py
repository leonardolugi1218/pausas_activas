# src/exercise_manager.py
import json
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal
import random
from PyQt5.QtCore import QObject

class ExerciseManager(QObject):
    exercises_loaded = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.exercises = []
        self.load_exercises()
    
    def load_exercises(self):
        """Cargar ejercicios desde archivo JSON"""
        exercises_file = Path("assets/data/exercises.json")
        
        try:
            with open(exercises_file, "r", encoding="utf-8") as f:
                self.exercises = json.load(f)
            self.exercises_loaded.emit()
        except Exception as e:
            print(f"Error loading exercises: {e}")
            # Cargar ejercicios por defecto
            self.exercises = [
                {
                    "id": "neck_stretch",
                    "name": "Estiramiento de cuello",
                    "description": "Incline su cabeza hacia un lado y mantenga por 10 segundos. Repita del otro lado.",
                    "type": "stretch",
                    "duration": 30,
                    "image": "neck_stretch.png",
                    "video": "neck_stretch.mp4"
                },
                # Más ejercicios...
            ]
    
    def get_exercise(self, exercise_id):
        """Obtener ejercicio por ID"""
        for exercise in self.exercises:
            if exercise["id"] == exercise_id:
                return exercise
        return None
    
    def get_exercises_by_type(self, exercise_type):
        """Obtener todos los ejercicios de un tipo específico"""
        return [ex for ex in self.exercises if ex["type"] == exercise_type]
    
    def get_random_exercise(self, exercise_type=None):
        """Obtener un ejercicio aleatorio"""
        if exercise_type:
            exercises = self.get_exercises_by_type(exercise_type)
            return random.choice(exercises) if exercises else None
        return random.choice(self.exercises) if self.exercises else None