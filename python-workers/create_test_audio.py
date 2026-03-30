import numpy as np
import wave
import struct

# Generate a simple sine wave (440 Hz = A note)
duration = 2  # seconds
sample_rate = 16000
frequency = 440

t = np.linspace(0, duration, int(sample_rate * duration))
samples = (32767 * 0.5 * np.sin(2 * np.pi * frequency * t)).astype(np.int16)

# Save as WAV file
with wave.open("../datasets/test_audio/test_tone.wav", 'w') as wav_file:
    wav_file.setnchannels(1)  # mono
    wav_file.setsampwidth(2)   # 16-bit
    wav_file.setframerate(sample_rate)
    wav_file.writeframes(struct.pack('<' + ('h' * len(samples)), *samples))

print("✅ Created test_tone.wav")
