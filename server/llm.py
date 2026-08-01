class LLM:

    def generate(self, prompt):

        print("[LLM] generating")

        intent = prompt.plan["intent"]

        if intent == "greeting":
            return "Hello. I'm here."

        if intent == "question":
            return "I am listening. Let me think."

        return "I'm here with you."