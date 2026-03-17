#!/usr/bin/env python
"""
STRESS_ANALYZER.PY - LAYER 3: Vocal Stress Detection for Lumen Project

This module extracts acoustic features from speech to detect stress:
- Pitch (F0) - How high/low the voice is
- Jitter - Cycle-to-cycle pitch variations (voice shakiness)
- Shimmer - Cycle-to-cycle amplitude variations (breathiness)

Input:  Audio file + Speaker segments from Layer 2
Output: Stress scores for each segment (0-1 scale)
"""

import librosa
import numpy as np
import os
import json
import warnings
from typing import List, Dict, Tuple, Optional
import matplotlib.pyplot as plt
from datetime import timedelta

# Suppress librosa warnings
warnings.filterwarnings('ignore')

# ============================================
# PART 1: PITCH EXTRACTION
# ============================================

def extract_pitch(audio: np.ndarray, sr: int, fmin: float = 50, fmax: float = 400) -> Dict:
    """
    Extract pitch (F0) statistics from audio segment.
    
    Pitch = fundamental frequency of voice (how high/deep the voice sounds)
    
    Args:
        audio: Audio signal as numpy array
        sr: Sample rate (Hz)
        fmin: Minimum frequency to detect (Hz) - typical male voice ~85Hz
        fmax: Maximum frequency to detect (Hz) - typical female voice ~255Hz
    
    Returns:
        Dictionary with pitch statistics
    """
    
    # Use piptrack to detect pitch
    pitches, magnitudes = librosa.piptrack(
        y=audio, 
        sr=sr,
        fmin=fmin,
        fmax=fmax
    )
    
    # Extract pitch values where magnitude is highest
    pitch_values = []
    for t in range(pitches.shape[1]):
        # Find the frequency with maximum magnitude at this time
        index = magnitudes[:, t].argmax()
        pitch = pitches[index, t]
        if pitch > 0:  # Only include detected pitches
            pitch_values.append(pitch)
    
    if not pitch_values:
        return {
            "mean_pitch": 0.0,
            "std_pitch": 0.0,
            "min_pitch": 0.0,
            "max_pitch": 0.0,
            "pitch_range": 0.0,
            "pitch_25_percentile": 0.0,
            "pitch_75_percentile": 0.0
        }
    
    # Calculate statistics
    pitch_array = np.array(pitch_values)
    
    return {
        "mean_pitch": float(np.mean(pitch_array)),
        "std_pitch": float(np.std(pitch_array)),
        "min_pitch": float(np.min(pitch_array)),
        "max_pitch": float(np.max(pitch_array)),
        "pitch_range": float(np.max(pitch_array) - np.min(pitch_array)),
        "pitch_25_percentile": float(np.percentile(pitch_array, 25)),
        "pitch_75_percentile": float(np.percentile(pitch_array, 75))
    }


# ============================================
# PART 2: JITTER CALCULATION (Pitch Variation)
# ============================================

def calculate_jitter(audio: np.ndarray, sr: int, pitch_values: List[float]) -> Dict:
    """
    Calculate jitter - cycle-to-cycle variation of fundamental frequency.
    
    Jitter measures the shakiness/irregularity of voice.
    Higher jitter = more irregular voice (potential stress indicator)
    
    Args:
        audio: Audio signal (unused but kept for API consistency)
        sr: Sample rate (unused)
        pitch_values: List of pitch values from extract_pitch
    
    Returns:
        Dictionary with jitter metrics
    """
    
    if len(pitch_values) < 4:  # Need at least a few values
        return {
            "jitter_abs": 0.0,      # Absolute jitter in seconds
            "jitter_rel": 0.0,       # Relative jitter (percentage)
            "jitter_ppq5": 0.0,      # 5-point Period Perturbation Quotient
            "jitter_rap": 0.0        # Relative Average Perturbation
        }
    
    # Convert pitch (Hz) to period (seconds)
    periods = [1.0 / f for f in pitch_values if f > 0]
    
    if len(periods) < 4:
        return {
            "jitter_abs": 0.0,
            "jitter_rel": 0.0,
            "jitter_ppq5": 0.0,
            "jitter_rap": 0.0
        }
    
    periods = np.array(periods)
    
    # 1. Absolute Jitter - average absolute difference between consecutive periods
    abs_diffs = np.abs(np.diff(periods))
    jitter_abs = float(np.mean(abs_diffs))
    
    # 2. Relative Jitter - jitter_abs / average period
    avg_period = float(np.mean(periods))
    jitter_rel = jitter_abs / avg_period if avg_period > 0 else 0.0
    
    # 3. RAP (Relative Average Perturbation) - 3-point average
    rap_values = []
    for i in range(1, len(periods) - 1):
        avg_3 = np.mean(periods[i-1:i+2])
        rap_values.append(abs(periods[i] - avg_3) / avg_3)
    jitter_rap = float(np.mean(rap_values)) if rap_values else 0.0
    
    # 4. PPQ5 (5-point Period Perturbation Quotient)
    ppq5_values = []
    for i in range(2, len(periods) - 2):
        avg_5 = np.mean(periods[i-2:i+3])
        ppq5_values.append(abs(periods[i] - avg_5) / avg_5)
    jitter_ppq5 = float(np.mean(ppq5_values)) if ppq5_values else 0.0
    
    return {
        "jitter_abs": jitter_abs,
        "jitter_rel": jitter_rel,
        "jitter_rap": jitter_rap,
        "jitter_ppq5": jitter_ppq5
    }


