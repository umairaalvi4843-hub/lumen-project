import numpy as np
import wave
import struct
import os
import math

sample_rate = 16000
duration = 5

# Create a more speech-like sound by modulating frequency
t = np.linspace(0, duration, int(sample_rate * duration))

# Vary frequency to simulate speech
freq = 150 + 50 * np.sin(2 * np.pi * 2 * t)  # Pitch variation
samples = (32767 * 0.3 * np.sin(2 * np.pi * freq * t)).astype(np.int16)

os.makedirs("../datasets/test_audio", exist_ok=True)
filepath = "../datasets/test_audio/speech_test.wav"

with wave.open(filepath, 'w') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    wav_file.writeframes(struct.pack('<' + ('h' * len(samples)), *samples))

print(f"✅ Created speech test audio: {filepath}")
