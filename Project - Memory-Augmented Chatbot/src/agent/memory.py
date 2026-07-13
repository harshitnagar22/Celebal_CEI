import os
from langgraph.checkpoint.sqlite import SqliteSaver
from src.core.config import config

import sqlite3

class MemoryManager:
    # keeps track of chat history using sqlite checkpointer
    def __init__(self):
        # We use SQLite to persist the graph state across interactions
        self.db_path = os.path.join(config.DATA_DIR, "memory.sqlite")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Create connection string for sqlite saver
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.checkpointer = SqliteSaver(self.conn)
        # Langgraph checkpoint Sqlite needs setup
        self.checkpointer.setup()

    def get_checkpointer(self):
        return self.checkpointer

memory_manager = MemoryManager()
