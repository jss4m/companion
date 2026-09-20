import winsound
from pathlib import Path


class Playback:

    def play(self, audio_path):
        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )

        winsound.PlaySound(
            str(audio_path),
            winsound.SND_FILENAME
        )