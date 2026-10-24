"""
Grievance360 Audio Transcription & Language Detection Utility
Powered by OpenAI Whisper base model.

Usage:
    python transcribe_audio.py [audio_file_path]
    e.g. python transcribe_audio.py sample_complaint.mp3
"""

import sys
import os
import argparse

# Set UTF-8 encoding for standard output on Windows
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add apps/api to sys.path so services are importable if needed
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_sample_audio_if_missing(audio_path: str):
    """
    If the requested sample audio doesn't exist, generate a dummy sample WAV
    so the script can be tested immediately without crashing.
    """
    if os.path.exists(audio_path):
        return audio_path

    # Check relative to script directory
    script_dir_sample = os.path.join(os.path.dirname(__file__), os.path.basename(audio_path))
    if os.path.exists(script_dir_sample):
        return script_dir_sample

    script_dir_wav = os.path.join(os.path.dirname(__file__), os.path.splitext(os.path.basename(audio_path))[0] + ".wav")
    if os.path.exists(script_dir_wav):
        return script_dir_wav

    # If it's sample_complaint.mp3 or sample_complaint.wav, create a sample wav
    sample_wav = os.path.splitext(audio_path)[0] + ".wav"
    if not os.path.exists(sample_wav):
        print(f"[Notice] '{audio_path}' not found. Generating sample audio tone '{sample_wav}' for testing...")
        import wave
        import math
        import struct

        with wave.open(sample_wav, "w") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(16000)
            # 2 seconds of 16kHz sine wave
            for i in range(32000):
                sample = int(16000 * math.sin(2 * math.pi * 300 * i / 16000))
                f.writeframes(struct.pack("<h", sample))

    return sample_wav if not os.path.exists(audio_path) else audio_path


def load_audio_safely(audio_path: str):
    """
    Attempts to read audio file into a 16kHz float32 numpy array.
    If ffmpeg is installed, uses Whisper's native load_audio.
    Otherwise, if WAV format, reads via Python standard library wave module.
    """
    import numpy as np

    # 1. Try native whisper load_audio (requires ffmpeg)
    try:
        from whisper.audio import load_audio
        return load_audio(audio_path)
    except Exception as e:
        # Fallback for WAV files without requiring external ffmpeg
        if audio_path.lower().endswith(".wav"):
            try:
                import wave
                with wave.open(audio_path, "rb") as wf:
                    n_channels = wf.getnchannels()
                    sampwidth = wf.getsampwidth()
                    framerate = wf.getframerate()
                    n_frames = wf.getnframes()
                    raw_data = wf.readframes(n_frames)

                if sampwidth == 2:
                    audio_int16 = np.frombuffer(raw_data, dtype=np.int16)
                    # Downmix stereo to mono if needed
                    if n_channels > 1:
                        audio_int16 = audio_int16.reshape(-1, n_channels).mean(axis=1).astype(np.int16)
                    audio_float32 = audio_int16.astype(np.float32) / 32768.0

                    # Resample to 16000 Hz if necessary
                    if framerate != 16000 and len(audio_float32) > 0:
                        indices = np.linspace(0, len(audio_float32) - 1, int(len(audio_float32) * 16000 / framerate))
                        audio_float32 = np.interp(indices, np.arange(len(audio_float32)), audio_float32).astype(np.float32)

                    return audio_float32
            except Exception as wav_err:
                print(f"[Warning] WAV fallback reader failed: {wav_err}")

        # If we cannot load via ffmpeg or wave, return audio_path and let whisper attempt
        return audio_path


def main():
    parser = argparse.ArgumentParser(description="Transcribe voice grievance using OpenAI Whisper")
    parser.add_argument(
        "audio_path",
        nargs="?",
        default="sample_complaint.mp3",
        help="Path to audio file (.mp3, .wav, .m4a)",
    )
    parser.add_argument(
        "--model",
        default="base",
        help="Whisper model name: tiny, base, small, medium (default: base)",
    )
    parser.add_argument(
        "--triage",
        action="store_true",
        help="Run AICTE Bureau & Priority classification on the transcribed text",
    )
    args = parser.parse_args()

    audio_path = args.audio_path
    if not os.path.exists(audio_path):
        audio_path = generate_sample_audio_if_missing(audio_path)

    import whisper

    # 1. Load the lightweight base model (~140MB download on first run)
    print(f"Loading Whisper Model ('{args.model}')...")
    model = whisper.load_model(args.model)

    # 2. Pass your audio file path (e.g., recorded Telugu/Tamil/Hindi audio)
    print(f"Target Audio Path: {audio_path}")

    # 3. Transcribe & Auto-Detect Language
    print("Transcribing audio...")
    try:
        # Load audio safely with numpy/wave fallback if ffmpeg is missing
        audio_input = load_audio_safely(audio_path)
        result = model.transcribe(audio_input)
    except Exception as exc:
        print(f"[Warning] Direct inference encountered: {exc}")
        print("Falling back to Grievance360 Multilingual Service parser...")
        from services.multilingual_service import transcribe_audio_detailed
        result = transcribe_audio_detailed(audio_path)

    print("\n----------------------------------------")
    print(f"Detected Language: {result.get('language')}")
    print(f"Transcribed Text: {result.get('text', '').strip()}")
    print("----------------------------------------\n")

    # Optional: Run AICTE NLP Triage
    if args.triage:
        text = result.get("text", "").strip()
        if text:
            from services.multilingual_service import translate_to_english
            from services.nlp_engine import classify_bureau_and_priority

            lang = result.get("language", "en")
            translated = translate_to_english(text, lang)
            print(f"English Translation: {translated}")

            triage = classify_bureau_and_priority(translated)
            print(f"Assigned Bureau: {triage['bureau_name']}")
            print(f"Assigned Priority: {triage['priority']}")


if __name__ == "__main__":
    main()
