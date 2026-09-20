import json
import math

from .database import get_connection
from .embeddings import Embeddings


class MemoryManager:

    def __init__(self):
        self.embeddings = Embeddings()


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


    def get_pinned_memories_with_ids(self):
        print("[Memory] pinned retrieve with ids")

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, timestamp, content
            FROM pinned_memories
            ORDER BY id DESC
            """
        )

        rows = cursor.fetchall()

        connection.close()

        return [
            {
                "id": row[0],
                "timestamp": row[1],
                "content": row[2]
            }
            for row in rows
        ]


    def normalize_memory(self, content):
        normalized = content.strip().lower()

        while normalized.endswith((".", "!", "?")):
            normalized = normalized[:-1].rstrip()

        return normalized


    def add_pinned_memory(self, content):
        print("[Memory] pinned store")

        connection = get_connection()
        cursor = connection.cursor()

        normalized_content = self.normalize_memory(content)

        cursor.execute(
            """
            SELECT id, content
            FROM pinned_memories
            """
        )

        rows = cursor.fetchall()

        for row in rows:
            existing_normalized = self.normalize_memory(row[1])

            if existing_normalized == normalized_content:
                connection.close()
                return False

        embedding = self.embeddings.generate(content)
        embedding_json = json.dumps(embedding)

        cursor.execute(
            """
            INSERT INTO pinned_memories
            (content, embedding)
            VALUES (?, ?)
            """,
            (
                content.strip(),
                embedding_json
            )
        )

        connection.commit()
        connection.close()

        return True


    def update_pinned_memory(self, memory_id, content):
        print("[Memory] pinned update")

        connection = get_connection()
        cursor = connection.cursor()

        normalized_content = self.normalize_memory(content)

        cursor.execute(
            """
            SELECT id, content
            FROM pinned_memories
            WHERE id != ?
            """,
            (memory_id,)
        )

        rows = cursor.fetchall()

        for row in rows:
            existing_normalized = self.normalize_memory(row[1])

            if existing_normalized == normalized_content:
                connection.close()
                return -1

        embedding = self.embeddings.generate(content)
        embedding_json = json.dumps(embedding)

        cursor.execute(
            """
            UPDATE pinned_memories
            SET content = ?,
                embedding = ?,
                timestamp = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                content.strip(),
                embedding_json,
                memory_id
            )
        )

        updated = cursor.rowcount

        connection.commit()
        connection.close()

        return updated


    def delete_pinned_memory(self, content):
        print("[Memory] pinned delete")

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM pinned_memories
            WHERE content = ?
            """,
            (content,)
        )

        deleted = cursor.rowcount

        connection.commit()
        connection.close()

        return deleted


    def delete_pinned_memory_by_id(self, memory_id):
        print("[Memory] pinned delete by id")

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM pinned_memories
            WHERE id = ?
            """,
            (memory_id,)
        )

        deleted = cursor.rowcount

        connection.commit()
        connection.close()

        return deleted


    def backfill_embeddings(self):
        print("[Memory] embedding backfill")

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, content
            FROM pinned_memories
            WHERE embedding IS NULL
            ORDER BY id
            """
        )

        rows = cursor.fetchall()

        updated = 0

        for memory_id, content in rows:
            embedding = self.embeddings.generate(content)
            embedding_json = json.dumps(embedding)

            cursor.execute(
                """
                UPDATE pinned_memories
                SET embedding = ?
                WHERE id = ?
                """,
                (
                    embedding_json,
                    memory_id
                )
            )

            updated += cursor.rowcount

        connection.commit()
        connection.close()

        return updated


    def cosine_similarity(self, vector_a, vector_b):
        if len(vector_a) != len(vector_b):
            return 0.0

        dot_product = sum(
            a * b
            for a, b in zip(vector_a, vector_b)
        )

        magnitude_a = math.sqrt(
            sum(a * a for a in vector_a)
        )

        magnitude_b = math.sqrt(
            sum(b * b for b in vector_b)
        )

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return dot_product / (magnitude_a * magnitude_b)


    def semantic_retrieve(self, message, limit=3, threshold=0.6):
        print("[Memory] semantic retrieve")

        query_embedding = self.embeddings.generate(message)

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, content, embedding
            FROM pinned_memories
            WHERE embedding IS NOT NULL
            """
        )

        rows = cursor.fetchall()

        connection.close()

        matches = []

        for memory_id, content, embedding_json in rows:
            stored_embedding = json.loads(embedding_json)

            similarity = self.cosine_similarity(
                query_embedding,
                stored_embedding
            )

            if similarity >= threshold:
                matches.append({
                    "id": memory_id,
                    "content": content,
                    "similarity": similarity
                })

        matches.sort(
            key=lambda memory: memory["similarity"],
            reverse=True
        )

        return matches[:limit]


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