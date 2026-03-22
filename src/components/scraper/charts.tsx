import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

const weeklyData = [
  { day: "Mon", added: 45, updated: 120 },
  { day: "Tue", added: 62, updated: 98 },
  { day: "Wed", added: 38, updated: 144 },
  { day: "Thu", added: 91, updated: 167 },
  { day: "Fri", added: 127, updated: 89 },
  { day: "Sat", added: 24, updated: 56 },
  { day: "Sun", added: 18, updated: 43 },
];

const atsDist = [
  { name: "Greenhouse", value: 1420, color: "#34d399" },
  { name: "Lever", value: 780, color: "#60a5fa" },
  { name: "Ashby", value: 380, color: "#a78bfa" },
  { name: "Generic", value: 267, color: "#64748b" },
];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload?.length) {
    return (
      <div className="bg-slate-900 border border-slate-700/60 rounded px-3 py-2 text-[11px] font-mono shadow-xl">
        <div className="text-slate-400 mb-1">{label}</div>
        {payload.map((p: any) => (
          <div key={p.name} className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full" style={{ background: p.color }} />
            <span className="text-slate-400">{p.name}:</span>
            <span className="text-[#F8F7F4] tabular-nums">{p.value}</span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export function ActivityChart() {
  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
          <span className="text-[11px] font-mono text-slate-400 uppercase tracking-widest">Weekly Activity</span>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-sm bg-teal-500/70" />
            <span className="text-[10px] font-mono text-slate-600">new</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-sm bg-blue-500/50" />
            <span className="text-[10px] font-mono text-slate-600">updated</span>
          </div>
        </div>
      </div>
      <div className="px-4 pt-4 pb-2">
        <ResponsiveContainer width="100%" height={140}>
          <BarChart data={weeklyData} barGap={2} barSize={12}>
            <XAxis
              dataKey="day"
              tick={{ fontSize: 10, fontFamily: "monospace", fill: "#475569" }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis hide />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
            <Bar dataKey="added" fill="#2dd4bf" opacity={0.8} radius={[2, 2, 0, 0]} />
            <Bar dataKey="updated" fill="#3b82f6" opacity={0.4} radius={[2, 2, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export function ATSDistribution() {
  const total = atsDist.reduce((s, d) => s + d.value, 0);

  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-teal-400" />
          <span className="text-[11px] font-mono text-slate-400 uppercase tracking-widest">ATS Distribution</span>
        </div>
      </div>
      <div className="p-4 space-y-3">
        {atsDist.map((item) => (
          <div key={item.name}>
            <div className="flex items-center justify-between mb-1">
              <span className="text-[11px] font-mono text-slate-400">{item.name}</span>
              <span className="text-[11px] font-mono tabular-nums" style={{ color: item.color }}>
                {item.value.toLocaleString()}
              </span>
            </div>
            <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-700"
                style={{
                  width: `${(item.value / total) * 100}%`,
                  background: item.color,
                  opacity: 0.7,
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
