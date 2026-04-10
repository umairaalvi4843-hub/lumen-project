import sys
import os
import json
import numpy as np

# Configuration
ANOMALY_THRESHOLD = 0.55  # Lowered from 0.7 to make it more sensitive
DEBUG = True

def debug_print(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")

def main():
    if len(sys.argv) < 2:
        print("❌ Need audio file path")
        return

    job_id = os.path.basename(sys.argv[1]).replace('.wav', '')
    
    transcript_file = f"transcriptions/{job_id}_transcript.json"
    sentiment_file = f"sentiment_{job_id}.json"
    stress_file = f"stress_{job_id}.json"
    diarization_file = f"diarizations/{job_id}_speakers.json"
    output_file = f"aligned_{job_id}.json"

    debug_print(f"Job ID: {job_id}")
    
    # Check files
    missing = []
    for f in [transcript_file, sentiment_file]:
        if not os.path.exists(f):
            missing.append(f)
    
    if missing:
        print(f"❌ Missing files: {missing}")
        return

    with open(transcript_file) as f: 
        transcript = json.load(f)
        debug_print(f"Loaded {len(transcript.get('segments', []))} transcript segments")
    
    with open(sentiment_file) as f: 
        sentiment_data = json.load(f)
        debug_print(f"Loaded {len(sentiment_data.get('results', []))} sentiment results")
    
    # Load stress data
    stress_results = []
    if os.path.exists(stress_file):
        with open(stress_file) as f: 
            stress_results = json.load(f).get('results', [])
            debug_print(f"Loaded {len(stress_results)} stress results")
    
    # Load diarization data
    speakers = ["SPEAKER_00"]
    if os.path.exists(diarization_file):
        with open(diarization_file) as f: 
            diar_data = json.load(f)
            unique_speakers = list(set([s['speaker'] for s in diar_data.get('segments', [])]))
            if unique_speakers:
                speakers = unique_speakers
                debug_print(f"Found speakers: {speakers}")
    
    aligned_words = []
    total_stress = 0
    anomaly_count = 0
    
    sentiment_results = sentiment_data.get('results', [])
    sentiment_map = {}
    for sr in sentiment_results:
        sentiment_map[sr.get('start', 0)] = sr.get('sentiment', {}).get('sentiment', 'neutral')
    
    for i, seg in enumerate(transcript.get('segments', [])):
        text = seg.get('text', '').strip()
        start = seg.get('start', 0)
        
        # Get sentiment
        seg_sentiment = sentiment_map.get(start, 'neutral')
        if i < len(sentiment_results):
            sent_obj = sentiment_results[i].get('sentiment', {})
            seg_sentiment = sent_obj.get('sentiment', 'neutral')
        
        # Get stress
        seg_stress = 0.35
        if i < len(stress_results):
            seg_stress = stress_results[i].get('stress_score', 0.35)
        
        total_stress += seg_stress
        
        # Determine speaker
        seg_speaker = speakers[i % len(speakers)] if speakers else "SPEAKER_00"
        
        # Anomaly detection with lower threshold
        is_anomaly = (seg_sentiment == 'positive' and seg_stress > ANOMALY_THRESHOLD)
        
        if is_anomaly:
            anomaly_count += 1
            debug_print(f"⚠️ ANOMALY: '{text}' (sentiment={seg_sentiment}, stress={seg_stress:.3f})")
        
        aligned_words.append({
            "word": text,
            "start": float(round(start, 2)),
            "speaker": seg_speaker,
            "stress_score": float(round(seg_stress, 3)),
            "sentiment": seg_sentiment,
            "anomaly": is_anomaly
        })

    final_output = {
        "metadata": {
            "total_words": len(aligned_words),
            "anomalies": anomaly_count,
            "anomaly_threshold": ANOMALY_THRESHOLD,
            "speakers": speakers,
            "avg_stress": float(round(total_stress / len(aligned_words), 3)) if aligned_words else 0
        },
        "words": aligned_words
    }

    with open(output_file, 'w') as f:
        json.dump(final_output, f, indent=2)
    
    print(f"\n{'='*50}")
    print(f"✅ ALIGNMENT COMPLETE")
    print(f"   Total words: {len(aligned_words)}")
    print(f"   Anomalies detected: {anomaly_count}")
    print(f"   Average stress: {final_output['metadata']['avg_stress']:.3f}")
    print(f"   Anomaly threshold: {ANOMALY_THRESHOLD}")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    main()
