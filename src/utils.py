import os
from configparser import ConfigParser
from pathlib import Path
from PyQt5.QtWidgets import QMessageBox

def get_app_folder():
    """Obtener y crear la carpeta de la aplicación con todos los subdirectorios necesarios"""
    app_folder = Path.home() / ".pausas_activas"
    
    try:
        # Crear estructura completa de directorios
        os.makedirs(app_folder / "config", exist_ok=True)
        os.makedirs(app_folder / "database", exist_ok=True)
        return app_folder
    except Exception as e:
        QMessageBox.critical(None, "Error", f"No se pudo crear la carpeta de la aplicación: {str(e)}")
        return None

def load_config():
    """Cargar o crear configuración con manejo robusto de errores"""
    config = ConfigParser()
    
    # Configuración por defecto
    default_config = {
        "language": "es",
        "theme": "light",
        "notification_sound": "default",
        "work_interval": "50",
        "break_interval": "10",
        "minimize_to_tray": "true",
        "start_on_login": "false"
    }
    config["DEFAULT"] = default_config
    
    app_folder = get_app_folder()
    if app_folder is None:
        return config
    
    config_path = app_folder / "config" / "settings.ini"
    
    try:
        if config_path.exists():
            config.read(config_path)
        else:
            # Asegurarse de que el directorio existe
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                config.write(f)
    except Exception as e:
        QMessageBox.warning(None, "Advertencia", 
                          f"No se pudo carbar/crear configuración: {str(e)}\nSe usarán valores por defecto.")
    
    return config

def save_config(config):
    """Guardar configuración con manejo de errores"""
    app_folder = get_app_folder()
    if app_folder is None:
        return False
    
    config_path = app_folder / "config" / "settings.ini"
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            config.write(f)
        return True
    except Exception as e:
        QMessageBox.critical(None, "Error", f"No se pudo guardar la configuración: {str(e)}")
        return False