from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3
import os

from app.services.slot_service import SlotService


class SlotManagementService:
    """Service for managing slots in a SQLite database."""
    
    def __init__(self, db_path: str = "slots.db"):
        """
        Initialize the slot management service.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.slot_service = SlotService()
        self._init_db()
    
    def _init_db(self):
        """Initialize the database and create tables if they don't exist."""
        # Ensure directory exists
        db_dir = os.path.dirname(os.path.abspath(self.db_path))
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create the slots table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS slots (
            id TEXT PRIMARY KEY,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            is_available INTEGER NOT NULL,
            appointment_id TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_weekly_slots(self, 
                              start_date: datetime,
                              weeks_ahead: int = 4,
                              slot_duration: timedelta = timedelta(minutes=30),
                              daily_start_time: timedelta = timedelta(hours=9),
                              daily_end_time: timedelta = timedelta(hours=17),
                              excluded_days: List[int] = None) -> int:
        """
        Generate slots for multiple weeks ahead and save them to the database.
        
        Args:
            start_date: Starting date for slot generation
            weeks_ahead: Number of weeks to generate slots for
            slot_duration: Duration of each slot
            daily_start_time: Start time for each day
            daily_end_time: End time for each day
            excluded_days: Days to exclude (0=Monday, 6=Sunday)
            
        Returns:
            Number of slots generated
        """
        end_date = start_date + timedelta(weeks=weeks_ahead)
        
        # Generate slots in memory
        slot_ids = self.slot_service.generate_slots(
            start_date, end_date, slot_duration,
            daily_start_time, daily_end_time, excluded_days
        )
        
        # Save slots to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for slot_id in slot_ids:
            slot = self.slot_service.get_slot(slot_id)
            cursor.execute(
                '''
                INSERT OR REPLACE INTO slots 
                (id, start_time, end_time, is_available, appointment_id)
                VALUES (?, ?, ?, ?, ?)
                ''',
                (
                    slot["id"],
                    slot["start_time"].isoformat(),
                    slot["end_time"].isoformat(),
                    1 if slot["is_available"] else 0,
                    slot["appointment_id"]
                )
            )
        
        conn.commit()
        conn.close()
        
        return len(slot_ids)
    
    def get_available_slots(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Get available slots from the database within a date range.
        
        Args:
            start_date: Start date to search from
            end_date: End date to search to
            
        Returns:
            List of available slot dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            '''
            SELECT * FROM slots 
            WHERE is_available = 1 
              AND start_time >= ? 
              AND end_time <= ?
            ORDER BY start_time
            ''',
            (start_date.isoformat(), end_date.isoformat())
        )
        
        rows = cursor.fetchall()
        slots = []
        
        for row in rows:
            slots.append({
                "id": row["id"],
                "start_time": datetime.fromisoformat(row["start_time"]),
                "end_time": datetime.fromisoformat(row["end_time"]),
                "is_available": bool(row["is_available"]),
                "appointment_id": row["appointment_id"]
            })
        
        conn.close()
        return slots
    
    def book_slot(self, slot_id: str, appointment_id: str) -> bool:
        """
        Book a slot with a specific appointment ID.
        
        Args:
            slot_id: The ID of the slot to book
            appointment_id: The ID of the appointment
            
        Returns:
            True if successful, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''
            UPDATE slots 
            SET is_available = 0, appointment_id = ? 
            WHERE id = ? AND is_available = 1
            ''',
            (appointment_id, slot_id)
        )
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def clear_old_slots(self) -> int:
        """
        Remove slots that have passed from the database.
        
        Returns:
            Number of slots removed
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''
            DELETE FROM slots 
            WHERE end_time < ?
            ''',
            (datetime.now().isoformat(),)
        )
        
        removed_slots = cursor.rowcount
        conn.commit()
        conn.close()
        
        return removed_slots 