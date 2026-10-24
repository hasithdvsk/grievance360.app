"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";

interface ScrambleTextProps {
  phrases?: string[];
  defaultText?: string;
  className?: string;
  intervalMs?: number;
  scrambleSpeedMs?: number;
  pauseMs?: number;
  onHoverScramble?: boolean;
}

const GLYPHS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_!@#$%^&*[]{}<>/\\+=~█▓▒░";

export const ScrambleText: React.FC<ScrambleTextProps> = ({
  phrases = [
    "AI-Driven Redressal",
    "Statutory 24h Accountability",
    "Zero-Tolerance Campus Safety",
    "Autonomous Bureau Routing",
    "Geospatial SLA Enforcement",
  ],
  defaultText,
  className = "",
  intervalMs = 4000,
  scrambleSpeedMs = 28,
  pauseMs = 2500,
  onHoverScramble = true,
}) => {
  const currentPhrases = defaultText ? [defaultText] : phrases;
  const [phraseIndex, setPhraseIndex] = useState(0);
  const targetText = currentPhrases[phraseIndex % currentPhrases.length];
  const [displayText, setDisplayText] = useState(targetText);
  const [isScrambling, setIsScrambling] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const frameRef = useRef<number | null>(null);

  // Scramble animation engine
  const runScramble = useCallback(
    (newTarget: string, onComplete?: () => void) => {
      setIsScrambling(true);
      let step = 0;
      const totalSteps = newTarget.length * 3; // Number of iteration frames

      if (timerRef.current) clearInterval(timerRef.current);

      timerRef.current = setInterval(() => {
        step++;
        const resolvedChars = Math.floor(step / 3);

        const scrambled = newTarget
          .split("")
          .map((char, idx) => {
            if (char === " ") return " ";
            if (idx < resolvedChars) {
              return char;
            }
            return GLYPHS[Math.floor(Math.random() * GLYPHS.length)];
          })
          .join("");

        setDisplayText(scrambled);

        if (step >= totalSteps) {
          if (timerRef.current) clearInterval(timerRef.current);
          setDisplayText(newTarget);
          setIsScrambling(false);
          if (onComplete) onComplete();
        }
      }, scrambleSpeedMs);
    },
    [scrambleSpeedMs]
  );

  // Initial mount scramble & rotating sequence if multiple phrases
  useEffect(() => {
    runScramble(targetText);

    if (currentPhrases.length <= 1) return;

    let timeoutId: NodeJS.Timeout;

    const cycleNext = () => {
      timeoutId = setTimeout(() => {
        setPhraseIndex((prev) => {
          const nextIndex = (prev + 1) % currentPhrases.length;
          const nextWord = currentPhrases[nextIndex];
          runScramble(nextWord, cycleNext);
          return nextIndex;
        });
      }, intervalMs);
    };

    cycleNext();

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [currentPhrases.length, intervalMs, runScramble, targetText]);

  // Hover effect: re-scrambles current word dynamically on mouse enter
  const handleMouseEnter = () => {
    if (!onHoverScramble || isScrambling) return;
    runScramble(targetText);
  };

  return (
    <span
      onMouseEnter={handleMouseEnter}
      data-cursor="pointer"
      className={`inline-block font-mono tracking-tight select-none transition-colors ${className}`}
      title="Interactive Decryption Node"
    >
      <span className="relative">
        {displayText}
        {/* Blinking futuristic cursor glyph */}
        <span
          className={`inline-block w-2 sm:w-2.5 h-[1.1em] ml-1 bg-white align-middle shadow-[0_0_8px_rgba(255,255,255,0.9)] ${
            isScrambling ? "opacity-100" : "animate-pulse opacity-70"
          }`}
        />
      </span>
    </span>
  );
};

export default ScrambleText;
