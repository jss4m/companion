class Planner:

    def create_plan(self, message, memories):
        print("[Planner] planning")

        text = message.lower()

        if any(word in text for word in ["hello", "hi", "hey"]):
            return {
                "intent": "greeting"
            }

        if "?" in message:
            return {
                "intent": "question"
            }

        return {
            "intent": "conversation"
        }