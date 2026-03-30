export interface AlignedWord {
  word: string;
  start: number;
  end: number;
  speaker: string;
  stress_score: number;
  sentiment: string;
  sentiment_confidence: number;
  anomaly: boolean;
}

export interface AlignedData {
  metadata: {
    total_words: number;
    anomalies: number;
    anomaly_rate: number;
    speakers: string[];
    avg_stress: number;
  };
  words: AlignedWord[];
}

export interface AnalysisResponse {
  jobId: string;
  status: string;
  message?: string;
  createdAt?: string;
  result?: AlignedData;
  errorMessage?: string;
}
