import os
import random
import shutil

# Paths
source_base_paths = ["augmented_data", "records"]  # Base paths for the source datasets
test_dataset_path = "test_dataset"  # Path to store the test dataset

# Create a new folder for the test dataset
os.makedirs(test_dataset_path, exist_ok=True)

def generate_flat_test_dataset(source_paths, dest_path, sample_size=30):
    """
    Generate a test dataset by randomly selecting files from each subfolder and placing them into a flat structure.
    
    Args:
        source_paths (list): List of paths to source folders containing subfolders.
        dest_path (str): Path to save the test dataset.
        sample_size (int): Number of files to select from each folder.
    """
    for source_path in source_paths:
        for root, dirs, _ in os.walk(source_path):
            for sub_dir in dirs:
                src_subfolder = os.path.join(root, sub_dir)
                dest_subfolder = os.path.join(dest_path, sub_dir)
                
                # Create a folder in the test dataset for each subfolder
                os.makedirs(dest_subfolder, exist_ok=True)
                
                # Get all files in the source subfolder
                files = [f for f in os.listdir(src_subfolder) if os.path.isfile(os.path.join(src_subfolder, f))]
                
                # Randomly select files (up to the sample size)
                selected_files = random.sample(files, min(len(files), sample_size))
                
                # Copy selected files to the destination subfolder
                for file in selected_files:
                    src_file = os.path.join(src_subfolder, file)
                    dest_file = os.path.join(dest_subfolder, file)
                    shutil.copy(src_file, dest_file)
                    print(f"Copied {src_file} to {dest_file}")

# Generate the flat test dataset
generate_flat_test_dataset(source_base_paths, test_dataset_path)

print("Test dataset generation complete!")
