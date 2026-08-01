class MemoryManager:
    def __init__(self):
        self.history = []

    def retrieve(self, message):
        print("[Memory] retrieve")

        return self.history[-5:]

    def store(self, user_message, assistant_reply):
        print("[Memory] store")

        self.history.append({
            "user": user_message,
            "assistant": assistant_reply
        })