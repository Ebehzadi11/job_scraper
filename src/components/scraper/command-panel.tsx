import { useState } from "react";
import { ATSType, CollectorType } from "@/types/scraper";
import { X, Terminal, Globe } from "lucide-react";

interface ScrapeCommandPanelProps {
  onClose?: () => void;
}

export function ScrapeCommandPanel({ onClose }: ScrapeCommandPanelProps) {
  const [company, setCompany] = useState("");
  const [url, setUrl] = useState("");
  const [useBrowser, setUseBrowser] = useState(false);
  const [atsHint, setAtsHint] = useState<ATSType | "">("");

  const inferATS = (u: string): ATSType | "" => {
    if (u.includes("greenhouse.io")) return "greenhouse";
    if (u.includes("lever.co")) return "lever";
    if (u.includes("ashby")) return "ashby";
    return "";
  };

  const handleUrlChange = (val: string) => {
    setUrl(val);
    const inferred = inferATS(val);
    if (inferred) setAtsHint(inferred);
  };

  const command = `python -m jobscraper.cli scrape-company \\
  --company "${company || "<company>"}" \\
  --url "${url || "<url>"}"`
    + (useBrowser ? " \\\n  --browser" : "")
    + (atsHint ? ` \\\n  --ats-hint ${atsHint}` : "");

  return (
    <div className="bg-slate-900/80 border border-slate-800/80 rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-800/80 flex items-center justify-between bg-slate-900/60">
        <div className="flex items-center gap-2">
          <Terminal size={13} className="text-amber-400" />
          <span className="text-[11px] font-mono text-slate-400 uppercase tracking-widest">Scrape Command Builder</span>
        </div>
        {onClose && (
          <button onClick={onClose} className="text-slate-600 hover:text-slate-400 transition-colors">
            <X size={14} />
          </button>
        )}
      </div>

      <div className="p-4 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="text-[10px] font-mono text-slate-600 uppercase tracking-widest block mb-1.5">
              --company
            </label>
            <input
              type="text"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              placeholder="Stripe"
              className="w-full bg-[#0a0c10] border border-slate-700/60 rounded px-3 py-2 text-sm font-mono text-[#F8F7F4] placeholder-slate-700 focus:outline-none focus:border-amber-500/50 transition-colors"
            />
          </div>
          <div>
            <label className="text-[10px] font-mono text-slate-600 uppercase tracking-widest block mb-1.5">
              --url
            </label>
            <input
              type="text"
              value={url}
              onChange={(e) => handleUrlChange(e.target.value)}
              placeholder="https://boards.greenhouse.io/stripe"
              className="w-full bg-[#0a0c10] border border-slate-700/60 rounded px-3 py-2 text-sm font-mono text-[#F8F7F4] placeholder-slate-700 focus:outline-none focus:border-amber-500/50 transition-colors"
            />
          </div>
        </div>

        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <div
              onClick={() => setUseBrowser(!useBrowser)}
              className={`w-8 h-4 rounded-full transition-colors relative cursor-pointer ${useBrowser ? "bg-amber-500/70" : "bg-slate-700"}`}
            >
              <span className={`absolute top-0.5 w-3 h-3 rounded-full bg-white transition-transform ${useBrowser ? "translate-x-4" : "translate-x-0.5"}`} />
            </div>
            <span className="text-[11px] font-mono text-slate-400">--browser (Playwright)</span>
          </label>

          {atsHint && (
            <div className="flex items-center gap-1.5">
              <Globe size={11} className="text-teal-400" />
              <span className="text-[10px] font-mono text-teal-400">inferred: {atsHint}</span>
            </div>
          )}
        </div>

        <div className="bg-[#0a0c10] rounded border border-slate-800/60 p-3">
          <div className="text-[9px] font-mono text-slate-700 mb-2 uppercase tracking-widest">Generated Command</div>
          <pre className="text-[11px] font-mono text-slate-300 whitespace-pre-wrap leading-relaxed overflow-x-auto">
            {command}
          </pre>
        </div>

        <div className="border-t border-slate-800/60 pt-3">
          <div className="text-[10px] font-mono text-slate-700 mb-2 uppercase tracking-widest">Other Commands</div>
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono text-slate-700 w-24">initdb</span>
              <code className="text-[10px] font-mono text-slate-500 bg-[#0a0c10] px-2 py-0.5 rounded border border-slate-800/40">
                python -m jobscraper.cli initdb
              </code>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono text-slate-700 w-24">scrape-all</span>
              <code className="text-[10px] font-mono text-slate-500 bg-[#0a0c10] px-2 py-0.5 rounded border border-slate-800/40">
                python -m jobscraper.cli scrape-all
              </code>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono text-slate-700 w-24">discover</span>
              <code className="text-[10px] font-mono text-slate-500 bg-[#0a0c10] px-2 py-0.5 rounded border border-slate-800/40">
                python -m jobscraper.cli discover --url &lt;url&gt;
              </code>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
