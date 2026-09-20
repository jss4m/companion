from pathlib import Path

from .tts import TTS
from .playback import Playback


class VoiceOutput:

    def __init__(self, model_path):
        self.tts = TTS(model_path)
        self.playback = Playback()

    def speak(self, text):
        output_path = Path("voice_output.wav")

        self.tts.synthesize(
            text,
            output_path
        )

        self.playback.play(output_path)

        return output_path