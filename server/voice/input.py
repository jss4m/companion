from pathlib import Path

from .microphone import Microphone
from .stt import STT


class VoiceInput:

    def __init__(self):
        self.microphone = Microphone()
        self.stt = STT()

    def listen(self, duration=5):
        audio_path = Path("voice_input.wav")

        self.microphone.record(
            duration=duration,
            output_path=audio_path
        )

        result = self.stt.transcribe(audio_path)

        return result
