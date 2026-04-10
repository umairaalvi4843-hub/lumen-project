import numpy as np
import wave
import struct
import os

os.makedirs("../datasets/test_audio", exist_ok=True)

def create_wav(filename, duration, frequency):
    sample_rate = 16000
    t = np.linspace(0, duration, int(sample_rate * duration))
    samples = (32767 * 0.5 * np.sin(2 * np.pi * frequency * t)).astype(np.int16)
    
    with wave.open(f"../datasets/test_audio/{filename}", 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(struct.pack('<' + ('h' * len(samples)), *samples))

# Create all needed test files
create_wav("test_tone.wav", 3, 440)
create_wav("speech_sample.wav", 5, 440)
create_wav("sample_call.wav", 3, 440)
create_wav("valid_test.wav", 3, 440)

print("✅ Created all audio files:")
print("   - test_tone.wav")
print("   - speech_sample.wav")
print("   - sample_call.wav")
print("   - valid_test.wav")
