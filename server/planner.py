class Planner:

    def create_plan(self, message, memories):
        print("[Planner] planning")

        text = message.lower().strip()

        if text.startswith("remember that "):
            return {
                "intent": "remember",
                "content": message[len("remember that "):].strip()
            }

        if text.startswith("forget memory "):
            memory_id = text[len("forget memory "):].strip()

            if memory_id.isdigit():
                return {
                    "intent": "forget_by_id",
                    "memory_id": int(memory_id)
                }

        if text.startswith("forget that "):
            return {
                "intent": "forget",
                "content": message[len("forget that "):].strip()
            }

        if text.startswith("update memory "):
            remainder = message[len("update memory "):].strip()

            if " to " in remainder.lower():
                memory_id_text, content = remainder.split(" to ", 1)

                if memory_id_text.strip().isdigit():
                    return {
                        "intent": "update_memory",
                        "memory_id": int(memory_id_text.strip()),
                        "content": content.strip()
                    }

        if text in [
            "what do you remember about me?",
            "what do you remember?",
            "what do you know about me?"
        ]:
            return {
                "intent": "recall_memory"
            }

        if text in [
            "list memories",
            "show memories",
            "show my memories",
            "list my memories"
        ]:
            return {
                "intent": "list_memories"
            }

        memory_prefixes = [
            "i like ",
            "i love ",
            "i enjoy ",
            "i prefer ",
            "i hate ",
            "i dislike ",
            "i'm a ",
            "i am a ",
            "i'm an ",
            "i am an "
        ]

        if any(text.startswith(prefix) for prefix in memory_prefixes):
            print("[Planner] memory candidate")

            return {
                "intent": "memory_candidate",
                "content": message.strip()
            }

        return {
            "intent": "conversation"
        }