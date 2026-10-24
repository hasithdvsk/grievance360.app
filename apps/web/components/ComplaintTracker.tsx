"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  Clock,
  AlertTriangle,
  CheckCircle2,
  Building2,
  ShieldAlert,
  ArrowRight,
  FileText,
  Sparkles,
  Copy,
  Check,
  Loader2,
  Calendar,
  Layers,
  User,
  History,
} from "lucide-react";

interface AuditLog {
  log_id: string;
  action_taken: string;
  from_bureau_name?: string | null;
  to_bureau_name?: string | null;
  officer_remarks?: string | null;
  actor_id?: string | null;
  timestamp: string;
}

interface ComplaintData {
  complaint_id: string;
  tracking_id: string;
  title: string;
  description: string;
  complainant_role: string;
  complainant_email: string;
  complainant_phone?: string;
  institution_name?: string;
  institution_city?: string;
  institution_state?: string;
  bureau_name: string;
  priority: string;
  status: string;
  is_duplicate: boolean;
  master_complaint_id?: string | null;
  sla_deadline?: string;
  created_at: string;
  updated_at: string;
  timeline: AuditLog[];
}

// Built-in fallback mock data for testing/demo when backend API is offline
const FALLBACK_MOCK: Record<string, ComplaintData> = {
  "GRV-2026-00001": {
    complaint_id: "30000000-0000-0000-0000-000000000001",
    tracking_id: "GRV-2026-00001",
    title: "Hostel curfew intimidation and verbal ragging of first-year boarders",
    description:
      "Senior hostel residents in Block C subjected new entrants to unpermitted late-night physical roll calls and verbal abuse.",
    complainant_role: "STUDENT",
    complainant_email: "victim.student@example.org",
    complainant_phone: "+919811223344",
    institution_name: "Indian Institute of Technology Delhi (IIT Delhi)",
    institution_city: "New Delhi",
    institution_state: "Delhi",
    bureau_name: "Anti-Ragging Bureau",
    priority: "CRITICAL",
    status: "IN_PROGRESS",
    is_duplicate: false,
    sla_deadline: new Date(Date.now() + 10 * 3600 * 1000).toISOString(),
    created_at: new Date(Date.now() - 4 * 3600 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 2 * 3600 * 1000).toISOString(),
    timeline: [
      {
        log_id: "40000000-0000-0000-0000-000000000001",
        action_taken: "AUTO_TRIAGED_BY_AI",
        to_bureau_name: "Anti-Ragging Bureau",
        officer_remarks:
          "NLP semantic classifier detected severity keywords: curfew intimidation, ragging. Priority set to CRITICAL.",
        actor_id: "SYSTEM_NLP_TRIAGE_WORKER",
        timestamp: new Date(Date.now() - 4 * 3600 * 1000).toISOString(),
      },
      {
        log_id: "40000000-0000-0000-0000-000000000002",
        action_taken: "NOTICE_SERVED_TO_INSTITUTION",
        to_bureau_name: "Anti-Ragging Bureau",
        officer_remarks:
          "Formal inquiry email dispatched to Dean of Student Affairs. Proactive warden report requested within 12 hours.",
        actor_id: "OFFICER_ANTIRAGGING_04",
        timestamp: new Date(Date.now() - 2 * 3600 * 1000).toISOString(),
      },
    ],
  },
};

const STATUS_STEPS = [
  { key: "SUBMITTED", label: "Submitted", desc: "Recorded in Register" },
  { key: "UNDER_REVIEW", label: "Under Review", desc: "AI Triage & Assigned" },
  { key: "ACTION_TAKEN", label: "Action Taken", desc: "Official Notice Served" },
  { key: "RESOLVED", label: "Resolved", desc: "Disposed & Closed" },
];

