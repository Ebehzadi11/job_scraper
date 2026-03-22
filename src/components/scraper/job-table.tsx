import { JobPosting } from "@/types/scraper";
import { ATSBadge } from "./badges";
import { ExternalLink, CheckCircle2, XCircle } from "lucide-react";

interface JobTableProps {
  jobs: JobPosting[];
  searchQuery?: string;
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

export function JobTable({ jobs, searchQuery }: JobTableProps) {
  const filtered = searchQuery
    ? jobs.filter(
        (j) =>
          j.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          j.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
          j.location.toLowerCase().includes(searchQuery.toLowerCase()) ||
          (j.department ?? "").toLowerCase().includes(searchQuery.toLowerCase())
      )
    : jobs;

  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
          <span className="text-[11px] font-mono text-slate-400 uppercase tracking-widest">Job Postings</span>
        </div>
        <span className="text-[10px] font-mono text-slate-600">{filtered.length} records</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-800/60">
              <th className="text-left px-4 py-2.5 text-[10px] font-mono text-slate-600 uppercase tracking-widest font-medium">Title</th>
              <th className="text-left px-4 py-2.5 text-[10px] font-mono text-slate-600 uppercase tracking-widest font-medium">Company</th>
              <th className="text-left px-4 py-2.5 text-[10px] font-mono text-slate-600 uppercase tracking-widest font-medium">Location</th>
              <th className="text-left px-4 py-2.5 text-[10px] font-mono text-slate-600 uppercase tracking-widest font-medium">Dept</th>
              <th className="text-left px-4 py-2.5 text-[10px] font-mono text-slate-600 uppercase tracking-widest font-medium">ATS</th>
              <th className="text-left px-4 py-2.5 text-[10px] font-mono text-slate-600 uppercase tracking-widest font-medium">Scraped</th>
              <th className="text-left px-4 py-2.5 text-[10px] font-mono text-slate-600 uppercase tracking-widest font-medium">Active</th>
              <th className="px-4 py-2.5"></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((job) => (
              <tr
                key={job.id}
                className="border-b border-slate-800/40 last:border-0 hover:bg-slate-800/30 transition-colors"
              >
                <td className="px-4 py-3">
                  <span className="text-[#F8F7F4] font-medium text-sm leading-snug">{job.title}</span>
                  {job.external_job_id && (
                    <div className="text-[9px] font-mono text-slate-700 mt-0.5">#{job.external_job_id}</div>
                  )}
                </td>
                <td className="px-4 py-3">
                  <span className="text-sm text-slate-300">{job.company}</span>
                </td>
                <td className="px-4 py-3">
                  <span className="text-[11px] font-mono text-slate-400">{job.location}</span>
                </td>
                <td className="px-4 py-3">
                  <span className="text-[11px] font-mono text-slate-500">{job.department ?? "—"}</span>
                </td>
                <td className="px-4 py-3">
                  <ATSBadge type={job.source_type} />
                </td>
                <td className="px-4 py-3">
                  <span className="text-[11px] font-mono text-slate-500">{formatRelativeTime(job.scraped_at)}</span>
                </td>
                <td className="px-4 py-3">
                  {job.is_active ? (
                    <CheckCircle2 size={14} className="text-teal-400" />
                  ) : (
                    <XCircle size={14} className="text-red-500/60" />
                  )}
                </td>
                <td className="px-4 py-3">
                  <a
                    href={job.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-1 text-slate-700 hover:text-slate-400 transition-colors inline-flex"
                  >
                    <ExternalLink size={12} />
                  </a>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={8} className="px-4 py-8 text-center text-slate-600 font-mono text-sm">
                  no records found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
