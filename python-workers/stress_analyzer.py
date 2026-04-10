#!/usr/bin/env python
import librosa
import numpy as np
import json
import os
import sys

def calculate_stress(audio, sr):
    """
    Calculate stress using multiple features: pitch variation, energy, and spectral centroid
    Returns a score between 0 and 1
    """
    try:
        # 1. Pitch variation (main stress indicator)
        pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(float(pitch))
        
        if len(pitch_values) < 5:
            return 0.3
        
        # Normalized pitch std dev (0-1 range)
        pitch_std = np.std(pitch_values)
        pitch_score = min(pitch_std / 80.0, 1.0)  # 80Hz variation = max stress
        
        # 2. Energy/RMS variation (volume changes indicate stress)
        rms = librosa.feature.rms(y=audio, frame_length=512, hop_length=256)[0]
        if len(rms) > 1:
            rms_var = np.var(rms) / (np.mean(rms) + 0.01)
            energy_score = min(rms_var / 0.1, 1.0)
        else:
            energy_score = 0.3
        
        # 3. Spectral centroid (brightness of voice - stress makes voice brighter)
        spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
        if len(spectral_centroids) > 1:
            centroid_var = np.var(spectral_centroids) / 1000
            centroid_score = min(centroid_var / 0.5, 1.0)
        else:
            centroid_score = 0.3
        
        # Combined stress score (weighted)
        stress = (0.5 * pitch_score + 0.3 * energy_score + 0.2 * centroid_score)
        
        # Add some natural variation (not all segments are the same)
        stress = min(max(stress, 0.15), 0.95)
        
        return round(stress, 3)
        
    except Exception as e:
        print(f"Error calculating stress: {e}")
        return 0.3

def analyze_audio(filepath, start_time, end_time):
    try:
        # Load just the segment
        audio, sr = librosa.load(filepath, sr=16000, offset=start_time, duration=end_time-start_time)
        
        if len(audio) < sr * 0.2:  # Less than 200ms
            return 0.3
        
        stress = calculate_stress(audio, sr)
        return stress
        
    except Exception as e:
        print(f"Error analyzing segment {start_time}-{end_time}: {e}")
        return 0.3

def main():
    if len(sys.argv) < 2:
        print("❌ Need audio file path")
        return
    
    audio_file = sys.argv[1]
    job_id = os.path.basename(audio_file).replace('.wav', '')
    
    transcript_file = f"transcriptions/{job_id}_transcript.json"
    if not os.path.exists(transcript_file):
        print(f"❌ Transcript not found: {transcript_file}")
        return
    
    with open(transcript_file, 'r') as f:
        transcript = json.load(f)
    
    results = []
    total_segments = len(transcript.get('segments', []))
    
    for i, seg in enumerate(transcript.get('segments', [])):
        start = seg.get('start', 0)
        end = seg.get('end', start + 1)
        stress = analyze_audio(audio_file, start, end)
        
        results.append({
            "start": float(round(start, 2)),
            "end": float(round(end, 2)),
            "stress_score": float(stress)
        })
        
        # Show progress
        if (i + 1) % 5 == 0 or i == total_segments - 1:
            print(f"  Progress: {i+1}/{total_segments} segments")
    
    output_file = f"stress_{job_id}.json"
    with open(output_file, 'w') as f:
        json.dump({"results": results}, f, indent=2)
    
    # Print summary
    avg_stress = sum(r['stress_score'] for r in results) / len(results) if results else 0
    print(f"✅ Stress analysis complete: {output_file}")
    print(f"   Average stress: {avg_stress:.3f}")
    print(f"   Stress range: {min(r['stress_score'] for r in results):.3f} - {max(r['stress_score'] for r in results):.3f}")

if __name__ == "__main__":
    main()