export default function ComplaintTracker() {
  const [ticketInput, setTicketInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [complaint, setComplaint] = useState<ComplaintData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  // Map API status to visual step index (0 to 3)
  const getStepIndex = (statusStr: string): number => {
    const s = statusStr.toUpperCase();
    if (s === "SUBMITTED") return 0;
    if (s === "AUTO_ASSIGNED" || s === "IN_PROGRESS") return 1;
    if (s === "ACTION_TAKEN" || s === "ESCALATED") return 2;
    if (s === "RESOLVED" || s === "CLOSED") return 3;
    return 1;
  };

  const handleSearch = async (ticketIdToSearch?: string) => {
    const query = (ticketIdToSearch || ticketInput).trim();
    if (!query) {
      setError("Please enter a valid ticket number or complaint ID.");
      return;
    }

    setLoading(true);
    setError(null);

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    try {
      const res = await fetch(`${apiUrl}/api/v1/complaints/track/${encodeURIComponent(query)}`);
      if (res.ok) {
        const data = await res.json();
        setComplaint(data);
      } else {
        // Fallback check in mock store if local dev server is not running
        if (FALLBACK_MOCK[query.toUpperCase()]) {
          setComplaint(FALLBACK_MOCK[query.toUpperCase()]);
        } else {
          setError(`No grievance found matching ticket ID "${query}". Please verify the number.`);
          setComplaint(null);
        }
      }
    } catch {
      // Offline fallback
      if (FALLBACK_MOCK[query.toUpperCase()]) {
        setComplaint(FALLBACK_MOCK[query.toUpperCase()]);
      } else {
        setError(`Cannot reach API at ${apiUrl}. Verified against local mock: Ticket not found.`);
        setComplaint(null);
      }
    } finally {
      setLoading(false);
    }
  };

  const copyTrackingId = (id: string) => {
    navigator.clipboard.writeText(id);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6" id="tracker">
      {/* Search Header Container */}
      <div className="glass-panel rounded-2xl p-6 sm:p-8 space-y-4 border border-zinc-800/80">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-zinc-400">
          <Search className="w-4 h-4 text-zinc-300" />
          <span>Real-time AICTE Grievance Tracking Engine</span>
        </div>
        <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
          Track Your Grievance Status
        </h2>
        <p className="text-sm text-zinc-400">
          Enter your unique Grievance Tracking ID (e.g. <code className="text-zinc-200 font-mono">GRV-2026-00001</code>)
          to monitor bureau dispatch, dynamic SLA countdown, and live audit actions.
        </p>

        {/* Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSearch();
          }}
          className="flex flex-col sm:flex-row gap-3 pt-2"
        >
          <div className="relative flex-1">
            <Search className="w-5 h-5 absolute left-4 top-3.5 text-zinc-500" />
            <input
              type="text"
              value={ticketInput}
              onChange={(e) => setTicketInput(e.target.value)}
              placeholder="e.g. GRV-2026-00001"
              className="w-full pl-12 pr-4 py-3 text-sm sm:text-base rounded-xl bg-zinc-900 border border-zinc-700/80 text-white placeholder-zinc-500 focus:outline-none focus:border-white focus:ring-2 focus:ring-white/20 transition-all font-mono"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-white hover:bg-zinc-200 font-bold text-black shadow-lg shadow-white/10 border border-white transition-all disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-black" />
                <span>Searching...</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4 text-black" />
                <span>Track Status</span>
              </>
            )}
          </button>
        </form>

        {/* Quick Sample Buttons */}
        <div className="flex flex-wrap items-center gap-2 pt-1 text-xs text-zinc-400">
          <span>Try quick sample:</span>
          <button
            type="button"
            onClick={() => {
              setTicketInput("GRV-2026-00001");
              handleSearch("GRV-2026-00001");
            }}
            className="px-2.5 py-1 rounded-md bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border border-zinc-700 transition-colors font-mono"
          >
            GRV-2026-00001 (Ragging / Critical)
          </button>
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs sm:text-sm flex items-center gap-2"
          >
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </motion.div>
        )}
      </div>

      {/* Ticket Details with Framer Motion Smooth Entrance */}
      <AnimatePresence mode="wait">
        {complaint && (
          <motion.div
            key={complaint.tracking_id}
            initial={{ opacity: 0, y: 20, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -15, scale: 0.98 }}
            transition={{ duration: 0.4, ease: "easeOut" }}
            className="glass-panel rounded-2xl p-6 sm:p-8 space-y-8 border border-slate-700/60"
          >
            {/* Top Bar with Ticket ID & Priority Badge */}
            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-6">
              <div className="space-y-1">
                <div className="flex items-center gap-3">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Tracking ID
                  </span>
                  <button
                    onClick={() => copyTrackingId(complaint.tracking_id)}
                    className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md bg-slate-800 text-xs text-slate-300 hover:text-white transition-colors"
                  >
                    {copied ? (
                      <>
                        <Check className="w-3 h-3 text-emerald-400" />
                        <span className="text-emerald-400">Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3 h-3" />
                        <span>Copy</span>
                      </>
                    )}
                  </button>
                </div>
                <div className="text-2xl sm:text-3xl font-extrabold text-white font-mono tracking-tight">
                  {complaint.tracking_id}
                </div>
              </div>

              {/* Dynamic Priority Status Badge */}
              <div className="flex items-center gap-2">
                {complaint.priority === "CRITICAL" ? (
                  <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/10 border border-white/30 text-white text-xs font-bold tracking-wide animate-pulse">
                    <ShieldAlert className="w-4 h-4 text-white" />
                    <span>CRITICAL PRIORITY</span>
                  </div>
                ) : complaint.priority === "HIGH" || complaint.priority === "MEDIUM" ? (
                  <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-zinc-800/80 border border-zinc-700 text-zinc-200 text-xs font-bold tracking-wide">
                    <AlertTriangle className="w-4 h-4 text-zinc-300" />
                    <span>{complaint.priority} PRIORITY</span>
                  </div>
                ) : (
                  <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-zinc-900 border border-zinc-800 text-zinc-400 text-xs font-bold tracking-wide">
                    <CheckCircle2 className="w-4 h-4 text-zinc-400" />
                    <span>{complaint.priority} PRIORITY</span>
                  </div>
                )}
              </div>
            </div>

            {/* Step-by-Step Progress Visualizer */}
            <div className="space-y-4">
              <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">
                Resolution Lifecycle Progress
              </span>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 relative">
                {STATUS_STEPS.map((step, idx) => {
                  const currentStepIdx = getStepIndex(complaint.status);
                  const isCompleted = idx < currentStepIdx;
                  const isCurrent = idx === currentStepIdx;

                  return (
                    <div
                      key={step.key}
                      className={`relative p-4 rounded-xl border transition-all ${
                        isCurrent
                          ? "bg-white/10 border-white/40 shadow-lg shadow-white/5"
                          : isCompleted
                          ? "bg-zinc-900/80 border-zinc-700/80"
                          : "bg-zinc-950/40 border-zinc-800/60 opacity-60"
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <div
                          className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                            isCurrent
                              ? "bg-white text-black"
                              : isCompleted
                              ? "bg-zinc-700 text-white"
                              : "bg-zinc-900 text-zinc-500"
                          }`}
                        >
                          {isCompleted ? <Check className="w-3.5 h-3.5" /> : idx + 1}
                        </div>
                        <span
                          className={`text-xs font-bold ${
                            isCurrent
                              ? "text-white"
                              : isCompleted
                              ? "text-zinc-200"
                              : "text-zinc-500"
                          }`}
                        >
                          {step.label}
                        </span>
                      </div>
                      <p className="text-[11px] text-zinc-400 leading-snug">{step.desc}</p>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Complaint Header & Core Metadata */}
            <div className="space-y-3 p-5 rounded-xl bg-zinc-900/60 border border-zinc-800">
              <h3 className="text-lg sm:text-xl font-bold text-white leading-snug">
                {complaint.title}
              </h3>
              <p className="text-sm text-zinc-300 leading-relaxed">{complaint.description}</p>
            </div>

            {/* Quick Metadata Details Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
              <div className="p-4 rounded-xl bg-zinc-900/40 border border-zinc-800/80 space-y-1">
                <div className="flex items-center gap-1.5 text-zinc-400">
                  <Building2 className="w-3.5 h-3.5 text-zinc-300" />
                  <span>Assigned AICTE Bureau</span>
                </div>
                <div className="font-semibold text-zinc-200 text-sm">{complaint.bureau_name}</div>
              </div>

              <div className="p-4 rounded-xl bg-zinc-900/40 border border-zinc-800/80 space-y-1">
                <div className="flex items-center gap-1.5 text-zinc-400">
                  <Clock className="w-3.5 h-3.5 text-zinc-300" />
                  <span>Dynamic SLA Deadline</span>
                </div>
                <div className="font-semibold text-zinc-200 text-sm">
                  {complaint.sla_deadline
                    ? new Date(complaint.sla_deadline).toLocaleString("en-US", {
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })
                    : "Under Assessment"}
                </div>
              </div>

              <div className="p-4 rounded-xl bg-zinc-900/40 border border-zinc-800/80 space-y-1">
                <div className="flex items-center gap-1.5 text-zinc-400">
                  <Building2 className="w-3.5 h-3.5 text-zinc-300" />
                  <span>Educational Institution</span>
                </div>
                <div className="font-semibold text-zinc-200 text-sm truncate">
                  {complaint.institution_name || "Central AICTE Registry"}
                </div>
              </div>
            </div>

            {/* Audit Trail Timeline */}
            <div className="space-y-4 pt-2">
              <div className="flex items-center gap-2 text-xs font-semibold text-zinc-300 uppercase tracking-wider">
                <History className="w-4 h-4 text-zinc-300" />
                <span>Chronological Audit Trail & Officer Actions</span>
              </div>

              <div className="space-y-3 relative pl-4 border-l-2 border-zinc-800">
                {complaint.timeline && complaint.timeline.length > 0 ? (
                  complaint.timeline.map((log) => (
                    <div key={log.log_id} className="relative space-y-1 text-xs">
                      {/* Timeline Dot */}
                      <div className="w-2.5 h-2.5 rounded-full bg-white absolute -left-[21px] top-1.5 ring-4 ring-black" />
                      <div className="flex items-center justify-between text-zinc-400">
                        <span className="font-semibold text-zinc-200 uppercase tracking-wide">
                          {log.action_taken.replace(/_/g, " ")}
                        </span>
                        <span>
                          {new Date(log.timestamp).toLocaleString("en-US", {
                            month: "short",
                            day: "numeric",
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                      </div>
                      <div className="p-3 rounded-lg bg-zinc-900/70 border border-zinc-800/80 text-zinc-300">
                        {log.officer_remarks || "Action logged and verified by system."}
                      </div>
                      <div className="text-[10px] text-zinc-500">
                        Actor: <code className="text-zinc-400">{log.actor_id || "SYSTEM"}</code>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-zinc-500">No additional audit actions recorded yet.</p>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
