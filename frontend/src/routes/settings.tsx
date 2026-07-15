import { createFileRoute } from "@tanstack/react-router";
import { AppShell, Card } from "@/components/AppShell";
import { Switch } from "@/components/ui/switch";
import { useState } from "react";
import { Activity } from "lucide-react";

export const Route = createFileRoute("/settings")({
  head: () => ({ meta: [{ title: "Settings — FraudShield" }] }),
  component: Settings,
});

function Settings() {
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [slaWarn, setSlaWarn] = useState(true);
  const [dailySummary, setDailySummary] = useState(false);

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-primary">Settings</h1>
        <p className="text-sm text-muted-foreground">Workspace, model thresholds, and integrations</p>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h2 className="font-semibold text-primary">Model Thresholds</h2>
          <p className="text-xs text-muted-foreground mt-1">Tune SAFE / REVIEW / BLOCK boundaries</p>
          <div className="mt-5 space-y-4">
            {[
              { label: "SAFE ≤", value: 40, color: "bg-success" },
              { label: "REVIEW <", value: 70, color: "bg-warning" },
              { label: "BLOCK ≥", value: 70, color: "bg-danger" },
            ].map((t) => (
              <div key={t.label}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-medium">{t.label}</span>
                  <span className="text-muted-foreground">{t.value}/100</span>
                </div>
                <div className="h-2 bg-muted rounded overflow-hidden">
                  <div className={`h-full ${t.color}`} style={{ width: `${t.value}%` }} />
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="font-semibold text-primary">Alert Preferences</h2>
          <p className="text-xs text-muted-foreground mt-1">Choose which notifications you receive</p>
          <div className="mt-5 space-y-4">
            {[
              { label: "Email alerts for BLOCK decisions", value: emailAlerts, set: setEmailAlerts },
              { label: "SLA warnings at 75% deadline", value: slaWarn, set: setSlaWarn },
              { label: "Daily fraud summary report", value: dailySummary, set: setDailySummary },
            ].map((row) => (
              <div key={row.label} className="flex items-center justify-between py-2 border-b last:border-0">
                <span className="text-sm">{row.label}</span>
                <Switch checked={row.value} onCheckedChange={row.set} />
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-accent" />
            <h2 className="font-semibold text-primary">Model Health</h2>
          </div>
          <p className="text-xs text-muted-foreground mt-1">Live status of production models</p>
          <div className="mt-5 space-y-3 text-sm">
            {[
              ["Current model version", "1.0"],
              ["Last trained", "June 2025"],
              ["Training data", "1,048,575 transactions"],
              ["XGBoost PR-AUC", "0.9621"],
            ].map(([k, v]) => (
              <div key={k} className="flex items-center justify-between py-2 border-b last:border-0">
                <span className="text-muted-foreground">{k}</span>
                <span className="font-medium">{v}</span>
              </div>
            ))}
          </div>
          <button className="mt-5 w-full bg-accent text-white py-2.5 rounded-lg text-sm font-medium hover:opacity-90">
            Request Retraining
          </button>
        </Card>

        <Card className="p-6">
          <h2 className="font-semibold text-primary">Integrations</h2>
          <p className="text-xs text-muted-foreground mt-1">Connected systems</p>
          <div className="mt-5 space-y-3 text-sm">
            {[
              ["NPCI UPI Switch", "Connected"],
              ["ChromaDB Vector Store", "Connected"],
              ["Groq LLM Gateway", "Connected"],
              ["Neo4j Graph", "Connected"],
            ].map(([k, v]) => (
              <div key={k} className="flex items-center justify-between py-2 border-b last:border-0">
                <span>{k}</span>
                <span className="text-xs text-success font-medium">● {v}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
