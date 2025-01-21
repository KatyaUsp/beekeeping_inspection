import os
from vosk_recognition import VoskRecognizer
from answer_matching import AnswerMatcher
from utils.file_utils import save_results_to_csv
import shutil

def main():
    model_path = "models/vosk-model-small-en-us-0.15"
    base_folder_path = "augmented_data/numbers2"
    predefined_answers_path = "data/predefined_answers.json"
    output_file = "data/num2.csv"
    unmatched_folder = "unmatched"  # Folder to store unmatched files

    recognizer = VoskRecognizer(model_path)
    matcher = AnswerMatcher(predefined_answers_path)

    folder_results = {}

    # Create the unmatched folder if it doesn't exist
    os.makedirs(unmatched_folder, exist_ok=True)

    for folder_name in os.listdir(base_folder_path):
        folder_path = os.path.join(base_folder_path, folder_name)
        if not os.path.isdir(folder_path):
            continue

        target_word = folder_name.lower()  # Assume folder name matches target word
        total_files = 0
        correct_predictions = 0

        # Create a subfolder inside unmatched folder for the current target word
        unmatched_target_folder = os.path.join(unmatched_folder, folder_name)
        os.makedirs(unmatched_target_folder, exist_ok=True)

        for file_name in os.listdir(folder_path):
            if file_name.lower().endswith(".wav"):
                file_path = os.path.join(folder_path, file_name)
                recognized_text = recognizer.audio_file_to_text(file_path)
                matched_answer = matcher.match_answer(recognized_text)
                print(recognized_text)
                print(target_word)

                total_files += 1
                if matched_answer.lower() == target_word:
                    correct_predictions += 1
                else:
                    # If the answer doesn't match, move the file to the unmatched folder
                    unmatched_file_path = os.path.join(unmatched_target_folder, file_name)
                    shutil.copy(file_path, unmatched_file_path)  # Move to the unmatched folder
                    print(f"Unmatched: {file_name}")

                print(f"Total files: {total_files}")
                print(f"Correct predictions: {correct_predictions}")

        # Calculate accuracy
        accuracy = (correct_predictions / total_files) * 100 if total_files > 0 else 0
        folder_results[folder_name] = {
            "target": target_word,
            "accuracy": accuracy,
            "correct_predictions": correct_predictions,
            "total_files": total_files
        }

        print(f"Folder: {folder_name}, Accuracy: {accuracy:.2f}% ({correct_predictions}/{total_files})")

    # Save results to CSV
    save_results_to_csv(folder_results, output_file)

if __name__ == "__main__":
    main()
