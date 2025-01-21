import os
import Levenshtein
from fuzzywuzzy import process
import jellyfish
import vosk
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

# Matching algorithms
def match_levenshtein(recognized_text, predefined_answers):
    best_match = None
    best_score = float('inf')
    for answer in predefined_answers:
        score = Levenshtein.distance(recognized_text, answer.lower())
        if score < best_score:
            best_score = score
            best_match = answer
    return best_match

def match_fuzzy(recognized_text, predefined_answers):
    best_match, confidence = process.extractOne(recognized_text, predefined_answers)
    return best_match

def match_phonetic(recognized_text, predefined_answers):
    recognized_text_soundex = jellyfish.soundex(recognized_text)
    for answer in predefined_answers:
        if jellyfish.soundex(answer) == recognized_text_soundex:
            return answer
    return None

def match_combined(recognized_text, predefined_answers):
    # Phonetic Matching
    recognized_text_soundex = jellyfish.soundex(recognized_text)
    for answer in predefined_answers:
        if jellyfish.soundex(answer) == recognized_text_soundex:
            return answer

    # Fuzzy Matching
    best_match, confidence = process.extractOne(recognized_text, predefined_answers)
    if confidence >= 80:
        return best_match

    # Levenshtein Matching
    best_match = match_levenshtein(recognized_text, predefined_answers)
    return best_match

# Test function for the dataset
def evaluate_algorithms(dataset_path, model_path, predefined_answers):
    results = defaultdict(lambda: {"Levenshtein": 0, "Fuzzy": 0, "Phonetic": 0, "Combined": 0, "Total": 0})
    total_correct = {"Levenshtein": 0, "Fuzzy": 0, "Phonetic": 0, "Combined": 0}
    total_files = 0

    for folder_name in os.listdir(dataset_path):
        folder_path = os.path.join(dataset_path, folder_name)
        if os.path.isdir(folder_path):
            print(f"Evaluating folder: {folder_name}")
            for file_name in os.listdir(folder_path):
                if file_name.lower().endswith(".wav"):
                    file_path = os.path.join(folder_path, file_name)
                    recognized_text = audio_to_text_vosk(file_path, model_path)
                    
                    results[folder_name]["Total"] += 1
                    total_files += 1
                    print(folder_name, total_files)
                    print(recognized_text)
                

                    # Evaluate each algorithm
                    if match_levenshtein(recognized_text, predefined_answers) == folder_name:
                        results[folder_name]["Levenshtein"] += 1
                        total_correct["Levenshtein"] += 1
                        print('Levenstein matched')
                    if match_fuzzy(recognized_text, predefined_answers) == folder_name:
                        results[folder_name]["Fuzzy"] += 1
                        total_correct["Fuzzy"] += 1
                        print('Fuzzy matched')
                    if match_phonetic(recognized_text, predefined_answers) == folder_name:
                        results[folder_name]["Phonetic"] += 1
                        total_correct["Phonetic"] += 1
                        print('Phonetic matched')
                    if match_combined(recognized_text, predefined_answers) == folder_name:
                        results[folder_name]["Combined"] += 1
                        total_correct["Combined"] += 1
                        print('Combined matched')

    # Print folder-wise accuracy
    for answer, counts in results.items():
        total = counts["Total"]
        print(f"Results for '{answer}':")
        print(f"  Levenshtein Accuracy: {counts['Levenshtein'] / total:.2%}")
        print(f"  Fuzzy Accuracy: {counts['Fuzzy'] / total:.2%}")
        print(f"  Phonetic Accuracy: {counts['Phonetic'] / total:.2%}")
        print(f"  Combined Accuracy: {counts['Combined'] / total:.2%}")
        print()

    # Print average accuracy across all folders
    print("Average Accuracy Across All Folders:")
    for method, correct_count in total_correct.items():
        print(f"  {method}: {correct_count / total_files:.2%}")

# Base dataset paths
source_base_paths = ["augmented_data", "records"]

# Function to collect all subfolder names
def collect_all_folders(base_paths):
    all_folders = set()
    for base_path in base_paths:
        for root, dirs, _ in os.walk(base_path):
            for sub_dir in dirs:
                all_folders.add(sub_dir)
    return sorted(all_folders)  # Sort alphabetically for consistency


# Usage
if __name__ == "__main__":
    dataset_path = "unmatched" 
    model_path = "models/vosk-model-small-en-us-0.15"
    predefined_answers = collect_all_folders(source_base_paths)
    evaluate_algorithms(dataset_path, model_path, predefined_answers)
