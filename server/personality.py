from .models import Prompt


class Personality:

    def build_prompt(self, message, memories, plan):

        return Prompt(
            user_message=message,
            memories=memories,
            personality="calm, teasing, tender. Replies under 30 words.",
            plan=plan
        )