export type ATSType = "greenhouse" | "lever" | "ashby" | "generic";
export type JobStatus = "active" | "inactive" | "pending";
export type CollectorType = "http" | "playwright";
export type ScrapeStatus = "idle" | "running" | "success" | "error";

export interface JobPosting {
  id: string;
  title: string;
  company: string;
  location: string;
  department?: string;
  employment_type?: string;
  source_url: string;
  source_type: ATSType;
  external_job_id?: string;
  is_active: boolean;
  scraped_at: string;
  created_at: string;
  description_text?: string;
}

export interface Company {
  id: string;
  name: string;
  url: string;
  ats_type: ATSType;
  collector_type: CollectorType;
  last_scraped?: string;
  job_count: number;
  status: ScrapeStatus;
}

export interface ScrapeLog {
  id: string;
  timestamp: string;
  level: "INFO" | "WARN" | "ERROR" | "SUCCESS";
  prefix: "[FETCH]" | "[EXTRACT]" | "[PERSIST]" | "[DEDUPE]" | "[INIT]" | "[CONFIG]" | "[RETRY]";
  message: string;
  company?: string;
}

export interface PipelineStats {
  total_jobs: number;
  active_jobs: number;
  companies_tracked: number;
  last_run?: string;
  jobs_added_today: number;
  jobs_updated_today: number;
}

export interface ScrapeRun {
  company: string;
  url: string;
  ats_type: ATSType;
  collector_type: CollectorType;
  jobs_found: number;
  jobs_inserted: number;
  jobs_updated: number;
  duration_ms: number;
  status: ScrapeStatus;
  timestamp: string;
}
