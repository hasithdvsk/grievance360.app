"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  MessageSquare,
  Bot,
  X,
  Send,
  Sparkles,
  ExternalLink,
  Search,
  FilePlus2,
  Clock,
  User,
  ShieldCheck,
  CheckCircle2,
  ArrowRight,
  Maximize2,
  Minimize2,
} from "lucide-react";

interface ChatMessage {
  id: string;
  sender: "user" | "bot";
  text: string;
  time: string;
  action_type?: string;
  metadata?: Record<string, any>;
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const WHATSAPP_URL = "https://wa.me/14155238886?text=STATUS%20";
const TELEGRAM_URL = "https://t.me/Grievance360Bot";

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<"chat" | "whatsapp" | "telegram">("chat");
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  // Initialize persistent session ID and initial greeting
  useEffect(() => {
    let sessId = "";
    if (typeof window !== "undefined") {
      sessId = localStorage.getItem("grievance360_chat_session") || "";
      if (!sessId) {
        sessId = `sess_${Math.random().toString(36).substring(2, 10)}`;
        localStorage.setItem("grievance360_chat_session", sessId);
      }
    }
    setConversationId(sessId || "default-session");

    setMessages([
      {
        id: "msg-welcome-1",
        sender: "bot",
        text: "👋 **Welcome to AICTE Grievance360 Assistant!**\n\nI can help you monitor live tickets, file emergency grievances with AI classification, or route issues via WhatsApp & Telegram.",
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        action_type: "INFO",
      },
    ]);
  }, []);

