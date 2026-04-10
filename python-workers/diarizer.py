#!/usr/bin/env python
import torch
import torch.serialization
import json
import os
import sys
from pyannote.audio import Pipeline
from dotenv import load_dotenv

# Fix for PyTorch 2.6 weights_only issue
try:
    from torch.torch_version import TorchVersion
    torch.serialization.add_safe_globals([TorchVersion])
except:
    pass

def main():
    if len(sys.argv) < 2:
        print("❌ Need audio file path")
        return
    
    audio_file = sys.argv[1]
    job_id = os.path.basename(audio_file).replace('.wav', '')
    
    load_dotenv()
    token = os.getenv("HUGGINGFACE_TOKEN")
    if not token:
        print("❌ No Hugging Face token found")
        return
    
    print(f"🎙️ Processing: {job_id}")
    
    try:
        # Patch torch.load to work with older models (weights_only fix)
        original_load = torch.load
        def patched_load(*args, **kwargs):
            kwargs['weights_only'] = False
            return original_load(*args, **kwargs)
        torch.load = patched_load
        
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=token
        )
        
        # Determine initial device
        device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        pipeline.to(device)
        print(f"✅ Using {device.type.upper()} ({'Apple GPU' if device.type == 'mps' else 'CPU'})")
        
        # --- ATTEMPT DIARIZATION ---
        try:
            diarization = pipeline(audio_file)
        except RuntimeError as e:
            # Check for the specific Apple MPS size mismatch error
            if "Sizes of tensors must match" in str(e) and device.type == "mps":
                print("⚠️ MPS Size Mismatch detected. Falling back to CPU for stability...")
                pipeline.to(torch.device("cpu"))
                diarization = pipeline(audio_file)
            else:
                raise e
        
        segments = []
        for segment, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                "speaker": speaker,
                "start": float(round(segment.start, 2)),
                "end": float(round(segment.end, 2))
            })
        
        output_file = f"diarizations/{job_id}_speakers.json"
        os.makedirs("diarizations", exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump({"segments": segments}, f, indent=2)
        
        unique_speakers = set(s['speaker'] for s in segments)
        print(f"✅ Found {len(unique_speakers)} speaker(s): {', '.join(unique_speakers)}")
        
    except Exception as e:
        print(f"❌ Diarization failed: {e}")

if __name__ == "__main__":
    main()