import json
import os
import numpy as np
from collections import Counter

class LumenAligner:
    def __init__(self, tolerance=0.25):
        self.tolerance = tolerance
        
    def load_json(self, filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def load_all_outputs(self, transcript_file, diarization_file, stress_file, sentiment_file):
        self.transcript = self.load_json(transcript_file)
        self.diarization = self.load_json(diarization_file)
        self.stress = self.load_json(stress_file)
        self.sentiment = self.load_json(sentiment_file)
        
    def extract_words(self):
        words = []
        for segment in self.transcript.get('segments', []):
            for word in segment.get('words', []):
                words.append({
                    'text': word['word'],
                    'start': word['start'],
                    'end': word['end'],
                    'confidence': word.get('confidence', 1.0)
                })
        return words
    
    def get_first_speaker(self):
        if self.diarization.get('segments'):
            return self.diarization['segments'][0]['speaker']
        return 'SPEAKER_00'
    
    def find_speaker_at_time(self, timestamp):
        if timestamp < 0.1:
            return self.get_first_speaker()
        
        for seg in self.diarization.get('segments', []):
            if seg['start'] <= timestamp <= seg['end']:
                return seg['speaker']
        
        closest_seg = None
        min_diff = float('inf')
        
        for seg in self.diarization.get('segments', []):
            diff = min(abs(timestamp - seg['start']), abs(timestamp - seg['end']))
            if diff < min_diff and diff <= self.tolerance:
                min_diff = diff
                closest_seg = seg
        
        if closest_seg:
            return closest_seg['speaker']
        
        return self.get_first_speaker()
    
    def find_stress_at_time(self, timestamp):
        segments = self.stress.get('segments', [])
        if not segments and 'results' in self.stress:
            segments = self.stress['results']
        
        for seg in segments:
            start = seg.get('start', seg.get('start_time', 0))
            end = seg.get('end', seg.get('end_time', 0))
            if start <= timestamp <= end:
                return seg.get('stress_score', 0.5)
        
        return 0.5
    
    def find_sentiment_at_time(self, timestamp):
        segments = self.sentiment.get('segments', [])
        if not segments and 'results' in self.sentiment:
            segments = self.sentiment['results']
        
        for seg in segments:
            start = seg.get('start_time', seg.get('start', 0))
            end = seg.get('end_time', seg.get('end', 0))
            if start <= timestamp <= end:
                sentiment_data = seg.get('sentiment', {})
                if isinstance(sentiment_data, dict):
                    return sentiment_data
                return {'sentiment': sentiment_data, 'confidence': 0.8}
        
        return {'sentiment': 'neutral', 'confidence': 0.5}
    
    def align(self):
        words = self.extract_words()
        aligned = []
        first_speaker = self.get_first_speaker()
        
        for word in words:
            speaker = self.find_speaker_at_time(word['start'])
            stress = self.find_stress_at_time(word['start'])
            sentiment = self.find_sentiment_at_time(word['start'])
            
            if word['start'] < 0.5 and speaker == 'UNKNOWN':
                speaker = first_speaker
            
            is_anomaly = (sentiment.get('sentiment') == 'positive' and stress > 0.7)
            
            aligned.append({
                'word': word['text'],
                'start': round(word['start'], 2),
                'end': round(word['end'], 2),
                'speaker': speaker,
                'stress_score': round(stress, 3),
                'sentiment': sentiment.get('sentiment', 'neutral'),
                'sentiment_confidence': round(sentiment.get('confidence', 0), 3),
                'anomaly': is_anomaly
            })
        
        return aligned
    
    def save_aligned(self, aligned_data, output_file='aligned_output.json'):
        speakers = list(set(w['speaker'] for w in aligned_data if w['speaker'] != 'UNKNOWN'))
        anomalies = [w for w in aligned_data if w['anomaly']]
        
        output = {
            'metadata': {
                'total_words': len(aligned_data),
                'anomalies': len(anomalies),
                'anomaly_rate': round(len(anomalies)/len(aligned_data)*100, 2) if aligned_data else 0,
                'tolerance_ms': self.tolerance * 1000,
                'speakers': speakers,
                'avg_stress': round(np.mean([w['stress_score'] for w in aligned_data]), 3)
            },
            'words': aligned_data
        }
        
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n✅ Aligned data saved to {output_file}")
        print(f"📊 Total words: {output['metadata']['total_words']}")
        print(f"⚠️ Anomalies detected: {output['metadata']['anomalies']} ({output['metadata']['anomaly_rate']}%)")
        print(f"👥 Speakers found: {output['metadata']['speakers']}")
        print(f"📈 Average stress: {output['metadata']['avg_stress']}")

def main():
    print("="*60)
    print("🔄 LUMEN ALIGNMENT ALGORITHM - PRODUCTION READY")
    print("="*60)
    
    aligner = LumenAligner(tolerance=0.25)
    
    transcript_file = 'transcriptions/speech_sample_transcript.json'
    diarization_file = 'diarizations/speech_sample_speakers.json'
    stress_file = 'stress_analysis.json'
    sentiment_file = 'sentiment_analysis.json'
    
    for name, path in [('transcript', transcript_file), 
                       ('diarization', diarization_file),
                       ('stress', stress_file), 
                       ('sentiment', sentiment_file)]:
        if not os.path.exists(path):
            print(f"❌ File not found: {path}")
            return
        print(f"✅ Found {name} file")
    
    aligner.load_all_outputs(
        transcript_file=transcript_file,
        diarization_file=diarization_file,
        stress_file=stress_file,
        sentiment_file=sentiment_file
    )
    
    aligned = aligner.align()
    aligner.save_aligned(aligned)
    
    print("\n🔍 First 10 aligned words:")
    for i, word in enumerate(aligned[:10]):
        anomaly_mark = "⚠️" if word['anomaly'] else "✅"
        print(f"   {i+1:2d}. {anomaly_mark} '{word['word']:10s}' | {word['speaker']:10s} | "
              f"stress:{word['stress_score']:.3f} | {word['sentiment']}")

if __name__ == "__main__":
    main()
