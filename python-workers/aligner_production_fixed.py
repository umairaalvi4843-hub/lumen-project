import sys
import os
import json
import numpy as np

def main():
    if len(sys.argv) < 2:
        print("❌ Need Job ID")
        return

    # FIX: Clean the Job ID from the path
    job_id = os.path.basename(sys.argv[1]).replace('.wav', '')
    
    transcript_file = f"transcriptions/{job_id}_transcript.json"
    sentiment_file = f"sentiment_{job_id}.json"
    # Fallbacks for other layers
    stress_file = f"stress_{job_id}.json"
    output_file = f"aligned_{job_id}.json"

    # Verify critical files
    for p in [transcript_file, sentiment_file]:
        if not os.path.exists(p):
            print(f"❌ Missing critical file: {p}")
            return

    with open(transcript_file) as f: transcript = json.load(f)
    with open(sentiment_file) as f: sentiment = json.load(f)
    
    # Load stress if exists, else default
    stress_data = []
    if os.path.exists(stress_file):
        with open(stress_file) as f: stress_data = json.load(f).get('results', [])

    aligned_words = []
    total_stress = 0
    
    # Logic: Aligning Whisper segments to Sentiment/Stress
    for i, seg in enumerate(transcript.get('segments', [])):
        text = seg['text'].strip()
        start = seg['start']
        
        # Match sentiment for this segment
        seg_sentiment = sentiment['results'][i]['sentiment']['sentiment'] if i < len(sentiment['results']) else "neutral"
        
        # Mock/Calculate stress for this segment
        seg_stress = 0.45 # Default base stress
        if i < len(stress_data):
            seg_stress = stress_data[i].get('stress_score', 0.45)
        
        total_stress += seg_stress

        aligned_words.append({
            "word": text,
            "start": round(start, 2),
            "speaker": "SPEAKER_00",
            "stress_score": round(seg_stress, 2),
            "sentiment": seg_sentiment,
            "anomaly": (seg_sentiment == "positive" and seg_stress > 0.6)
        })

    # FINAL METADATA
    final_output = {
        "metadata": {
            "total_words": len(aligned_words),
            "anomalies": len([w for w in aligned_words if w['anomaly']]),
            "speakers": ["SPEAKER_00"],
            "avg_stress": round(total_stress / len(aligned_words), 2) if aligned_words else 0
        },
        "words": aligned_words
    }

    with open(output_file, 'w') as f:
        json.dump(final_output, f, indent=2)
    
    print(f"✅ SUCCESS: Aligned data saved to {output_file}")

if __name__ == "__main__":
    main()