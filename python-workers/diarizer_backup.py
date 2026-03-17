"""
DIARIZER.PY - LAYER 2: Speaker Identification for Lumen Project

What this does:
1. Takes an audio file
2. Identifies different speakers
3. Tells us when each person speaks

This is like having a voice expert who can say:
"SPEAKER_01 spoke from 0-5 seconds, SPEAKER_02 spoke from 5-10 seconds"
"""

# ============================================
# PART 1: IMPORTS - Bringing in the tools we need
# ============================================

import torch
"""
What: The engine that runs AI models
Why: pyannote (our diarization model) runs on PyTorch
Analogy: Like having electricity to power your appliances
"""

from pyannote.audio import Pipeline
"""
What: The actual speaker diarization model from Hugging Face
Why: This AI model identifies different voices in audio
Analogy: Like hiring a voice recognition expert
"""

from pyannote.core import Segment
"""
What: Helps handle time segments
Why: We need to work with start and end times
Analogy: Like having a stopwatch that records exact moments
"""

import os
"""
What: File operations
Why: To check if files exist, create folders, save results
Analogy: Like having a filing system for your documents
"""

import json
"""
What: Save data in structured format
Why: So we can easily read and use the results later
Analogy: Like using labeled folders instead of loose papers
"""

from dotenv import load_dotenv
"""
What: Reads secret tokens from .env file
Why: To keep our Hugging Face token secure
Analogy: Like using a key card instead of writing password on a sticky note
"""

# ============================================
# PART 2: TOKEN MANAGEMENT - Getting access to Hugging Face
# ============================================

def check_token():
    """
    Check if Hugging Face token exists in .env file
    """
    # Load environment variables
    load_dotenv()
    
    # Get token and remove any quotes or spaces
    token = os.getenv("HUGGINGFACE_TOKEN", "").strip().strip('"').strip("'")
    
    if not token:
        print("\n" + "="*50)
        print("❌ ERROR: No Hugging Face token found!")
        print("="*50)
        print("\nPlease follow these steps:")
        print("1. Go to https://huggingface.co/settings/tokens")
        print("2. Create a token (or use existing one)")
        print("3. Add this to your .env file:")
        print("   HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxx")
        return None
    
    # Verify token format
    if not token.startswith("hf_"):
        print(f"\n⚠️ Warning: Token doesn't start with 'hf_'")
        print(f"Current token: {token[:10]}...")
        print("Make sure you copied the full token from Hugging Face")
    
    print(f"✅ Hugging Face token found! (starts with: {token[:10]}...)")
    return token

# ============================================
# PART 3: MODEL LOADING - Getting the AI ready to work
# ============================================

def load_diarization_pipeline(token):
    """
    Load the speaker diarization model from Hugging Face
    
    Args:
        token: Hugging Face authentication token
    
    Returns:
        Loaded pipeline object or None if failed
    
    This is like:
    - Hiring a voice expert
    - They need to study (download model)
    - Takes 2-5 minutes first time (downloading 2GB)
    - Faster after that (model is cached)
    """
    print("\n" + "="*50)
    print("📥 Loading speaker diarization model...")
    print("="*50)
    print("(This downloads ~2GB model - takes 2-5 minutes first time)")
    print("(Subsequent runs will be faster - model is cached)")
    
    try:
        # Load the pipeline from Hugging Face
        # 'use_auth_token' is like showing your library card
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=token
        )
        
        # Check what hardware we have and use the fastest available
        if torch.cuda.is_available():
            # NVIDIA GPU - fastest
            pipeline = pipeline.to(torch.device("cuda"))
            print("✅ Using NVIDIA GPU (fastest!)")
            
        elif torch.backends.mps.is_available():
            # Apple M1/M2/M3/M4 GPU - also very fast
            pipeline = pipeline.to(torch.device("mps"))
            print("✅ Using Apple M-series GPU (fast!)")
            print("   Your M4 chip will work great!")
            
        else:
            # CPU - slower but works everywhere
            print("⚠️ Using CPU (slower but will work)")
            print("   For faster processing, consider using a GPU")
        
        print("✅ Diarization model loaded successfully!")
        return pipeline
        
    except Exception as e:
        print(f"\n❌ Failed to load model: {e}")
        print("\nCommon issues:")
        print("1. Token is invalid - check your .env file")
        print("2. No internet connection")
        print("3. Hugging Face is down (rare)")
        return None

# ============================================
# PART 4: AUDIO PROCESSING - The actual diarization work
# ============================================

