import { useState } from "react";
import { Header } from "./scraper/header";
import { StatsBar } from "./scraper/stats-bar";
import { CompanyTable } from "./scraper/company-table";
import { JobTable } from "./scraper/job-table";
import { LogPanel } from "./scraper/log-panel";
import { ScrapeHistory } from "./scraper/scrape-history";
import { ScrapeCommandPanel } from "./scraper/command-panel";
import { ActivityChart, ATSDistribution } from "./scraper/charts";
import {
  mockStats,
  mockCompanies,
  mockJobs,
  mockLogs,
  mockScrapeHistory,
} from "@/data/mock-data";
import { Company, ScrapeLog, PipelineStats } from "@/types/scraper";
import { Search, X } from "lucide-react";

function Home() {
  const [activeTab, setActiveTab] = useState("overview");
  const [isRunning, setIsRunning] = useState(false);
  const [logs, setLogs] = useState<ScrapeLog[]>(mockLogs);
  const [stats, setStats] = useState<PipelineStats>(mockStats);
  const [searchQuery, setSearchQuery] = useState("");

  const handleRunAll = () => {
    if (isRunning) return;
    setIsRunning(true);
    setActiveTab("logs");

    const newLogs: ScrapeLog[] = [
      {
        id: `run-${Date.now()}-1`,
        timestamp: new Date().toISOString(),
        level: "INFO",
        prefix: "[CONFIG]",
        message: "scrape-all triggered — loading sources.yaml",
      },
      {
        id: `run-${Date.now()}-2`,
        timestamp: new Date(Date.now() + 500).toISOString(),
        level: "INFO",
        prefix: "[INIT]",
        message: `Concurrency pool initialized — MAX_CONCURRENCY=4`,
      },
    ];

    setLogs((prev) => [...prev, ...newLogs]);

    const companies = mockCompanies.slice(0, 3);
    companies.forEach((c, i) => {
      setTimeout(() => {
        setLogs((prev) => [
          ...prev,
          {
            id: `run-${Date.now()}-fetch-${i}`,
            timestamp: new Date().toISOString(),
            level: "INFO",
            prefix: "[FETCH]",
            message: `Starting ${c.collector_type === "playwright" ? "Playwright" : "HTTP"} fetch for ${c.url.replace("https://", "")}`,
            company: c.name,
          },
        ]);

        setTimeout(() => {
          setLogs((prev) => [
            ...prev,
            {
              id: `run-${Date.now()}-extract-${i}`,
              timestamp: new Date().toISOString(),
              level: "SUCCESS",
              prefix: "[EXTRACT]",
              message: `Parsed ${c.job_count} job postings`,
              company: c.name,
            },
            {
              id: `run-${Date.now()}-persist-${i}`,
              timestamp: new Date().toISOString(),
              level: "INFO",
              prefix: "[PERSIST]",
              message: `Upserted ${c.job_count} records`,
              company: c.name,
            },
          ]);
        }, 600);
      }, i * 800);
    });

    setTimeout(() => {
      setLogs((prev) => [
        ...prev,
        {
          id: `run-${Date.now()}-done`,
          timestamp: new Date().toISOString(),
          level: "SUCCESS",
          prefix: "[INIT]",
          message: `scrape-all complete — 3 companies processed`,
        },
      ]);
      setStats((prev) => ({
        ...prev,
        last_run: new Date().toISOString(),
        jobs_added_today: prev.jobs_added_today + 23,
        jobs_updated_today: prev.jobs_updated_today + 41,
      }));
      setIsRunning(false);
    }, 4000);
  };

  const handleScrapeCompany = (company: Company) => {
    setActiveTab("logs");
    setLogs((prev) => [
      ...prev,
      {
        id: `manual-${Date.now()}`,
        timestamp: new Date().toISOString(),
        level: "INFO",
        prefix: "[FETCH]",
        message: `Manual scrape triggered for ${company.url.replace("https://", "")}`,
        company: company.name,
      },
    ]);
  };

  return (
    <div className="min-h-screen bg-[#0F1117] text-[#F8F7F4]">
      <Header
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onRunAll={handleRunAll}
        isRunning={isRunning}
      />

      <main className="max-w-[1400px] mx-auto px-6 py-6">
        {/* Overview Tab */}
        {activeTab === "overview" && (
          <div className="space-y-6">
            <StatsBar stats={stats} />
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <ActivityChart />
              </div>
              <div>
                <ATSDistribution />
              </div>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ScrapeHistory runs={mockScrapeHistory} />
              <LogPanel logs={logs.slice(-8)} autoScroll={false} maxHeight="280px" />
            </div>
            <CompanyTable companies={mockCompanies.slice(0, 5)} onScrape={handleScrapeCompany} />
          </div>
        )}

        {/* Sources Tab */}
        {activeTab === "sources" && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-mono font-semibold text-[#F8F7F4]">Source Registry</h2>
                <p className="text-[11px] font-mono text-slate-600 mt-0.5">
                  sources.yaml — {mockCompanies.length} companies configured
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono text-slate-700 bg-slate-900/60 border border-slate-800 rounded px-2 py-1">
                  MAX_CONCURRENCY=4
                </span>
              </div>
            </div>
            <CompanyTable companies={mockCompanies} onScrape={handleScrapeCompany} />
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-lg p-4">
              <div className="text-[10px] font-mono text-slate-600 uppercase tracking-widest mb-3">sources.yaml preview</div>
              <pre className="text-[11px] font-mono text-slate-400 overflow-x-auto leading-relaxed">
{`companies:
  - name: Stripe
    url: https://boards.greenhouse.io/stripe
    ats_type: greenhouse
    collector: http

  - name: Vercel
    url: https://vercel.com/careers
    ats_type: lever
    collector: playwright

  - name: Linear
    url: https://linear.app/careers
    ats_type: ashby
    collector: http

  # Add more companies below...`}
              </pre>
            </div>
          </div>
        )}

        {/* Jobs Tab */}
        {activeTab === "jobs" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-mono font-semibold text-[#F8F7F4]">Job Postings</h2>
                <p className="text-[11px] font-mono text-slate-600 mt-0.5">
                  jobposting — {mockJobs.length} records
                </p>
              </div>
              <div className="relative">
                <Search size={12} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-600" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search title, company, location..."
                  className="bg-[#0a0c10] border border-slate-700/60 rounded pl-8 pr-8 py-2 text-[11px] font-mono text-[#F8F7F4] placeholder-slate-700 focus:outline-none focus:border-amber-500/40 w-64 transition-colors"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery("")}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-600 hover:text-slate-400"
                  >
                    <X size={11} />
                  </button>
                )}
              </div>
            </div>
            <JobTable jobs={mockJobs} searchQuery={searchQuery} />
          </div>
        )}

        {/* Logs Tab */}
        {activeTab === "logs" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-mono font-semibold text-[#F8F7F4]">Pipeline Logs</h2>
                <p className="text-[11px] font-mono text-slate-600 mt-0.5">
                  {logs.length} entries — structured output
                </p>
              </div>
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-teal-400" />
                  <span className="text-[10px] font-mono text-slate-600">{logs.filter(l => l.level === "SUCCESS").length} success</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
                  <span className="text-[10px] font-mono text-slate-600">{logs.filter(l => l.level === "ERROR").length} error</span>
                </div>
              </div>
            </div>
            <LogPanel logs={logs} autoScroll maxHeight="calc(100vh - 240px)" />
          </div>
        )}

        {/* CLI Tab */}
        {activeTab === "cli" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-lg font-mono font-semibold text-[#F8F7F4]">CLI Interface</h2>
              <p className="text-[11px] font-mono text-slate-600 mt-0.5">
                jobscraper.cli — Typer-powered command interface
              </p>
            </div>
            <ScrapeCommandPanel />

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-lg overflow-hidden">
              <div className="px-4 py-3 border-b border-slate-800/80">
                <div className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-500" />
                  <span className="text-[11px] font-mono text-slate-400 uppercase tracking-widest">Architecture Overview</span>
                </div>
              </div>
              <div className="p-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {[
                    {
                      title: "Collectors",
                      color: "border-blue-800/50",
                      accent: "text-blue-400",
                      items: ["HTTPCollector (HTTPX async)", "PlaywrightCollector (Playwright)", "Tenacity retry wrapper", "Exponential backoff"],
                    },
                    {
                      title: "Extractors",
                      color: "border-violet-800/50",
                      accent: "text-violet-400",
                      items: ["GreenhouseExtractor", "LeverExtractor", "AshbyExtractor", "GenericCareersExtractor", "Registry + URL routing"],
                    },
                    {
                      title: "Services",
                      color: "border-teal-800/50",
                      accent: "text-teal-400",
                      items: ["DedupeService", "PersistenceService (upsert)", "RawStorageService (HTML)", "data/raw/ snapshots"],
                    },
                  ].map((section) => (
                    <div key={section.title} className={`border ${section.color} rounded-lg p-3 bg-slate-900/40`}>
                      <div className={`text-[10px] font-mono uppercase tracking-widest mb-2.5 ${section.accent}`}>
                        {section.title}
                      </div>
                      <ul className="space-y-1.5">
                        {section.items.map((item) => (
                          <li key={item} className="flex items-center gap-2">
                            <span className="w-1 h-1 rounded-full bg-slate-700 shrink-0" />
                            <span className="text-[11px] font-mono text-slate-400">{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>

                <div className="mt-4 bg-[#0a0c10] rounded border border-slate-800/60 p-4">
                  <div className="text-[10px] font-mono text-slate-700 uppercase tracking-widest mb-3">Pipeline Flow</div>
                  <div className="flex items-center gap-2 text-[11px] font-mono flex-wrap">
                    {[
                      { label: "fetch HTML", color: "bg-blue-900/40 text-blue-400 border-blue-800/40" },
                      { label: "→", color: "text-slate-700", plain: true },
                      { label: "save snapshot", color: "bg-slate-800/60 text-slate-500 border-slate-700/40" },
                      { label: "→", color: "text-slate-700", plain: true },
                      { label: "resolve extractor", color: "bg-violet-900/40 text-violet-400 border-violet-800/40" },
                      { label: "→", color: "text-slate-700", plain: true },
                      { label: "validate schema", color: "bg-amber-900/30 text-amber-400 border-amber-800/30" },
                      { label: "→", color: "text-slate-700", plain: true },
                      { label: "dedupe check", color: "bg-slate-800/60 text-slate-500 border-slate-700/40" },
                      { label: "→", color: "text-slate-700", plain: true },
                      { label: "upsert DB", color: "bg-teal-900/40 text-teal-400 border-teal-800/40" },
                    ].map((step, i) =>
                      step.plain ? (
                        <span key={i} className={step.color}>{step.label}</span>
                      ) : (
                        <span key={i} className={`px-2 py-0.5 rounded border ${step.color}`}>{step.label}</span>
                      )
                    )}
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-lg p-4">
              <div className="text-[10px] font-mono text-slate-600 uppercase tracking-widest mb-3">Project Structure</div>
              <pre className="text-[11px] font-mono text-slate-500 leading-relaxed">
{`jobscraper/
├── config.py          # pydantic-settings env loader
├── models.py          # SQLModel JobPosting table
├── schemas.py         # JobPostingIn input schema
├── db.py              # engine, session, init_db()
├── registry.py        # extractor router
├── cli.py             # Typer CLI entry point
├── collectors/
│   ├── base.py        # abstract collector
│   ├── http_collector.py
│   └── playwright_collector.py
├── extractors/
│   ├── base.py        # abstract extractor
│   ├── greenhouse.py
│   ├── lever.py
│   ├── ashby.py
│   └── generic_careers.py
├── pipelines/
│   ├── scrape_company.py
│   ├── scrape_all.py
│   └── discover.py
├── services/
│   ├── raw_storage.py
│   ├── dedupe.py
│   └── persistence.py
└── utils/
    ├── urls.py
    ├── hashing.py
    └── time.py`}
              </pre>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default Home;
