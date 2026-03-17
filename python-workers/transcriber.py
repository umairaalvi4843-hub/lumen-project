# transcriber.py
# This is our first real Lumen component!

"""
LUMEN TRANSCRIBER MODULE
Purpose: Convert audio to text with word-level timestamps
Input: Path to audio file (.mp3 or .wav)
Output: JSON with transcribed text and timestamps
"""

# === PART 1: IMPORT LIBRARIES ===
# Think of these as hiring specialists for specific jobs

import whisper
# whisper: Our speech-to-text expert
# Like hiring a professional transcriber

import json
# json: Helps us save data in a structured way
# Like using proper forms instead of scribbling on napkins

import os
# os: Helps us work with files and folders
# Like having a personal assistant who knows where everything is

from datetime import timedelta
# timedelta: Helps us format time nicely
# Converts 185.3 seconds → "03:05.3" (minutes:seconds)

import torch
# torch: The engine that runs Whisper
# Like the electricity powering our equipment


# === PART 2: CHECK IF WE HAVE GPU ===
# GPU = Graphics Card = Faster processing
# Think of GPU as a sports car, CPU as a family car

def check_device():
    """
    This function checks if we have a GPU available.
    If yes, we'll use it (much faster).
    If no, we'll use CPU (slower but works).
    """
    if torch.cuda.is_available():
        print("✅ GPU detected! Using NVIDIA GPU")
        print(f"GPU name: {torch.cuda.get_device_name(0)}")
        return "cuda"
    else:
        print("⚠️ No GPU found, using CPU (slower but will work)")
        print("For M4 Mac, we're using CPU - that's fine for testing!")
        return "cpu"

# === PART 3: LOAD THE WHISPER MODEL ===

def load_whisper_model(model_size="tiny"):
    """
    Loads Whisper model into memory.
    
    model_size options (smallest to largest):
    - "tiny"    : 75MB, fastest, least accurate
    - "base"    : 150MB, good for testing
    - "small"   : 500MB, better accuracy
    - "medium"  : 1.5GB, even better
    - "large"   : 3GB, best accuracy, slowest
    
    For learning: Start with "tiny" (instant loading)
    For final project: Use "large" for best results
    """
    
    print(f"📥 Loading Whisper {model_size} model...")
    print("(This happens only once, then model stays in memory)")
    
    # Check what device we're using
    device = check_device()
    
    # Load the model
    # 'model' is now our AI assistant ready to transcribe
    model = whisper.load_model(model_size)
    
    # Move model to appropriate device (GPU/CPU)
    model = model.to(device)
    
    print(f"✅ Whisper {model_size} model loaded successfully!")
    print(f"Model is running on: {device}")
    
    return model

# === PART 4: TRANSCRIBE AUDIO ===

def transcribe_audio(model, audio_path):
    """
    This is the MAIN FUNCTION that does the actual work.
    
    Args:
        model: The loaded Whisper model
        audio_path: Path to your audio file
    
    Returns:
        Dictionary with transcription results
    """
    
    print(f"\n🎤 Transcribing: {os.path.basename(audio_path)}")
    print("⏳ This may take a few seconds...")
    
    # Perform transcription
    # 'transcribe' is like pressing "Start" on a dictation machine
    result = model.transcribe(
        audio_path,
        word_timestamps=True,  # CRITICAL: Get timing for each word!
        verbose=False,         # Don't show progress bars
        language='en'          # Assuming English earnings calls
    )
    
    print("✅ Transcription complete!")
    
    return result

# === PART 5: FORMAT THE RESULTS ===

def format_transcription(result):
    """
    Takes raw Whisper output and makes it readable.
    
    Whisper gives us:
    - Full text
    - Segments (sentences/phrases)
    - Words with timestamps
    
    We'll organize this beautifully.
    """
    
    formatted = {
        "full_text": result["text"].strip(),
        "language": result["language"],
        "segments": []
    }
    
    # Process each segment (usually sentences)
    for segment in result["segments"]:
        seg_info = {
            "start_time": segment["start"],
            "end_time": segment["end"],
            "text": segment["text"].strip(),
            "words": []
        }
        
        # Process each word in this segment
        # 'words' might be None if word_timestamps wasn't enabled
        if "words" in segment:
            for word in segment["words"]:
                word_info = {
                    "word": word["word"].strip(),
                    "start": word["start"],
                    "end": word["end"],
                    "confidence": word.get("confidence", 1.0)
                    # confidence: How sure Whisper is (0-1)
                    # 1.0 = 100% confident
                }
                seg_info["words"].append(word_info)
        
        formatted["segments"].append(seg_info)
    
    return formatted

