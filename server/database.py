import sqlite3


DATABASE_NAME = "memory.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)

    return connection

def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_message TEXT NOT NULL,
            assistant_reply TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pinned_memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            content TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()
    
def cleanup_old_conversations():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM conversations
        WHERE timestamp < datetime('now', '-3 days')
        """
    )

    connection.commit()
    connection.close()    