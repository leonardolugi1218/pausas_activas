# src/custom_exercises.py
import json
import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, QSpinBox, 
    QComboBox, QPushButton, QListWidget, QMessageBox, QInputDialog,
    QHBoxLayout, QLabel, QFileDialog, QListWidgetItem
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QPixmap


class CustomExerciseManager(QObject):
    exercises_updated = pyqtSignal()  # Señal emitida cuando los ejercicios cambian
    
    def __init__(self):
        super().__init__()
        self.exercises_dir = Path.home() / ".pausas_activas" / "custom_exercises"
        self.exercises_dir.mkdir(parents=True, exist_ok=True)
        self.exercises_file = self.exercises_dir / "custom_exercises.json"
        self.images_dir = self.exercises_dir / "images"
        self.images_dir.mkdir(exist_ok=True)
        self.load_exercises()
    
    def load_exercises(self):
        """Cargar ejercicios personalizados desde el archivo JSON"""
        try:
            if self.exercises_file.exists():
                with open(self.exercises_file, 'r', encoding='utf-8') as f:
                    self.exercises = json.load(f)
            else:
                self.exercises = []
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error loading custom exercises: {e}")
            self.exercises = []
    
    def save_exercises(self):
        """Guardar ejercicios personalizados en el archivo JSON"""
        try:
            with open(self.exercises_file, 'w', encoding='utf-8') as f:
                json.dump(self.exercises, f, ensure_ascii=False, indent=2)
            self.exercises_updated.emit()
            return True
        except Exception as e:
            print(f"Error saving custom exercises: {e}")
            return False
    
    def add_exercise(self, exercise_data):
        """Añadir nuevo ejercicio personalizado"""
        # Asignar ID único si no viene con uno
        if 'id' not in exercise_data:
            exercise_data['id'] = f"custom_{len(self.exercises) + 1}"
        
        exercise_data['custom'] = True
        self.exercises.append(exercise_data)
        return self.save_exercises()
    
    def update_exercise(self, exercise_id, new_data):
        """Actualizar un ejercicio existente"""
        for i, ex in enumerate(self.exercises):
            if ex['id'] == exercise_id:
                # Mantener el ID y marcar como custom
                new_data['id'] = exercise_id
                new_data['custom'] = True
                self.exercises[i] = new_data
                return self.save_exercises()
        return False
    
    def delete_exercise(self, exercise_id):
        """Eliminar un ejercicio personalizado"""
        self.exercises = [ex for ex in self.exercises if ex['id'] != exercise_id]
        return self.save_exercises()
    
    def get_exercise(self, exercise_id):
        """Obtener un ejercicio por su ID"""
        for ex in self.exercises:
            if ex['id'] == exercise_id:
                return ex
        return None
    
    def get_exercises(self):
        """Obtener todos los ejercicios personalizados"""
        return self.exercises
    
    def get_exercises_by_type(self, exercise_type):
        """Obtener ejercicios filtrados por tipo"""
        return [ex for ex in self.exercises if ex['type'] == exercise_type]
    
    def import_image(self, source_path):
        """Importar una imagen al directorio de ejercicios"""
        if not os.path.exists(source_path):
            return None
        
        # Crear nombre único para la imagen
        ext = os.path.splitext(source_path)[1]
        dest_filename = f"exercise_img_{len(os.listdir(self.images_dir))}{ext}"
        dest_path = self.images_dir / dest_filename
        
        try:
            # Copiar la imagen (en un caso real usaríamos shutil.copy)
            with open(source_path, 'rb') as src, open(dest_path, 'wb') as dst:
                dst.write(src.read())
            return str(dest_path)
        except Exception as e:
            print(f"Error importing image: {e}")
            return None


