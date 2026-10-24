"use client";

import React from "react";
import { motion } from "framer-motion";
import {
  ShieldCheck,
  Cpu,
  MapPin,
  Clock,
  Sparkles,
  Layers,
  Scale,
  BrainCircuit,
  Radio,
} from "lucide-react";

interface MarqueeItem {
  icon: React.ElementType;
  text: string;
  badge?: string;
}

const ITEMS: MarqueeItem[] = [
  { icon: ShieldCheck, text: "AICTE AUTONOMOUS REDRESSAL", badge: "LIVE" },
  { icon: Cpu, text: "SENTENCE-TRANSFORMERS NLP CLASSIFIER", badge: "0.85 SIMILARITY" },
  { icon: Clock, text: "24H RAGGING SLA PRIORITY", badge: "EXPEDITED" },
  { icon: MapPin, text: "POSTGIS GEOSPATIAL CLUSTERING", badge: "GIST INDEX" },
  { icon: BrainCircuit, text: "WHISPER MULTILINGUAL SPEECH INTAKE", badge: "6 LANGUAGES" },
  { icon: Scale, text: "STATUTORY OMBUDSMAN GOVERNANCE", badge: "AICTE 2026" },
  { icon: Radio, text: "TWILIO WHATSAPP & TELEGRAM DISPATCH", badge: "WEBHOOK ACTIVE" },
  { icon: Sparkles, text: "ZERO-TOLERANCE CAMPUS SAFETY", badge: "INSTANT FIR" },
];

export const InfiniteMarquee: React.FC = () => {
  return (
    <div className="relative w-full overflow-hidden py-4 border-y border-zinc-800/80 bg-black/60 select-none">
      {/* Edge gradient fade masks */}
      <div className="pointer-events-none absolute left-0 top-0 bottom-0 w-24 bg-gradient-to-r from-[#050507] to-transparent z-10" />
      <div className="pointer-events-none absolute right-0 top-0 bottom-0 w-24 bg-gradient-to-l from-[#050507] to-transparent z-10" />

      {/* Marquee Track with dual clones for seamless loop */}
      <motion.div
        className="flex whitespace-nowrap gap-8 w-max"
        animate={{ x: ["0%", "-50%"] }}
        transition={{
          repeat: Infinity,
          ease: "linear",
          duration: 32,
        }}
        whileHover={{ animationPlayState: "paused" }}
      >
        {[...ITEMS, ...ITEMS].map((item, idx) => {
          const Icon = item.icon;
          return (
            <div
              key={idx}
              className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-zinc-950/80 border border-zinc-800/80 text-xs font-mono tracking-wider text-zinc-300 hover:border-white/30 hover:text-white transition-colors cursor-default"
            >
              <Icon className="w-3.5 h-3.5 text-zinc-400" />
              <span>{item.text}</span>
              {item.badge && (
                <span className="px-1.5 py-0.2 rounded text-[9px] font-bold tracking-widest uppercase bg-white/10 text-white border border-white/20">
                  {item.badge}
                </span>
              )}
            </div>
          );
        })}
      </motion.div>
    </div>
  );
};

export default InfiniteMarquee;
