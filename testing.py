import os
import Levenshtein
import vosk
from fuzzywuzzy import process
import jellyfish
from vosk import Model, KaldiRecognizer
import wave
import json
from collections import defaultdict


# Recognizer function using Vosk
def audio_to_text_vosk(file_path, model_path):
    model = Model(model_path)
    vosk.SetLogLevel(-1)
    wf = wave.open(file_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
        raise ValueError(f"File {file_path} must be mono and 16 kHz.")
    recognizer = KaldiRecognizer(model, wf.getframerate())
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        recognizer.AcceptWaveform(data)
    result = json.loads(recognizer.FinalResult())
    return result.get("text", "").strip()

def match_levenshtein(recognized_text, predefined_answers):
    best_match = None
    best_score = float('inf')
    for answer in predefined_answers:
        score = Levenshtein.distance(recognized_text, answer.lower())
        if score < best_score:
            best_score = score
            best_match = answer
    return best_match


dataset_path = "test_dataset" 
model_path = "models/vosk-model-small-en-us-0.15"
folder_name = 'blue'
folder_path = os.path.join(dataset_path, folder_name)
total_files = 0
source_base_paths = ["augmented_data", "records"]

# Function to collect all subfolder names
def collect_all_folders(base_paths):
    all_folders = set()
    for base_path in base_paths:
        for root, dirs, _ in os.walk(base_path):
            for sub_dir in dirs:
                all_folders.add(sub_dir)
    return sorted(all_folders)  # Sort alphabetically for consistency

predefined_answers = collect_all_folders(source_base_paths)

if os.path.isdir(folder_path):
    print(f"Evaluating folder: {folder_name}")
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(".wav"):
            file_path = os.path.join(folder_path, file_name)
            recognized_text = audio_to_text_vosk(file_path, model_path)
            total_files+=1
            print(file_path)
            print(total_files)

            print(match_levenshtein(recognized_text, predefined_answers))
            print('folder', folder_name)
            if match_levenshtein(recognized_text, predefined_answers) == folder_name:
                print('match')
