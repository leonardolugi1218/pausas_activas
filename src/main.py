# main.py
import sys
from PyQt5.QtWidgets import QApplication
from app_window import MainWindow
from utils import load_config

def main():
    app = QApplication(sys.argv)
    
    # Configuración inicial de la aplicación
    app.setApplicationName("Pausas Activas Profesional")
    app.setApplicationDisplayName("Pausas Activas Profesional")
    app.setApplicationVersion("1.0.0")
    
    config = load_config()
    
    # Pasar la configuración al crear la ventana
    window = MainWindow(config)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()