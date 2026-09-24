"""Mock Text-to-Speech implementation generating valid WAV audio bytes."""

import io
import math
import struct
import wave

from zoom_ai_copilot.tts.base import TextToSpeech


class MockTTS(TextToSpeech):
    """Mock TTS generating valid synthetic WAV audio without external API calls."""

    def __init__(
        self,
        sample_rate: int = 16000,
        frequency: float = 440.0,
        duration_sec: float = 0.3,
    ) -> None:
        self.sample_rate = sample_rate
        self.frequency = frequency
        self.duration_sec = duration_sec

    async def synthesize(self, text: str) -> bytes:
        """Generate a valid PCM 16-bit WAV file with a short test tone."""
        num_samples = int(self.sample_rate * self.duration_sec)
        bio = io.BytesIO()

        with wave.open(bio, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)

            # Generate short gentle sine tone
            frames = bytearray()
            for i in range(num_samples):
                # Envelope to avoid click sounds at start/end
                env = min(1.0, i / 200, (num_samples - i) / 200)
                val = int(
                    32767.0
                    * 0.2
                    * env
                    * math.sin(2.0 * math.pi * self.frequency * i / self.sample_rate)
                )
                frames.extend(struct.pack("<h", val))

            wf.writeframes(frames)

        return bio.getvalue()
