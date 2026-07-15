import { createFileRoute } from "@tanstack/react-router";
import { AppShell, Badge, Card } from "@/components/AppShell";
import { muleAccounts, maskVpa } from "@/lib/mockData";
import { useState } from "react";

export const Route = createFileRoute("/graph")({
  head: () => ({ meta: [{ title: "Graph — FraudShield" }] }),
  component: GraphPage,
});

// Static positioned nodes for placeholder network viz
const nodes = [
  { id: "A", x: 200, y: 180, type: "normal", label: "rahul123" },
  { id: "B", x: 340, y: 100, type: "suspicious", label: "vikas.m" },
  { id: "C", x: 480, y: 200, type: "fraud", label: "shop9x" },
  { id: "D", x: 380, y: 300, type: "fraud", label: "cash4u" },
  { id: "E", x: 560, y: 340, type: "suspicious", label: "quickpay" },
  { id: "F", x: 620, y: 130, type: "normal", label: "amit.k" },
  { id: "G", x: 240, y: 350, type: "normal", label: "priya" },
  { id: "H", x: 700, y: 240, type: "fraud", label: "fastmoney" },
  { id: "I", x: 140, y: 280, type: "suspicious", label: "arjun_r" },
];
const edges = [
  ["A", "C"], ["A", "B"], ["B", "C"], ["C", "D"], ["D", "E"], ["C", "F"],
  ["E", "H"], ["G", "D"], ["I", "D"], ["I", "C"], ["B", "F"], ["H", "F"],
];
const color = (t: string) => (t === "fraud" ? "#C62828" : t === "suspicious" ? "#FF6B00" : "#1A237E");

function GraphPage() {
  const [showMule, setShowMule] = useState(true);

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-primary">Fraud Network Intelligence</h1>
        <p className="text-sm text-muted-foreground">Graph-based mule detection and fraud ring analysis</p>
      </div>

      <Card className="mb-6 p-4 flex flex-wrap items-center gap-3">
        <input placeholder="Enter VPA to load account graph..." defaultValue="cash4u@ybl" className="flex-1 min-w-[240px] px-3 py-2 border rounded-md text-sm bg-background focus:outline-none focus:ring-2 focus:ring-primary" />
        <button className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium">Load Account Graph</button>
        <label className="flex items-center gap-2 text-sm cursor-pointer">
          <input type="checkbox" checked={showMule} onChange={(e) => setShowMule(e.target.checked)} className="rounded" />
          Show Mule Accounts
        </label>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <div className="p-5 border-b flex items-center justify-between">
            <h2 className="font-semibold text-primary">Account Graph · 2-hop neighborhood</h2>
            <span className="text-xs text-muted-foreground">9 nodes · 12 edges</span>
          </div>
          <div className="relative bg-muted/30" style={{ height: 480 }}>
            <svg viewBox="0 0 800 480" className="w-full h-full">
              {edges.map(([a, b], i) => {
                const na = nodes.find((n) => n.id === a)!;
                const nb = nodes.find((n) => n.id === b)!;
                return <line key={i} x1={na.x} y1={na.y} x2={nb.x} y2={nb.y} stroke="#94a3b8" strokeWidth={1.5} strokeOpacity={0.5} />;
              })}
              {nodes.map((n) => (
                <g key={n.id}>
                  <circle cx={n.x} cy={n.y} r={n.type === "fraud" ? 18 : 14} fill={color(n.type)} opacity={0.9}>
                    {n.type === "fraud" && <animate attributeName="r" values="18;22;18" dur="2s" repeatCount="indefinite" />}
                  </circle>
                  <text x={n.x} y={n.y + 34} textAnchor="middle" fontSize="11" fill="#334155" fontFamily="ui-monospace">{n.label}</text>
                </g>
              ))}
            </svg>
            <div className="absolute bottom-4 left-4 bg-card border rounded-lg p-3 text-xs space-y-1.5 shadow-sm">
              <div className="font-semibold text-primary mb-1">Legend</div>
              <div className="flex items-center gap-2"><span className="h-3 w-3 rounded-full bg-primary" />Normal account</div>
              <div className="flex items-center gap-2"><span className="h-3 w-3 rounded-full bg-accent" />Suspicious</div>
              <div className="flex items-center gap-2"><span className="h-3 w-3 rounded-full bg-danger" />Confirmed fraud</div>
              <div className="flex items-center gap-2"><span className="h-0.5 w-3 bg-muted-foreground" />Transaction</div>
            </div>
          </div>
        </Card>

        <Card>
          <div className="p-5 border-b flex items-center justify-between">
            <h2 className="font-semibold text-primary">Mule Accounts</h2>
            <Badge variant="block">{muleAccounts.length}</Badge>
          </div>
          <div className="divide-y">
            {muleAccounts.map((m) => (
              <div key={m.vpa} className="p-4 hover:bg-muted/40">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs">{maskVpa(m.vpa)}</span>
                  <span className="text-xs font-bold text-danger">{m.score}</span>
                </div>
                <div className="mt-2 h-1.5 bg-muted rounded overflow-hidden">
                  <div className="h-full bg-danger" style={{ width: `${m.score}%` }} />
                </div>
                <div className="mt-2 flex gap-3 text-[11px] text-muted-foreground">
                  <span>in <strong className="text-foreground">{m.inDeg}</strong></span>
                  <span>out <strong className="text-foreground">{m.outDeg}</strong></span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Card className="mt-6">
        <div className="p-5 border-b"><h2 className="font-semibold text-primary">Fraud Rings Detected</h2></div>
        <div className="divide-y">
          {[
            { id: "RING-014", members: 6, exposure: 1240000, type: "velocity_attack" },
            { id: "RING-013", members: 4, exposure: 720000, type: "mule_chain" },
            { id: "RING-012", members: 9, exposure: 3100000, type: "layering" },
          ].map((r) => (
            <div key={r.id} className="p-4 flex items-center justify-between hover:bg-muted/40">
              <div className="flex items-center gap-4">
                <span className="font-mono text-sm text-primary font-semibold">{r.id}</span>
                <Badge variant="primary">{r.type}</Badge>
                <span className="text-xs text-muted-foreground">{r.members} accounts</span>
              </div>
              <div className="text-sm font-semibold text-danger">₹{r.exposure.toLocaleString("en-IN")} exposure</div>
            </div>
          ))}
        </div>
      </Card>
    </AppShell>
  );
}
