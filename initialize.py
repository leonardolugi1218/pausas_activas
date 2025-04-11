import os
from pathlib import Path
import json
from utils import get_app_folder

def initialize_project():
    # Crear estructura de directorios
    assets_folders = ["data", "images", "icons", "sounds"]
    for folder in assets_folders:
        os.makedirs(f"assets/{folder}", exist_ok=True)
    
    # Crear archivo de ejercicios básico si no existe
    exercises_path = "assets/data/exercises.json"
    if not os.path.exists(exercises_path):
        basic_exercises = [
            {
                "id": "neck_stretch",
                "name": "Estiramiento de cuello",
                "description": "Incline su cabeza hacia un lado\nMantenga por 10 segundos\nRepita del otro lado",
                "type": "stretch",
                "duration": 30,
                "image": "neck_stretch.png",
                "video": "neck_stretch.mp4",
                "difficulty": "fácil"
            }
        ]
        with open(exercises_path, 'w', encoding='utf-8') as f:
            json.dump(basic_exercises, f, ensure_ascii=False, indent=2)
    
    # Crear archivo de configuración
    from utils import load_config, save_config
    config = load_config()
    save_config(config)
    
    print("Inicialización completada. Estructura creada:")
    print(f"- Configuración en: {get_app_folder()}")
    print("- Assets en: assets/")

if __name__ == "__main__":
    initialize_project()