def diarize_audio(pipeline, audio_path):
    """
    Identify who spoke when in the audio file
    
    Args:
        pipeline: Loaded diarization model
        audio_path: Path to the audio file
    
    Returns:
        List of segments with speaker labels, or empty list if failed
    
    This is the MAIN FUNCTION that does the actual work:
    - Takes the audio
    - Runs it through the AI model
    - Returns segments with speaker labels
    """
    
    print(f"\n" + "="*50)
    print(f"🎙️ Analyzing speakers in: {os.path.basename(audio_path)}")
    print("="*50)
    print("⏳ This may take 10-30 seconds depending on audio length...")
    
    try:
        # Run the diarization pipeline on the audio file
        # This is where the magic happens!
        diarization = pipeline(audio_path)
        
        # Convert the output to a list we can work with
        segments = []
        
        # 'itertracks' gives us each segment one by one
        # yield_label=True gives us the speaker name
        for segment, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                "speaker": speaker,                    # Who spoke (e.g., "SPEAKER_01")
                "start": round(segment.start, 2),      # When they started (rounded to 0.01s)
                "end": round(segment.end, 2),          # When they stopped
                "duration": round(segment.end - segment.start, 2)  # How long they spoke
            })
        
        # Count unique speakers
        unique_speakers = set(s['speaker'] for s in segments)
        
        print(f"\n✅ Analysis complete!")
        print(f"📊 Found {len(unique_speakers)} different speakers")
        print(f"📊 Total speaking segments: {len(segments)}")
        
        return segments
        
    except Exception as e:
        print(f"\n❌ Diarization failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check if the audio file is valid")
        print("2. Make sure the file path is correct")
        print("3. Try with a shorter audio file first")
        return []

# ============================================
# PART 5: FORMATTING - Making the results organized
# ============================================

def format_diarization(segments):
    """
    Organize diarization results into a clean structure
    
    Args:
        segments: Raw list of segments from diarize_audio()
    
    Returns:
        Dictionary with organized speaker information
    
    This is like taking raw notes and organizing them
    into a proper report with summaries and statistics
    """
    
    if not segments:
        return {"error": "No segments to format"}
    
    # Group segments by speaker
    # This creates a dictionary where:
    # Key = speaker name (e.g., "SPEAKER_01")
    # Value = list of all segments from that speaker
    speakers = {}
    for seg in segments:
        speaker = seg["speaker"]
        if speaker not in speakers:
            speakers[speaker] = []
        speakers[speaker].append(seg)
    
    # Calculate statistics for each speaker
    speakers_info = {}
    total_duration = sum(s["duration"] for s in segments)
    
    for speaker, spk_segments in speakers.items():
        speaker_duration = sum(s["duration"] for s in spk_segments)
        speakers_info[speaker] = {
            "segments_count": len(spk_segments),        # How many times they spoke
            "total_time": round(speaker_duration, 2),   # Total speaking time
            "percentage": round((speaker_duration / total_duration) * 100, 1),  # % of conversation
            "segments": spk_segments                     # The actual segments
        }
    
    # Create the final formatted structure
    formatted = {
        "total_speakers": len(speakers),
        "total_segments": len(segments),
        "total_duration": round(total_duration, 2),
        "speakers": speakers_info,
        "all_segments": segments  # Keep the original list for alignment with transcription
    }
    
    return formatted

# ============================================
# PART 6: SAVING - Writing results to a file
# ============================================

def save_diarization(formatted_result, audio_path, output_dir="diarizations"):
    """
    Save diarization results to a JSON file
    
    Args:
        formatted_result: The formatted data from format_diarization()
        audio_path: Original audio file path (to derive filename)
        output_dir: Folder to save in (default: "diarizations")
    
    Returns:
        Path to saved JSON file or None if failed
    
    This is like:
    - Taking your organized report
    - Putting it in a labeled folder
    - Saving it for later use
    """
    
    try:
        # Create the output directory if it doesn't exist
        # exist_ok=True means: don't error if folder already exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename from audio file
        # Example: "speech_sample.wav" → "speech_sample_speakers.json"
        base_name = os.path.basename(audio_path)
        name_without_ext = os.path.splitext(base_name)[0]
        output_file = os.path.join(output_dir, f"{name_without_ext}_speakers.json")
        
        # Save to JSON file
        # indent=2 makes the JSON readable (pretty printed)
        # ensure_ascii=False keeps special characters (like é, ñ) intact
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(formatted_result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"\n❌ Failed to save results: {e}")
        return None

# ============================================
# PART 7: VISUALIZATION - Showing a simple timeline
# ============================================