# ============================================
# PART 3: SHIMMER CALCULATION (Amplitude Variation)
# ============================================

def calculate_shimmer(audio: np.ndarray, sr: int) -> Dict:
    """
    Calculate shimmer - cycle-to-cycle variation of amplitude.
    
    Shimmer measures breathiness/amplitude instability.
    Higher shimmer = more amplitude variation (potential stress indicator)
    
    Args:
        audio: Audio signal
        sr: Sample rate
    
    Returns:
        Dictionary with shimmer metrics
    """
    
    # Compute RMS (Root Mean Square) energy over time
    # This gives us the amplitude envelope
    frame_length = int(0.03 * sr)  # 30ms frames
    hop_length = frame_length // 2   # 50% overlap
    
    rms = librosa.feature.rms(
        y=audio, 
        frame_length=frame_length,
        hop_length=hop_length
    )[0]
    
    if len(rms) < 5:
        return {
            "shimmer_abs": 0.0,      # Absolute shimmer in amplitude units
            "shimmer_db": 0.0,        # Shimmer in decibels
            "shimmer_apq3": 0.0,      # 3-point Amplitude Perturbation Quotient
            "shimmer_apq5": 0.0,      # 5-point Amplitude Perturbation Quotient
            "shimmer_mean_db": 0.0
        }
    
    # Convert to dB (decibels) for perceptual relevance
    # Add small constant to avoid log(0)
    rms_db = 20 * np.log10(rms + 1e-10)
    
    # 1. Absolute Shimmer - average absolute difference between consecutive amplitudes
    abs_diffs = np.abs(np.diff(rms))
    shimmer_abs = float(np.mean(abs_diffs))
    
    # 2. Shimmer in dB
    db_diffs = np.abs(np.diff(rms_db))
    shimmer_db = float(np.mean(db_diffs))
    
    # 3. APQ3 (3-point Amplitude Perturbation Quotient)
    apq3_values = []
    for i in range(1, len(rms_db) - 1):
        avg_3 = np.mean(rms_db[i-1:i+2])
        apq3_values.append(abs(rms_db[i] - avg_3) / abs(avg_3 + 1e-10))
    shimmer_apq3 = float(np.mean(apq3_values)) if apq3_values else 0.0
    
    # 4. APQ5 (5-point Amplitude Perturbation Quotient)
    apq5_values = []
    for i in range(2, len(rms_db) - 2):
        avg_5 = np.mean(rms_db[i-2:i+3])
        apq5_values.append(abs(rms_db[i] - avg_5) / abs(avg_5 + 1e-10))
    shimmer_apq5 = float(np.mean(apq5_values)) if apq5_values else 0.0
    
    # 5. Mean amplitude in dB (for reference)
    shimmer_mean_db = float(np.mean(rms_db))
    
    return {
        "shimmer_abs": shimmer_abs,
        "shimmer_db": shimmer_db,
        "shimmer_apq3": shimmer_apq3,
        "shimmer_apq5": shimmer_apq5,
        "shimmer_mean_db": shimmer_mean_db
    }


# ============================================
# PART 4: STRESS SCORE CALCULATION (Custom Formula)
# ============================================

