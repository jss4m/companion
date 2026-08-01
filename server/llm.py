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

    def build_prompt(self, prompt):

        return f"""
You are a private personal companion.

Personality:
{prompt.personality}

Conversation:
{prompt.memories}

User:
{prompt.user_message}

Reply naturally and keep it under 30 words.
"""