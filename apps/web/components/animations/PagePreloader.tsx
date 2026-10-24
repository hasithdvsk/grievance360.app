"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Logo from "@/components/Logo";

interface PagePreloaderProps {
  onComplete?: () => void;
}

const TELEMETRY_LOGS = [
  "INITIALIZING NEURAL NLP TRIAGE ENGINE (all-MiniLM-L6-v2)...",
  "CALIBRATING POSTGIS GEOSPATIAL CLUSTERS & GIST INDEXES...",
  "CONNECTING 24H RAGGING & STATUTORY SLA CRON TIMERS...",
  "VERIFYING AICTE AUTONOMOUS OMBUDSMAN PROTOCOLS...",
  "SYSTEM SECURE. LAUNCHING GRIEVANCE360 WORKSPACE...",
];

export const PagePreloader: React.FC<PagePreloaderProps> = ({ onComplete }) => {
  const [progress, setProgress] = useState(0);
  const [logIndex, setLogIndex] = useState(0);
  const [isFinished, setIsFinished] = useState(false);

  useEffect(() => {
    // Prevent body scrolling during initialization
    document.body.style.overflow = "hidden";

    // Progress counter ticker with organic speed curve
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        // Organic step increments
        const increment = Math.floor(Math.random() * 8) + 3;
        const next = Math.min(prev + increment, 100);

        // Update corresponding telemetry message
        const currentLog = Math.min(
          Math.floor((next / 100) * TELEMETRY_LOGS.length),
          TELEMETRY_LOGS.length - 1
        );
        setLogIndex(currentLog);

        return next;
      });
    }, 40);

    return () => {
      clearInterval(interval);
      document.body.style.overflow = "";
    };
  }, []);

  // When counter hits 100%, trigger smooth Awwwards curtain transition
  useEffect(() => {
    if (progress >= 100) {
      const exitTimer = setTimeout(() => {
        setIsFinished(true);
        document.body.style.overflow = "";
        if (onComplete) onComplete();
      }, 350);

      return () => clearTimeout(exitTimer);
    }
  }, [progress, onComplete]);

  return (
    <AnimatePresence>
      {!isFinished && (
        <motion.div
          key="preloader-overlay"
          initial={{ y: "0%" }}
          exit={{
            y: "-100%",
            transition: {
              duration: 0.85,
              ease: [0.76, 0, 0.24, 1], // Signature Awwwards cubic-bezier curve
            },
          }}
          className="fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-[#050507] text-white select-none overflow-hidden"
        >
          {/* Subtle Ambient Grid & Center Spotlight Halo */}
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_50%,rgba(255,255,255,0.06),transparent_70%)] pointer-events-none" />
          <div className="absolute inset-0 opacity-[0.03] bg-[linear-gradient(to_right,#ffffff_1px,transparent_1px),linear-gradient(to_bottom,#ffffff_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none" />

          {/* Central Initializer Stage */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 15 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, y: -40, filter: "blur(8px)", transition: { duration: 0.35 } }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="relative z-10 flex flex-col items-center text-center px-6 max-w-lg w-full"
          >
            {/* Redesigned Grievance360 Emblem with Breathing Halo */}
            <div className="relative mb-6">
              <div className="absolute -inset-4 rounded-full bg-white/[0.08] blur-xl animate-pulse" />
              <Logo size={58} showText={false} animate={false} />
            </div>

            {/* Brand Title & Statutory Badges */}
            <div className="flex items-center gap-2 mb-2">
              <span className="font-extrabold text-2xl tracking-tight text-white">
                Grievance<span className="text-zinc-400 font-black">360°</span>
              </span>
              <span className="px-2 py-0.5 text-[9px] font-mono font-bold uppercase rounded bg-white/10 text-zinc-300 border border-white/20">
                v1.0.0 CORE
              </span>
            </div>

            <p className="text-xs text-zinc-400 uppercase tracking-widest font-mono mb-8">
              AICTE Autonomous Redressal Intelligence
            </p>

            {/* Large Awwwards Percentage Counter */}
            <div className="flex items-baseline justify-center font-mono font-black tracking-tighter text-6xl sm:text-7xl mb-4">
              <span className="text-white drop-shadow-[0_0_20px_rgba(255,255,255,0.3)]">
                {progress.toString().padStart(2, "0")}
              </span>
              <span className="text-2xl sm:text-3xl text-zinc-500 ml-1 font-semibold">%</span>
            </div>

            {/* Hairline Progress Bar */}
            <div className="w-64 sm:w-80 h-[3px] rounded-full bg-zinc-900 border border-zinc-800/80 overflow-hidden mb-6 relative">
              <motion.div
                className="h-full bg-gradient-to-r from-zinc-400 via-white to-zinc-300 shadow-[0_0_12px_rgba(255,255,255,0.8)]"
                style={{ width: `${progress}%` }}
                transition={{ ease: "easeOut" }}
              />
            </div>

            {/* Real-time Telemetry Status Log */}
            <div className="h-6 flex items-center justify-center font-mono text-[11px] text-zinc-400 tracking-wider">
              <span className="w-1.5 h-1.5 rounded-full bg-white animate-ping mr-2" />
              <span className="truncate max-w-[320px] sm:max-w-md">
                {TELEMETRY_LOGS[logIndex]}
              </span>
            </div>
          </motion.div>

          {/* Bottom Telemetry Footer */}
          <div className="absolute bottom-8 left-0 right-0 px-8 flex items-center justify-between text-[10px] font-mono text-zinc-600">
            <span>AICTE CENTRAL REPOSITORY</span>
            <span>SECURE BOOT PROTOCOL</span>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default PagePreloader;
