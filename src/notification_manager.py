# src/notification_manager.py
import platform
from plyer import notification
from PyQt5.QtCore import QObject, pyqtSignal
from playsound import playsound

class NotificationManager(QObject):
    def __init__(self, config):
        super().__init__()
        self.config = config
    
    def show_notification(self, title, message, sound=True):
        """Mostrar notificación del sistema"""
        try:
            # Mostrar notificación visual
            notification.notify(
                title=title,
                message=message,
                app_name="Pausas Activas",
                timeout=10
            )
            
            # Reproducir sonido si está habilitado
            if sound and self.config.getboolean("DEFAULT", "play_sounds"):
                sound_file = self.config.get("DEFAULT", "notification_sound")
                playsound(f"assets/sounds/{sound_file}.mp3")
        
        except Exception as e:
            print(f"Error showing notification: {e}")
    
    def show_exercise_notification(self, exercise_name):
        """Mostrar notificación para ejercicio"""
        title = "¡Hora de una pausa activa!"
        message = f"Es hora de hacer: {exercise_name}\nTómate 5 minutos para estirarte."
        self.show_notification(title, message)
    
    def show_reminder_notification(self):
        """Mostrar recordatorio genérico"""
        title = "Recuerda moverte"
        message = "Llevas mucho tiempo sentado. Levántate y estira las piernas."
        self.show_notification(title, message)