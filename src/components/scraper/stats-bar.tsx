import { PipelineStats } from "@/types/scraper";
import { Database, TrendingUp, Building2, Clock, Plus, RefreshCw } from "lucide-react";

interface StatsBarProps {
  stats: PipelineStats;
}

function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${Math.floor(diffHours / 24)}d ago`;
}

interface StatCardProps {
  label: string;
  value: string | number;
  sub?: string;
  icon: React.ReactNode;
  accent?: string;
}

function StatCard({ label, value, sub, icon, accent = "text-slate-400" }: StatCardProps) {
  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-lg p-4 flex items-start gap-3">
      <div className={`mt-0.5 ${accent}`}>{icon}</div>
      <div className="min-w-0">
        <div className="text-[10px] font-mono text-slate-500 uppercase tracking-widest mb-1">{label}</div>
        <div className="text-xl font-mono font-semibold text-[#F8F7F4] tabular-nums">{value}</div>
        {sub && <div className="text-[10px] font-mono text-slate-500 mt-0.5">{sub}</div>}
      </div>
    </div>
  );
}

export function StatsBar({ stats }: StatsBarProps) {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      <StatCard
        label="Total Jobs"
        value={stats.total_jobs.toLocaleString()}
        sub={`${stats.active_jobs.toLocaleString()} active`}
        icon={<Database size={16} />}
        accent="text-teal-400"
      />
      <StatCard
        label="Companies"
        value={stats.companies_tracked}
        sub="tracked sources"
        icon={<Building2 size={16} />}
        accent="text-blue-400"
      />
      <StatCard
        label="Added Today"
        value={`+${stats.jobs_added_today}`}
        sub={`${stats.jobs_updated_today} updated`}
        icon={<Plus size={16} />}
        accent="text-amber-400"
      />
      <StatCard
        label="Last Run"
        value={stats.last_run ? formatRelativeTime(stats.last_run) : "—"}
        sub={stats.last_run ? new Date(stats.last_run).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "never"}
        icon={<Clock size={16} />}
        accent="text-violet-400"
      />
    </div>
  );
}
