"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import {
  ShieldAlert,
  Building2,
  Scale,
  BrainCircuit,
  Clock,
  ArrowRight,
  Layers,
  LayoutGrid,
  Sparkles,
  CheckCircle2,
} from "lucide-react";

interface BureauData {
  id: string;
  name: string;
  code: string;
  sla: string;
  slaHours: number;
  officer: string;
  complianceRate: string;
  desc: string;
  tags: string[];
  icon: React.ElementType;
  accent: string;
  badgeBg: string;
}

const BUREAUS: BureauData[] = [
  {
    id: "ragging",
    name: "Anti-Ragging Bureau",
    code: "RAGGING",
    sla: "24h Priority SLA",
    slaHours: 24,
    officer: "Dr. K. S. Ramanathan",
    complianceRate: "99.1%",
    desc: "Hostel intimidation, psychological bullying, late-night roll calls, physical harassment, and immediate campus safety interventions.",
    tags: ["Hostel Security", "Zero Tolerance", "Nodal Dispatch", "Immediate FIR"],
    icon: ShieldAlert,
    accent: "text-white",
    badgeBg: "bg-white/10 border-white/20 text-white",
  },
  {
    id: "approval",
    name: "Approval & Affiliation Bureau",
    code: "APPROVAL",
    sla: "48h Standard SLA",
    slaHours: 48,
    officer: "Prof. Ananya Sen",
    complianceRate: "97.4%",
    desc: "Unauthorized college operations, fraudulent seat expansion, faculty deficiency, substandard lab norms, and infrastructure compliance.",
    tags: ["Seat Sanctions", "Faculty Audit", "AICTE Standards", "Lab Equipment"],
    icon: Building2,
    accent: "text-zinc-200",
    badgeBg: "bg-zinc-800/80 border-zinc-700/60 text-zinc-200",
  },
  {
    id: "finance",
    name: "Finance & Fellowship Bureau",
    code: "FINANCE",
    sla: "72h Fiscal SLA",
    slaHours: 72,
    officer: "CA Rajeshwar Rao",
    complianceRate: "95.8%",
    desc: "Pragati & Saksham scholarship delays, tuition fee refunds, capitation fee extortion, and PG scholarship direct bank transfers.",
    tags: ["Scholarship DBT", "Capitation Fraud", "Fee Refunds", "Audit Trials"],
    icon: Scale,
    accent: "text-white",
    badgeBg: "bg-white/10 border-white/20 text-white",
  },
  {
    id: "legal",
    name: "Legal & Statutory Bureau",
    code: "LEGAL",
    sla: "96h Statutory SLA",
    slaHours: 96,
    officer: "Adv. Sunita Mukherjee",
    complianceRate: "94.6%",
    desc: "Statutory governance non-compliance, unlawful faculty service terminations, institutional writ petitions, and arbitration appeals.",
    tags: ["Service Appeals", "Writ Response", "Regulatory Orders", "Ombudsman"],
    icon: BrainCircuit,
    accent: "text-zinc-200",
    badgeBg: "bg-zinc-800/80 border-zinc-700/60 text-zinc-200",
  },
];