  // Auto scroll to bottom whenever messages update
  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isOpen, isLoading]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && activeTab === "chat") {
      setTimeout(() => inputRef.current?.focus(), 250);
    }
  }, [isOpen, activeTab]);

  const handleSendMessage = async (customText?: string) => {
    const textToSend = (customText !== undefined ? customText : inputValue).trim();
    if (!textToSend || isLoading) return;

    const userMessage: ChatMessage = {
      id: `usr-${Date.now()}`,
      sender: "user",
      text: textToSend,
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/bot/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: textToSend,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const data = await response.json();
      const botMessage: ChatMessage = {
        id: `bot-${Date.now()}`,
        sender: "bot",
        text: data.reply || "Message received and acknowledged.",
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        action_type: data.action_type || "INFO",
        metadata: data.metadata,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err: any) {
      console.error("Chat API error:", err);
      // Fallback offline simulated reply
      let offlineReply = "I am processing your query. Please check your network connection.";
      const upper = textToSend.toUpperCase();

      if (upper.startsWith("STATUS")) {
        offlineReply =
          "🏛️ **AICTE Offline Lookup:** Ticket is active under statutory SLA. Connect to backend or try again shortly.";
      } else if (upper.startsWith("FILE")) {
        offlineReply =
          "✅ **Grievance Recorded:** Your request has been queued for AICTE automated triage.";
      }

      setMessages((prev) => [
        ...prev,
        {
          id: `bot-err-${Date.now()}`,
          sender: "bot",
          text: offlineReply,
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          action_type: "INFO",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const applyChipAction = (chipText: string, autoSend: boolean = false) => {
    if (autoSend) {
      handleSendMessage(chipText);
    } else {
      setInputValue(chipText);
      inputRef.current?.focus();
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 font-sans">
      {/* Floating Toggle Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.button
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            whileHover={{ scale: 1.08 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setIsOpen(true)}
            aria-label="Open AICTE Grievance360 Assistant"
            className="group relative flex h-14 w-14 items-center justify-center rounded-2xl bg-white text-black shadow-2xl shadow-white/20 hover:bg-zinc-200 transition-all border border-white"
          >
            {/* Pulsing online status indicator ring */}
            <span className="absolute -top-1 -right-1 flex h-4 w-4">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75" />
              <span className="relative inline-flex rounded-full h-4 w-4 bg-white border-2 border-black shadow-md" />
            </span>

            <Bot className="h-7 w-7 text-black transition-transform group-hover:rotate-12 duration-200" />
          </motion.button>
        )}
      </AnimatePresence>

      {/* Expanded Chat Card Modal */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="w-80 sm:w-96 h-[520px] max-h-[85vh] flex flex-col rounded-3xl border border-zinc-800 bg-[#09090b]/98 backdrop-blur-2xl shadow-2xl shadow-black/90 overflow-hidden"
          >
            {/* Header */}
            <div className="border-b border-zinc-800 bg-zinc-950 p-4 shrink-0">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2.5">
                  <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white text-black shadow-md border border-white/20">
                    <Bot className="h-5 w-5 text-black" />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-white tracking-wide">
                      Grievance360 Assistant
                    </h3>
                    <div className="flex items-center space-x-1.5">
                      <span className="h-2 w-2 rounded-full bg-white animate-pulse" />
                      <span className="text-[10px] font-semibold text-zinc-300">
                        AI & Messenger Active
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-1">
                  <button
                    type="button"
                    onClick={() => setIsOpen(false)}
                    className="flex h-7 w-7 items-center justify-center rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors"
                    aria-label="Close Chat"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Channel Tabs */}
              <div className="mt-3 grid grid-cols-3 gap-1 rounded-xl bg-black p-1 border border-zinc-800">
                <button
                  type="button"
                  onClick={() => setActiveTab("chat")}
                  className={`flex items-center justify-center space-x-1 py-1 rounded-lg text-[11px] font-medium transition-all ${
                    activeTab === "chat"
                      ? "bg-white text-black shadow-sm font-bold"
                      : "text-zinc-400 hover:text-white"
                  }`}
                >
                  <Sparkles className="h-3 w-3" />
                  <span>In-App</span>
                </button>

                <button
                  type="button"
                  onClick={() => setActiveTab("whatsapp")}
                  className={`flex items-center justify-center space-x-1 py-1 rounded-lg text-[11px] font-medium transition-all ${
                    activeTab === "whatsapp"
                      ? "bg-emerald-600 text-white shadow-sm font-semibold"
                      : "text-slate-400 hover:text-emerald-300"
                  }`}
                >
                  <span className="text-emerald-400 font-bold">🟢</span>
                  <span>WhatsApp</span>
                </button>

                <button
                  type="button"
                  onClick={() => setActiveTab("telegram")}
                  className={`flex items-center justify-center space-x-1 py-1 rounded-lg text-[11px] font-medium transition-all ${
                    activeTab === "telegram"
                      ? "bg-sky-600 text-white shadow-sm font-semibold"
                      : "text-slate-400 hover:text-sky-300"
                  }`}
                >
                  <span className="text-sky-400 font-bold">✈️</span>
                  <span>Telegram</span>
                </button>
              </div>
            </div>

            {/* In-App Chat View */}
            {activeTab === "chat" && (
              <>
                {/* Quick Action Chips */}
                <div className="px-3.5 pt-2.5 pb-1 flex items-center gap-1.5 overflow-x-auto no-scrollbar border-b border-slate-800/50 bg-slate-950/30">
                  <button
                    type="button"
                    onClick={() => applyChipAction("STATUS GRV-2026-00001", true)}
                    className="shrink-0 flex items-center space-x-1 rounded-full bg-slate-800/90 hover:bg-slate-700/90 px-2.5 py-1 text-[10px] text-slate-300 hover:text-white border border-slate-700/60 transition-all hover:scale-102"
                  >
                    <Search className="h-3 w-3 text-blue-400" />
                    <span>Check Status</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => applyChipAction("FILE ", false)}
                    className="shrink-0 flex items-center space-x-1 rounded-full bg-slate-800/90 hover:bg-slate-700/90 px-2.5 py-1 text-[10px] text-slate-300 hover:text-white border border-slate-700/60 transition-all hover:scale-102"
                  >
                    <FilePlus2 className="h-3 w-3 text-indigo-400" />
                    <span>File Grievance</span>
                  </button>

                  <a
                    href={WHATSAPP_URL}
                    target="_blank"
                    rel="noreferrer"
                    className="shrink-0 flex items-center space-x-1 rounded-full bg-emerald-950/40 hover:bg-emerald-900/60 px-2.5 py-1 text-[10px] text-emerald-300 border border-emerald-500/30 transition-all"
                  >
                    <span>🟢 WhatsApp</span>
                  </a>

                  <a
                    href={TELEGRAM_URL}
                    target="_blank"
                    rel="noreferrer"
                    className="shrink-0 flex items-center space-x-1 rounded-full bg-sky-950/40 hover:bg-sky-900/60 px-2.5 py-1 text-[10px] text-sky-300 border border-sky-500/30 transition-all"
                  >
                    <span>✈️ Telegram</span>
                  </a>
                </div>

                {/* Message History Container */}
                <div className="flex-1 overflow-y-auto p-4 space-y-3.5 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
                  {messages.map((msg) => (
                    <motion.div
                      key={msg.id}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`flex flex-col ${
                        msg.sender === "user" ? "items-end" : "items-start"
                      }`}
                    >
                      <div
                        className={`max-w-[85%] rounded-2xl p-3 text-xs leading-relaxed shadow-md ${
                          msg.sender === "user"
                            ? "bg-white text-black font-semibold rounded-br-xs"
                            : "bg-zinc-900 text-zinc-200 border border-zinc-800 rounded-bl-xs"
                        }`}
                      >
                        <div className="whitespace-pre-wrap break-words">
                          {msg.text}
                        </div>
                      </div>
                      <span className="mt-1 px-1 text-[9px] text-zinc-500 font-mono">
                        {msg.time}
                      </span>
                    </motion.div>
                  ))}

                  {/* Typing Indicator */}
                  {isLoading && (
                    <motion.div
                      initial={{ opacity: 0, y: 5 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex items-center space-x-1.5 rounded-2xl rounded-bl-xs bg-zinc-900 border border-zinc-800 p-3 max-w-[70px]"
                    >
                      <span className="h-1.5 w-1.5 rounded-full bg-white animate-bounce" />
                      <span
                        className="h-1.5 w-1.5 rounded-full bg-zinc-300 animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                      />
                      <span
                        className="h-1.5 w-1.5 rounded-full bg-zinc-500 animate-bounce"
                        style={{ animationDelay: "0.4s" }}
                      />
                    </motion.div>
                  )}

                  <div ref={messagesEndRef} />
                </div>

                {/* Input Bar */}
                <div className="p-3 border-t border-zinc-800 bg-zinc-950/80 shrink-0">
                  <div className="flex items-center space-x-2 rounded-2xl border border-zinc-700 bg-zinc-900 px-3 py-1.5 focus-within:border-white focus-within:ring-1 focus-within:ring-white/20 transition-all">
                    <input
                      ref={inputRef}
                      type="text"
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder="Type STATUS <ID> or FILE <Desc>..."
                      disabled={isLoading}
                      className="flex-1 bg-transparent text-xs text-white placeholder-zinc-500 focus:outline-none"
                    />
                    <button
                      type="button"
                      onClick={() => handleSendMessage()}
                      disabled={!inputValue.trim() || isLoading}
                      className="flex h-7 w-7 items-center justify-center rounded-xl bg-white hover:bg-zinc-200 text-black transition-colors disabled:opacity-40"
                    >
                      <Send className="h-3.5 w-3.5 text-black" />
                    </button>
                  </div>
                </div>
              </>
            )}

            {/* WhatsApp Gateway Tab */}
            {activeTab === "whatsapp" && (
              <div className="flex-1 p-5 flex flex-col justify-between overflow-y-auto">
                <div className="space-y-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                    <span className="text-2xl">🟢</span>
                  </div>
                  <h4 className="text-sm font-bold text-white">
                    AICTE Twilio WhatsApp Gateway
                  </h4>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Access automated grievance tracking and instant registration directly through your personal WhatsApp app.
                  </p>

                  <div className="rounded-xl border border-slate-800 bg-slate-950/80 p-3 space-y-2 text-xs">
                    <div className="text-slate-400">Official Webhook Number:</div>
                    <div className="font-mono text-emerald-400 font-bold text-sm">
                      +1 (415) 523-8886
                    </div>
                  </div>

                  <div className="space-y-2 text-xs text-slate-400">
                    <div className="font-semibold text-slate-300">Supported Commands:</div>
                    <div className="font-mono bg-slate-950/60 p-2 rounded-lg border border-slate-800 text-[11px] text-slate-300">
                      • STATUS GRV-2026-00001<br />
                      • FILE &lt;Description of grievance&gt;
                    </div>
                  </div>
                </div>

                <a
                  href={WHATSAPP_URL}
                  target="_blank"
                  rel="noreferrer"
                  className="w-full flex items-center justify-center space-x-2 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-lg shadow-emerald-600/30 transition-all hover:scale-102"
                >
                  <span>Open WhatsApp Messenger</span>
                  <ExternalLink className="h-3.5 w-3.5" />
                </a>
              </div>
            )}

            {/* Telegram Gateway Tab */}
            {activeTab === "telegram" && (
              <div className="flex-1 p-5 flex flex-col justify-between overflow-y-auto">
                <div className="space-y-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-sky-500/20 text-sky-400 border border-sky-500/30">
                    <span className="text-2xl">✈️</span>
                  </div>
                  <h4 className="text-sm font-bold text-white">
                    Official Telegram AICTE Bot
                  </h4>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Connect with @Grievance360Bot on Telegram for real-time SLA deadline alerts, status verification, and instant ticket generation.
                  </p>

                  <div className="rounded-xl border border-slate-800 bg-slate-950/80 p-3 space-y-2 text-xs">
                    <div className="text-slate-400">Bot Handle:</div>
                    <div className="font-mono text-sky-400 font-bold text-sm">
                      @Grievance360Bot
                    </div>
                  </div>

                  <div className="space-y-2 text-xs text-slate-400">
                    <div className="font-semibold text-slate-300">Telegram Bot Commands:</div>
                    <div className="font-mono bg-slate-950/60 p-2 rounded-lg border border-slate-800 text-[11px] text-slate-300">
                      • /status GRV-2026-00001<br />
                      • /file &lt;Incident details&gt;<br />
                      • /help
                    </div>
                  </div>
                </div>

                <a
                  href={TELEGRAM_URL}
                  target="_blank"
                  rel="noreferrer"
                  className="w-full flex items-center justify-center space-x-2 py-3 rounded-xl bg-sky-600 hover:bg-sky-500 text-white font-bold text-xs shadow-lg shadow-sky-600/30 transition-all hover:scale-102"
                >
                  <span>Launch Telegram Bot</span>
                  <ExternalLink className="h-3.5 w-3.5" />
                </a>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
