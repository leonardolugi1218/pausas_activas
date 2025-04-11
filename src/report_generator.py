# src/report_generator.py
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtGui import QPainter, QTextDocument
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import csv
from pathlib import Path
from datetime import datetime

class ReportGenerator:
    def __init__(self):
        self.reports_dir = Path.home() / ".pausas_activas" / "reports"
        self.reports_dir.mkdir(exist_ok=True)
    
    def generate_daily_report(self, date=None):
        """Generar reporte diario en PDF"""
        if date is None:
            date = datetime.now().date()
        
        # Obtener datos de la base de datos
        stats = self.get_daily_stats(date)
        exercises = self.get_daily_exercises(date)
        
        # Crear documento HTML
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial; margin: 20px; }}
                h1 {{ color: #2c3e50; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .stats {{ margin-bottom: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .footer {{ margin-top: 30px; font-size: 0.8em; text-align: center; color: #7f8c8d; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Reporte Diario de Pausas Activas</h1>
                <p>{date.strftime('%A, %d de %B de %Y')}</p>
            </div>
            
            <div class="stats">
                <h2>Estadísticas</h2>
                <p><strong>Pausas completadas:</strong> {stats.get('exercises_completed', 0)}</p>
                <p><strong>Tiempo total:</strong> {stats.get('total_time', 0)} minutos</p>
            </div>
            
            <div class="exercises">
                <h2>Ejercicios Realizados</h2>
                <table>
                    <tr>
                        <th>Hora</th>
                        <th>Ejercicio</th>
                        <th>Duración</th>
                    </tr>
        """
        
        for ex in exercises:
            html += f"""
                    <tr>
                        <td>{ex['time']}</td>
                        <td>{ex['name']}</td>
                        <td>{ex['duration']} min</td>
                    </tr>
            """
        
        html += """
                </table>
            </div>
            
            <div class="footer">
                <p>Generado por Pausas Activas Profesional • {date}</p>
            </div>
        </body>
        </html>
        """
        
        # Generar PDF
        report_path = self.reports_dir / f"reporte_{date.strftime('%Y%m%d')}.pdf"
        self.html_to_pdf(html, str(report_path))
        
        return report_path
    
    def get_daily_stats(self, date):
        """Obtener estadísticas diarias desde la base de datos"""
        conn = sqlite3.connect("database/stats.db")
        cursor = conn.cursor()
        
        date_str = date.strftime("%Y-%m-%d")
        cursor.execute("""
        SELECT exercises_completed, total_time 
        FROM daily_stats 
        WHERE date = ?
        """, (date_str,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "exercises_completed": result[0],
                "total_time": result[1]
            }
        return {}
    
    def get_daily_exercises(self, date):
        """Obtener ejercicios diarios desde la base de datos"""
        conn = sqlite3.connect("database/stats.db")
        cursor = conn.cursor()
        
        start_time = datetime.combine(date, datetime.min.time()).isoformat()
        end_time = datetime.combine(date + timedelta(days=1), datetime.min.time()).isoformat()
        
        cursor.execute("""
        SELECT es.start_time, e.name, es.duration
        FROM exercise_sessions es
        JOIN exercises e ON es.exercise_id = e.id
        WHERE es.start_time BETWEEN ? AND ?
        ORDER BY es.start_time
        """, (start_time, end_time))
        
        exercises = []
        for row in cursor.fetchall():
            dt = datetime.fromisoformat(row[0])
            exercises.append({
                "time": dt.strftime("%H:%M"),
                "name": row[1],
                "duration": row[2]
            })
        
        conn.close()
        return exercises
    
    def html_to_pdf(self, html, output_path):
        """Convertir HTML a PDF"""
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(output_path)
        
        doc = QTextDocument()
        doc.setHtml(html)
        doc.setPageSize(printer.pageRect().size())
        
        painter = QPainter(printer)
        doc.drawContents(painter)
        painter.end()

    def export_to_csv(self, start_date, end_date):
        """Exportar datos a CSV"""
        data = self.get_range_stats(start_date, end_date)
        
        csv_path = self.reports_dir / f"export_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.csv"
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Escribir encabezados
            writer.writerow(["Fecha", "Pausas Completadas", "Tiempo Total (min)", "Ejercicios Realizados"])
            
            # Escribir datos
            for row in data:
                writer.writerow([
                    row['date'],
                    row['exercises_completed'],
                    row['total_time'],
                    ", ".join(row['exercises'])
                ])
        
        return csv_path
    
    def get_range_stats(self, start_date, end_date):
        """Obtener estadísticas para un rango de fechas"""
        conn = sqlite3.connect("database/stats.db")
        cursor = conn.cursor()
        
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Obtener estadísticas diarias
        cursor.execute("""
        SELECT date, exercises_completed, total_time
        FROM daily_stats
        WHERE date BETWEEN ? AND ?
        ORDER BY date
        """, (start_str, end_str))
        
        stats = []
        for row in cursor.fetchall():
            stats.append({
                "date": row[0],
                "exercises_completed": row[1],
                "total_time": row[2],
                "exercises": []
            })
        
        # Obtener ejercicios para cada día
        for day in stats:
            cursor.execute("""
            SELECT e.name
            FROM exercise_sessions es
            JOIN exercises e ON es.exercise_id = e.id
            WHERE es.start_time BETWEEN ? AND ?
            """, (
                f"{day['date']}T00:00:00",
                f"{day['date']}T23:59:59"
            ))
            
            day['exercises'] = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return stats