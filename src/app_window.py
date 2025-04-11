import sys
import os
import random
import sqlite3
import csv
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import cv2
import random
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

from PyQt5.QtWidgets import (
    QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QLabel, QPushButton,
    QStatusBar, QToolBar, QAction, QListWidget, QDialog, QMessageBox,
    QCalendarWidget, QTabWidget, QComboBox, QLineEdit, QSpinBox, QCheckBox,
    QDialogButtonBox, QFormLayout, QHBoxLayout, QGroupBox, QDateEdit,
    QListWidgetItem, QTextEdit, QSystemTrayIcon, QMenu, QApplication,
    QFileDialog, QTextBrowser, QInputDialog
)
from PyQt5.QtCore import (
    Qt, pyqtSignal, QObject, QTimer, QSize, QDateTime, QDate, QTime,
    QSettings, QMutex, QThread
)
from PyQt5.QtGui import (
    QIcon, QPixmap, QImage, QPainter, QTextDocument, QFont, QColor
)
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtChart import QChart, QChartView, QLineSeries



# Importar otros módulos de la aplicación
from exercise_manager import ExerciseManager
from stats_tracker import StatsTracker
from scheduler import ExerciseScheduler 
from notification_manager import NotificationManager
from calendar_integration import CalendarIntegration
from health_integration import HealthIntegration
from cloud_sync import CloudSync
from report_generator import ReportGenerator
from achievements import AchievementSystem
from utils import load_config, save_config


class MainWindow(QMainWindow):
    config_changed = pyqtSignal()
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        
        # Inicializar módulos principales
        self.exercise_manager = ExerciseManager()
        self.stats_tracker = StatsTracker()
        self.notification_manager = NotificationManager(config)
        self.calendar_integration = CalendarIntegration(config)
        self.health_integration = HealthIntegration(config)
        self.posture_analyzer = self.PostureAnalyzerStub()
        #self.posture_analyzer = self.create_posture_analyzer()  # Cambiado esta línea
        self.cloud_sync = CloudSync(config)
        self.report_generator = ReportGenerator()
        self.achievement_system = AchievementSystem()
        self.scheduler = ExerciseScheduler(config)
        
        # Configuración inicial de la ventana
        self.setWindowTitle("Pausas Activas Profesional")
        self.setMinimumSize(800, 600)
        
        # Configurar icono
        self.setWindowIcon(QIcon("assets/icons/app_icon.png"))
        
        # Inicializar UI
        self.init_ui()
        self.setup_connections()
        
        # Cargar configuración
        self.load_settings()
        
        # Iniciar servicios
        self.scheduler.start()
        self.start_services()
    
    def init_ui(self):
        """Inicializar toda la interfaz de usuario"""
        # Barra de menú
        self.setup_menu()
        
        # Barra de herramientas
        self.setup_toolbar()
        
        # Widget central y layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.main_layout = QVBoxLayout()
        central_widget.setLayout(self.main_layout)
        
        # Widget apilado para diferentes vistas
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        # Configurar páginas
        self.setup_home_page()
        self.setup_exercise_page()
        self.setup_settings_page()
        self.setup_stats_page()
        self.setup_achievements_ui()
        self.setup_calendar_ui()
        self.setup_health_ui()
        self.setup_posture_ui()
        self.setup_cloud_sync_ui()
        
        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo")
        
        # Tray icon
        self.setup_tray_icon()
    def create_posture_analyzer(self):
        """Crea un analizador de postura adecuado según las dependencias disponibles"""
        try:
            from posture_analysis import PostureAnalyzer
            print("Usando analizador de postura completo")
            return PostureAnalyzer()
        except ImportError:
            print("Usando simulador de postura - Dependencias no disponibles")
            return self.PostureAnalyzerStub()

