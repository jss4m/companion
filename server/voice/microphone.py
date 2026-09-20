from pathlib import Path

import sounddevice as sd
import soundfile as sf


class Microphone:

    def __init__(
        self,
        sample_rate=16000,
        channels=1
    ):
        self.sample_rate = sample_rate
        self.channels = channels

    def record(self, duration, output_path):
        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32"
        )

        sd.wait()

        sf.write(
            str(output_path),
            audio,
            self.sample_rate
        )

        return output_path
