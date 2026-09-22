from pathlib import Path
import re

from faster_whisper import WhisperModel


class STT:
    def __init__(
        self,
        model_size="base",
        device="cpu",
        compute_type="int8"
    ):
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )

    def transcribe(self, audio_path):
        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )

        segments, info = self.model.transcribe(
            str(audio_path),
            beam_size=5
        )

        text = " ".join(
            segment.text.strip()
            for segment in segments
        ).strip()

        if self.is_non_speech(text):
            text = ""

        return {
            "text": text,
            "language": info.language,
            "language_probability": info.language_probability
        }

    def is_non_speech(self, text):
        if not text:
            return True

        normalized = text.strip().lower()

        if not normalized:
            return True

        normalized = re.sub(r"\s+", " ", normalized)

        non_speech_patterns = [
            r"^[.\s]+$",
            r"^[…\s]+$",
            r"^[-–—\s]+$",
            r"^\*+\s*$",
            r"^\[blank_audio\]$",
            r"^\[silence\]$",
            r"^\(silence\)$",
            r"^\(blank audio\)$",
        ]

        return any(
            re.fullmatch(pattern, normalized)
            for pattern in non_speech_patterns
        )
