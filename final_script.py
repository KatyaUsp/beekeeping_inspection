import os
import random
import json
import Levenshtein
from vosk import Model, KaldiRecognizer
import wave

# Speech recognition 
def recognize_speech(audio_path, model_path):
    model = Model(model_path)
    wf = wave.open(audio_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
        raise ValueError("Audio file must be mono, 16-bit PCM, and 16 kHz.")
    recognizer = KaldiRecognizer(model, wf.getframerate())
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        recognizer.AcceptWaveform(data)
    result = json.loads(recognizer.FinalResult())
    return result.get("text", "").strip()

# Matching predefined answers
def match_predefined(recognized_text, predefined_answers):
    recognized_text_lower = recognized_text.lower()
    if recognized_text_lower in predefined_answers:
        return predefined_answers[recognized_text_lower]
    return None

# Levenshtein matching algorithm for unmatched words
def match_levenshtein_unmatched(recognized_text, predefined_answers):
    best_match = None
    best_score = float('inf')
    for answer, value in predefined_answers.items():
        score = Levenshtein.distance(recognized_text.lower(), answer.lower())
        if score < best_score:
            best_score = score
            best_match = value
    return best_match

# Select random file from random folder for testing
def select_random_file(dataset_path):
    folder_list = [folder for folder in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, folder))]
    if not folder_list:
        raise FileNotFoundError("No folders found in the dataset directory.")
    random_folder = random.choice(folder_list)
    folder_path = os.path.join(dataset_path, random_folder)
    file_list = [file for file in os.listdir(folder_path) if file.lower().endswith(".wav")]
    if not file_list:
        raise FileNotFoundError(f"No .wav files found in folder: {random_folder}")
    random_file = random.choice(file_list)
    return random_folder, os.path.join(folder_path, random_file)


def main():
    model_path = "models/vosk-model-small-en-us-0.15"
    # Folder containing folders with audio files
    dataset_path = "test_dataset"  
    predefined_answers_path = "data/predefined_answers.json"

    # Loading predefined answers from JSON dictionary
    with open(predefined_answers_path, "r") as file:
        predefined_answers = json.load(file)

    # Select a random file from a random folder
    try:
        folder_name, audio_path = select_random_file(dataset_path)
        print(f"Selected Folder: {folder_name}")
        print(f"Selected File: {audio_path}")

        # Recognize text from audio
        recognized_text = recognize_speech(audio_path, model_path)
        print(f"Recognized Text: {recognized_text}")

        # Match with predefined answers
        matched_answer = match_predefined(recognized_text, predefined_answers)
        if matched_answer:
            print(f"Matched Answer: {matched_answer}")
        else:
            # If no match, Levenshtein matching
            matched_answer = match_levenshtein_unmatched(recognized_text, predefined_answers)
            print(f"Matched using Levenshtein: {matched_answer}")

        # Print final result
        print(f"Final Matched Answer: {matched_answer}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