export const StackedBureauCards: React.FC = () => {
  const [activeId, setActiveId] = useState<string>("ragging");
  const [viewMode, setViewMode] = useState<"stacked" | "grid">("stacked");

  const activeBureau = BUREAUS.find((b) => b.id === activeId) || BUREAUS[0];

  return (
    <div className="space-y-8">
      {/* View Mode Toggle Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-zinc-800/80 pb-4">
        <div>
          <span className="text-xs font-bold tracking-widest uppercase text-zinc-500">
            Automated Jurisdictional Routing
          </span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
            Specialized AICTE Redressal Bureaus
          </h2>
        </div>

        {/* Tactile Toggle Pill */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-black/80 border border-zinc-800/80 self-start sm:self-auto">
          <button
            onClick={() => setViewMode("stacked")}
            data-cursor="pointer"
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              viewMode === "stacked"
                ? "bg-white text-black shadow-md font-bold"
                : "text-zinc-400 hover:text-white"
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Stacked Deck</span>
          </button>
          <button
            onClick={() => setViewMode("grid")}
            data-cursor="pointer"
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              viewMode === "grid"
                ? "bg-white text-black shadow-md font-bold"
                : "text-zinc-400 hover:text-white"
            }`}
          >
            <LayoutGrid className="w-3.5 h-3.5" />
            <span>Tactile Grid</span>
          </button>
        </div>
      </div>

      {/* STACKED DECK INTERACTION MODE */}
      {viewMode === "stacked" ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start pt-2">
          {/* Left Column: Stacked Physical Cards */}
          <div className="lg:col-span-5 relative min-h-[380px] sm:min-h-[420px] flex items-center justify-center">
            <div className="relative w-full max-w-sm h-[320px]">
              {BUREAUS.map((bureau, index) => {
                const isActive = bureau.id === activeId;
                const orderIndex =
                  (BUREAUS.findIndex((b) => b.id === activeId) - index + BUREAUS.length) %
                  BUREAUS.length;

                // Stack transform physics
                const yOffset = orderIndex * 16;
                const scale = 1 - orderIndex * 0.05;
                const rotation = (orderIndex - 1) * 3;
                const zIndex = BUREAUS.length - orderIndex;

                const IconComponent = bureau.icon;

                return (
                  <motion.div
                    key={bureau.id}
                    layout
                    onClick={() => setActiveId(bureau.id)}
                    style={{ zIndex }}
                    animate={{
                      y: yOffset,
                      scale,
                      rotate: rotation,
                      opacity: orderIndex > 3 ? 0 : 1 - orderIndex * 0.15,
                    }}
                    whileHover={
                      !isActive
                        ? { y: yOffset - 12, scale: scale + 0.03, rotate: 0 }
                        : { scale: 1.02 }
                    }
                    transition={{ type: "spring", stiffness: 350, damping: 28 }}
                    className={`absolute inset-x-0 top-0 cursor-pointer p-6 rounded-2xl border transition-colors select-none ${
                      isActive
                        ? "border-white/30 bg-zinc-900 shadow-2xl"
                        : "bg-zinc-950/90 border-zinc-800/80 shadow-lg hover:border-zinc-700/60"
                    }`}
                    data-cursor="pointer"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                            isActive
                              ? "bg-black text-white border border-white/20"
                              : "bg-zinc-900 text-zinc-400"
                          }`}
                        >
                          <IconComponent className="w-5 h-5" />
                        </div>
                        <div>
                          <h4 className="font-bold text-white text-base tracking-tight">
                            {bureau.name}
                          </h4>
                          <span className="text-[11px] font-mono font-medium text-zinc-500">
                            {bureau.code} BUREAU
                          </span>
                        </div>
                      </div>

                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-md uppercase tracking-wider ${bureau.badgeBg}`}
                      >
                        {bureau.sla}
                      </span>
                    </div>

                    <p className="mt-4 text-xs text-zinc-400 line-clamp-2 leading-relaxed">
                      {bureau.desc}
                    </p>

                    <div className="mt-4 pt-3 border-t border-zinc-800/80 flex items-center justify-between text-[11px]">
                      <span className="text-zinc-500 font-medium">
                        Officer: <span className="text-zinc-200">{bureau.officer}</span>
                      </span>
                      <span className="text-zinc-200 font-semibold flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3 text-white" />
                        {bureau.complianceRate}
                      </span>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>

          {/* Right Column: Debossed Tactile Reveal Stage */}
          <div className="lg:col-span-7">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeBureau.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.25 }}
                className="p-6 sm:p-8 rounded-2xl bg-zinc-950/90 border border-zinc-800/80 relative overflow-hidden"
              >
                {/* Background Ambient Glow */}
                <div className="absolute top-0 right-0 w-64 h-64 bg-white/[0.02] rounded-full blur-3xl pointer-events-none" />

                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-1 text-xs font-bold rounded-md bg-zinc-900 text-zinc-300 border border-zinc-700/50">
                      Active Bureau Dossier
                    </span>
                    <span className={`text-xs font-bold px-2.5 py-1 rounded-md ${activeBureau.badgeBg}`}>
                      {activeBureau.sla}
                    </span>
                  </div>

                  <span className="text-xs font-mono text-zinc-500">
                    Jurisdiction Code: <strong className="text-white font-bold">{activeBureau.code}</strong>
                  </span>
                </div>

                <h3 className="text-2xl font-black text-white tracking-tight mt-4">
                  {activeBureau.name}
                </h3>

                <p className="mt-2 text-sm text-zinc-300 leading-relaxed">
                  {activeBureau.desc}
                </p>

                {/* Debossed Metrics Inset Well */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 my-6 p-4 rounded-xl bg-black border border-zinc-800/80">
                  <div className="space-y-0.5">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-zinc-500">
                      Standard SLA
                    </span>
                    <div className="text-lg font-black text-white flex items-center gap-1.5">
                      <Clock className="w-4 h-4 text-white" />
                      <span>{activeBureau.slaHours} Hours</span>
                    </div>
                  </div>

                  <div className="space-y-0.5">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-zinc-500">
                      Nodal Lead
                    </span>
                    <div className="text-sm font-bold text-zinc-200 truncate">
                      {activeBureau.officer}
                    </div>
                  </div>

                  <div className="space-y-0.5">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-zinc-500">
                      Audit Adherence
                    </span>
                    <div className="text-lg font-black text-white flex items-center gap-1">
                      <CheckCircle2 className="w-4 h-4 text-white" />
                      <span>{activeBureau.complianceRate}</span>
                    </div>
                  </div>
                </div>

                {/* Jurisdiction Tags */}
                <div className="space-y-2">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-zinc-500">
                    Covered Infraction Areas
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {activeBureau.tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-2.5 py-1 text-xs font-medium rounded-lg bg-zinc-900/90 text-zinc-200 border border-zinc-800"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Direct Action Trigger */}
                <div className="mt-8 pt-6 border-t border-zinc-800/80 flex flex-col sm:flex-row items-center justify-between gap-4">
                  <span className="text-xs text-zinc-500">
                    Embeddings pre-computed via <code className="text-zinc-300 font-mono">MiniLM-L6-v2</code>
                  </span>

                  <Link
                    href={`/file-complaint?bureau=${activeBureau.code}`}
                    data-cursor="pointer"
                    className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-bold text-xs uppercase tracking-wider text-black bg-white hover:bg-zinc-200 shadow-xl shadow-white/10 transition-transform hover:scale-[1.02] border border-white"
                  >
                    <span>File Grievance to {activeBureau.code}</span>
                    <ArrowRight className="w-4 h-4 text-black" />
                  </Link>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      ) : (
        /* TACTILE GRID MODE */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 pt-2">
          {BUREAUS.map((bureau) => {
            const IconComponent = bureau.icon;
            return (
              <motion.div
                key={bureau.id}
                whileHover={{ y: -4, scale: 1.01 }}
                className="p-6 rounded-2xl bg-zinc-950 border border-zinc-800/80 hover:border-white/20 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-black text-white border border-zinc-800">
                      <IconComponent className="w-5 h-5" />
                    </div>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-md uppercase tracking-wider ${bureau.badgeBg}`}
                    >
                      {bureau.sla}
                    </span>
                  </div>

                  <h4 className="mt-4 font-bold text-white text-lg tracking-tight">
                    {bureau.name}
                  </h4>
                  <p className="mt-2 text-xs text-zinc-400 leading-relaxed line-clamp-3">
                    {bureau.desc}
                  </p>
                </div>

                <div className="mt-6 pt-4 border-t border-zinc-800/80">
                  <div className="flex items-center justify-between text-xs mb-3">
                    <span className="text-zinc-500 font-medium">Compliance</span>
                    <span className="text-zinc-200 font-bold">{bureau.complianceRate}</span>
                  </div>
                  <Link
                    href={`/file-complaint?bureau=${bureau.code}`}
                    data-cursor="pointer"
                    className="w-full flex items-center justify-center gap-1.5 py-2 text-xs font-bold rounded-lg text-zinc-200 bg-zinc-900 border border-zinc-800 hover:bg-white hover:text-black hover:border-white transition-all"
                  >
                    <span>Direct Dispatch</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default StackedBureauCards;
