from pathlib import Path
import wave

from piper import PiperVoice, SynthesisConfig


class TTS:

    def __init__(self, model_path, config_path=None):
        self.model_path = Path(model_path)

        self.config_path = (
            Path(config_path)
            if config_path
            else None
        )

        self.voice = PiperVoice.load(
            self.model_path,
            config_path=self.config_path
        )

    def synthesize(self, text, output_path):
        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with wave.open(str(output_path), "wb") as wav_file:
            self.voice.synthesize_wav(
                text,
                wav_file,
                SynthesisConfig()
            )

        return output_path