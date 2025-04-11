import sqlite3
from pathlib import Path

def init_databases():
    """Inicializar todas las bases de datos necesarias"""
    app_folder = Path.home() / ".pausas_activas"
    app_folder.mkdir(exist_ok=True)
    
    # Base de datos de estadísticas
    init_stats_db(app_folder / "database" / "stats.db")
    
    # Base de datos de logros
    init_achievements_db(app_folder / "database" / "achievements.db")
    
    # Base de datos de ejercicios
    init_exercises_db(app_folder / "database" / "exercises.db")

def init_stats_db(db_path):
    """Inicializar base de datos de estadísticas"""
    db_path.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tabla de sesiones de ejercicio
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exercise_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exercise_id TEXT NOT NULL,
        start_time TEXT NOT NULL,
        duration INTEGER NOT NULL,
        completed BOOLEAN NOT NULL
    )
    """)
    
    # Tabla de estadísticas diarias
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_stats (
        date TEXT PRIMARY KEY,
        exercises_completed INTEGER NOT NULL,
        total_time INTEGER NOT NULL,
        current_streak INTEGER NOT NULL DEFAULT 0
    )
    """)
    
    # Tabla de estadísticas globales
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lifetime_stats (
        id INTEGER PRIMARY KEY DEFAULT 1,
        total_sessions INTEGER NOT NULL DEFAULT 0,
        total_time INTEGER NOT NULL DEFAULT 0,
        longest_streak INTEGER NOT NULL DEFAULT 0
    )
    """)
    
    # Insertar registro inicial si no existe
    cursor.execute("""
    INSERT OR IGNORE INTO lifetime_stats (id, total_sessions, total_time, longest_streak)
    VALUES (1, 0, 0, 0)
    """)
    
    conn.commit()
    conn.close()

def init_achievements_db(db_path):
    """Inicializar base de datos de logros"""
    conn = sqlite3.connect(db_path)
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
    
    # Tabla de logros desbloqueados
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_achievements (
        user_id INTEGER,
        achievement_id TEXT,
        unlocked_at TEXT,
        PRIMARY KEY (user_id, achievement_id)
    )
    """)
    
    # Insertar logros básicos
    cursor.execute("SELECT COUNT(*) FROM achievements")
    if cursor.fetchone()[0] == 0:
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
    
    conn.commit()
    conn.close()

def init_exercises_db(db_path):
    """Inicializar base de datos de ejercicios"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exercises (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        type TEXT NOT NULL,
        duration INTEGER NOT NULL,
        difficulty TEXT NOT NULL,
        image_path TEXT,
        video_path TEXT,
        custom BOOLEAN NOT NULL DEFAULT 0
    )
    """)
    
    # Insertar ejercicios básicos
    cursor.execute("SELECT COUNT(*) FROM exercises")
    if cursor.fetchone()[0] == 0:
        default_exercises = [
            ("neck_stretch", "Estiramiento de cuello", 
             "Incline su cabeza hacia un lado\nMantenga por 10 segundos\nRepita del otro lado", 
             "stretch", 30, "fácil", "neck_stretch.png", "neck_stretch.mp4", 0),
            # ... más ejercicios
        ]
        
        cursor.executemany("""
        INSERT INTO exercises (id, name, description, type, duration, difficulty, image_path, video_path, custom)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, default_exercises)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_databases()
    print("Bases de datos inicializadas correctamente.")