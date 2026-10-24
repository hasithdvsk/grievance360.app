"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Mic,
  Square,
  Upload,
  Play,
  Pause,
  Loader2,
  Sparkles,
  CheckCircle,
  RefreshCw,
  AlertCircle,
  Volume2,
} from "lucide-react";

export interface VoiceTranscriptionPayload {
  transcription: string;
  englishText: string;
  detectedLanguage: string;
  assignedBureau: string;
  priority: string;
}

interface VoiceRecorderProps {
  onTranscriptionComplete: (payload: VoiceTranscriptionPayload) => void;
  className?: string;
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function VoiceRecorder({
  onTranscriptionComplete,
  className = "",
}: VoiceRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [recordedFileName, setRecordedFileName] = useState<string>("voice_complaint.wav");

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Clean up audio URL and timer when unmounting
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (audioUrl) URL.revokeObjectURL(audioUrl);
    };
  }, [audioUrl]);

  const startRecording = async () => {
    setError(null);
    setSuccess(false);
    audioChunksRef.current = [];

    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error("Microphone access is not supported in this browser.");
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : MediaRecorder.isTypeSupported("audio/mp4")
        ? "audio/mp4"
        : "audio/wav";

      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = () => {
        const mime = audioChunksRef.current[0]?.type || "audio/wav";
        const blob = new Blob(audioChunksRef.current, { type: mime });
        const url = URL.createObjectURL(blob);
        setAudioBlob(blob);
        setAudioUrl(url);
        setRecordedFileName("microphone_voice_complaint.wav");

        // Stop all media tracks to release microphone hardware
        stream.getTracks().forEach((track) => track.stop());
      };

      recorder.start(200); // 200ms slice chunks
      setIsRecording(true);
      setRecordingDuration(0);

      timerRef.current = setInterval(() => {
        setRecordingDuration((prev) => prev + 1);
      }, 1000);
    } catch (err: any) {
      console.error("Microphone access error:", err);
      setError(
        err.message || "Could not access microphone. Please check permissions."
      );
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setError(null);
    setSuccess(false);

    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }

    const url = URL.createObjectURL(file);
    setAudioBlob(file);
    setAudioUrl(url);
    setRecordedFileName(file.name);
  };

  const togglePlayback = () => {
    if (!audioPlayerRef.current) return;

    if (isPlaying) {
      audioPlayerRef.current.pause();
      setIsPlaying(false);
    } else {
      audioPlayerRef.current.play();
      setIsPlaying(true);
    }
  };

  const handleAudioEnded = () => {
    setIsPlaying(false);
  };

  const resetRecording = () => {
    if (audioPlayerRef.current) {
      audioPlayerRef.current.pause();
    }
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }
    setAudioBlob(null);
    setAudioUrl(null);
    setIsPlaying(false);
    setSuccess(false);
    setError(null);
    setRecordingDuration(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const submitAudioForTranscription = async () => {
    if (!audioBlob) {
      setError("Please record audio or upload an audio file first.");
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      const formData = new FormData();
      const ext = recordedFileName.endsWith(".mp3")
        ? ".mp3"
        : recordedFileName.endsWith(".m4a")
        ? ".m4a"
        : ".wav";

      formData.append(
        "audio_file",
        audioBlob,
        `complaint_audio_${Date.now()}${ext}`
      );
      formData.append("source_language", "auto");

      const response = await fetch(
        `${API_BASE_URL}/api/v1/multilingual/submit-voice`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `Server returned HTTP ${response.status}`
        );
      }

      const data = await response.json();

      const payload: VoiceTranscriptionPayload = {
        transcription: data.transcription || data.voice_transcription || "",
        englishText:
          data.english_translation ||
          data.englishText ||
          data.translated_english ||
          "",
        detectedLanguage:
          data.detected_language || data.detectedLanguage || "unknown",
        assignedBureau:
          data.assigned_bureau || data.assignedBureau || "BUR_GENERIC",
        priority: data.priority || "MEDIUM",
      };

      setSuccess(true);
      onTranscriptionComplete(payload);
    } catch (err: any) {
      console.error("Audio processing failed:", err);
      setError(
        err.message || "Failed to process audio note. Please try again."
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs
      .toString()
      .padStart(2, "0")}`;
  };

  return (
    <div
      className={`relative overflow-hidden rounded-2xl border border-zinc-800/80 bg-zinc-950/90 p-5 shadow-2xl backdrop-blur-xl transition-all duration-300 hover:border-zinc-700 ${className}`}
    >
      {/* Decorative ambient subtle spotlight */}
      <div className="pointer-events-none absolute -right-16 -top-16 h-36 w-36 rounded-full bg-white/[0.02] blur-3xl" />
      <div className="pointer-events-none absolute -bottom-16 -left-16 h-36 w-36 rounded-full bg-white/[0.02] blur-3xl" />

      {/* Header title */}
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white text-black shadow-lg border border-white/20">
            <Mic className="h-4 w-4 text-black" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white tracking-wide">
              AI Multilingual Voice Grievance Intake
            </h3>
            <p className="text-xs text-zinc-400">
              Speak in Telugu, Tamil, Hindi, Marathi, Bengali, or English
            </p>
          </div>
        </div>

        {audioBlob && (
          <button
            type="button"
            onClick={resetRecording}
            className="flex items-center space-x-1 text-xs text-zinc-400 hover:text-white transition-colors py-1 px-2.5 rounded-lg hover:bg-zinc-800/70"
            title="Reset audio"
          >
            <RefreshCw className="h-3 w-3" />
            <span>Reset</span>
          </button>
        )}
      </div>

      {/* Main recording and playback controls */}
      <div className="space-y-4">
        {/* Controls container */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Record / Stop Button */}
          {!isRecording ? (
            <motion.button
              type="button"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={startRecording}
              disabled={isProcessing}
              className="flex items-center space-x-2 rounded-xl bg-white hover:bg-zinc-200 px-4 py-2.5 text-xs font-bold text-black shadow-lg shadow-white/10 transition-all disabled:opacity-50 border border-white"
            >
              <Mic className="h-4 w-4 text-black" />
              <span>Record Voice Note</span>
            </motion.button>
          ) : (
            <motion.button
              type="button"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={stopRecording}
              className="flex items-center space-x-2 rounded-xl bg-zinc-900 border border-white px-4 py-2.5 text-xs font-bold text-white shadow-lg transition-all animate-pulse"
            >
              <Square className="h-4 w-4 fill-white" />
              <span>Stop Recording ({formatDuration(recordingDuration)})</span>
            </motion.button>
          )}

          {/* Upload Audio File Fallback */}
          <div>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept="audio/*,.wav,.mp3,.m4a"
              className="hidden"
              id="voice-file-upload"
            />
            <motion.button
              type="button"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => fileInputRef.current?.click()}
              disabled={isRecording || isProcessing}
              className="flex items-center space-x-2 rounded-xl border border-zinc-700 bg-zinc-900 hover:bg-zinc-800 px-3.5 py-2.5 text-xs font-medium text-zinc-300 hover:text-white transition-colors disabled:opacity-50"
            >
              <Upload className="h-3.5 w-3.5 text-zinc-400" />
              <span>Upload Audio</span>
            </motion.button>
          </div>

          {/* Audio preview player */}
          {audioUrl && !isRecording && (
            <div className="flex items-center space-x-2 rounded-xl border border-zinc-700 bg-zinc-900 px-3 py-1.5">
              <audio
                ref={audioPlayerRef}
                src={audioUrl}
                onEnded={handleAudioEnded}
                className="hidden"
              />
              <button
                type="button"
                onClick={togglePlayback}
                className="flex h-7 w-7 items-center justify-center rounded-lg bg-white text-black hover:bg-zinc-200 transition-colors"
                title={isPlaying ? "Pause" : "Play"}
              >
                {isPlaying ? (
                  <Pause className="h-3.5 w-3.5 text-black" />
                ) : (
                  <Play className="h-3.5 w-3.5 ml-0.5 text-black" />
                )}
              </button>
              <div className="flex items-center space-x-1.5 text-xs text-zinc-300">
                <Volume2 className="h-3.5 w-3.5 text-zinc-300" />
                <span className="max-w-[130px] truncate text-[11px] text-zinc-400">
                  {recordedFileName}
                </span>
              </div>
            </div>
          )}

          {/* Process with Whisper Button */}
          {audioBlob && !isRecording && (
            <motion.button
              type="button"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={submitAudioForTranscription}
              disabled={isProcessing}
              className="ml-auto flex items-center space-x-2 rounded-xl bg-white hover:bg-zinc-200 px-4 py-2.5 text-xs font-bold text-black shadow-lg shadow-white/10 transition-all disabled:opacity-50 border border-white"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin text-black" />
                  <span>Transcribing with Whisper...</span>
                </>
              ) : success ? (
                <>
                  <CheckCircle className="h-4 w-4 text-black" />
                  <span>Transcribed & Classified</span>
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 text-black" />
                  <span>Transcribe & Auto-Triage</span>
                </>
              )}
            </motion.button>
          )}
        </div>

        {/* Live sound wave visualization when recording */}
        {isRecording && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="flex items-center justify-between rounded-xl border border-red-500/30 bg-red-950/20 px-4 py-3"
          >
            <div className="flex items-center space-x-2">
              <span className="relative flex h-3 w-3">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-red-400 opacity-75" />
                <span className="relative inline-flex h-3 w-3 rounded-full bg-red-500" />
              </span>
              <span className="text-xs font-medium text-red-300">
                Recording microphone audio... Speak your grievance clearly
              </span>
            </div>
            {/* Visual sound waves simulation */}
            <div className="flex items-center space-x-1">
              {[40, 70, 30, 90, 60, 100, 45, 80, 55, 30].map((height, i) => (
                <motion.span
                  key={i}
                  animate={{
                    height: [`${height * 0.25}px`, `${height * 0.4}px`, `${height * 0.15}px`],
                  }}
                  transition={{
                    repeat: Infinity,
                    duration: 0.6 + (i % 3) * 0.2,
                    ease: "easeInOut",
                  }}
                  className="w-1 rounded-full bg-rose-400/80"
                  style={{ minHeight: "4px" }}
                />
              ))}
            </div>
          </motion.div>
        )}

        {/* Status alerts */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              className="flex items-center space-x-2 rounded-xl border border-red-500/30 bg-red-950/40 p-3 text-xs text-red-300"
            >
              <AlertCircle className="h-4 w-4 shrink-0 text-red-400" />
              <span>{error}</span>
            </motion.div>
          )}

          {success && (
            <motion.div
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              className="flex items-center space-x-2 rounded-xl border border-emerald-500/30 bg-emerald-950/40 p-3 text-xs text-emerald-300"
            >
              <CheckCircle className="h-4 w-4 shrink-0 text-emerald-400" />
              <span>
                Audio successfully transcribed! Grievance description and AI bureau classification populated below.
              </span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
