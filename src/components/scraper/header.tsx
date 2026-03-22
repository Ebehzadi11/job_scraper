import { Terminal, Database, Cpu, GitBranch, RefreshCw } from "lucide-react";
import { useState } from "react";

interface HeaderProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  onRunAll?: () => void;
  isRunning?: boolean;
}

const TABS = [
  { id: "overview", label: "Overview" },
  { id: "sources", label: "Sources" },
  { id: "jobs", label: "Jobs" },
  { id: "logs", label: "Logs" },
  { id: "cli", label: "CLI" },
];

export function Header({ activeTab, onTabChange, onRunAll, isRunning }: HeaderProps) {
  return (
    <header className="border-b border-slate-800/80 bg-[#0F1117]/90 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-[1400px] mx-auto px-6">
        <div className="flex items-center justify-between h-14">
          {/* Brand */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5">
              <div className="w-6 h-6 rounded bg-amber-500/20 border border-amber-500/30 flex items-center justify-center">
                <Terminal size={12} className="text-amber-400" />
              </div>
              <span className="font-mono font-semibold text-[#F8F7F4] text-sm tracking-tight">jobscraper</span>
            </div>
            <div className="flex items-center gap-1.5 pl-3 border-l border-slate-800">
              <span className="w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse" />
              <span className="text-[10px] font-mono text-slate-500">pipeline active</span>
            </div>
          </div>

          {/* Nav */}
          <nav className="flex items-center gap-0.5">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`px-3 py-1.5 text-[11px] font-mono uppercase tracking-wider rounded transition-colors ${
                  activeTab === tab.id
                    ? "text-[#F8F7F4] bg-slate-800/60"
                    : "text-slate-600 hover:text-slate-400 hover:bg-slate-800/30"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2 text-[10px] font-mono text-slate-700">
              <Database size={11} />
              <span>sqlite://jobs.db</span>
            </div>
            <button
              onClick={onRunAll}
              disabled={isRunning}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-mono rounded border transition-all ${
                isRunning
                  ? "bg-amber-500/10 border-amber-500/30 text-amber-400 cursor-not-allowed"
                  : "bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700 hover:border-slate-600"
              }`}
            >
              <RefreshCw size={11} className={isRunning ? "animate-spin" : ""} />
              {isRunning ? "running..." : "scrape-all"}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
