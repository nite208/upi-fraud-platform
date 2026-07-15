import { createFileRoute } from "@tanstack/react-router";
import { AppShell, Badge, Card } from "@/components/AppShell";
import { scoreDistribution, decisionBreakdown, fraudTypeDist } from "@/lib/mockData";
import {
  Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid, Legend,
} from "recharts";

export const Route = createFileRoute("/analytics")({
  head: () => ({ meta: [{ title: "Analytics — FraudShield" }] }),
  component: Analytics,
});

const decColor = (d: string) => (d === "SAFE" ? "#2E7D32" : d === "REVIEW" ? "#F57F17" : "#C62828");

const metrics = [
  { name: "XGB PR-AUC", value: 0.9621, color: "#1A237E" },
  { name: "RF PR-AUC", value: 0.9555, color: "#3949AB" },
  { name: "Ensemble PR-AUC", value: 0.9606, color: "#FF6B00" },
  { name: "Best F2", value: 0.9553, color: "#2E7D32" },
];

function Analytics() {
  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-primary">Risk Intelligence Analytics</h1>
        <p className="text-sm text-muted-foreground">Model performance, decision distributions, and fraud patterns</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card>
          <div className="p-5 border-b"><h2 className="font-semibold text-primary">Score Distribution</h2><p className="text-xs text-muted-foreground mt-0.5">Today's transactions by risk bucket</p></div>
          <div className="p-4" style={{ height: 320 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={scoreDistribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="bucket" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8 }} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {scoreDistribution.map((s, i) => <Cell key={i} fill={decColor(s.decision)} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <div className="p-5 border-b"><h2 className="font-semibold text-primary">Decision Breakdown</h2><p className="text-xs text-muted-foreground mt-0.5">Auto-approve vs review vs block</p></div>
          <div className="p-4" style={{ height: 320 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={decisionBreakdown} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2}>
                  {decisionBreakdown.map((d, i) => <Cell key={i} fill={d.color} />)}
                </Pie>
                <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8 }} />
                <Legend iconType="circle" />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <Card className="mb-6">
        <div className="p-5 border-b flex items-center justify-between">
          <div>
            <h2 className="font-semibold text-primary">Model Performance</h2>
            <p className="text-xs text-muted-foreground mt-0.5">Latest evaluation on holdout set</p>
          </div>
          <Badge variant="primary">Model Version 1.0</Badge>
        </div>
        <div className="p-5 grid grid-cols-2 lg:grid-cols-4 gap-6">
          {metrics.map((m) => (
            <div key={m.name}>
              <div className="text-xs text-muted-foreground font-medium">{m.name}</div>
              <div className="mt-1 text-3xl font-bold" style={{ color: m.color }}>{m.value.toFixed(4)}</div>
              <div className="mt-3 h-2 bg-muted rounded overflow-hidden">
                <div className="h-full rounded" style={{ width: `${m.value * 100}%`, backgroundColor: m.color }} />
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <div className="p-5 border-b"><h2 className="font-semibold text-primary">Fraud Type Distribution</h2><p className="text-xs text-muted-foreground mt-0.5">Confirmed fraud cases (last 30 days)</p></div>
        <div className="p-4" style={{ height: 320 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={fraudTypeDist} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis type="number" tick={{ fontSize: 11 }} />
              <YAxis type="category" dataKey="type" tick={{ fontSize: 11 }} width={140} />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8 }} />
              <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                {fraudTypeDist.map((f, i) => <Cell key={i} fill={f.color} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </AppShell>
  );
}
