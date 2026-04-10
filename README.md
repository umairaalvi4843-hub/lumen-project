<img width="1469" height="832" alt="image" src="https://github.com/user-attachments/assets/f89b8c0d-4e67-435e-9d48-8a7f19e5cda2" />
<img width="1470" height="809" alt="image" src="https://github.com/user-attachments/assets/e3bab02f-748c-4729-8079-7cfa8d3acba8" />
<img width="1468" height="831" alt="image" src="https://github.com/user-attachments/assets/d34b0865-abe2-42ac-9c3f-54e254e6b009" />
<img width="1470" height="832" alt="image" src="https://github.com/user-attachments/assets/ec42c09e-d608-4368-adea-f7d6574d2451" />

# 🎙️ Lumen - Forensic Audio Intelligence

**Detect sentiment anomalies in corporate earnings calls through multimodal AI analysis**

---

## 📋 Overview

Lumen is a multimodal forensic audio engine that analyzes earnings call recordings to detect discrepancies between what executives say and how they say it. By fusing speech transcription, speaker diarization, vocal stress analysis, and financial sentiment analysis, Lumen flags moments where positive sentiment contradicts high vocal stress—potential indicators of deception or hidden bad news.

---

## ✨ Features

| Layer | Model | Output |
|-------|-------|--------|
| Layer 1 | OpenAI Whisper large-v3 | Word-level transcript with timestamps |
| Layer 2 | pyannote.audio 3.1 | Speaker segments with labels |
| Layer 3 | librosa (custom) | Vocal stress score (0-1) |
| Layer 4 | FinBERT | Financial sentiment (positive/negative/neutral) |
| Layer 5 | Custom alignment | Unified JSON with anomaly flags |

### Dashboard Features

- 📊 **Stress Timeline** - Area chart showing stress across the call
- ⚠️ **Anomaly Detection** - Positive sentiment + stress > 0.55 threshold
- 👥 **Speaker Analysis** - Per-speaker stats (word count, avg stress, anomalies)
- 📝 **Word-Level Table** - Sortable table with timestamps, stress, sentiment
- 🎨 **Dark Theme** - Modern Material-UI design with animations
- 🔄 **Real-time Status** - Live processing updates

---

## 🏗️ System Architecture
Audio Input → Whisper → Text + Timestamps
→ pyannote → Speaker Segments
→ librosa → Stress Scores
→ FinBERT → Sentiment Analysis
→ Alignment → Unified JSON + Anomaly Flags


---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Java 17+
- Node.js 18+
- Maven 3.8+
- FFmpeg

### 1. Clone Repository
```bash
git clone https://github.com/umairaalvi4843-hub/lumen-project.git
cd lumen-project

cd python-workers
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

HUGGINGFACE_TOKEN=hf_your_token_here

cd ../spring-backend
mvn clean install
mvn spring-boot:run

cd ../react-frontend
npm install
npm start

Open http://localhost:3000
Select audio file (.wav or .mp3)
Click "Analyze Earnings Call"
Wait for processing (2-5 minutes)
Explore the dashboard!

```

API Endpoints
Method	Endpoint	Description
POST	/api/analysis/upload	Upload audio file for analysis
GET	/api/analysis/status/{jobId}	Check processing status
GET	/api/analysis/results/{jobId}	Get analysis results
GET	/api/test	Health check

lumen-project/
├── python-workers/           # Python ML pipeline
│   ├── transcriber.py        # Layer 1: Whisper ASR
│   ├── diarizer.py           # Layer 2: pyannote diarization
│   ├── stress_analyzer.py    # Layer 3: librosa stress
│   ├── sentiment_analyzer.py # Layer 4: FinBERT
│   ├── aligner_production_fixed.py # Layer 5: Alignment
│   └── requirements.txt
│
├── spring-backend/           # Spring Boot REST API
│   └── src/main/java/com/lumen/
│       ├── controller/       # REST endpoints
│       ├── service/          # Business logic
│       └── repository/       # JPA repositories
│
├── react-frontend/           # React dashboard
│   └── src/
│       ├── components/       # UI components
│       ├── services/         # API client
│       └── App.tsx           # Main application
│
└── datasets/                 # Audio files (gitignored)

📊 Stress Score Interpretation

Range	Interpretation
0.0 - 0.3	Relaxed / Normal speech
0.3 - 0.55	Mild stress / Emphasis
0.55 - 0.7	Moderate stress (warning zone)
0.7 - 1.0	High stress (anomaly threshold)
Anomaly Detection: sentiment == "positive" AND stress > 0.55

🛠️ Tech Stack

Component	Technology
Backend	Spring Boot 2.7, Java 17
Frontend	React 18, TypeScript, Material-UI
ML/AI	PyTorch, Whisper, pyannote, librosa, FinBERT
Database	H2 (in-memory)
Build Tools	Maven, npm
📝 License

MIT License

🙏 Acknowledgments

OpenAI Whisper for speech recognition
pyannote.audio for speaker diarization
librosa for audio analysis
Hugging Face for FinBERT and model hosting
Material-UI for React components

<div align="center"> Built with ❤️ for forensic audio intelligence </div> ```





