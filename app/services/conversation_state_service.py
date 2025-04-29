import sqlite3
import json
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./health_gpt.db")
# Extract the path from the URL (remove sqlite:///)
DB_PATH = DATABASE_URL.split("///")[-1]

class ConversationStateService:
    """
    Manages the state and context of conversations using an SQLite database.
    """
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._create_table()

    def _get_db_connection(self):
        """Establishes a connection to the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        # Optional: Use Row factory for dictionary-like access, though not strictly needed here
        # conn.row_factory = sqlite3.Row 
        return conn

    def _create_table(self):
        """Creates the conversation_state table if it doesn't exist."""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_state (
                phone_number TEXT PRIMARY KEY,
                state TEXT NOT NULL,
                context TEXT,  -- Storing context as JSON string
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def save_state(self, phone_number: str, state: str, context: Optional[Dict[str, Any]] = None):
        """Saves or updates the state and context for a given phone number."""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        context_json = json.dumps(context) if context is not None else None
        
        cursor.execute("""
            INSERT INTO conversation_state (phone_number, state, context, last_updated)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(phone_number) DO UPDATE SET
                state = excluded.state,
                context = excluded.context,
                last_updated = CURRENT_TIMESTAMP;
        """, (phone_number, state, context_json))
        
        conn.commit()
        conn.close()
        print(f"[StateService] Saved state for {phone_number}: State={state}, Context={context_json}")

    def get_state(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the state and context for a given phone number.
        Returns None if the phone number is not found.
        """
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT state, context 
            FROM conversation_state 
            WHERE phone_number = ?
        """, (phone_number,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            state, context_json = row
            context = json.loads(context_json) if context_json else None
            print(f"[StateService] Retrieved state for {phone_number}: State={state}, Context={context}")
            return {"state": state, "context": context}
        else:
            print(f"[StateService] No state found for {phone_number}. Treating as NEW.")
            return None # Indicate not found, can be treated as 'NEW' state by caller

    def delete_state(self, phone_number: str):
        """Deletes the state entry for a given phone number."""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM conversation_state 
            WHERE phone_number = ?
        """, (phone_number,))
        
        conn.commit()
        rows_deleted = cursor.rowcount
        conn.close()
        
        if rows_deleted > 0:
             print(f"[StateService] Deleted state for {phone_number}.")
        else:
            print(f"[StateService] No state found for {phone_number} to delete.")

# Example Usage (for testing purposes)
if __name__ == '__main__':
    service = ConversationStateService()
    
    # Example save
    test_phone = "+1234567890"
    initial_context = {"attempt": 1, "last_message": "hello"}
    service.save_state(test_phone, "AWAITING_TYPE", initial_context)
    
    # Example retrieve
    state_info = service.get_state(test_phone)
    print(f"Retrieved: {state_info}")
    
    # Example update
    updated_context = {"attempt": 2, "last_message": "insurance", "insurance_name_guess": "BlueCross"}
    service.save_state(test_phone, "AWAITING_INSURANCE_DOCS", updated_context)
    state_info_updated = service.get_state(test_phone)
    print(f"Retrieved updated: {state_info_updated}")

    # Example retrieve non-existent
    state_info_none = service.get_state("+0987654321")
    print(f"Retrieved non-existent: {state_info_none}")

    # Example delete
    service.delete_state(test_phone)
    state_info_deleted = service.get_state(test_phone)
    print(f"Retrieved after delete: {state_info_deleted}") 