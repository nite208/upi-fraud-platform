import { createFileRoute, Link } from "@tanstack/react-router";
import { AppShell, Badge, Card } from "@/components/AppShell";
import { cases } from "@/lib/mockData";
import { CheckCircle2, Clock, User } from "lucide-react";
import { useState } from "react";

export const Route = createFileRoute("/cases/")({
  head: () => ({ meta: [{ title: "Cases — FraudShield" }] }),
  component: Cases,
});

const tabs = ["All", "Open", "In Progress", "Closed"] as const;

function CircleScore({ score }: { score: number }) {
  const color = score >= 75 ? "#C62828" : score >= 50 ? "#F57F17" : "#2E7D32";
  const dash = (score / 100) * 176;
  return (
    <div className="relative h-16 w-16">
      <svg className="h-16 w-16 -rotate-90" viewBox="0 0 64 64">
        <circle cx="32" cy="32" r="28" fill="none" stroke="#e2e8f0" strokeWidth="6" />
        <circle cx="32" cy="32" r="28" fill="none" stroke={color} strokeWidth="6" strokeDasharray={`${dash} 176`} strokeLinecap="round" />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center text-sm font-bold" style={{ color }}>{score}</div>
    </div>
  );
}

function Cases() {
  const [tab, setTab] = useState<typeof tabs[number]>("All");
  const filtered = tab === "All" ? cases : cases.filter((c) => c.status === tab);

  return (
    <AppShell>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-primary flex items-center gap-3">
            Case Queue
            <span className="text-sm bg-secondary text-primary px-2.5 py-1 rounded-full font-semibold">{cases.length}</span>
          </h1>
          <p className="text-sm text-muted-foreground">Fraud cases pending analyst review</p>
        </div>
      </div>

      <div className="flex gap-1 border-b mb-6">
        {tabs.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${tab === t ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground"}`}
          >
            {t}
            <span className="ml-2 text-xs">{t === "All" ? cases.length : cases.filter((c) => c.status === t).length}</span>
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <Card className="p-12 text-center">
          <CheckCircle2 className="h-12 w-12 text-success mx-auto" />
          <h3 className="mt-4 font-semibold text-foreground">No cases in queue</h3>
          <p className="text-sm text-muted-foreground">You're all caught up.</p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((c) => (
            <Card key={c.id} className="p-5 hover:shadow-md transition-shadow">
              <div className="flex items-start gap-4">
                <CircleScore score={c.score} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <div className="font-mono text-sm font-semibold text-primary">{c.id}</div>
                    <Badge variant={c.status === "Open" ? "block" : c.status === "In Progress" ? "review" : "safe"}>{c.status}</Badge>
                  </div>
                  <div className="mt-1 text-xs text-muted-foreground font-mono">{c.txnId}</div>
                  <div className="mt-2 flex items-center gap-4 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1"><User className="h-3 w-3" />{c.analyst}</span>
                    {c.slaMinutes > 0 && (
                      <span className={`flex items-center gap-1 font-medium ${c.slaMinutes < 30 ? "text-danger" : "text-foreground"}`}>
                        <Clock className="h-3 w-3" />SLA {c.slaMinutes}m
                      </span>
                    )}
                  </div>
                  <div className="mt-2">
                    <Badge variant="primary">{c.fraudType}</Badge>
                  </div>
                </div>
              </div>
              <div className="mt-4 flex justify-end">
                <Link
                  to="/cases/$id"
                  params={{ id: c.id }}
                  className="text-sm bg-primary text-primary-foreground px-4 py-2 rounded-md font-medium hover:bg-primary/90"
                >
                  Investigate →
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}
    </AppShell>
  );
}
