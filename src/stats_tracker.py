# src/stats_tracker.py
import sqlite3
from datetime import datetime
from PyQt5.QtCore import QObject

class StatsTracker(QObject):
    def __init__(self):
        super().__init__()
        self.db_path = "database/stats.db"
        self.init_db()
    
    def init_db(self):
        """Inicializar base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS exercise_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise_id TEXT NOT NULL,
            start_time TEXT NOT NULL,
            duration INTEGER NOT NULL,
            completed BOOLEAN NOT NULL
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_stats (
            date TEXT PRIMARY KEY,
            exercises_completed INTEGER NOT NULL,
            total_time INTEGER NOT NULL
        )
        """)
        
        conn.commit()
        conn.close()
    
    def log_exercise(self, exercise_id, duration, completed=True):
        """Registrar un ejercicio completado"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO exercise_sessions (exercise_id, start_time, duration, completed)
        VALUES (?, ?, ?, ?)
        """, (exercise_id, datetime.now().isoformat(), duration, completed))
        
        # Actualizar estadísticas diarias
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
        INSERT OR IGNORE INTO daily_stats (date, exercises_completed, total_time)
        VALUES (?, 0, 0)
        """, (today,))
        
        if completed:
            cursor.execute("""
            UPDATE daily_stats 
            SET exercises_completed = exercises_completed + 1,
                total_time = total_time + ?
            WHERE date = ?
            """, (duration, today))
        
        conn.commit()
        conn.close()
    
    def get_today_stats(self):
        """Obtener estadísticas de hoy"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
        SELECT exercises_completed, total_time 
        FROM daily_stats 
        WHERE date = ?
        """, (today,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "exercises_completed": result[0],
                "total_time": result[1]
            }
        return {"exercises_completed": 0, "total_time": 0}
    
    def get_weekly_stats(self):
        """Obtener estadísticas de la última semana"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT date, exercises_completed, total_time 
        FROM daily_stats 
        WHERE date >= date('now', '-7 days')
        ORDER BY date
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        stats = []
        for row in results:
            stats.append({
                "date": row[0],
                "exercises_completed": row[1],
                "total_time": row[2]
            })
        
        return stats