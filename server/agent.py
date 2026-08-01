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

    def chat(self, message: str):
        memories = self.memory.retrieve(message)

        plan = self.planner.create_plan(message, memories)

        prompt = self.personality.build_prompt(message, memories, plan)
        
        reply = self.llm.generate(prompt)

        self.memory.store(message, reply)

        return reply