def calculate_stress_score(pitch: Dict, jitter: Dict, shimmer: Dict) -> float:
    """
    Calculate a combined stress score from 0 to 1.
    
    0.0 = completely relaxed / normal speech
    1.0 = extremely stressed
    
    This is a CUSTOM formula based on research literature.
    You can adjust the weights based on your needs!
    
    Formula components:
    - Pitch variation (40%): Higher pitch range = more emotional/stressed
    - Jitter (30%): More voice shakiness = more stressed
    - Shimmer (30%): More amplitude variation = more stressed
    """
    
    # Normalize pitch variation (cap at 100Hz variation)
    # Typical pitch range: 80-300Hz, so 100Hz variation is significant
    pitch_var = min(pitch['std_pitch'] / 100.0, 1.0)
    
    # Normalize jitter (typical jitter_rel < 0.02 for normal speech)
    # Scale: 0.02 = 1.0 in normalized score
    jitter_score = min(jitter['jitter_rel'] * 50.0, 1.0)
    
    # Normalize shimmer (typical shimmer_db < 1.0 for normal speech)
    # Scale: 3.0 dB = 1.0 in normalized score
    shimmer_score = min(shimmer['shimmer_db'] / 3.0, 1.0)
    
    # Weighted combination (weights sum to 1.0)
    stress_score = (
        0.4 * pitch_var +    # Pitch variation: 40% weight
        0.3 * jitter_score +  # Jitter: 30% weight
        0.3 * shimmer_score   # Shimmer: 30% weight
    )
    
    return round(stress_score, 3)


# ============================================
# PART 5: SINGLE SEGMENT ANALYSIS
# ============================================

def analyze_segment(audio_path: str, start_time: float, end_time: float, 
                    segment_id: int = 0, speaker: str = "UNKNOWN") -> Dict:
    """
    Analyze a single segment of audio for stress features.
    
    Args:
        audio_path: Path to audio file
        start_time: Start time in seconds
        end_time: End time in seconds
        segment_id: Segment index (for tracking)
        speaker: Speaker label
    
    Returns:
        Dictionary with all stress features for this segment
    """
    
    # Load the audio segment
    try:
        audio, sr = librosa.load(
            audio_path,
            sr=16000,  # Standard sample rate for analysis
            offset=start_time,
            duration=end_time - start_time
        )
    except Exception as e:
        print(f"   ⚠️ Error loading segment {segment_id}: {e}")
        return {
            "segment_id": segment_id,
            "speaker": speaker,
            "start": start_time,
            "end": end_time,
            "duration": end_time - start_time,
            "error": str(e)
        }
    
    # Check if segment is too short
    if len(audio) < sr * 0.1:  # Less than 100ms
        return {
            "segment_id": segment_id,
            "speaker": speaker,
            "start": start_time,
            "end": end_time,
            "duration": end_time - start_time,
            "error": "Segment too short (<100ms)"
        }
    
    # Extract pitch
    pitch_stats = extract_pitch(audio, sr)
    
    # Get pitch values for jitter calculation
    pitches, _ = librosa.piptrack(y=audio, sr=sr)
    pitch_values = []
    for t in range(pitches.shape[1]):
        index = pitches[:, t].argmax()
        pitch = pitches[index, t]
        if pitch > 0:
            pitch_values.append(pitch)
    
    # Calculate jitter and shimmer
    jitter_stats = calculate_jitter(audio, sr, pitch_values)
    shimmer_stats = calculate_shimmer(audio, sr)
    
    # Calculate overall stress score
    stress_score = calculate_stress_score(pitch_stats, jitter_stats, shimmer_stats)
    
    return {
        "segment_id": segment_id,
        "speaker": speaker,
        "start": round(start_time, 2),
        "end": round(end_time, 2),
        "duration": round(end_time - start_time, 2),
        "stress_score": stress_score,
        "pitch": pitch_stats,
        "jitter": jitter_stats,
        "shimmer": shimmer_stats
    }


# ============================================
# PART 6: BATCH PROCESSING
# ============================================

