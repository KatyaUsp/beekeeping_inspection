from gtts import gTTS
from pydub import AudioSegment, effects
from pydub.generators import WhiteNoise
import os
import random

def generate_base_audio(answer, output_dir="base_audio"):
    """Generate base audio file for each predefined answer."""
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{answer.replace(' ', '_').lower()}.wav")
    
    # Generate audio with gTTS and save as MP3 temporarily
    tts = gTTS(text=answer, lang='en', slow=False)
    temp_path = output_path.replace(".wav", ".mp3")
    tts.save(temp_path)
    
    # Convert to WAV and ensure 16 kHz mono
    audio = AudioSegment.from_mp3(temp_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(output_path, format="wav")
    os.remove(temp_path)  # Clean up temporary MP3 file
    
    return output_path

def augment_audio(base_audio_path, output_dir, count=10):
    """Generate augmented versions of the base audio."""
    os.makedirs(output_dir, exist_ok=True)
    base_audio = AudioSegment.from_file(base_audio_path)
    
    for i in range(count):
        # Apply random augmentations
        augmented_audio = base_audio
        augmented_audio = change_speed(augmented_audio, random.uniform(0.9, 1.1))
        augmented_audio = change_pitch(augmented_audio, random.randint(-2, 2))
        augmented_audio = add_noise(augmented_audio, noise_level=random.uniform(0.01, 0.05))
        augmented_audio = adjust_volume(augmented_audio, random.uniform(-3, 3))
        
        # Save augmented file as WAV (16 kHz mono)
        augmented_audio = augmented_audio.set_frame_rate(16000).set_channels(1)
        augmented_audio.export(os.path.join(output_dir, f"{i+1}.wav"), format="wav")

def change_speed(audio, speed=1.0):
    """Change the speed of the audio."""
    return audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * speed)}).set_frame_rate(audio.frame_rate)

def change_pitch(audio, semitones=0):
    """Change the pitch of the audio by semitones."""
    new_sample_rate = int(audio.frame_rate * (2.0 ** (semitones / 12.0)))
    return audio._spawn(audio.raw_data, overrides={"frame_rate": new_sample_rate}).set_frame_rate(audio.frame_rate)

def add_noise(audio, noise_level=0.02):
    """Add white noise to the audio."""
    noise = WhiteNoise().to_audio_segment(duration=len(audio), volume=-30)  # Generate white noise
    return audio.overlay(noise - (1 / noise_level), position=0)

def adjust_volume(audio, gain_db=0):
    """Adjust the volume of the audio."""
    return audio + gain_db

# Predefined answers
predefined_answers = [
    "White", "Yellow", "Red", "Green", "Blue",  # Colors
    "High", "Normal"                            # Temperature levels
]
predefined_answers.extend([str(num) for num in range(10, 21)])  # Add numbers from 10 to 20

# Generate dataset
for answer in predefined_answers:
    print(f"Generating data for: {answer}")
    base_audio_path = generate_base_audio(answer)  # Generate base audio
    output_folder = f"augmented_data/{answer.replace(' ', '_').lower()}"  # Folder for augmented files
    augment_audio(base_audio_path, output_folder, count=2000)  # Create 2000 augmented files
