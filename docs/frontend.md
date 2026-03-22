# Frontend Documentation

React + TypeScript dashboard for managing and monitoring the job scraping pipeline.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | React 18 + TypeScript |
| Build | Vite |
| Styling | Tailwind CSS |
| Components | shadcn/ui (new-york style) |
| Primitives | Radix UI |
| Charts | Recharts |
| Routing | React Router v6 |
| Forms | React Hook Form + Zod |
| Backend | Supabase |

## Project Structure

```
src/
├── components/
│   ├── ui/              # shadcn/ui components (do not modify)
│   └── scraper/         # Custom dashboard components
├── lib/
│   └── supabase.ts      # Supabase client
├── types/
│   └── supabase.ts      # Generated database types
├── data/                # Mock data for development
└── App.tsx              # Main app with routing
```

## Development Commands

```bash
npm run dev          # Start dev server (http://localhost:5173)
npm run build        # Type check + production build
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

## Path Aliases

```typescript
// tsconfig.json
"@/*" → "./src/*"

// Usage
import { Button } from "@/components/ui/button"
import { supabase } from "@/lib/supabase"
```

## Design System

### Colors

| Purpose | Value | CSS Variable |
|---------|-------|--------------|
| Background | `#0F1117` | `--background` |
| Foreground | `#F8F7F4` | `--foreground` |
| Primary | Amber | `--primary` |
| Success | Teal | `--accent` |
| Borders | Slate | `--border` |

### Typography

- **Font**: Monospace throughout (`font-mono`)
- **Aesthetic**: Terminal-inspired, dark theme

### Component Guidelines

1. Use shadcn/ui components from `@/components/ui/`
2. Custom components go in `@/components/scraper/`
3. Use Lucide icons from `lucide-react`
4. Follow existing monospace aesthetic

## Adding shadcn Components

```bash
npx shadcn@latest add <component-name>

# Examples
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add table
```

## Key Types

```typescript
// Company source configuration
interface Company {
  id: string
  name: string
  url: string
  ats_type: ATSType
  collector_type: CollectorType
  enabled: boolean
}

// Job listing data
interface JobPosting {
  id: string
  company_name: string
  job_title: string
  location_text?: string
  department?: string
  canonical_job_url: string
  created_at: string
}

// Scrape execution log
interface ScrapeLog {
  id: string
  company_id: string
  status: 'success' | 'error' | 'partial'
  jobs_found: number
  started_at: string
  completed_at: string
}

// Dashboard statistics
interface PipelineStats {
  total_jobs: number
  total_companies: number
  jobs_today: number
  success_rate: number
}

// ATS platforms
type ATSType = 'greenhouse' | 'lever' | 'ashby' | 'generic'

// Collection methods
type CollectorType = 'http' | 'playwright'
```

## Supabase Integration

### Client Setup

```typescript
// src/lib/supabase.ts
import { createClient } from '@supabase/supabase-js'
import type { Database } from '@/types/supabase'

export const supabase = createClient<Database>(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)
```

### Regenerating Types

```bash
SUPABASE_PROJECT_ID=your-project-id npx supabase gen types typescript --project-id $SUPABASE_PROJECT_ID > src/types/supabase.ts
```

### Environment Variables

Required in `.env`:
```
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
```

## Component Patterns

### Dashboard Cards

```tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

<Card>
  <CardHeader>
    <CardTitle className="font-mono">Pipeline Stats</CardTitle>
  </CardHeader>
  <CardContent>
    {/* Content */}
  </CardContent>
</Card>
```

### Data Tables

```tsx
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Company</TableHead>
      <TableHead>Jobs</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    {data.map((row) => (
      <TableRow key={row.id}>
        <TableCell>{row.company}</TableCell>
        <TableCell>{row.jobs}</TableCell>
      </TableRow>
    ))}
  </TableBody>
</Table>
```

### Status Badges

```tsx
import { Badge } from "@/components/ui/badge"

<Badge variant="default">Active</Badge>
<Badge variant="secondary">Pending</Badge>
<Badge variant="destructive">Error</Badge>
```