def process_audio_file(audio_path: str, segments: List[Dict]) -> List[Dict]:
    """
    Process all segments from a diarization output.
    
    Args:
        audio_path: Path to audio file
        segments: List of segments with speaker and timestamps
    
    Returns:
        List of segments with added stress features
    """
    
    print(f"\n🎙️ Analyzing stress for {len(segments)} segments...")
    print("⏳ This may take a minute...")
    
    results = []
    for i, seg in enumerate(segments):
        # Show progress
        print(f"   Processing segment {i+1}/{len(segments)}...", end='\r')
        
        # Extract speaker and timestamps (handles different formats)
        speaker = seg.get('speaker', 'SPEAKER_00')
        start = seg.get('start', seg.get('start_time', 0))
        end = seg.get('end', seg.get('end_time', 0))
        
        # Analyze this segment
        stress_features = analyze_segment(
            audio_path,
            start,
            end,
            segment_id=i,
            speaker=speaker
        )
        
        # Combine with original segment data
        results.append(stress_features)
    
    print("\n✅ Stress analysis complete!                ")
    return results


# ============================================
# PART 7: SAVE RESULTS
# ============================================

def save_stress_results(results: List[Dict], output_path: str = "stress_analysis.json"):
    """
    Save stress analysis results to JSON file with summary statistics.
    
    Args:
        results: List of analyzed segments
        output_path: Path to save JSON file
    """
    
    # Filter out error segments for statistics
    valid_results = [r for r in results if 'error' not in r]
    
    if not valid_results:
        print("❌ No valid segments to analyze")
        return
    
    # Calculate overall statistics
    stress_scores = [r['stress_score'] for r in valid_results]
    
    # Group by speaker
    speakers = {}
    for r in valid_results:
        spk = r['speaker']
        if spk not in speakers:
            speakers[spk] = []
        speakers[spk].append(r['stress_score'])
    
    speaker_stats = {}
    for spk, scores in speakers.items():
        speaker_stats[spk] = {
            "mean_stress": round(float(np.mean(scores)), 3),
            "max_stress": round(float(np.max(scores)), 3),
            "min_stress": round(float(np.min(scores)), 3),
            "segment_count": len(scores)
        }
    
    # Prepare output
    output = {
        "analysis_timestamp": str(np.datetime64('now')),
        "total_segments": len(results),
        "valid_segments": len(valid_results),
        "error_segments": len(results) - len(valid_results),
        "overall_stats": {
            "mean_stress": round(float(np.mean(stress_scores)), 3),
            "median_stress": round(float(np.median(stress_scores)), 3),
            "std_stress": round(float(np.std(stress_scores)), 3),
            "max_stress": round(float(np.max(stress_scores)), 3),
            "min_stress": round(float(np.min(stress_scores)), 3)
        },
        "speaker_stats": speaker_stats,
        "segments": results
    }
    
    # Save to file
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_path}")
    
    # Print summary
    print("\n📊 STRESS ANALYSIS SUMMARY")
    print("="*60)
    print(f"📈 Overall average stress: {output['overall_stats']['mean_stress']:.3f}")
    print(f"📊 Stress range: {output['overall_stats']['min_stress']:.3f} - {output['overall_stats']['max_stress']:.3f}")
    
    print("\n👥 By speaker:")
    for spk, stats in speaker_stats.items():
        print(f"   {spk}: {stats['mean_stress']:.3f} average "
              f"(over {stats['segment_count']} segments)")
    
    # Show most stressed segments
    sorted_segs = sorted(valid_results, key=lambda x: x['stress_score'], reverse=True)
    print("\n🔥 Top 3 most stressed segments:")
    for seg in sorted_segs[:3]:
        duration = seg['end'] - seg['start']
        print(f"   {seg['speaker']}: {seg['start']}s-{seg['end']}s "
              f"({duration:.1f}s) - stress: {seg['stress_score']:.3f}")


# ============================================
# PART 8: VISUALIZATION (Optional)
# ============================================

