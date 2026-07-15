import { createFileRoute, Link, useParams } from "@tanstack/react-router";
import { AppShell, Badge, Card } from "@/components/AppShell";
import { cases, transactions, shapValues, formatINR, maskVpa } from "@/lib/mockData";
import { Bot, ChevronRight, FileText, Network as NetworkIcon, Send, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { getRole, type Role } from "@/lib/auth";

export const Route = createFileRoute("/cases/$id")({
  head: () => ({ meta: [{ title: "Case Detail — FraudShield" }] }),
  component: CaseDetail,
});

function Gauge({ label, value, color }: { label: string; value: number; color: string }) {
  const dash = (value / 100) * 226;
  return (
    <div className="text-center">
      <div className="relative h-24 w-24 mx-auto">
        <svg className="h-24 w-24 -rotate-90" viewBox="0 0 96 96">
          <circle cx="48" cy="48" r="36" fill="none" stroke="#e2e8f0" strokeWidth="8" />
          <circle cx="48" cy="48" r="36" fill="none" stroke={color} strokeWidth="8" strokeDasharray={`${dash} 226`} strokeLinecap="round" />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center text-xl font-bold" style={{ color }}>{value}</div>
      </div>
      <div className="text-xs text-muted-foreground mt-2 font-medium">{label}</div>
    </div>
  );
}

function CaseDetail() {
  const { id } = useParams({ from: "/cases/$id" });
  const kase = cases.find((c) => c.id === id) ?? cases[0];
  const txn = transactions.find((t) => t.id === kase.txnId) ?? transactions[0];
  const [messages, setMessages] = useState<{ role: "user" | "ai"; text: string }[]>([
    { role: "ai", text: "I've reviewed this case. The transaction shows classic velocity attack patterns. What would you like to explore?" },
  ]);
  const [input, setInput] = useState("");
  const [notes, setNotes] = useState("");
  const [toast, setToast] = useState<string | null>(null);
  const [role, setRoleState] = useState<Role | null>(null);
  useEffect(() => setRoleState(getRole()), []);
  const canInvestigate = role === "investigator" || role === "admin";
  const readOnly = role === "risk_manager";

  const send = () => {
    if (!input.trim()) return;
    setMessages((m) => [...m, { role: "user", text: input }, { role: "ai", text: "Based on the sender's txn history, this receiver is flagged in 3 other cases within 24 hours. Consistent with mule chain behavior." }]);
    setInput("");
  };

  const submitDisposition = (label: string) => {
    setToast(`Disposition recorded: ${label}`);
    setTimeout(() => setToast(null), 2400);
  };

  return (
    <AppShell>
      <nav className="text-sm text-muted-foreground mb-4 flex items-center gap-1">
        <Link to="/cases" className="hover:text-primary">Cases</Link>
        <ChevronRight className="h-3.5 w-3.5" />
        <span className="text-foreground font-medium">{kase.id}</span>
      </nav>

      <div className="mb-6 flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-primary">Case {kase.id}</h1>
          <p className="text-sm text-muted-foreground">Opened 24m ago · Assigned to {kase.analyst}</p>
        </div>
        <div className="flex items-center gap-3">
          {canInvestigate && (
            <>
              <Link to="/graph" className="inline-flex items-center gap-2 text-sm px-3 py-2 rounded-md border bg-background hover:bg-muted">
                <NetworkIcon className="h-4 w-4" /> Graph Network
              </Link>
              <button
                onClick={() => submitDisposition("SAR draft generated")}
                className="inline-flex items-center gap-2 text-sm px-3 py-2 rounded-md bg-accent text-white font-medium hover:opacity-90"
              >
                <FileText className="h-4 w-4" /> Generate SAR
              </button>
            </>
          )}
          <Badge variant="block">Risk {kase.score}/100</Badge>
        </div>
      </div>


      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        <div className="lg:col-span-3 space-y-6">
          <Card>
            <div className="p-5 border-b"><h2 className="font-semibold text-primary">Transaction Details</h2></div>
            <div className="p-5">
              <dl className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
                {[
                  ["Transaction ID", <span className="font-mono">{txn.id}</span>],
                  ["Sender VPA", maskVpa(txn.sender)],
                  ["Receiver VPA", maskVpa(txn.receiver)],
                  ["Amount", <span className="font-semibold">{formatINR(txn.amount)}</span>],
                  ["Timestamp", `${txn.time} · Jul 3, 2026`],
                  ["Channel", "UPI Mobile"],
                  ["Bank", "ICICI → Paytm"],
                  ["MCC", "6011 (Financial)"],
                ].map(([k, v], i) => (
                  <div key={i}>
                    <dt className="text-xs text-muted-foreground uppercase tracking-wider">{k}</dt>
                    <dd className="mt-0.5">{v}</dd>
                  </div>
                ))}
              </dl>
            </div>
          </Card>

          <Card>
            <div className="p-5 border-b">
              <h2 className="font-semibold text-primary">SHAP Feature Importance</h2>
              <p className="text-xs text-muted-foreground mt-0.5">Top drivers of this decision</p>
            </div>
            <div className="p-5 space-y-3">
              {shapValues.map((s) => {
                const abs = Math.abs(s.value);
                const color = s.direction === "fraud" ? "bg-accent" : "bg-primary";
                return (
                  <div key={s.feature}>
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="font-mono text-xs">{s.feature}</span>
                      <span className={`font-semibold text-xs ${s.direction === "fraud" ? "text-accent" : "text-primary"}`}>
                        {s.value > 0 ? "+" : ""}{s.value.toFixed(2)}
                      </span>
                    </div>
                    <div className="h-2 bg-muted rounded overflow-hidden">
                      <div className={`h-full ${color}`} style={{ width: `${abs * 200}%` }} />
                    </div>
                  </div>
                );
              })}
              <div className="pt-3 flex gap-4 text-xs">
                <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-accent" />Pushes toward fraud</span>
                <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-primary" />Pushes toward normal</span>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-5 border-b"><h2 className="font-semibold text-primary">Risk Score Breakdown</h2></div>
            <div className="p-5 grid grid-cols-3 gap-4">
              <Gauge label="ML Model" value={88} color="#1A237E" />
              <Gauge label="Graph" value={94} color="#FF6B00" />
              <Gauge label="Anomaly" value={76} color="#C62828" />
            </div>
          </Card>
        </div>

        <div className="lg:col-span-2 space-y-6">
          <Card>
            <div className="p-5 border-b flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-accent/10 flex items-center justify-center">
                <Bot className="h-4 w-4 text-accent" />
              </div>
              <h2 className="font-semibold text-primary">AI Fraud Explanation</h2>
            </div>
            <div className="p-5">
              <p className="text-sm text-foreground leading-relaxed">
                Transaction flagged as <strong>velocity attack</strong>. Sender opened UPI handle 3 days ago and has already
                initiated 3 high-value transfers, all to newly-created receivers with high in-degree in the account
                graph — consistent with layering. Receiver <code className="text-xs bg-muted px-1 py-0.5 rounded">shop9x@paytm</code> is
                linked to 2 confirmed mule accounts within 2 hops. Amount (₹2,45,000) exceeds sender's 30-day
                p95 by 8.2×.
              </p>
              <div className="mt-4 flex flex-wrap gap-1.5">
                <Badge variant="primary">rbi_guideline</Badge>
                <Badge variant="primary">velocity_attack</Badge>
                <Badge variant="primary">mule_chain_evidence</Badge>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-5 border-b"><h2 className="font-semibold text-primary">Disposition{readOnly && <span className="ml-2 text-xs font-normal text-muted-foreground">(read only)</span>}</h2></div>
            <div className="p-5 space-y-3">
              {readOnly ? (
                <p className="text-sm text-muted-foreground">Risk Manager view — case details are read only. Contact an Investigator to change disposition.</p>
              ) : (
                <>
                  <div className="grid grid-cols-3 gap-2">
                    <button onClick={() => submitDisposition("Confirmed Fraud")} className="text-xs py-2 rounded-md bg-danger text-danger-foreground font-medium hover:opacity-90">Confirm Fraud</button>
                    <button onClick={() => submitDisposition("False Positive")} className="text-xs py-2 rounded-md bg-success text-success-foreground font-medium hover:opacity-90">False Positive</button>
                    <button onClick={() => submitDisposition("Inconclusive")} className="text-xs py-2 rounded-md bg-warning text-warning-foreground font-medium hover:opacity-90">Inconclusive</button>
                  </div>
                  <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Analyst notes..."
                    rows={3}
                    className="w-full text-sm px-3 py-2 border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                  />
                  <button onClick={() => submitDisposition("Notes saved")} className="w-full bg-primary text-primary-foreground py-2 rounded-md text-sm font-medium hover:bg-primary/90">
                    Submit Disposition
                  </button>
                </>
              )}
            </div>
          </Card>

          <Card>
            <div className="p-5 border-b flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-accent" />
              <h2 className="font-semibold text-primary">Ask about this case</h2>
            </div>
            <div className="p-4 max-h-64 overflow-y-auto space-y-2">
              {messages.map((m, i) => (
                <div key={i} className={`text-sm p-2.5 rounded-lg ${m.role === "user" ? "bg-primary text-primary-foreground ml-8" : "bg-muted mr-8"}`}>
                  {m.text}
                </div>
              ))}
            </div>
            <div className="p-3 border-t flex gap-2">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && send()}
                placeholder="Ask about this case..."
                className="flex-1 text-sm px-3 py-2 border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <button onClick={send} className="bg-primary text-primary-foreground px-3 rounded-md">
                <Send className="h-4 w-4" />
              </button>
            </div>
          </Card>
        </div>
      </div>

      {toast && (
        <div className="fixed bottom-6 right-6 bg-foreground text-background px-4 py-3 rounded-lg shadow-lg text-sm font-medium">
          ✓ {toast}
        </div>
      )}
    </AppShell>
  );
}
