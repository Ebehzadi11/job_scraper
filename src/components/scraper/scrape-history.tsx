import { ScrapeRun } from "@/types/scraper";
import { ATSBadge, CollectorBadge, StatusDot } from "./badges";

interface ScrapeHistoryProps {
  runs: ScrapeRun[];
}

export function ScrapeHistory({ runs }: ScrapeHistoryProps) {
  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-violet-400" />
          <span className="text-[11px] font-mono text-slate-400 uppercase tracking-widest">Recent Runs</span>
        </div>
        <span className="text-[10px] font-mono text-slate-600">{runs.length} runs</span>
      </div>
      <div className="divide-y divide-slate-800/40">
        {runs.map((run, i) => (
          <div key={i} className="px-4 py-3 flex items-center gap-3 hover:bg-slate-800/20 transition-colors">
            <StatusDot status={run.status} />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-sm text-[#F8F7F4] font-medium">{run.company}</span>
                <ATSBadge type={run.ats_type} />
                <CollectorBadge type={run.collector_type} />
              </div>
              <div className="flex items-center gap-3 mt-1">
                {run.status === "success" ? (
                  <>
                    <span className="text-[10px] font-mono text-teal-400">+{run.jobs_inserted} new</span>
                    <span className="text-[10px] font-mono text-slate-500">↻ {run.jobs_updated} updated</span>
                    <span className="text-[10px] font-mono text-slate-600">{run.jobs_found} total</span>
                  </>
                ) : (
                  <span className="text-[10px] font-mono text-red-400">fetch failed — timeout</span>
                )}
              </div>
            </div>
            <div className="text-right shrink-0">
              <div className="text-[10px] font-mono text-slate-500">
                {run.duration_ms >= 1000 ? `${(run.duration_ms / 1000).toFixed(1)}s` : `${run.duration_ms}ms`}
              </div>
              <div className="text-[9px] font-mono text-slate-700 mt-0.5">
                {new Date(run.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