def plot_stress_timeline(results: List[Dict], output_path: str = "stress_timeline.png"):
    """
    Create a visualization of stress over time.
    
    Args:
        results: List of analyzed segments
        output_path: Path to save the plot
    """
    try:
        import matplotlib.pyplot as plt
        
        # Filter valid segments
        valid_results = [r for r in results if 'error' not in r]
        
        if not valid_results:
            print("⚠️ No valid results to plot")
            return
        
        # Extract data
        starts = [r['start'] for r in valid_results]
        ends = [r['end'] for r in valid_results]
        scores = [r['stress_score'] for r in valid_results]
        speakers = [r['speaker'] for r in valid_results]
        
        # Create figure
        plt.figure(figsize=(12, 6))
        
        # Plot each segment as a horizontal bar
        unique_speakers = list(set(speakers))
        colors = plt.cm.Set3(np.linspace(0, 1, len(unique_speakers)))
        speaker_colors = {spk: colors[i] for i, spk in enumerate(unique_speakers)}
        
        for i, (start, end, score, spk) in enumerate(zip(starts, ends, scores, speakers)):
            plt.barh(i, end-start, left=start, height=0.8, 
                    color=speaker_colors[spk], alpha=score,
                    label=spk if i == 0 else "")
            
            # Add stress score as text
            mid_point = start + (end-start)/2
            plt.text(mid_point, i, f'{score:.2f}', 
                    ha='center', va='center', fontsize=8)
        
        plt.xlabel('Time (seconds)')
        plt.ylabel('Segment')
        plt.title('Vocal Stress Timeline (darker = higher stress)')
        plt.legend(unique_speakers)
        plt.tight_layout()
        
        plt.savefig(output_path, dpi=100)
        print(f"📊 Timeline plot saved to: {output_path}")
        
    except Exception as e:
        print(f"⚠️ Could not create plot: {e}")


# ============================================
# PART 9: MAIN FUNCTION
# ============================================

def main():
    """
    Main function to run stress analysis using diarization results.
    """
    print("="*60)
    print("🎙️ LUMEN STRESS ANALYSIS - LAYER 3")
    print("="*60)
    print("Extracting vocal stress features from speech segments")
    print("="*60)
    
    # Find most recent diarization file
    diarization_dir = "diarizations"
    if not os.path.exists(diarization_dir):
        print(f"❌ Diarization folder not found: {diarization_dir}")
        print("Please run diarizer.py first")
        return
    
    # Look for JSON files in diarizations folder
    json_files = [f for f in os.listdir(diarization_dir) if f.endswith('_speakers.json')]
    
    if not json_files:
        print(f"❌ No speaker diarization files found in {diarization_dir}")
        print("Please run diarizer.py first")
        return
    
    # Use the most recent file
    diarization_file = os.path.join(diarization_dir, json_files[0])
    print(f"📂 Using diarization file: {diarization_file}")
    
    # Load diarization results
    try:
        with open(diarization_file, 'r') as f:
            diarization = json.load(f)
    except Exception as e:
        print(f"❌ Error loading diarization file: {e}")
        return
    
    # Extract segments (handles different formats)
    if 'segments' in diarization:
        segments = diarization['segments']
    elif 'results' in diarization:
        segments = diarization['results']
    else:
        # Try to find any list of segments
        for key, value in diarization.items():
            if isinstance(value, list) and len(value) > 0:
                if 'speaker' in value[0] or 'start' in value[0]:
                    segments = value
                    print(f"📊 Found segments under key: '{key}'")
                    break
        else:
            print("❌ Could not find segments in diarization file")
            return
    
    # Get audio filename
    if 'audio_file' in diarization:
        audio_filename = diarization['audio_file']
    else:
        # Guess from the diarization filename
        audio_filename = json_files[0].replace('_speakers.json', '.wav')
    
    audio_path = f"../datasets/test_audio/{audio_filename}"
    
    if not os.path.exists(audio_path):
        # Try alternative paths
        alt_path = f"../datasets/test_audio/{audio_filename.replace('.wav', '.mp3')}"
        if os.path.exists(alt_path):
            audio_path = alt_path
        else:
            print(f"❌ Audio file not found: {audio_path}")
            print(f"   Also tried: {alt_path}")
            return
    
    print(f"🎵 Audio file: {audio_path}")
    print(f"📊 Loaded {len(segments)} segments from diarization")
    
    # Process audio
    results = process_audio_file(audio_path, segments)
    
    # Save results
    output_file = "stress_analysis.json"
    save_stress_results(results, output_file)
    
    # Create visualization
    try:
        plot_stress_timeline(results, "stress_timeline.png")
    except Exception as e:
        print(f"⚠️ Visualization skipped: {e}")
    
    print("\n" + "="*60)
    print("✅ LAYER 3 COMPLETE!")
    print("="*60)


# ============================================
# PART 10: RUN MAIN FUNCTION
# ============================================

if __name__ == "__main__":
    main()