def print_timeline(segments, max_width=50):
    """
    Print a simple ASCII timeline of who spoke when
    
    Args:
        segments: List of segments with speaker and timestamps
        max_width: Width of the timeline in characters
    
    This creates a visual representation like:
    SPEAKER_01: [████████░░░░░░░░░░░░] 45%
    SPEAKER_02: [░░░░░░░░██████░░░░░░] 30%
    SPEAKER_03: [░░░░░░░░░░░░░░██████] 25%
    """
    
    if not segments:
        return
    
    # Get total duration
    total_duration = max(s["end"] for s in segments)
    
    # Group by speaker
    speakers = {}
    for seg in segments:
        spk = seg["speaker"]
        if spk not in speakers:
            speakers[spk] = []
        speakers[spk].append(seg)
    
    print("\n📊 Speaker Timeline:")
    print("-" * 60)
    
    # For each speaker, create a timeline
    for speaker in sorted(speakers.keys()):
        # Calculate total speaking time
        speaker_time = sum(s["duration"] for s in speakers[speaker])
        percentage = (speaker_time / total_duration) * 100
        
        # Create a simple bar chart
        bar_length = int((percentage / 100) * max_width)
        bar = "█" * bar_length + "░" * (max_width - bar_length)
        
        print(f"{speaker}: [{bar}] {percentage:.1f}%")
    
    print("-" * 60)

# ============================================
# PART 8: MAIN FUNCTION - The conductor of our orchestra
# ============================================

def main():
    """
    Main function that orchestrates everything
    
    This is like a conductor leading an orchestra:
    1. Check we have all tools (token)
    2. Get the musicians ready (load model)
    3. Perform the piece (run diarization)
    4. Write down what happened (save results)
    5. Show the audience (print summary)
    """
    
    print("\n" + "="*60)
    print("🎙️ LUMEN SPEAKER DIARIZATION - LAYER 2")
    print("="*60)
    print("Identifying who speaks when in audio files")
    print("="*60)
    
    # STEP 1: Check for Hugging Face token
    print("\n📋 STEP 1: Checking authentication...")
    token = check_token()
    if not token:
        return
    
    # STEP 2: Define audio file path (same as transcriber)
    audio_path = "../datasets/test_audio/speech_sample.wav"
    print(f"\n📋 STEP 2: Audio file: {audio_path}")
    
    # Check if audio file exists
    if not os.path.exists(audio_path):
        print(f"\n❌ ERROR: Audio file not found at: {audio_path}")
        print("\nPlease make sure you have a test audio file.")
        print("You can download one with:")
        print("  cd ../datasets/test_audio")
        print('  curl -L "https://www.voiptroubleshooter.com/open_speech/american/OSR_us_000_0010_8k.wav" -o speech_sample.wav')
        return
    
    # STEP 3: Load the diarization model
    print("\n📋 STEP 3: Loading AI model...")
    pipeline = load_diarization_pipeline(token)
    if not pipeline:
        return
    
    # STEP 4: Run diarization on the audio
    print("\n📋 STEP 4: Analyzing speakers...")
    segments = diarize_audio(pipeline, audio_path)
    if not segments:
        return
    
    # STEP 5: Format the results
    print("\n📋 STEP 5: Organizing results...")
    formatted = format_diarization(segments)
    
    # STEP 6: Save to file
    print("\n📋 STEP 6: Saving results...")
    save_diarization(formatted, audio_path)
    
    # STEP 7: Print summary
    print("\n📋 STEP 7: Summary")
    print("="*60)
    print(f"🎙️ Total speakers detected: {formatted['total_speakers']}")
    print(f"⏱️  Total audio duration: {formatted['total_duration']} seconds")
    print(f"📊 Total segments: {formatted['total_segments']}")
    
    # Show speaker breakdown
    print("\n👥 Speaker Breakdown:")
    for speaker, info in formatted['speakers'].items():
        print(f"   {speaker}:")
        print(f"      - Spoke {info['segments_count']} times")
        print(f"      - Total time: {info['total_time']} seconds")
        print(f"      - {info['percentage']}% of conversation")
    
    # Print visual timeline
    print_timeline(segments)
    
    print("\n" + "="*60)
    print("✅ LAYER 2 COMPLETE!")
    print("="*60)
    print("\nNext step: Layer 3 - Stress Analysis with librosa")
    print("Check the 'diarizations' folder for the JSON output.")

# ============================================
# PART 9: THE MAGIC LINE - Run main() only if executed directly
# ============================================

if __name__ == "__main__":
    """
    This line ensures that main() runs only when we
    run this file directly (python diarizer.py)
    
    If we import this file from another script,
    main() won't run automatically - we can just
    use the functions we've defined.
    """
    main
import json
