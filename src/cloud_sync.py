# src/cloud_sync.py
import requests
from PyQt5.QtCore import QObject, pyqtSignal, QSettings, QTimer
import json
import hashlib
from datetime import datetime

class CloudSync(QObject):
    sync_started = pyqtSignal()
    sync_completed = pyqtSignal(bool, str)  # (success, message)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.settings = QSettings("PausasActivas", "CloudSync")
        self.api_url = "https://api.pausasactivas.example.com/v1"  # URL de ejemplo
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.sync_data)
        self.load_credentials()
    
    def load_credentials(self):
        """Cargar credenciales de sincronización"""
        self.user_email = self.settings.value("user_email", "")
        self.auth_token = self.settings.value("auth_token", "")
        self.last_sync = self.settings.value("last_sync", "")
        self.auto_sync = self.settings.value("auto_sync", False, type=bool)
        self.sync_interval = self.settings.value("sync_interval", 60, type=int)  # minutos
    
    def save_credentials(self):
        """Guardar credenciales de sincronización"""
        self.settings.setValue("user_email", self.user_email)
        self.settings.setValue("auth_token", self.auth_token)
        self.settings.setValue("last_sync", self.last_sync)
        self.settings.setValue("auto_sync", self.auto_sync)
        self.settings.setValue("sync_interval", self.sync_interval)
    
    def start_auto_sync(self):
        """Iniciar sincronización automática"""
        if self.auto_sync:
            self.sync_timer.start(self.sync_interval * 60 * 1000)  # Convertir a milisegundos
    
    def stop_auto_sync(self):
        """Detener sincronización automática"""
        self.sync_timer.stop()
    
    def login(self, email, password):
        """Iniciar sesión en el servicio de nube"""
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        payload = {
            "email": email,
            "password": hashed_password
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/login",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.user_email = email
                self.auth_token = data["token"]
                self.last_sync = datetime.now().isoformat()
                self.save_credentials()
                self.start_auto_sync()
                return True, "Inicio de sesión exitoso"
            else:
                return False, "Credenciales incorrectas"
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"
    
    def sync_data(self):
        """Sincronizar datos con la nube"""
        if not self.auth_token:
            return False, "No autenticado"
        
        self.sync_started.emit()
        
        try:
            # Obtener datos locales para sincronizar
            stats = self.get_local_stats()
            settings = self.get_local_settings()
            
            # Enviar a la nube
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            payload = {
                "stats": stats,
                "settings": settings,
                "last_sync": self.last_sync
            }
            
            response = requests.put(
                f"{self.api_url}/sync",
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                self.last_sync = datetime.now().isoformat()
                self.save_credentials()
                
                # Actualizar datos locales si hay cambios remotos
                if "remote_changes" in data:
                    self.apply_remote_changes(data["remote_changes"])
                
                self.sync_completed.emit(True, "Sincronización exitosa")
                return True, "Sincronización exitosa"
            else:
                self.sync_completed.emit(False, "Error en la sincronización")
                return False, "Error en el servidor"
        except Exception as e:
            self.sync_completed.emit(False, f"Error de conexión: {str(e)}")
            return False, f"Error de conexión: {str(e)}"
    
    def get_local_stats(self):
        """Obtener estadísticas locales para sincronizar"""
        # Implementar según tu estructura de datos
        return {}
    
    def get_local_settings(self):
        """Obtener configuración local para sincronizar"""
        # Implementar según tu estructura de datos
        return {}
    
    def apply_remote_changes(self, changes):
        """Aplicar cambios desde la nube"""
        # Implementar según tu estructura de datos
        pass