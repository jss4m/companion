from click import prompt
import requests


class LLM:

    def generate(self, prompt):

        print("[LLM] generating")

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:3b",
                "prompt": self.build_prompt(prompt),
                "stream": False
            }
        )

        data = response.json()

        return data["response"]

    def format_memories(self, memories):
        if not memories:
            return "No pinned information."

        return "\n".join(
          f"- {memory}"
           for memory in memories
        )

    def build_prompt(self, prompt):

        print("PINNED:", prompt.pinned_memories)

        return f"""
You are a private personal companion.

Follow these rules:
- Keep replies under 30 words.
- Be calm, warm, and slightly teasing.
- Do not give advice unless the user asks.
- Answer the user's actual question first.

Important user preferences:
{prompt.pinned_memories}

Recent conversation:
Pinned user information:
{self.format_memories(prompt.pinned_memories)}

Current user message:
{prompt.user_message}

Your response:
"""