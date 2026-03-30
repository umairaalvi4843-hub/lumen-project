#!/usr/bin/env python
"""
SENTIMENT_ANALYZER.PY - LAYER 4: Financial Sentiment Analysis for Lumen Project
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import json
import os
import numpy as np

class FinBERTAnalyzer:
    def __init__(self, model_name="ProsusAI/finbert"):
        print("\n" + "="*60)
        print("📥 Loading FinBERT model...")
        print("="*60)
        
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
            print("✅ Using NVIDIA GPU")
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
            print("✅ Using Apple Silicon GPU (MPS)")
        else:
            self.device = torch.device("cpu")
            print("⚠️ Using CPU")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model = self.model.to(self.device)
        self.model.eval()
        
        print(f"✅ FinBERT model loaded successfully!")
        self.id2label = {0: 'positive', 1: 'negative', 2: 'neutral'}
    
    def analyze_text(self, text):
        if not text or len(text.strip()) == 0:
            return {
                "sentiment": "neutral",
                "confidence": 1.0,
                "scores": {"positive": 0.0, "negative": 0.0, "neutral": 1.0}
            }
        
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        pred_id = torch.argmax(probs, dim=-1).item()
        scores = probs.cpu().numpy()[0]
        
        return {
            "sentiment": self.id2label[pred_id],
            "confidence": float(np.max(scores)),
            "scores": {
                "positive": float(scores[0]),
                "negative": float(scores[1]),
                "neutral": float(scores[2])
            }
        }
    
    def analyze_segments(self, segments):
        print(f"\n📊 Analyzing sentiment for {len(segments)} segments...")
        results = []
        
        for i, seg in enumerate(segments):
            text = seg.get('text', '')
            if not text and 'words' in seg:
                text = ' '.join([w['word'] for w in seg['words']])
            
            sentiment = self.analyze_text(text)
            results.append({**seg, "sentiment": sentiment})
        
        print(f"✅ Sentiment analysis complete!")
        return results

def load_transcript(transcript_path):
    with open(transcript_path, 'r') as f:
        data = json.load(f)
    
    if 'segments' in data:
        return data['segments'], data.get('full_text', '')
    return [], ''

def main():
    print("="*60)
    print("📈 LUMEN SENTIMENT ANALYSIS - LAYER 4")
    print("="*60)
    
    transcript_dir = "transcriptions"
    json_files = [f for f in os.listdir(transcript_dir) if f.endswith('.json')]
    
    if not json_files:
        print("❌ No transcript files found")
        return
    
    transcript_file = os.path.join(transcript_dir, json_files[0])
    print(f"📂 Using: {transcript_file}")
    
    segments, full_text = load_transcript(transcript_file)
    print(f"📊 Loaded {len(segments)} segments")
    
    analyzer = FinBERTAnalyzer()
    full_sentiment = analyzer.analyze_text(full_text)
    print(f"\n📝 Full text: {full_sentiment['sentiment'].upper()} (conf: {full_sentiment['confidence']:.3f})")
    
    results = analyzer.analyze_segments(segments)
    
    output = {
        "overall": {
            "full_text_sentiment": full_sentiment,
            "segment_count": len(results)
        },
        "segments": results
    }
    
    with open("sentiment_analysis.json", 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Results saved to sentiment_analysis.json")
    print("\n" + "="*60)
    print("✅ LAYER 4 COMPLETE!")

if __name__ == "__main__":
    main()
