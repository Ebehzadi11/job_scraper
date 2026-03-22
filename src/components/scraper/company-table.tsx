import { Company } from "@/types/scraper";
import { ATSBadge, CollectorBadge, StatusDot } from "./badges";
import { ExternalLink, RefreshCw } from "lucide-react";

interface CompanyTableProps {
  companies: Company[];
  onScrape?: (company: Company) => void;
}

function formatTime(dateStr?: string): string {
  if (!dateStr) return "never";
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${Math.floor(diffHours / 24)}d ago`;
}

export function CompanyTable({ companies, onScrape }: CompanyTableProps) {
  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-teal-400" />
          <span className="text-[11px] font-mono text-slate-400 uppercase tracking-widest">Sources Registry</span>
        </div>
        <span className="text-[10px] font-mono text-slate-600">{companies.length} companies</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-800/60">
              <th className="text-left px-4 py-2.5 text-[10px] font-mono text-slate-600 uppercase tracking-widest font-medium">Company</th>
              <th className="text-left px-4 py-2.5 text-[10px] font-mono text-slate-600 uppercase tracking-widest font-medium">ATS</th>
              <th className="text-left px-4 py-2.5 text-[10px] font-mono text-slate-600 uppercase tracking-widest font-medium">Collector</th>
              <th className="text-right px-4 py-2.5 text-[10px] font-mono text-slate-600 uppercase tracking-widest font-medium">Jobs</th>
              <th className="text-left px-4 py-2.5 text-[10px] font-mono text-slate-600 uppercase tracking-widest font-medium">Last Scraped</th>
              <th className="text-left px-4 py-2.5 text-[10px] font-mono text-slate-600 uppercase tracking-widest font-medium">Status</th>
              <th className="px-4 py-2.5"></th>
            </tr>
          </thead>
          <tbody>
            {companies.map((company, i) => (
              <tr
                key={company.id}
                className="border-b border-slate-800/40 last:border-0 hover:bg-slate-800/30 transition-colors group"
              >
                <td className="px-4 py-3">
                  <div className="flex flex-col gap-0.5">
                    <span className="text-[#F8F7F4] font-medium text-sm">{company.name}</span>
                    <a
                      href={company.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[10px] font-mono text-slate-600 hover:text-slate-400 transition-colors flex items-center gap-1 w-fit"
                    >
                      {company.url.replace(/^https?:\/\//, "").slice(0, 40)}
                      {company.url.length > 46 && "…"}
                      <ExternalLink size={9} />
                    </a>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <ATSBadge type={company.ats_type} />
                </td>
                <td className="px-4 py-3">
                  <CollectorBadge type={company.collector_type} />
                </td>
                <td className="px-4 py-3 text-right">
                  <span className="font-mono text-[#F8F7F4] text-sm tabular-nums">{company.job_count}</span>
                </td>
                <td className="px-4 py-3">
                  <span className="text-[11px] font-mono text-slate-500">{formatTime(company.last_scraped)}</span>
                </td>
                <td className="px-4 py-3">
                  <StatusDot status={company.status} showLabel />
                </td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => onScrape?.(company)}
                    className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded hover:bg-slate-700/60 text-slate-500 hover:text-amber-400"
                    title="Scrape now"
                  >
                    <RefreshCw size={12} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
