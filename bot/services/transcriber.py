from faster_whisper import WhisperModel


class Transcriber:
    def __init__(self, model_name: str) -> None:
        self.model = WhisperModel(model_name, device="cpu", compute_type="int8")

    def transcribe(self, audio_path: str) -> str:
        segments, _ = self.model.transcribe(audio_path, beam_size=5, language=None)
        text = " ".join(segment.text.strip() for segment in segments)
        return text if text.strip() else "Речь не распознана."
