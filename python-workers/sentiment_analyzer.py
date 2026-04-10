import sys
import os
import json
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class FinBERTAnalyzer:
    def __init__(self):
        model_name = "ProsusAI/finbert"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.id2label = {0: 'positive', 1: 'negative', 2: 'neutral'}

    def analyze(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        pred_id = torch.argmax(probs, dim=-1).item()
        return {"sentiment": self.id2label[pred_id], "confidence": float(torch.max(probs))}

def main():
    if len(sys.argv) < 2: return
    
    # FIX: Clean the Job ID from the path
    job_id = os.path.basename(sys.argv[1]).replace('.wav', '')
    transcript_file = f"transcriptions/{job_id}_transcript.json"
    output_file = f"sentiment_{job_id}.json"

    if not os.path.exists(transcript_file):
        print(f"❌ Transcript not found for Job: {job_id}")
        return

    with open(transcript_file, 'r') as f:
        data = json.load(f)

    analyzer = FinBERTAnalyzer()
    results = []
    for seg in data.get('segments', []):
        res = analyzer.analyze(seg.get('text', ''))
        results.append({"start": seg['start'], "end": seg['end'], "sentiment": res})

    with open(output_file, 'w') as f:
        json.dump({"results": results}, f, indent=2)
    print(f"✅ Sentiment analysis complete: {output_file}")

if __name__ == "__main__":
    main()