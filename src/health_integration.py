# src/health_integration.py
import requests
from datetime import datetime, timedelta
import json
import os
from PyQt5.QtCore import QObject, pyqtSignal, QSettings
import sys
from PyQt5.QtCore import QObject, pyqtSignal

class HealthIntegration(QObject):
    sync_complete = pyqtSignal(dict)  # Datos de salud sincronizados
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.settings = QSettings("PausasActivas", "HealthIntegration")
        self.load_credentials()
    
    def load_credentials(self):
        """Cargar credenciales de API"""
        self.google_fit_credentials = {
            "client_id": self.settings.value("google_fit/client_id", ""),
            "client_secret": self.settings.value("google_fit/client_secret", ""),
            "access_token": self.settings.value("google_fit/access_token", ""),
            "refresh_token": self.settings.value("google_fit/refresh_token", "")
        }
        
        # Para Apple Health, generalmente se usa acceso local
        self.apple_health_authorized = self.settings.value("apple_health/authorized", False, type=bool)
    
    def save_credentials(self):
        """Guardar credenciales de API"""
        self.settings.setValue("google_fit/client_id", self.google_fit_credentials["client_id"])
        self.settings.setValue("google_fit/client_secret", self.google_fit_credentials["client_secret"])
        self.settings.setValue("google_fit/access_token", self.google_fit_credentials["access_token"])
        self.settings.setValue("google_fit/refresh_token", self.google_fit_credentials["refresh_token"])
        self.settings.setValue("apple_health/authorized", self.apple_health_authorized)
    
    def authorize_google_fit(self, auth_code):
        """Autorizar con Google Fit"""
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": auth_code,
            "client_id": self.google_fit_credentials["client_id"],
            "client_secret": self.google_fit_credentials["client_secret"],
            "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
            "grant_type": "authorization_code"
        }
        
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            tokens = response.json()
            self.google_fit_credentials["access_token"] = tokens["access_token"]
            self.google_fit_credentials["refresh_token"] = tokens["refresh_token"]
            self.save_credentials()
            return True
        return False
    
    def refresh_google_token(self):
        """Refrescar token de Google"""
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "refresh_token": self.google_fit_credentials["refresh_token"],
            "client_id": self.google_fit_credentials["client_id"],
            "client_secret": self.google_fit_credentials["client_secret"],
            "grant_type": "refresh_token"
        }
        
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            tokens = response.json()
            self.google_fit_credentials["access_token"] = tokens["access_token"]
            self.save_credentials()
            return True
        return False
    
    def get_google_fit_data(self, days=7):
        """Obtener datos de Google Fit"""
        if not self.google_fit_credentials["access_token"]:
            return None
        
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # Convertir a nanosegundos desde la época
        start_ns = int(start_time.timestamp()) * 10**9
        end_ns = int(end_time.timestamp()) * 10**9
        
        headers = {
            "Authorization": f"Bearer {self.google_fit_credentials['access_token']}",
            "Content-Type": "application/json"
        }
        
        # Obtener pasos
        steps_url = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"
        steps_body = {
            "aggregateBy": [{
                "dataTypeName": "com.google.step_count.delta",
                "dataSourceId": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
            }],
            "bucketByTime": {"durationMillis": 86400000},  # 1 día
            "startTimeMillis": start_ns // 10**6,
            "endTimeMillis": end_ns // 10**6
        }
        
        try:
            response = requests.post(steps_url, headers=headers, json=steps_body)
            if response.status_code == 200:
                data = response.json()
                return self.process_fit_data(data)
            elif response.status_code == 401:  # Token expirado
                if self.refresh_google_token():
                    return self.get_google_fit_data(days)
        except Exception as e:
            print(f"Error fetching Google Fit data: {e}")
        
        return None
    
    def process_fit_data(self, data):
        """Procesar datos de Google Fit"""
        processed = {
            "steps": [],
            "heart_rate": [],
            "activity": []
        }
        
        for bucket in data.get("bucket", []):
            date = datetime.fromtimestamp(int(bucket["startTimeMillis"])/1000)
            for dataset in bucket.get("dataset", []):
                if dataset["dataSourceId"] == "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps":
                    for point in dataset.get("point", []):
                        processed["steps"].append({
                            "date": date,
                            "value": int(point.get("value", [{}])[0].get("intVal", 0))
                        })
        
        return processed
    
    def sync_apple_health(self):
        """Sincronizar con Apple Health (solo macOS)"""
        # En macOS, esto requeriría usar pyobjc para acceder a HealthKit
        # Esta es una implementación simplificada
        if not self.apple_health_authorized:
            return None
        
        # En una implementación real, aquí se usaría HealthKit
        return {
            "steps": [],
            "heart_rate": [],
            "activity": []
        }
    
    def sync_health_data(self):
        """Sincronizar datos de salud según la plataforma"""
        health_data = {}
        
        if sys.platform == "darwin" and self.apple_health_authorized:
            health_data = self.sync_apple_health()
        elif self.google_fit_credentials["access_token"]:
            health_data = self.get_google_fit_data()
        
        if health_data:
            self.sync_complete.emit(health_data)
        
        return health_data