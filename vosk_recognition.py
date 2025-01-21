import os
import wave
import json
from vosk import Model, KaldiRecognizer

class VoskRecognizer:
    def __init__(self, model_path):
        self.model = Model(model_path)

    def audio_file_to_text(self, file_path):
        wf = wave.open(file_path, "rb")

        # Check audio format
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in [8000, 16000]:
            raise ValueError(f"File {file_path} must be mono and 16 kHz.")
        
        recognizer = KaldiRecognizer(self.model, wf.getframerate())
        results = []

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                results.append(result["text"])
        
        final_result = json.loads(recognizer.FinalResult())
        results.append(final_result["text"])
        return " ".join(results)
