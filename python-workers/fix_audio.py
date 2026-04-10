import numpy as np
import wave
import struct
import os

# Create a valid WAV file
sample_rate = 16000
duration = 3
frequency = 440

t = np.linspace(0, duration, int(sample_rate * duration))
samples = (32767 * 0.5 * np.sin(2 * np.pi * frequency * t)).astype(np.int16)

# Save to the correct location
os.makedirs("../datasets/test_audio", exist_ok=True)
filepath = "../datasets/test_audio/valid_test.wav"

with wave.open(filepath, 'w') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    wav_file.writeframes(struct.pack('<' + ('h' * len(samples)), *samples))

print(f"✅ Created valid test audio: {filepath}")
print(f"📁 File size: {os.path.getsize(filepath)} bytes")
