import sys
#!/usr/bin/env python
"""
DIARIZER.PY - LAYER 2: Speaker Identification for Lumen Project
Clean, working version with PyTorch 2.6 fix
"""

import torch
import torch.serialization
from pyannote.audio import Pipeline
from dotenv import load_dotenv
import os
import json
from torch.torch_version import TorchVersion

torch.serialization.add_safe_globals([TorchVersion])

def check_token():
    load_dotenv()
    token = os.getenv("HUGGINGFACE_TOKEN")
    if not token:
        print("❌ ERROR: No Hugging Face token found!")
        print("Please add HUGGINGFACE_TOKEN to your .env file")
        return None
    print(f"✅ Token found: {token[:10]}...")
    return token

def load_model(token):
    print("\n📥 Loading speaker diarization model...")
    
    original_load = torch.load
    def patched_load(*args, **kwargs):
        kwargs['weights_only'] = False
        return original_load(*args, **kwargs)
    torch.load = patched_load
    
    try:
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=token
        )
        
        if torch.backends.mps.is_available():
            pipeline = pipeline.to(torch.device("mps"))
            print("✅ Using Apple M-series GPU")
        else:
            print("⚠️ Using CPU (slower but works)")
        
        print("✅ Model loaded successfully!")
        return pipeline
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return None

def process_audio(pipeline, audio_path):
    print(f"\n🎙️ Processing: {os.path.basename(audio_path)}")
    print("⏳ This takes 10-30 seconds...")
    
    try:
        diarization = pipeline(audio_path)
        
        segments = []
        speakers = set()
        
        for segment, _, speaker in diarization.itertracks(yield_label=True):
            speakers.add(speaker)
            segments.append({
                "speaker": speaker,
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "duration": round(segment.end - segment.start, 2)
            })
        
        print(f"✅ Found {len(speakers)} speaker(s): {', '.join(speakers)}")
        print(f"📊 Total segments: {len(segments)}")
        
        return segments, speakers
        
    except Exception as e:
        print(f"❌ Diarization failed: {e}")
        return [], set()

def save_results(segments, speakers, audio_path):
    os.makedirs("diarizations", exist_ok=True)
    
    base_name = os.path.basename(audio_path)
    name_without_ext = os.path.splitext(base_name)[0]
    output_file = f"diarizations/{name_without_ext}_speakers.json"
    
    results = {
        "audio_file": base_name,
        "num_speakers": len(speakers),
        "speakers": list(speakers),
        "total_segments": len(segments),
        "segments": segments
    }
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    print("\n📋 First 5 segments:")
    for seg in segments[:5]:
        print(f"   {seg['speaker']}: {seg['start']}s - {seg['end']}s ({seg['duration']}s)")

def main():
    print("="*60)
    print("🎙️ LUMEN SPEAKER DIARIZATION - LAYER 2")
    print("="*60)
    
    token = check_token()
    if not token:
        return
    
    audio_path = sys.argv[1] if len(sys.argv) > 1 else "../datasets/test_audio/real_speech.wav"
    if not os.path.exists(audio_path):
        print(f"❌ Audio file not found: {audio_path}")
        print("Please download a test audio file first.")
        return
    
    pipeline = load_model(token)
    if not pipeline:
        return
    
    segments, speakers = process_audio(pipeline, audio_path)
    
    if segments:
        save_results(segments, speakers, audio_path)
    else:
        print("❌ No segments found - check your audio file")

if __name__ == "__main__":
    main()
