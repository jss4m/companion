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
    
    
    def get_pinned_memories(self):
        print("[Memory] pinned retrieve")

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT content
            FROM pinned_memories
            ORDER BY id DESC
            """
        )

        rows = cursor.fetchall()

        connection.close()

        return [
            row[0]
            for row in rows
        ]


    def add_pinned_memory(self, content):
        print("[Memory] pinned store")

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO pinned_memories
            (content)
            VALUES (?)
            """,
            (content,)
        )

        connection.commit()
        connection.close()
        
    def get_relevant_pinned_memories(self, message):
        pinned = self.get_pinned_memories()

        if not pinned:
            return []

        message_words = set(message.lower().split())

        relevant = []

        for memory in pinned:
            memory_words = set(memory.lower().split())

            if message_words & memory_words:
                relevant.append(memory)

        if relevant:
            return relevant

        return pinned[:2]