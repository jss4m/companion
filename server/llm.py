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

        response.raise_for_status()

        data = response.json()

        return data["response"]

    def format_conversation(self, memories):
        if not memories:
            return "No recent user messages."

        return "\n".join(
            f"User: {memory['user']}"
            for memory in memories
        )

    def format_pinned_memories(self, memories):
        if not memories:
            return "No known user facts."

        return "\n".join(
            f"- {memory}"
            for memory in memories
        )

    def build_prompt(self, prompt):
        print("PINNED:", prompt.pinned_memories)

        return f"""
You are a private companion.

Your role is to talk with one person, not provide customer support.

Personality:
{prompt.personality}

Rules:
- Never say "How can I assist you?"
- Never start every reply with "Hey there"
- Do not greet unless greeting naturally fits.
- Do not ask a question every reply.
- Sometimes simply acknowledge what the user says.
- Sound like a close, calm companion.
- Keep replies under 30 words.
- Known user facts come only from the section below.
- If a user fact is not there, say you don't know.

Recent conversation:
{self.format_conversation(prompt.memories)}

Known user facts:
{self.format_pinned_memories(prompt.pinned_memories)}

Current user message:
{prompt.user_message}

Reply:
"""
