from .input import VoiceInput
from .output import VoiceOutput


class VoicePipeline:

    def __init__(self, agent, model_path):
        self.agent = agent
        self.input = VoiceInput()
        self.output = VoiceOutput(model_path)

    def run(self, duration=5):
        voice_input = self.input.listen(duration)

        text = voice_input["text"]

        if not text:
            return {
                "text": "",
                "reply": ""
            }

        reply = self.agent.chat(text)

        self.output.speak(reply)

        return {
            "text": text,
            "reply": reply
        }