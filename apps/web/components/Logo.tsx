"use client";

import React from "react";
import { motion } from "framer-motion";

interface LogoProps {
  className?: string;
  size?: number | "sm" | "md" | "lg";
  showText?: boolean;
  showBadge?: boolean;
  animate?: boolean;
}

export const Logo: React.FC<LogoProps> = ({
  className = "",
  size = "md",
  showText = true,
  showBadge = true,
  animate = true,
}) => {
  // Resolve numeric dimension
  const dimension =
    typeof size === "number"
      ? size
      : size === "sm"
      ? 30
      : size === "lg"
      ? 52
      : 42;

  return (
    <motion.div
      className={`inline-flex items-center gap-3.5 select-none ${className}`}
      whileHover={animate ? { scale: 1.025 } : undefined}
      whileTap={animate ? { scale: 0.98 } : undefined}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
      data-cursor="pointer"
    >
      {/* Informative Vector Emblem SVG */}
      <div
        className="relative flex items-center justify-center flex-shrink-0"
        style={{ width: dimension, height: dimension }}
      >
        {/* Soft Monochromatic Ambient Backlight */}
        <div className="absolute inset-0 rounded-2xl bg-white/10 blur-lg pointer-events-none" />

        <svg
          viewBox="0 0 120 120"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-full h-full drop-shadow-[0_2px_14px_rgba(255,255,255,0.25)]"
        >
          <defs>
            {/* Platinum / Metallic Silver Gradients */}
            <linearGradient id="logoPlatinumGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#FFFFFF" />
              <stop offset="45%" stopColor="#E4E4E7" />
              <stop offset="80%" stopColor="#A1A1AA" />
              <stop offset="100%" stopColor="#71717A" />
            </linearGradient>

            <linearGradient id="logoCoreGlow" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#FFFFFF" />
              <stop offset="100%" stopColor="#D4D4D8" />
            </linearGradient>

            {/* Specular Dropshadow Filter */}
            <filter id="logoSpecularGlow" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow
                dx="0"
                dy="1"
                stdDeviation="3"
                floodColor="#FFFFFF"
                floodOpacity="0.4"
              />
            </filter>
          </defs>

          {/* 1. OUTER 360° ORBITAL COMPASS RING WITH 4 BUREAU CARDINAL TICKS */}
          <circle
            cx="60"
            cy="60"
            r="54"
            stroke="url(#logoPlatinumGrad)"
            strokeWidth="2.5"
            strokeDasharray="280 18 12 18"
            className="origin-center"
            filter="url(#logoSpecularGlow)"
          />

          {/* 4 Cardinal Bureau Precision Nodes (Ragging, Approval, Finance, Legal) */}
          {/* North (0°): Anti-Ragging */}
          <circle cx="60" cy="6" r="3.2" fill="#FFFFFF" className="animate-pulse" />
          <line x1="60" y1="2" x2="60" y2="11" stroke="#FFFFFF" strokeWidth="1.5" />

          {/* East (90°): Approval & Affiliation */}
          <circle cx="114" cy="60" r="2.6" fill="#E4E4E7" />
          <line x1="109" y1="60" x2="118" y2="60" stroke="#E4E4E7" strokeWidth="1.5" />

          {/* South (180°): Finance & Fellowship */}
          <circle cx="60" cy="114" r="2.6" fill="#A1A1AA" />
          <line x1="60" y1="109" x2="60" y2="118" stroke="#A1A1AA" strokeWidth="1.5" />

          {/* West (270°): Legal & Statutory */}
          <circle cx="6" cy="60" r="2.6" fill="#E4E4E7" />
          <line x1="2" y1="60" x2="11" y2="60" stroke="#E4E4E7" strokeWidth="1.5" />

          {/* Continuously Rotating Satellite Orbit Track */}
          <g className="origin-center animate-[spin_12s_linear_infinite]">
            <circle cx="98" cy="30" r="2.2" fill="#FFFFFF" />
            <circle cx="22" cy="90" r="1.8" fill="#D4D4D8" />
          </g>

          {/* 2. PROTECTIVE AUTONOMOUS SHIELD CREST */}
          <path
            d="M60 18 L94 34 V62 C94 82 79 97 60 104 C41 97 26 82 26 62 V34 Z"
            stroke="url(#logoPlatinumGrad)"
            strokeWidth="2.8"
            strokeOpacity="0.8"
            fill="url(#logoPlatinumGrad)"
            fillOpacity="0.04"
            strokeLinejoin="round"
          />

          {/* Inner Reinforcement Shield Inset Line */}
          <path
            d="M60 26 L86 38 V60 C86 76 74 88 60 94 C46 88 34 76 34 60 V38 Z"
            stroke="url(#logoPlatinumGrad)"
            strokeWidth="1.2"
            strokeOpacity="0.35"
            fill="none"
          />

          {/* 3. SCALES OF JUSTICE & OMBUDSMAN STATUTORY PILLARS */}
          {/* Horizontal Justice Balance Beam */}
          <path
            d="M38 52 L82 52"
            stroke="#FFFFFF"
            strokeWidth="2.4"
            strokeLinecap="round"
          />

          {/* Left Pan (Equity / Grievant) */}
          <path
            d="M38 52 L31 66 M38 52 L45 66"
            stroke="#E4E4E7"
            strokeWidth="1.5"
            strokeLinecap="round"
          />
          <path
            d="M28 66 C28 71 48 71 48 66 Z"
            fill="#FFFFFF"
            fillOpacity="0.15"
            stroke="#FFFFFF"
            strokeWidth="1.5"
            strokeLinejoin="round"
          />

          {/* Right Pan (Accountability / Institution) */}
          <path
            d="M82 52 L75 66 M82 52 L89 66"
            stroke="#E4E4E7"
            strokeWidth="1.5"
            strokeLinecap="round"
          />
          <path
            d="M72 66 C72 71 92 71 92 66 Z"
            fill="#FFFFFF"
            fillOpacity="0.15"
            stroke="#FFFFFF"
            strokeWidth="1.5"
            strokeLinejoin="round"
          />

          {/* Central Vertical Pillar of Equilibrium */}
          <path
            d="M60 38 V80"
            stroke="url(#logoPlatinumGrad)"
            strokeWidth="2.5"
            strokeLinecap="round"
          />
          {/* Pillar Pedestal Base */}
          <path
            d="M52 80 H68"
            stroke="url(#logoPlatinumGrad)"
            strokeWidth="2.5"
            strokeLinecap="round"
          />

          {/* 4. AI NEURAL NEXUS (360 SPARKLE STAR & INTELLIGENCE NODE) */}
          <path
            d="M60 40 C60 47 53 52 46 52 C53 52 60 57 60 64 C60 57 67 52 74 52 C67 52 60 47 60 40 Z"
            fill="url(#logoCoreGlow)"
            filter="url(#logoSpecularGlow)"
          />
          {/* Core White Pulse Center */}
          <circle cx="60" cy="52" r="2.5" fill="#FFFFFF" />
        </svg>
      </div>

      {/* Informative Branding & Typography */}
      {showText && (
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className="font-extrabold text-lg sm:text-xl tracking-tight text-white flex items-center">
              Grievance
              <span className="text-zinc-300 font-black ml-0.5 tracking-tight flex items-baseline">
                360
                <span className="text-xs font-mono font-bold text-zinc-400 ml-0.5">°</span>
              </span>
            </span>

            {showBadge && (
              <span className="px-2 py-0.5 text-[9px] font-bold tracking-wider uppercase rounded-md bg-white/10 text-white border border-white/20 shadow-sm hidden sm:flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
                <span>AICTE CELL</span>
              </span>
            )}
          </div>

          <div className="flex items-center gap-2 -mt-0.5">
            <span className="text-[10px] text-zinc-400 font-medium tracking-wider uppercase hidden sm:inline">
              Autonomous Redressal & NLP Triage
            </span>
            <span className="text-[9px] text-zinc-500 font-mono hidden md:inline">
              • AICTE GOV PROTOCOL
            </span>
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default Logo;