class MainWindow(QMainWindow):
    class PostureAnalyzerStub(QObject):
        """Clase interna para simular el análisis de postura"""
        posture_alert = pyqtSignal(str)
        frame_processed = pyqtSignal(np.ndarray)
        
        def __init__(self):
            super().__init__()
            self.is_running = False
            self.timer = QTimer()
            self.timer.timeout.connect(self.generate_frame)
            self.posture_states = ["good", "bad"]
            self.message = "¡Endereza tu espalda!"
        
        def start(self):
            self.is_running = True
            self.timer.start(2000)
        
        def stop(self):
            self.is_running = False
            self.timer.stop()
        
        def generate_frame(self):
            state = random.choice(self.posture_states)
            color = (0, 255, 0) if state == "good" else (0, 0, 255)
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.rectangle(frame, (100, 100), (540, 380), color, -1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.frame_processed.emit(frame_rgb)
            if state == "bad":
                self.posture_alert.emit(self.message)

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.posture_analyzer = self.PostureAnalyzerStub()
    
    def setup_connections(self):
        """Conectar todas las señales entre componentes"""
        # Conectar scheduler
        self.scheduler.exercise_time.connect(self.show_exercise)
        
        # Conectar notificaciones
        self.notification_manager.notification_clicked.connect(self.handle_notification)
        
        # Conectar análisis postural
        self.posture_analyzer.posture_alert.connect(self.handle_posture_alert)
        self.posture_analyzer.frame_processed.connect(self.update_camera_view)
        
        # Conectar logros
        self.achievement_system.achievement_unlocked.connect(self.show_achievement_unlocked)
        
        # Conectar sincronización en nube
        self.cloud_sync.sync_started.connect(self.on_sync_started)
        self.cloud_sync.sync_completed.connect(self.on_sync_completed)
        
        # Conectar calendario
        self.calendar_integration.events_updated.connect(self.update_calendar_view)
    
    def setup_menu(self):
        """Configurar la barra de menú principal"""
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu("Archivo")
        
        report_action = QAction("Generar Reporte", self)
        report_action.triggered.connect(self.generate_report)
        file_menu.addAction(report_action)
        
        export_action = QAction("Exportar Datos", self)
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menú Configuración
        settings_menu = menubar.addMenu("Configuración")
        
        preferences_action = QAction("Preferencias", self)
        preferences_action.triggered.connect(self.show_settings)
        settings_menu.addAction(preferences_action)
        
        # Menú Ver
        self.view_menu = menubar.addMenu("Ver")
        
        presentation_action = QAction("Modo Presentación", self)
        presentation_action.triggered.connect(self.toggle_presentation_mode)
        self.view_menu.addAction(presentation_action)
        
        # Menú Herramientas
        tools_menu = menubar.addMenu("Herramientas")
        
        posture_action = QAction("Monitor de Postura", self)
        posture_action.triggered.connect(self.show_posture_monitor)
        tools_menu.addAction(posture_action)
        
        health_action = QAction("Integración de Salud", self)
        health_action.triggered.connect(self.show_health_integration)
        tools_menu.addAction(health_action)
        
        sync_action = QAction("Sincronización en Nube", self)
        sync_action.triggered.connect(self.show_cloud_sync)
        tools_menu.addAction(sync_action)
        
        # Menú Ayuda
        help_menu = menubar.addMenu("Ayuda")
        
        about_action = QAction("Acerca de", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def show_posture_monitor(self):
        """Mostrar el monitor de postura"""
        if not hasattr(self, 'posture_dialog'):
            self.setup_posture_ui()
        self.posture_dialog.exec_()
    
    def setup_toolbar(self):
        """Configurar la barra de herramientas"""
        toolbar = QToolBar("Barra de herramientas principal")
        self.addToolBar(toolbar)
        
        # Acciones principales
        home_action = QAction(QIcon("assets/icons/home.png"), "Inicio", self)
        home_action.triggered.connect(self.show_home)
        toolbar.addAction(home_action)
        
        exercise_action = QAction(QIcon("assets/icons/exercise.png"), "Ejercicios", self)
        exercise_action.triggered.connect(lambda: self.show_exercise("random"))
        toolbar.addAction(exercise_action)
        
        stats_action = QAction(QIcon("assets/icons/stats.png"), "Estadísticas", self)
        stats_action.triggered.connect(self.show_stats)
        toolbar.addAction(stats_action)
        
        achievements_action = QAction(QIcon("assets/icons/achievement.png"), "Logros", self)
        achievements_action.triggered.connect(self.show_achievements)
        toolbar.addAction(achievements_action)
        
        toolbar.addSeparator()
        
        settings_action = QAction(QIcon("assets/icons/settings.png"), "Configuración", self)
        settings_action.triggered.connect(self.show_settings)
        toolbar.addAction(settings_action)
    
    def setup_tray_icon(self):
        """Configurar el icono en la bandeja del sistema"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        
        self.tray_icon = QSystemTrayIcon(QIcon("assets/icons/tray_icon.png"), self)
        
        menu = QMenu()
        
        open_action = menu.addAction("Abrir")
        open_action.triggered.connect(self.show)
        
        exercise_action = menu.addAction("Comenzar Pausa")
        exercise_action.triggered.connect(lambda: self.show_exercise("random"))
        
        menu.addSeparator()
        
        exit_action = menu.addAction("Salir")
        exit_action.triggered.connect(self.quit_app)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def tray_icon_activated(self, reason):
        """Manejar clics en el icono de la bandeja"""
        if reason == QSystemTrayIcon.Trigger:
            self.show()
    
    # [Aquí irían todos los demás métodos setup_*_page y setup_*_ui]
    # [Y los métodos de manejo de eventos como show_exercise, show_settings, etc.]
    
    def closeEvent(self, event):
        """Manejar el cierre de la ventana"""
        if self.config.getboolean("DEFAULT", "minimize_to_tray", fallback=True):
            self.hide()
            event.ignore()
        else:
            self.quit_app()
            event.accept()
    
    def quit_app(self):
        """Salir de la aplicación correctamente"""
        self.scheduler.stop()
        self.posture_analyzer.stop()
        self.cloud_sync.stop_auto_sync()
        QApplication.quit()

    def setup_home_page(self):
        """Configurar la página de inicio"""
        self.home_page = QWidget()
        layout = QVBoxLayout()
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/images/logo.png")
        logo_label.setPixmap(logo_pixmap.scaled(400, 200, Qt.KeepAspectRatio))
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Mensaje de bienvenida
        welcome_label = QLabel("Bienvenido a Pausas Activas Profesional")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        # Estadísticas rápidas
        stats_widget = self.create_quick_stats_widget()
        
        # Botón para ejercicio rápido
        quick_exercise_btn = QPushButton("Comenzar Pausa Activa")
        quick_exercise_btn.setStyleSheet("font-size: 16px; padding: 10px;")
        quick_exercise_btn.clicked.connect(lambda: self.show_exercise("random"))
        
        layout.addWidget(logo_label)
        layout.addWidget(welcome_label)
        layout.addWidget(stats_widget)
        layout.addStretch()
        layout.addWidget(quick_exercise_btn)
        layout.addStretch()
        
        self.home_page.setLayout(layout)
        self.stacked_widget.addWidget(self.home_page)
    
    def create_quick_stats_widget(self):
        """Crear widget de estadísticas rápidas"""
        stats = self.stats_tracker.get_today_stats()
        
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Tu progreso hoy:")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px;")
        
        # Estadísticas
        exercises_label = QLabel(f"Pausas completadas: {stats['exercises_completed']}")
        time_label = QLabel(f"Tiempo total: {stats['total_time']} minutos")
        
        # Configurar estilo
        for label in [exercises_label, time_label]:
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-size: 16px;")
        
        layout.addWidget(title)
        layout.addWidget(exercises_label)
        layout.addWidget(time_label)
        
        widget.setLayout(layout)
        return widget
    
    def setup_exercise_page(self):
        """Configurar la página de ejercicio"""
        self.exercise_page = QWidget()
        layout = QVBoxLayout()
        
        # Título del ejercicio
        self.exercise_title = QLabel()
        self.exercise_title.setAlignment(Qt.AlignCenter)
        self.exercise_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        # Imagen/Video del ejercicio
        self.exercise_media = QLabel()
        self.exercise_media.setAlignment(Qt.AlignCenter)
        self.exercise_media.setMinimumSize(400, 300)
        
        # Descripción
        self.exercise_description = QTextEdit()
        self.exercise_description.setReadOnly(True)
        self.exercise_description.setAlignment(Qt.AlignCenter)
        
        # Temporizador
        self.timer_label = QLabel("00:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 32px; font-weight: bold;")
        
        # Botones de control
        control_layout = QHBoxLayout()
        
        pause_btn = QPushButton(QIcon("assets/icons/pause.png"), "Pausar")
        pause_btn.clicked.connect(self.pause_exercise)
        
        finish_btn = QPushButton(QIcon("assets/icons/stop.png"), "Finalizar")
        finish_btn.clicked.connect(self.finish_exercise)
        
        control_layout.addWidget(pause_btn)
        control_layout.addWidget(finish_btn)
        
        # Añadir al layout principal
        layout.addWidget(self.exercise_title)
        layout.addWidget(self.exercise_media)
        layout.addWidget(self.exercise_description)
        layout.addWidget(self.timer_label)
        layout.addLayout(control_layout)
        
        self.exercise_page.setLayout(layout)
        self.stacked_widget.addWidget(self.exercise_page)
    
    def setup_settings_page(self):
        """Configurar la página de ajustes"""
        self.settings_page = QWidget()
        layout = QVBoxLayout()
        
        # Pestañas para diferentes configuraciones
        tabs = QTabWidget()
        
        # Configuración general
        general_tab = QWidget()
        general_layout = QFormLayout()
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Español", "English"])
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Claro", "Oscuro"])
        
        self.notification_sound_combo = QComboBox()
        self.notification_sound_combo.addItems(["Default", "Soft", "Alert"])
        
        general_layout.addRow("Idioma:", self.language_combo)
        general_layout.addRow("Tema:", self.theme_combo)
        general_layout.addRow("Sonido de notificación:", self.notification_sound_combo)
        
        general_tab.setLayout(general_layout)
        tabs.addTab(general_tab, "General")
        
        # Configuración de pausas
        pauses_tab = QWidget()
        pauses_layout = QFormLayout()
        
        self.work_interval_spin = QSpinBox()
        self.work_interval_spin.setRange(10, 120)
        self.work_interval_spin.setSuffix(" minutos")
        
        self.break_interval_spin = QSpinBox()
        self.break_interval_spin.setRange(1, 30)
        self.break_interval_spin.setSuffix(" minutos")
        
        pauses_layout.addRow("Intervalo de trabajo:", self.work_interval_spin)
        pauses_layout.addRow("Intervalo de descanso:", self.break_interval_spin)
        
        pauses_tab.setLayout(pauses_layout)
        tabs.addTab(pauses_tab, "Pausas")
        
        # Configuración de sistema
        system_tab = QWidget()
        system_layout = QVBoxLayout()
        
        self.startup_check = QCheckBox("Iniciar con el sistema")
        self.minimize_check = QCheckBox("Minimizar a la bandeja al cerrar")
        
        system_layout.addWidget(self.startup_check)
        system_layout.addWidget(self.minimize_check)
        system_layout.addStretch()
        
        system_tab.setLayout(system_layout)
        tabs.addTab(system_tab, "Sistema")
        
        # Botones de acción
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.show_home)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        # Añadir al layout principal
        layout.addWidget(tabs)
        layout.addLayout(button_layout)
        
        self.settings_page.setLayout(layout)
        self.stacked_widget.addWidget(self.settings_page)
    
    # =============================================
    # Métodos para mostrar las diferentes páginas
    # =============================================

    def show_home(self):
        """Mostrar la página de inicio"""
        self.stacked_widget.setCurrentWidget(self.home_page)
        self.status_bar.showMessage("Listo")
    
    def show_exercise(self, exercise_id):
        """Mostrar un ejercicio específico"""
        exercise = self.exercise_manager.get_exercise(exercise_id)
        if not exercise:
            QMessageBox.warning(self, "Error", "Ejercicio no encontrado")
            return
        
        self.current_exercise = exercise
        
        # Actualizar UI
        self.exercise_title.setText(exercise['name'])
        
        # Cargar imagen
        pixmap = QPixmap(f"assets/images/{exercise['image']}")
        self.exercise_media.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio))
        
        self.exercise_description.setText(exercise['description'])
        
        # Configurar temporizador
        self.exercise_duration = exercise['duration']
        self.remaining_time = self.exercise_duration
        self.update_timer_display()
        
        # Iniciar temporizador
        self.exercise_timer = QTimer()
        self.exercise_timer.timeout.connect(self.update_exercise_timer)
        self.exercise_timer.start(1000)  # 1 segundo
        
        # Mostrar página de ejercicio
        self.stacked_widget.setCurrentWidget(self.exercise_page)
        self.status_bar.showMessage(f"Realizando: {exercise['name']}")
    
    def show_settings(self):
        """Mostrar la página de configuración"""
        # Cargar valores actuales
        self.language_combo.setCurrentText(
            "Español" if self.config.get("DEFAULT", "language") == "es" else "English"
        )
        self.theme_combo.setCurrentText(
            "Claro" if self.config.get("DEFAULT", "theme") == "light" else "Oscuro"
        )
        self.notification_sound_combo.setCurrentText(
            self.config.get("DEFAULT", "notification_sound").capitalize()
        )
        self.work_interval_spin.setValue(
            int(self.config.get("DEFAULT", "work_interval"))
        )
        self.break_interval_spin.setValue(
            int(self.config.get("DEFAULT", "break_interval"))
        )
        self.startup_check.setChecked(
            self.config.getboolean("DEFAULT", "start_on_login")
        )
        self.minimize_check.setChecked(
            self.config.getboolean("DEFAULT", "minimize_to_tray")
        )
        
        self.stacked_widget.setCurrentWidget(self.settings_page)
        self.status_bar.showMessage("Configuración")
    
    # =============================================
    # Métodos para manejo de ejercicios
    # =============================================

    def update_exercise_timer(self):
        """Actualizar el temporizador del ejercicio"""
        self.remaining_time -= 1
        self.update_timer_display()
        
        if self.remaining_time <= 0:
            self.finish_exercise()
    
    def update_timer_display(self):
        """Actualizar la visualización del temporizador"""
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")
    
    def pause_exercise(self):
        """Pausar el ejercicio actual"""
        if hasattr(self, 'exercise_timer') and self.exercise_timer.isActive():
            self.exercise_timer.stop()
            self.status_bar.showMessage("Ejercicio pausado")
        else:
            self.exercise_timer.start()
            self.status_bar.showMessage(f"Realizando: {self.current_exercise['name']}")
    
    def finish_exercise(self):
        """Finalizar el ejercicio actual"""
        if hasattr(self, 'exercise_timer'):
            self.exercise_timer.stop()
        
        # Registrar en estadísticas
        if hasattr(self, 'current_exercise'):
            self.stats_tracker.log_exercise(
                self.current_exercise['id'],
                self.exercise_duration
            )
            
            # Verificar logros
            stats = {
                'total_sessions': self.stats_tracker.get_lifetime_stats()['total_sessions'],
                'current_streak': self.stats_tracker.get_current_streak(),
                # ... otros datos para logros
            }
            self.achievement_system.check_achievements(1, stats)  # Asumiendo user_id=1
        
        # Mostrar notificación
        self.notification_manager.show_notification(
            "Ejercicio completado",
            f"¡Buen trabajo! Has completado {self.current_exercise['name']}"
        )
        
        # Volver a la página de inicio
        self.show_home()
    
    # =============================================
    # Métodos para manejo de configuración
    # =============================================

    def save_settings(self):
        """Guardar la configuración actual"""
        self.config["DEFAULT"]["language"] = (
            "es" if self.language_combo.currentText() == "Español" else "en"
        )
        self.config["DEFAULT"]["theme"] = (
            "light" if self.theme_combo.currentText() == "Claro" else "dark"
        )
        self.config["DEFAULT"]["notification_sound"] = (
            self.notification_sound_combo.currentText().lower()
        )
        self.config["DEFAULT"]["work_interval"] = (
            str(self.work_interval_spin.value())
        )
        self.config["DEFAULT"]["break_interval"] = (
            str(self.break_interval_spin.value())
        )
        self.config["DEFAULT"]["start_on_login"] = (
            "true" if self.startup_check.isChecked() else "false"
        )
        self.config["DEFAULT"]["minimize_to_tray"] = (
            "true" if self.minimize_check.isChecked() else "false"
        )
        
        # Guardar en disco
        if save_config(self.config):
            QMessageBox.information(self, "Guardado", "Configuración guardada correctamente")
            self.config_changed.emit()  # Notificar a otros componentes
            self.show_home()
        else:
            QMessageBox.warning(self, "Error", "No se pudo guardar la configuración")
    
    # =============================================
    # Métodos para características adicionales
    # =============================================

    def show_stats(self):
        """Mostrar estadísticas detalladas"""
        self.stats_window = QDialog(self)
        self.stats_window.setWindowTitle("Estadísticas")
        layout = QVBoxLayout()
        
        # Pestañas para diferentes vistas
        tabs = QTabWidget()
        
        # Vista diaria
        daily_tab = QWidget()
        daily_layout = QVBoxLayout()
        
        # Gráfico de días
        self.daily_chart = self.create_daily_chart()
        chart_view = QChartView(self.daily_chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        daily_layout.addWidget(chart_view)
        daily_tab.setLayout(daily_layout)
        tabs.addTab(daily_tab, "Diario")
        
        # Vista semanal
        weekly_tab = QWidget()
        weekly_layout = QVBoxLayout()
        
        # Gráfico semanal
        self.weekly_chart = self.create_weekly_chart()
        weekly_chart_view = QChartView(self.weekly_chart)
        weekly_chart_view.setRenderHint(QPainter.Antialiasing)
        
        weekly_layout.addWidget(weekly_chart_view)
        weekly_tab.setLayout(weekly_layout)
        tabs.addTab(weekly_tab, "Semanal")
        
        layout.addWidget(tabs)
        self.stats_window.setLayout(layout)
        self.stats_window.exec_()
    
    def create_daily_chart(self):
        """Crear gráfico de estadísticas diarias"""
        chart = QChart()
        chart.setTitle("Actividad diaria")
        
        # Obtener datos
        stats = self.stats_tracker.get_weekly_stats()
        
        # Crear series
        series = QLineSeries()
        series.setName("Pausas completadas")
        
        for day in stats:
            date = datetime.strptime(day['date'], "%Y-%m-%d").date()
            series.append(date.toJulianDay(), day['exercises_completed'])
        
        chart.addSeries(series)
        
        # Configurar ejes
        axis_x = QDateTimeAxis()
        axis_x.setFormat("dd MMM")
        axis_x.setTitleText("Fecha")
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setTitleText("Pausas")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        return chart
    def setup_posture_ui(self):
        """Configurar la interfaz del monitor de postura simplificado"""
        self.posture_dialog = QDialog(self)
        self.posture_dialog.setWindowTitle("Monitor de Postura Simulado")
        layout = QVBoxLayout()
        
        # Vista simulada de la cámara
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setStyleSheet("background-color: black;")
        
        # Indicador de estado
        self.posture_status = QLabel("Estado: No monitoreando")
        self.posture_status.setAlignment(Qt.AlignCenter)
        self.posture_status.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        # Botón de control
        self.posture_btn = QPushButton("Iniciar Monitor")
        self.posture_btn.clicked.connect(self.toggle_posture_monitoring)
        
        layout.addWidget(self.camera_label)
        layout.addWidget(self.posture_status)
        layout.addWidget(self.posture_btn)
        
        self.posture_dialog.setLayout(layout)

    def toggle_posture_monitoring(self):
        """Alternar el monitoreo de postura simplificado"""
        if self.posture_analyzer.is_running:
            self.posture_analyzer.stop()
            self.posture_btn.setText("Iniciar Monitor")
            self.posture_status.setText("Estado: Detenido")
            self.camera_label.clear()
        else:
            self.posture_analyzer.start()
            self.posture_btn.setText("Detener Monitor")
            self.posture_status.setText("Estado: Monitoreando...")

    def update_camera_view(self, frame):
        """Actualizar la vista de la cámara simulada"""
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        
        self.camera_label.setPixmap(pixmap.scaled(
            self.camera_label.width(), 
            self.camera_label.height(),
            Qt.KeepAspectRatio
        ))

    def handle_posture_alert(self, message):
        """Manejar alertas de postura simuladas"""
        self.notification_manager.show_notification("Alerta de Postura", message)
        self.posture_status.setText(f"Estado: {message}")
        self.posture_status.setStyleSheet("font-size: 18px; font-weight: bold; color: red;")
        
        # Resetear el color después de 3 segundos
        QTimer.singleShot(3000, lambda: self.posture_status.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: black;"
        ))

    def show_posture_monitor(self):
        """Mostrar el diálogo del monitor de postura"""
        if not hasattr(self, 'posture_dialog'):
            self.setup_posture_ui()
        self.posture_dialog.exec_()
        def start_services(self):
            """Iniciar servicios en segundo plano"""
            # Iniciar sincronización en la nube si está configurada
            if self.cloud_sync.auto_sync:
                self.cloud_sync.start_auto_sync()
            
            # Verificar si hay actualizaciones
            QTimer.singleShot(5000, self.check_for_updates)
    
    def check_for_updates(self):
        """Verificar si hay actualizaciones disponibles"""
        # Implementar lógica de actualización
        pass
    
    def show_about(self):
        """Mostrar diálogo 'Acerca de'"""
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle("Acerca de Pausas Activas Profesional")
        layout = QVBoxLayout()
        
        text = QTextBrowser()
        text.setOpenExternalLinks(True)
        text.setHtml("""
        <h1>Pausas Activas Profesional</h1>
        <p>Versión 1.0.0</p>
        <p>Una aplicación para mejorar tu salud y productividad mediante pausas activas programadas.</p>
        <p>Desarrollado por [Tu Nombre]</p>
        <p><a href="https://github.com/tuusuario/pausas-activas">GitHub</a></p>
        <p>© 2023 Todos los derechos reservados</p>
        """)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(about_dialog.close)
        
        layout.addWidget(text)
        layout.addWidget(close_btn)
        
        about_dialog.setLayout(layout)
        about_dialog.exec_()