class CustomExerciseDialog(QDialog):
    def __init__(self, exercise_manager, parent=None, exercise_id=None):
        super().__init__(parent)
        self.exercise_manager = exercise_manager
        self.exercise_id = exercise_id
        self.is_edit_mode = exercise_id is not None
        
        self.setWindowTitle("Editar Ejercicio" if self.is_edit_mode else "Nuevo Ejercicio")
        self.setMinimumSize(500, 600)
        
        self.init_ui()
        self.load_exercise_data()   
    
    def init_ui(self):
        """Inicializar la interfaz de usuario"""
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Nombre del ejercicio
        self.name_edit = QLineEdit()
        form_layout.addRow("Nombre:", self.name_edit)
        
        # Tipo de ejercicio
        self.type_combo = QComboBox()
        self.type_combo.addItems(["estiramiento", "fuerza", "respiración", "postura"])
        form_layout.addRow("Tipo:", self.type_combo)
        
        # Duración
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 60)
        self.duration_spin.setValue(5)
        form_layout.addRow("Duración (min):", self.duration_spin)
        
        # Descripción
        self.description_edit = QTextEdit()
        form_layout.addRow("Descripción:", self.description_edit)
        
        # Imagen del ejercicio
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(200, 200)
        self.image_label.setStyleSheet("border: 1px dashed #ccc;")
        
        self.image_button = QPushButton("Seleccionar Imagen")
        self.image_button.clicked.connect(self.select_image)
        
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.image_label)
        image_layout.addWidget(self.image_button)
        form_layout.addRow("Imagen:", image_layout)
        
        # Botones de acción
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_exercise)
        button_box.rejected.connect(self.reject)
        
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        self.setLayout(layout)
    
    def select_image(self):
        """Seleccionar una imagen para el ejercicio"""
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Imágenes (*.png *.jpg *.jpeg)")
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.load_image(selected_files[0])
    
    def load_image(self, image_path):
        """Cargar y mostrar una imagen"""
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.current_image_path = image_path
            self.image_label.setPixmap(
                pixmap.scaled(
                    self.image_label.size(), 
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )
    
    def load_exercise_data(self):
        """Cargar datos del ejercicio si está en modo edición"""
        if self.is_edit_mode:
            exercise = self.exercise_manager.get_exercise(self.exercise_id)
            if exercise:
                self.name_edit.setText(exercise.get('name', ''))
                self.type_combo.setCurrentText(exercise.get('type', 'estiramiento'))
                self.duration_spin.setValue(exercise.get('duration', 5))
                self.description_edit.setPlainText(exercise.get('description', ''))
                
                if 'image_path' in exercise:
                    self.load_image(exercise['image_path'])
    
    def save_exercise(self):
        """Guardar el ejercicio"""
        name = self.name_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        
        if not name:
            QMessageBox.warning(self, "Error", "El nombre del ejercicio es requerido")
            return
        
        if not description:
            QMessageBox.warning(self, "Error", "La descripción del ejercicio es requerida")
            return
        
        exercise_data = {
            'name': name,
            'type': self.type_combo.currentText(),
            'duration': self.duration_spin.value(),
            'description': description,
        }
        
        if hasattr(self, 'current_image_path'):
            exercise_data['image_path'] = self.current_image_path
        
        if self.is_edit_mode:
            success = self.exercise_manager.update_exercise(self.exercise_id, exercise_data)
        else:
            success = self.exercise_manager.add_exercise(exercise_data)
        
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "No se pudo guardar el ejercicio")


class CustomExercisesWindow(QDialog):
    def __init__(self, exercise_manager, parent=None):
        super().__init__(parent)
        self.exercise_manager = exercise_manager
        self.setWindowTitle("Ejercicios Personalizados")
        self.setMinimumSize(600, 400)
        
        self.init_ui()
        self.load_exercises()
    
    def init_ui(self):
        """Inicializar la interfaz de usuario"""
        layout = QVBoxLayout()
        
        # Lista de ejercicios
        self.exercises_list = QListWidget()
        self.exercises_list.itemDoubleClicked.connect(self.edit_exercise)
        layout.addWidget(self.exercises_list)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton(QIcon(":/icons/add.png"), "Añadir")
        self.add_button.clicked.connect(self.add_exercise)
        
        self.edit_button = QPushButton(QIcon(":/icons/edit.png"), "Editar")
        self.edit_button.clicked.connect(self.edit_selected_exercise)
        
        self.delete_button = QPushButton(QIcon(":/icons/delete.png"), "Eliminar")
        self.delete_button.clicked.connect(self.delete_exercise)
        
        self.import_button = QPushButton(QIcon(":/icons/import.png"), "Importar")
        self.import_button.clicked.connect(self.import_exercises)
        
        self.export_button = QPushButton(QIcon(":/icons/export.png"), "Exportar")
        self.export_button.clicked.connect(self.export_exercises)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.export_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_exercises(self):
        """Cargar la lista de ejercicios"""
        self.exercises_list.clear()
        for exercise in self.exercise_manager.get_exercises():
            item = QListWidgetItem(exercise['name'])
            item.setData(Qt.UserRole, exercise['id'])
            self.exercises_list.addItem(item)
    
    def add_exercise(self):
        """Añadir un nuevo ejercicio"""
        dialog = CustomExerciseDialog(self.exercise_manager, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_exercises()
    
    def edit_selected_exercise(self):
        """Editar el ejercicio seleccionado"""
        selected = self.exercises_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Error", "Seleccione un ejercicio para editar")
            return
        
        self.edit_exercise(selected)
    
    def edit_exercise(self, item):
        """Editar un ejercicio específico"""
        exercise_id = item.data(Qt.UserRole)
        dialog = CustomExerciseDialog(self.exercise_manager, self, exercise_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_exercises()
    
    def delete_exercise(self):
        """Eliminar el ejercicio seleccionado"""
        selected = self.exercises_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Error", "Seleccione un ejercicio para eliminar")
            return
        
        exercise_id = selected.data(Qt.UserRole)
        exercise_name = selected.text()
        
        confirm = QMessageBox.question(
            self, "Confirmar", 
            f"¿Está seguro de eliminar el ejercicio '{exercise_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            if self.exercise_manager.delete_exercise(exercise_id):
                self.load_exercises()
            else:
                QMessageBox.critical(self, "Error", "No se pudo eliminar el ejercicio")
    
    def import_exercises(self):
        """Importar ejercicios desde un archivo"""
        # Implementar lógica de importación
        pass
    
    def export_exercises(self):
        """Exportar ejercicios a un archivo"""
        # Implementar lógica de exportación
        pass