# src/settings_window.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QSpinBox, QComboBox, QCheckBox, QPushButton)
from PyQt5.QtCore import Qt

class SettingsWindow(QWidget):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interfaz de configuración"""
        self.setWindowTitle("Configuración")
        self.resize(500, 400)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Intervalo de trabajo
        work_layout = QHBoxLayout()
        work_label = QLabel("Intervalo de trabajo (minutos):")
        self.work_spinbox = QSpinBox()
        self.work_spinbox.setRange(10, 120)
        self.work_spinbox.setValue(int(self.config.get("DEFAULT", "work_interval")))
        
        work_layout.addWidget(work_label)
        work_layout.addWidget(self.work_spinbox)
        layout.addLayout(work_layout)
        
        # Intervalo de descanso
        break_layout = QHBoxLayout()
        break_label = QLabel("Intervalo de descanso (minutos):")
        self.break_spinbox = QSpinBox()
        self.break_spinbox.setRange(1, 30)
        self.break_spinbox.setValue(int(self.config.get("DEFAULT", "break_interval")))
        
        break_layout.addWidget(break_label)
        break_layout.addWidget(self.break_spinbox)
        layout.addLayout(break_layout)
        
        # Tema
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Tema:")
        self.theme_combobox = QComboBox()
        self.theme_combobox.addItems(["Claro", "Oscuro"])
        current_theme = self.config.get("DEFAULT", "theme")
        self.theme_combobox.setCurrentIndex(0 if current_theme == "light" else 1)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combobox)
        layout.addLayout(theme_layout)
        
        # Opciones adicionales
        self.minimize_checkbox = QCheckBox("Minimizar a la bandeja al cerrar")
        self.minimize_checkbox.setChecked(self.config.getboolean("DEFAULT", "minimize_to_tray"))
        
        self.startup_checkbox = QCheckBox("Iniciar con el sistema")
        self.startup_checkbox.setChecked(self.config.getboolean("DEFAULT", "start_on_login"))
        
        layout.addWidget(self.minimize_checkbox)
        layout.addWidget(self.startup_checkbox)
        layout.addStretch()
        
        # Botones
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.close)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
    
    def save_settings(self):
        """Guardar configuración"""
        self.config["DEFAULT"]["work_interval"] = str(self.work_spinbox.value())
        self.config["DEFAULT"]["break_interval"] = str(self.break_spinbox.value())
        self.config["DEFAULT"]["theme"] = "light" if self.theme_combobox.currentIndex() == 0 else "dark"
        self.config["DEFAULT"]["minimize_to_tray"] = "true" if self.minimize_checkbox.isChecked() else "false"
        self.config["DEFAULT"]["start_on_login"] = "true" if self.startup_checkbox.isChecked() else "false"
        
        # TODO: Implementar guardado real de configuración
        # y aplicar cambios en tiempo real
        
        self.close()