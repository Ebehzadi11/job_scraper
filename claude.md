# Job Scraper Dashboard

A React + TypeScript dashboard for managing and monitoring a job scraping pipeline that aggregates job postings from various company career pages.

## Tech Stack

- **Framework**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS with shadcn/ui components (new-york style)
- **UI Components**: Radix UI primitives via shadcn/ui
- **Charts**: Recharts
- **Routing**: React Router v6
- **Backend**: Supabase
- **Forms**: React Hook Form + Zod validation

## Project Structure

```
src/
├── components/
│   ├── ui/           # shadcn/ui components (do not modify directly)
│   └── scraper/      # Custom dashboard components
├── data/             # Mock data for development
├── types/            # TypeScript type definitions
├── lib/              # Utility functions (cn helper, etc.)
└── App.tsx           # Main app with routing
```

## Development Commands

```bash
npm run dev          # Start dev server
npm run build        # Type check + build
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

## Path Aliases

- `@/*` maps to `./src/*`

## Design System

- **Dark theme**: Background `#0F1117`, text `#F8F7F4`
- **Font**: Monospace throughout (font-mono)
- **Accent colors**: Amber for primary actions, Teal for success, Slate for borders
- **Base color**: Slate (configured in shadcn)

## Key Types

- `Company` - Source configuration for scraping
- `JobPosting` - Individual job listing data
- `ScrapeLog` - Pipeline execution logs
- `PipelineStats` - Dashboard statistics
- `ATSType` - ATS platforms: greenhouse, lever, ashby, generic
- `CollectorType` - http (HTTPX) or playwright

## Component Conventions

- Use shadcn/ui components from `@/components/ui/` for standard UI elements
- Custom scraper components go in `@/components/scraper/`
- Follow existing monospace, terminal-inspired aesthetic
- Use Lucide icons from `lucide-react`

## Adding shadcn Components

```bash
npx shadcn@latest add <component-name>
```
