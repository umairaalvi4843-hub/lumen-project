#!/usr/bin/env python
import librosa
import numpy as np
import json
import os
import sys

def extract_pitch(audio, sr):
    pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
    pitch_values = []
    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()
        pitch = pitches[index, t]
        if pitch > 0:
            pitch_values.append(pitch)
    if not pitch_values:
        return {"mean_pitch": 0, "std_pitch": 0}
    return {
        "mean_pitch": float(np.mean(pitch_values)),
        "std_pitch": float(np.std(pitch_values))
    }

def calculate_stress_score(pitch):
    return min(pitch['std_pitch'] / 100.0, 1.0)

def analyze_audio(filepath):
    audio, sr = librosa.load(filepath, sr=16000)
    pitch = extract_pitch(audio, sr)
    stress = calculate_stress_score(pitch)
    return {"stress_score": stress, "pitch": pitch}

def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--input":
        audio_file = sys.argv[2]
    else:
        audio_file = "../datasets/test_audio/real_speech.wav"
    
    if not os.path.exists(audio_file):
        print(f"Audio file not found: {audio_file}")
        return
    
    result = analyze_audio(audio_file)
    
    output = {
        "segments": [{
            "start": 0,
            "end": librosa.get_duration(filename=audio_file),
            "stress_score": result["stress_score"],
            "pitch": result["pitch"]
        }]
    }
    
    with open("stress_analysis.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("✅ Stress analysis complete")

if __name__ == "__main__":
    main()
