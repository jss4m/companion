from .database import get_connection


class MemoryManager:

    def retrieve(self, message):
        print("[Memory] retrieve")

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT user_message, assistant_reply
            FROM conversations
            ORDER BY id DESC
            LIMIT 5
            """
        )

        rows = cursor.fetchall()

        connection.close()

        memories = []

        for row in reversed(rows):
            memories.append({
                "user": row[0],
                "assistant": row[1]
            })

        return memories


    def store(self, user_message, assistant_reply):
        print("[Memory] store")

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO conversations
            (user_message, assistant_reply)
            VALUES (?, ?)
            """,
            (
                user_message,
                assistant_reply
            )
        )

        connection.commit()
        connection.close()