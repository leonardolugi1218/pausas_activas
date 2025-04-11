# src/presentation_mode.py
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt

class PresentationMode(QWidget):
    def __init__(self, exercise_manager):
        super().__init__()
        self.exercise_manager = exercise_manager
        self.current_exercise = None
        self.setup_ui()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def setup_ui(self):
        """Configurar interfaz de modo presentación"""
        self.setGeometry(0, 0, 
                       QApplication.desktop().screenGeometry().width(),
                       QApplication.desktop().screenGeometry().height())
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Fondo semitransparente
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.7);")
        
        # Contenedor de ejercicio
        self.exercise_container = QWidget()
        exercise_layout = QVBoxLayout()
        
        self.exercise_image = QLabel()
        self.exercise_image.setAlignment(Qt.AlignCenter)

class PresentationMode(QWidget):
    def __init__(self, exercise_manager):
        super().__init__()
        self.exercise_manager = exercise_manager
        self.current_exercise = None
        self.setup_ui()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
    
    def setup_ui(self):
        """Configurar interfaz de modo presentación"""
        self.setGeometry(0, 0, QApplication.desktop().screenGeometry().width(), 
                        QApplication.desktop().screenGeometry().height())
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Fondo semitransparente
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.7);")
        
        # Contenedor de ejercicio
        self.exercise_container = QWidget()
        exercise_layout = QVBoxLayout()
        
        self.exercise_image = QLabel()
        self.exercise_image.setAlignment(Qt.AlignCenter)
        
        self.exercise_title = QLabel()
        self.exercise_title.setAlignment(Qt.AlignCenter)
        self.exercise_title.setStyleSheet("color: white; font-size: 48px; font-weight: bold;")
        
        self.exercise_description = QLabel()
        self.exercise_description.setAlignment(Qt.AlignCenter)
        self.exercise_description.setStyleSheet("color: white; font-size: 36px;")
        self.exercise_description.setWordWrap(True)
        
        self.timer_label = QLabel("00:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("color: white; font-size: 72px; font-weight: bold;")
        
        exercise_layout.addWidget(self.exercise_image)
        exercise_layout.addWidget(self.exercise_title)
        exercise_layout.addWidget(self.exercise_description)
        exercise_layout.addWidget(self.timer_label)
        
        self.exercise_container.setLayout(exercise_layout)
        layout.addWidget(self.exercise_container)
        
        self.setLayout(layout)
        
        # Temporizador para rotar ejercicios
        self.rotation_timer = QTimer()
        self.rotation_timer.timeout.connect(self.next_exercise)
    
    def start_presentation(self, interval_minutes=60):
        """Iniciar modo presentación"""
        self.showFullScreen()
        self.next_exercise()
        self.rotation_timer.start(interval_minutes * 60 * 1000)  # Convertir a milisegundos
    
    def stop_presentation(self):
        """Detener modo presentación"""
        self.rotation_timer.stop()
        self.close()
    
    def next_exercise(self):
        """Mostrar siguiente ejercicio"""
        self.current_exercise = self.exercise_manager.get_random_exercise()
        if not self.current_exercise:
            return
        
        # Actualizar UI
        self.exercise_title.setText(self.current_exercise['name'])
        
        pixmap = QPixmap(f"assets/images/{self.current_exercise['image']}")
        self.exercise_image.setPixmap(pixmap.scaledToWidth(800, Qt.SmoothTransformation))
        
        self.exercise_description.setText(self.current_exercise['description'])
        
        # Iniciar temporizador de ejercicio
        self.remaining_time = self.current_exercise['duration']
        self.update_timer_display()
        
        if hasattr(self, 'exercise_timer'):
            self.exercise_timer.stop()
        
        self.exercise_timer = QTimer()
        self.exercise_timer.timeout.connect(self.update_exercise_timer)
        self.exercise_timer.start(1000)  # Actualizar cada segundo
    
    def update_exercise_timer(self):
        """Actualizar temporizador de ejercicio"""
        self.remaining_time -= 1
        self.update_timer_display()
        
        if self.remaining_time <= 0:
            self.exercise_timer.stop()
            self.next_exercise()
    
    def update_timer_display(self):
        """Actualizar visualización del temporizador"""
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")
    
    def keyPressEvent(self, event):
        """Manejar teclas para salir del modo presentación"""
        if event.key() == Qt.Key_Escape:
            self.stop_presentation()