# === PART 6: SAVE RESULTS TO FILE ===

def save_transcription(formatted_result, audio_path, output_dir="transcriptions"):
    """
    Saves the transcription to a JSON file.
    
    Args:
        formatted_result: Our formatted transcription
        audio_path: Original audio file path (to derive name)
        output_dir: Where to save the JSON
    
    Returns:
        Path to saved JSON file
    """
    
    # Create output directory if it doesn't exist
    # 'exist_ok=True' means: don't error if directory already exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename from audio file
    # Example: "sample_call.mp3" → "sample_call_transcript.json"
    base_name = os.path.basename(audio_path)
    name_without_ext = os.path.splitext(base_name)[0]
    output_file = os.path.join(output_dir, f"{name_without_ext}_transcript.json")
    
    # Save to JSON with nice formatting (indent=2 makes it readable)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(formatted_result, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Transcription saved to: {output_file}")
    return output_file

# === PART 7: PRINT HUMAN-READABLE SUMMARY ===

def print_summary(formatted_result):
    """
    Shows a nice summary of the transcription.
    This is just for us to see what happened.
    """
    
    print("\n" + "="*50)
    print("📋 TRANSCRIPTION SUMMARY")
    print("="*50)
    
    print(f"\n📝 Full text preview:")
    preview = formatted_result["full_text"][:200]
    print(f"   {preview}...")
    
    print(f"\n🗣️ Detected language: {formatted_result['language']}")
    
    total_words = sum(len(seg["words"]) for seg in formatted_result["segments"])
    print(f"📊 Total words: {total_words}")
    
    duration = formatted_result["segments"][-1]["end_time"] if formatted_result["segments"] else 0
    print(f"⏱️  Audio duration: {duration:.2f} seconds")
    
    print(f"\n📑 Segments: {len(formatted_result['segments'])}")
    
    # Show first few words with timestamps
    if formatted_result["segments"] and formatted_result["segments"][0]["words"]:
        print("\n🔍 First few words with timestamps:")
        for word in formatted_result["segments"][0]["words"][:5]:
            print(f"   '{word['word']}': {word['start']:.2f}s → {word['end']:.2f}s")
    
    print("\n" + "="*50)

# === PART 8: MAIN FUNCTION (THE CONTROLLER) ===

def main():
    """
    This is the main function that runs when we execute this script.
    It orchestrates everything:
    1. Load model
    2. Transcribe audio
    3. Format results
    4. Save results
    5. Show summary
    """
    
    print("🚀 LUMEN TRANSCRIBER INITIALIZING")
    print("="*50)
    
    # Define path to our test audio
    # Go up one folder (..) then into datasets/test_audio/
    audio_path = "../datasets/test_audio/speech_sample.wav"
    
    # Check if file exists
    if not os.path.exists(audio_path):
        print(f"❌ Error: Audio file not found at {audio_path}")
        print("Please download a sample file first.")
        return
    
    # Step 1: Load model (tiny for testing)
    print("\n📦 Step 1: Loading Whisper model...")
    model = load_whisper_model("tiny")
    
    # Step 2: Transcribe
    print("\n🎯 Step 2: Starting transcription...")
    result = transcribe_audio(model, audio_path)
    
    # Step 3: Format
    print("\n🔄 Step 3: Formatting results...")
    formatted = format_transcription(result)
    
    # Step 4: Save
    print("\n💾 Step 4: Saving to file...")
    save_transcription(formatted, audio_path)
    
    # Step 5: Show summary
    print("\n📊 Step 5: Generating summary...")
    print_summary(formatted)
    
    print("\n✨ TRANSCRIPTION COMPLETE! ✨")
    print("Check the 'transcriptions' folder for the JSON file.")

# === PART 9: RUN THE SCRIPT ===

# This line is Python's way of saying:
# "If this file is being run directly (not imported), run main()"
if __name__ == "__main__":
    main()