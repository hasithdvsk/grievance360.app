"""
AICTE Grievance360 - Voice Complaint Whisper Transcription
Direct implementation of Whisper base model transcription with auto-language detection.
"""

import os
import sys

# Set UTF-8 encoding for standard output on Windows
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

import whisper

# 1. Load the lightweight base model (~140MB download on first run)
print("Loading Whisper Model...")
model = whisper.load_model("base")

# 2. Pass your audio file path (e.g., recorded Telugu/Tamil/Hindi audio)
audio_path = sys.argv[1] if len(sys.argv) > 1 else "sample_complaint.mp3"

# If the file does not exist locally, fallback to sample in scripts directory
if not os.path.exists(audio_path):
    script_sample = os.path.join(os.path.dirname(__file__), "scripts", "sample_complaint.wav")
    if os.path.exists(script_sample):
        audio_path = script_sample
    else:
        print(f"Notice: Audio file '{audio_path}' not found. Please provide an audio file path.")
        sys.exit(0)

# Helper to load WAV without requiring external ffmpeg installation
def load_audio_safely(path: str):
    try:
        from whisper.audio import load_audio
        return load_audio(path)
    except Exception:
        if path.lower().endswith(".wav"):
            try:
                import wave
                import numpy as np
                with wave.open(path, "rb") as wf:
                    raw = wf.readframes(wf.getnframes())
                    data = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
                    return data
            except Exception:
                pass
        return path

# 3. Transcribe & Auto-Detect Language
print(f"Transcribing audio from: {audio_path}...")
audio_input = load_audio_safely(audio_path)
result = model.transcribe(audio_input)

print("----------------------------------------")
print(f"Detected Language: {result['language']}")
print(f"Transcribed Text: {result['text']}")
print("----------------------------------------")
