# src/social_sharing.py
import webbrowser
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton

class SocialSharing:
    def __init__(self, stats):
        self.stats = stats
    
    def share_stats(self, platform):
        """Compartir estadísticas en la plataforma seleccionada"""
        message = self.build_share_message()
        
        if platform == "twitter":
            url = f"https://twitter.com/intent/tweet?text={message}"
        elif platform == "facebook":
            url = f"https://www.facebook.com/sharer/sharer.php?u=https://pausasactivas.example.com&quote={message}"
        elif platform == "linkedin":
            url = f"https://www.linkedin.com/sharing/share-offsite/?url=https://pausasactivas.example.com&summary={message}"
        else:
            return False
        
        webbrowser.open(url)
        return True
    
    def build_share_message(self):
        """Construir mensaje para compartir"""
        total_exercises = self.stats.get("lifetime_sessions", 0)
        current_streak = self.stats.get("current_streak", 0)
        
        return (
            f"¡He completado {total_exercises} pausas activas con Pausas Activas Profesional! "
            f"Mi racha actual es de {current_streak} días. "
            "#PausasActivas #SaludLaboral"
        )

# Integración con MainWindow
class MainWindow(QMainWindow):
    # ... (métodos existentes)
    
    def share_to_social(self):
        """Compartir estadísticas en redes sociales"""
        stats = self.stats_tracker.get_lifetime_stats()
        sharer = SocialSharing(stats)
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Compartir en Redes Sociales")
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Seleccione la plataforma para compartir:"))
        
        platform_combo = QComboBox()
        platform_combo.addItem("Twitter", "twitter")
        platform_combo.addItem("Facebook", "facebook")
        platform_combo.addItem("LinkedIn", "linkedin")
        
        share_button = QPushButton("Compartir")
        share_button.clicked.connect(lambda: self.do_share(sharer, platform_combo.currentData(), dialog))
        
        layout.addWidget(platform_combo)
        layout.addWidget(share_button)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def do_share(self, sharer, platform, dialog):
        """Realizar acción de compartir"""
        if sharer.share_stats(platform):
            dialog.accept()
        else:
            QMessageBox.warning(self, "Error", "No se pudo compartir en la plataforma seleccionada")