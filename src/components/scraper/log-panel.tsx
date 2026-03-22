import { ScrapeLog } from "@/types/scraper";
import { LogLevelBadge, LogPrefix } from "./badges";
import { useEffect, useRef } from "react";

interface LogPanelProps {
  logs: ScrapeLog[];
  autoScroll?: boolean;
  maxHeight?: string;
  filterCompany?: string;
}

function formatTimestamp(ts: string): string {
  const d = new Date(ts);
  return d.toISOString().replace("T", " ").slice(0, 19);
}

export function LogPanel({ logs, autoScroll = true, maxHeight = "320px", filterCompany }: LogPanelProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  const filtered = filterCompany
    ? logs.filter((l) => !l.company || l.company === filterCompany)
    : logs;

  useEffect(() => {
    if (autoScroll && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [filtered.length, autoScroll]);

  return (
    <div className="bg-[#0a0c10] border border-slate-800/80 rounded-lg overflow-hidden font-mono">
      <div className="px-4 py-2.5 border-b border-slate-800/80 flex items-center justify-between bg-slate-900/50">
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
          <span className="text-[11px] text-slate-400 uppercase tracking-widest">Pipeline Log</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[10px] text-slate-600">{filtered.length} entries</span>
          <div className="flex gap-1">
            <span className="w-2 h-2 rounded-full bg-red-500/60" />
            <span className="w-2 h-2 rounded-full bg-amber-500/60" />
            <span className="w-2 h-2 rounded-full bg-teal-500/60" />
          </div>
        </div>
      </div>
      <div
        className="overflow-y-auto px-4 py-3 space-y-0.5"
        style={{ maxHeight }}
      >
        {filtered.map((log) => (
          <div
            key={log.id}
            className="flex items-start gap-3 py-0.5 hover:bg-slate-800/20 rounded px-1 -mx-1 transition-colors"
          >
            <span className="text-[10px] text-slate-700 shrink-0 tabular-nums w-[140px]">
              {formatTimestamp(log.timestamp)}
            </span>
            <LogLevelBadge level={log.level} />
            <LogPrefix prefix={log.prefix} />
            {log.company && (
              <span className="text-[10px] text-slate-600 shrink-0 w-16 truncate">
                {log.company}
              </span>
            )}
            <span className={`text-[11px] leading-tight ${
              log.level === "ERROR"
                ? "text-red-400"
                : log.level === "SUCCESS"
                ? "text-teal-300"
                : log.level === "WARN"
                ? "text-amber-400"
                : "text-slate-400"
            }`}>
              {log.message}
            </span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
