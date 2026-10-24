"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Search, Activity, FilePlus2 } from "lucide-react";
import Logo from "./Logo";

export const Navbar: React.FC = () => {
  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-zinc-800/80 backdrop-blur-xl bg-black/75">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo with micro-interactions */}
        <Link href="/" className="inline-block" data-cursor="pointer">
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            transition={{ type: "spring", stiffness: 400, damping: 25 }}
          >
            <Logo size={36} showBadge={true} />
          </motion.div>
        </Link>

        {/* Navigation & Action Links */}
        <nav className="flex items-center gap-1.5 sm:gap-4 flex-shrink-0">
          <Link
            href="/#tracker"
            data-cursor="pointer"
            className="flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 text-xs sm:text-sm font-medium text-zinc-300 hover:text-white rounded-lg hover:bg-zinc-900/80 border border-transparent hover:border-zinc-700/60 transition-all whitespace-nowrap"
            title="Track Ticket"
          >
            <Search className="w-4 h-4 text-zinc-400" />
            <span className="hidden md:inline">Track Ticket</span>
          </Link>

          <Link
            href="/admin/dashboard"
            data-cursor="pointer"
            className="flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 text-xs sm:text-sm font-medium text-zinc-300 hover:text-white rounded-lg hover:bg-zinc-900/80 border border-transparent hover:border-zinc-700/60 transition-all whitespace-nowrap"
            title="Admin Analytics"
          >
            <Activity className="w-4 h-4 text-zinc-400" />
            <span className="hidden md:inline">Admin Analytics</span>
          </Link>

          <Link
            href="/file-complaint"
            data-cursor="pointer"
            className="flex items-center gap-1.5 px-3 sm:px-4 py-1.5 text-xs sm:text-sm font-bold text-black bg-white hover:bg-zinc-200 rounded-lg shadow-lg shadow-white/10 border border-white transition-all hover:scale-[1.03] active:scale-[0.98] whitespace-nowrap"
          >
            <FilePlus2 className="w-4 h-4 text-black" />
            <span>File Grievance</span>
          </Link>
        </nav>
      </div>
    </header>
  );
};

export default Navbar;
