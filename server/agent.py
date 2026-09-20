from .memory import MemoryManager
from .personality import Personality
from .planner import Planner
from .llm import LLM


class Agent:
    def __init__(self):
        self.memory = MemoryManager()
        self.personality = Personality()
        self.planner = Planner()
        self.llm = LLM()
        
    def needs_memory(self, message):
        text = message.lower().strip()

        personal_terms = [
            "i",
            "i'm",
            "i am",
            "my",
            "me",
            "mine",
            "we",
            "our"
        ]

        return (
            "?" in text
            and any(
                f" {term} " in f" {text} "
                for term in personal_terms
            )
        )

    def chat(self, message: str):
        memories = self.memory.retrieve(message)
        plan = self.planner.create_plan(message, memories)

        if plan["intent"] == "remember":
            content = plan["content"]

            saved = self.memory.add_pinned_memory(content)

            if saved:
                return f"I'll remember that: {content}"

            return f"I already remember that: {content}"

        if plan["intent"] == "recall_memory":
            pinned = self.memory.get_pinned_memories_with_ids()

            if not pinned:
                return "I don't have any pinned memories yet."

            return "I remember:\n" + "\n".join(
                f"- [{memory['id']}] {memory['content']} "
                f"(updated {memory['timestamp']})"
                for memory in pinned
            )

        if plan["intent"] == "list_memories":
            pinned = self.memory.get_pinned_memories_with_ids()

            if not pinned:
                return "There are no pinned memories."

            return "Pinned memories:\n" + "\n".join(
                f"- [{memory['id']}] {memory['content']} "
                f"(updated {memory['timestamp']})"
                for memory in pinned
            )

        if plan["intent"] == "forget_by_id":
            memory_id = plan["memory_id"]

            deleted = self.memory.delete_pinned_memory_by_id(memory_id)

            if deleted:
                return f"I'll forget memory [{memory_id}]."

            return f"I couldn't find memory [{memory_id}]."

        if plan["intent"] == "forget":
            content = plan["content"]

            deleted = self.memory.delete_pinned_memory(content)

            if deleted:
                return f"I'll forget that: {content}"

            return f"I couldn't find that memory: {content}"

        if plan["intent"] == "update_memory":
            memory_id = plan["memory_id"]
            content = plan["content"]

            updated = self.memory.update_pinned_memory(
                memory_id,
                content
            )

            if updated == -1:
                return "I already have another memory with that information."

            if updated:
                return f"I've updated memory [{memory_id}]: {content}"

            return f"I couldn't find memory [{memory_id}]."

        if plan["intent"] == "memory_candidate":
            self.memory.add_pinned_memory(plan["content"])

        pinned_memories = []

        if self.needs_memory(message):
            semantic_memories = self.memory.semantic_retrieve(message)

            pinned_memories = [
                memory["content"]
                for memory in semantic_memories
            ]

        if plan["intent"] == "memory_question":
            if not pinned_memories:
                return "I don't have that saved in my memories."

            memories = []

        prompt = self.personality.build_prompt(
            message,
            memories,
            pinned_memories,
            plan
        )

        reply = self.llm.generate(prompt)
        self.memory.store(message, reply)

        return reply