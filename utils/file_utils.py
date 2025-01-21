import csv

def save_results_to_csv(results, output_file):
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Folder", "Target", "Accuracy", "Correct Predictions", "Total Files"])
        for folder, data in results.items():
            writer.writerow([folder, data["target"], data["accuracy"], data["correct_predictions"], data["total_files"]])
