import { ATSType, CollectorType, ScrapeStatus } from "@/types/scraper";
import { cn } from "@/lib/utils";

interface ATSBadgeProps {
  type: ATSType;
  className?: string;
}

export function ATSBadge({ type, className }: ATSBadgeProps) {
  const config: Record<ATSType, { label: string; color: string }> = {
    greenhouse: { label: "Greenhouse", color: "bg-emerald-900/40 text-emerald-400 border-emerald-800/50" },
    lever: { label: "Lever", color: "bg-blue-900/40 text-blue-400 border-blue-800/50" },
    ashby: { label: "Ashby", color: "bg-violet-900/40 text-violet-400 border-violet-800/50" },
    generic: { label: "Generic", color: "bg-slate-800/60 text-slate-400 border-slate-700/50" },
  };
  const { label, color } = config[type];
  return (
    <span className={cn("inline-flex items-center px-2 py-0.5 text-[10px] font-mono font-medium rounded border tracking-wider uppercase", color, className)}>
      {label}
    </span>
  );
}

interface CollectorBadgeProps {
  type: CollectorType;
  className?: string;
}

export function CollectorBadge({ type, className }: CollectorBadgeProps) {
  return (
    <span className={cn(
      "inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-mono font-medium rounded border tracking-wider uppercase",
      type === "playwright"
        ? "bg-amber-900/30 text-amber-400 border-amber-800/40"
        : "bg-slate-800/60 text-slate-400 border-slate-700/50",
      className
    )}>
      {type === "playwright" ? "⬡" : "◈"} {type}
    </span>
  );
}

interface StatusDotProps {
  status: ScrapeStatus;
  className?: string;
  showLabel?: boolean;
}

export function StatusDot({ status, className, showLabel = false }: StatusDotProps) {
  const config: Record<ScrapeStatus, { dot: string; label: string; text: string }> = {
    success: { dot: "bg-teal-400", label: "success", text: "text-teal-400" },
    error: { dot: "bg-red-500", label: "error", text: "text-red-400" },
    running: { dot: "bg-amber-400 animate-pulse", label: "running", text: "text-amber-400" },
    idle: { dot: "bg-slate-600", label: "idle", text: "text-slate-500" },
  };
  const { dot, label, text } = config[status];
  return (
    <span className={cn("inline-flex items-center gap-1.5", className)}>
      <span className={cn("w-1.5 h-1.5 rounded-full", dot)} />
      {showLabel && <span className={cn("text-xs font-mono", text)}>{label}</span>}
    </span>
  );
}

interface LogLevelBadgeProps {
  level: "INFO" | "WARN" | "ERROR" | "SUCCESS";
}

export function LogLevelBadge({ level }: LogLevelBadgeProps) {
  const config = {
    INFO: "text-slate-400",
    WARN: "text-amber-400",
    ERROR: "text-red-400",
    SUCCESS: "text-teal-400",
  };
  return (
    <span className={cn("text-[10px] font-mono font-semibold uppercase tracking-widest w-8", config[level])}>
      {level === "SUCCESS" ? "OK" : level}
    </span>
  );
}

interface LogPrefixProps {
  prefix: string;
}

export function LogPrefix({ prefix }: LogPrefixProps) {
  const color: Record<string, string> = {
    "[FETCH]": "text-blue-400",
    "[EXTRACT]": "text-violet-400",
    "[PERSIST]": "text-teal-400",
    "[DEDUPE]": "text-amber-400",
    "[INIT]": "text-slate-400",
    "[CONFIG]": "text-slate-400",
    "[RETRY]": "text-orange-400",
  };
  return (
    <span className={cn("text-[10px] font-mono font-semibold w-20 shrink-0", color[prefix] ?? "text-slate-400")}>
      {prefix}
    </span>
  );
}
