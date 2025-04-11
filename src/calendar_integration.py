# src/calendar_integration.py
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import os
from PyQt5.QtCore import QObject, pyqtSignal

class CalendarIntegration(QObject):
    events_updated = pyqtSignal(list)  # Lista de eventos
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.calendar_file = os.path.join(
            os.path.expanduser("~"), 
            ".pausas_activas", 
            "calendar.ics"
        )
        self.load_calendar()
    
    def load_calendar(self):
        """Cargar calendario desde archivo ICS"""
        if not os.path.exists(self.calendar_file):
            self.cal = Calendar()
            self.cal.add('prodid', '-//Pausas Activas//mxm.dk//')
            self.cal.add('version', '2.0')
            self.save_calendar()
        else:
            with open(self.calendar_file, 'rb') as f:
                self.cal = Calendar.from_ical(f.read())
    
    def save_calendar(self):
        """Guardar calendario a archivo"""
        with open(self.calendar_file, 'wb') as f:
            f.write(self.cal.to_ical())
    
    def add_exercise_event(self, exercise, start_time, duration_minutes):
        """Añadir evento de ejercicio al calendario"""
        event = Event()
        event.add('summary', f"Pausa Activa: {exercise['name']}")
        event.add('description', exercise['description'])
        event.add('dtstart', start_time)
        event.add('dtend', start_time + timedelta(minutes=duration_minutes))
        event.add('location', 'En el trabajo')
        event.add('priority', 5)
        
        self.cal.add_component(event)
        self.save_calendar()
        self.events_updated.emit(self.get_upcoming_events())
    
    def get_upcoming_events(self, days=7):
        """Obtener eventos próximos"""
        now = datetime.now()
        end_date = now + timedelta(days=days)
        
        upcoming = []
        for component in self.cal.walk():
            if component.name == "VEVENT":
                start = component.get('dtstart').dt
                if isinstance(start, datetime):
                    if now <= start <= end_date:
                        upcoming.append({
                            "summary": str(component.get('summary')),
                            "start": start,
                            "end": component.get('dtend').dt,
                            "description": str(component.get('description'))
                        })
        
        return sorted(upcoming, key=lambda x: x['start'])
    
    def sync_with_google_calendar(self):
        """Sincronizar con Google Calendar"""
        # Implementación requeriría OAuth y API de Google
        pass
    
    def sync_with_outlook(self):
        """Sincronizar con Outlook"""
        # Implementación requeriría API de Microsoft
        pass