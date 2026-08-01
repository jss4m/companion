from .models import Prompt


class Personality:

    def build_prompt(self, message, memories, pinned_memories, plan):

        return Prompt(
            user_message=message,
            memories=memories,
            pinned_memories=pinned_memories,
            personality="calm, teasing, tender. Replies under 30 words.",
            plan=plan
        )