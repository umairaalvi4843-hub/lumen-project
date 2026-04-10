import sys
import os
import json
import whisper

def main():
    if len(sys.argv) < 2:
        print("❌ Usage: python transcriber.py <full_path_to_audio>")
        return

    audio_path = sys.argv[1]
    # FIX: Extract only the ID (e.g., '48d0ea8f...') from the full path
    job_id = os.path.basename(audio_path).replace('.wav', '')
    
    print(f"🚀 LUMEN TRANSCRIBER: Processing {job_id}")
    
    # Ensure directory exists
    os.makedirs("transcriptions", exist_ok=True)
    output_path = f"transcriptions/{job_id}_transcript.json"

    try:
        model = whisper.load_model("tiny")
        result = model.transcribe(audio_path, verbose=False)
        
        # Structure data for the Aligner
        output_data = {
            "job_id": job_id,
            "full_text": result['text'],
            "segments": result['segments']
        }

        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
            
        print(f"✅ Transcription saved to: {output_path}")
        print(f"📊 Total words: {len(result['text'].split())}")

    except Exception as e:
        print(f"❌ Transcription error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()