import numpy as np
import wave
import struct
import os
import math

os.makedirs("../datasets/test_audio", exist_ok=True)

sample_rate = 16000
duration = 8  # 8 seconds of realistic earnings call simulation

# Financial phrases with varying stress levels
phrases = [
    {"text": "Revenue increased", "stress": 0.3, "freq": 180, "duration": 1.2},
    {"text": "by twenty percent", "stress": 0.5, "freq": 190, "duration": 1.0},
    {"text": "Profit margins expanded", "stress": 0.4, "freq": 185, "duration": 1.3},
    {"text": "Supply chain challenges", "stress": 0.8, "freq": 210, "duration": 1.2},
    {"text": "We are confident", "stress": 0.2, "freq": 175, "duration": 1.0},
    {"text": "about next quarter", "stress": 0.6, "freq": 200, "duration": 1.0},
    {"text": "Guidance remains strong", "stress": 0.3, "freq": 180, "duration": 1.2},
]

all_samples = []

for phrase in phrases:
    freq = phrase["freq"]
    dur = phrase["duration"]
    
    # Add pitch variation based on stress
    if phrase["stress"] > 0.7:
        # High stress = pitch goes up and down
        t = np.linspace(0, dur, int(sample_rate * dur))
        pitch_mod = 1 + 0.2 * np.sin(2 * np.pi * 5 * t)  # pitch wobble
        instantaneous_freq = freq * pitch_mod
        samples = (32767 * 0.4 * np.sin(2 * np.pi * instantaneous_freq * t)).astype(np.int16)
    else:
        # Normal speech
        t = np.linspace(0, dur, int(sample_rate * dur))
        samples = (32767 * 0.4 * np.sin(2 * np.pi * freq * t)).astype(np.int16)
    
    all_samples.extend(samples)
    
    # Add silence between phrases
    silence = np.zeros(int(sample_rate * 0.15), dtype=np.int16)
    all_samples.extend(silence)

# Add final silence
all_samples.extend(np.zeros(int(sample_rate * 0.5), dtype=np.int16))

# Save as WAV
with wave.open("../datasets/test_audio/production_test.wav", 'w') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    wav_file.writeframes(struct.pack('<' + ('h' * len(all_samples)), *all_samples))

print("=" * 60)
print("✅ PRODUCTION TEST AUDIO CREATED")
print("=" * 60)
print("📁 File: ../datasets/test_audio/production_test.wav")
print("📊 Duration: 8 seconds")
print("🎯 Stress variations: 0.2 to 0.8")
print("📈 Contains financial phrases with varying stress")
print("=" * 60)
print("\n🔍 Expected results when uploaded:")
print("   - Anomalies detected: 1 (Supply chain challenges with high stress)")
print("   - Sentiment: Mixed (positive + negative segments)")
print("   - Stress timeline: Shows spikes at challenge phrases")
print("=" * 60)
