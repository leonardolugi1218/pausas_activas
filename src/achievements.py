# src/achievements.py
import sqlite3
from PyQt5.QtCore import QObject, pyqtSignal

class AchievementSystem(QObject):
    achievement_unlocked = pyqtSignal(str, str)  # (logro_id, nombre_logro)
    
    def __init__(self):
        super().__init__()
        self.db_path = "database/achievements.db"
        self.init_db()
    
    def init_db(self):
        """Inicializar base de datos de logros"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de definición de logros
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            icon TEXT NOT NULL,
            condition_type TEXT NOT NULL,
            condition_value INTEGER NOT NULL
        )
        """)
        
        # Tabla de logros desbloqueados por el usuario
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_achievements (
            user_id INTEGER,
            achievement_id TEXT,
            unlocked_at TEXT,
            PRIMARY KEY (user_id, achievement_id)
        )
        """)
        
        # Insertar logros básicos si no existen
        cursor.execute("SELECT COUNT(*) FROM achievements")
        if cursor.fetchone()[0] == 0:
            self.create_default_achievements(cursor)
        
        conn.commit()
        conn.close()
    
    def create_default_achievements(self, cursor):
        """Crear logros predeterminados"""
        default_achievements = [
            ("first_time", "Primera Pausa", "Completaste tu primera pausa activa", "first_icon.png", "session_count", 1),
            ("daily_streak_3", "Racha de 3 días", "Completa pausas activas por 3 días seguidos", "streak_3.png", "daily_streak", 3),
            ("marathon", "Maratón", "Completa 100 pausas activas", "marathon.png", "total_sessions", 100),
            ("early_bird", "Madrugador", "Completa una pausa antes de las 8 AM", "early_bird.png", "early_session", 1),
            ("week_complete", "Semana Completa", "Completa pausas todos los días de la semana", "week_complete.png", "weekly_completion", 7)
        ]
        
        cursor.executemany("""
        INSERT INTO achievements (id, name, description, icon, condition_type, condition_value)
        VALUES (?, ?, ?, ?, ?, ?)
        """, default_achievements)
    
    def check_achievements(self, user_id, stats):
        """Verificar si se han desbloqueado nuevos logros"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Obtener todos los logros no desbloqueados
        cursor.execute("""
        SELECT a.id, a.name, a.condition_type, a.condition_value 
        FROM achievements a
        LEFT JOIN user_achievements ua ON a.id = ua.achievement_id AND ua.user_id = ?
        WHERE ua.achievement_id IS NULL
        """, (user_id,))
        
        potential_achievements = cursor.fetchall()
        
        unlocked = []
        
        for ach_id, name, cond_type, cond_value in potential_achievements:
            if self.check_condition(cond_type, cond_value, stats):
                unlocked.append((ach_id, name))
                # Registrar logro desbloqueado
                cursor.execute("""
                INSERT INTO user_achievements (user_id, achievement_id, unlocked_at)
                VALUES (?, ?, datetime('now'))
                """, (user_id, ach_id))
                
                # Emitir señal
                self.achievement_unlocked.emit(ach_id, name)
        
        conn.commit()
        conn.close()
        return unlocked
    
    def check_condition(self, cond_type, cond_value, stats):
        """Verificar condición específica"""
        if cond_type == "session_count":
            return stats["total_sessions"] >= cond_value
        elif cond_type == "daily_streak":
            return stats["current_streak"] >= cond_value
        elif cond_type == "total_sessions":
            return stats["lifetime_sessions"] >= cond_value
        elif cond_type == "early_session":
            return stats["early_sessions"] >= cond_value
        elif cond_type == "weekly_completion":
            return stats["weekly_days_completed"] >= cond_value
        return False
    
    def get_unlocked_achievements(self, user_id):
        """Obtener logros desbloqueados por el usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT a.id, a.name, a.description, a.icon, ua.unlocked_at
        FROM user_achievements ua
        JOIN achievements a ON ua.achievement_id = a.id
        WHERE ua.user_id = ?
        ORDER BY ua.unlocked_at DESC
        """, (user_id,))
        
        achievements = []
        for row in cursor.fetchall():
            achievements.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "icon": row[3],
                "unlocked_at": row[4]
            })
        
        conn.close()
        return achievements