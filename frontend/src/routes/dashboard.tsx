import { createFileRoute, Link } from "@tanstack/react-router";
import { AppShell, Badge, Card } from "@/components/AppShell";
import { ShieldCheck, TrendingUp, AlertTriangle, ShieldAlert } from "lucide-react";
import { useEffect, useState } from "react";

// ── Types ─────────────────────────────────────────────────────────────────────
interface Summary {
  total_txns:   number;
  blocked:      number;
  reviews:      number;
  safe:         number;
  avg_score:    number;
  total_amount: number;
}

interface Transaction {
  txn_id:          string;
  sender_vpa:      string;
  amount:          number;
  decision:        string;
  composite_score: number;
  timestamp:       string;
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function formatINR(n: number) {
  return "₹" + n.toLocaleString("en-IN");
}

function maskVpa(vpa: string) {
  const [name, bank] = vpa.split("@");
  if (!bank) return vpa;
  const masked = name.slice(0, 2) + "*".repeat(Math.max(0, name.length - 2));
  return `${masked}@${bank}`;
}

function timeAgo(ts: string) {
  const diff = Date.now() - new Date(ts).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1)  return "just now";
  if (mins < 60) return `${mins}m ago`;
  return `${Math.floor(mins / 60)}h ago`;
}

// ── Fallback mock data (shown while API loads or if API is down) ───────────────
const MOCK_SUMMARY: Summary = {
  total_txns: 12158, blocked: 198, reviews: 850, safe: 11110,
  avg_score: 18.4, total_amount: 45600000
};

const MOCK_TRANSACTIONS: Transaction[] = [
  { txn_id: "TXN001", sender_vpa: "rahul123@okicici", amount: 245000, decision: "BLOCK",  composite_score: 92, timestamp: new Date(Date.now() - 900000).toISOString() },
  { txn_id: "TXN002", sender_vpa: "priya@ybl",        amount: 4500,   decision: "SAFE",   composite_score: 12, timestamp: new Date(Date.now() - 1320000).toISOString() },
  { txn_id: "TXN003", sender_vpa: "vikram@okaxis",    amount: 89000,  decision: "REVIEW", composite_score: 78, timestamp: new Date(Date.now() - 1860000).toISOString() },
  { txn_id: "TXN004", sender_vpa: "neha@okicici",     amount: 1200,   decision: "SAFE",   composite_score: 8,  timestamp: new Date(Date.now() - 2280000).toISOString() },
  { txn_id: "TXN005", sender_vpa: "sanjay@ybl",       amount: 55000,  decision: "REVIEW", composite_score: 65, timestamp: new Date(Date.now() - 3060000).toISOString() },
];

// ── Component ─────────────────────────────────────────────────────────────────
export const Route = createFileRoute("/dashboard")({
  head: () => ({ meta: [{ title: "Dashboard — FraudShield" }] }),
  component: Dashboard,
});

function Dashboard() {
  const [summary,      setSummary]      = useState<Summary>(MOCK_SUMMARY);
  const [transactions, setTransactions] = useState<Transaction[]>(MOCK_TRANSACTIONS);
  const [liveAlerts,   setLiveAlerts]   = useState<Transaction[]>([]);
  const [apiOnline,    setApiOnline]    = useState(false);
  const [loading,      setLoading]      = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        // Try to fetch real data from FastAPI
        const [sumRes, txnRes] = await Promise.all([
          fetch("/api/analytics/summary"),
          fetch("/api/v1/transactions?limit=10"),
        ]);

        if (sumRes.ok) {
          const sumData = await sumRes.json();
          setSummary(sumData);
          setApiOnline(true);
        }

        if (txnRes.ok) {
          const txnData = await txnRes.json();
          if (Array.isArray(txnData) && txnData.length > 0) {
            setTransactions(txnData);
            // Use BLOCK/REVIEW as live alerts
            setLiveAlerts(txnData.filter((t: Transaction) =>
              t.decision === "BLOCK" || t.decision === "REVIEW"
            ).slice(0, 4));
          }
        }
      } catch {
        // API offline — keep mock data
        setApiOnline(false);
        setLiveAlerts(MOCK_TRANSACTIONS.filter(t =>
          t.decision === "BLOCK" || t.decision === "REVIEW"
        ));
      } finally {
        setLoading(false);
      }
    };

    load();
    // Refresh every 30 seconds
    const interval = apiOnline ? setInterval(load, 30000) : null;
    return () => { if (interval) clearInterval(interval); };
  }, []);

  const kpis = [
    { label: "Total Transactions", value: summary.total_txns.toLocaleString("en-IN"), sub: "Today",           icon: TrendingUp,    color: "bg-primary text-primary-foreground" },
    { label: "Blocked",            value: summary.blocked.toLocaleString("en-IN"),    sub: "1.6% of volume",  icon: ShieldAlert,   color: "bg-danger text-danger-foreground" },
    { label: "Under Review",       value: summary.reviews.toLocaleString("en-IN"),    sub: "Awaiting analyst",icon: AlertTriangle, color: "bg-warning text-warning-foreground" },
    { label: "Safe",               value: summary.safe.toLocaleString("en-IN"),       sub: "Auto-approved",   icon: ShieldCheck,   color: "bg-success text-success-foreground" },
  ];

  const alertsToShow = liveAlerts.length > 0
    ? liveAlerts
    : MOCK_TRANSACTIONS.filter(t => t.decision !== "SAFE");

  return (
    <AppShell>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-primary">Operations Dashboard</h1>
          <p className="text-sm text-muted-foreground">
            Real-time UPI transaction monitoring · IST timezone
            {apiOnline && <span className="ml-2 text-success text-xs font-medium">● Live API</span>}
            {!apiOnline && !loading && <span className="ml-2 text-warning text-xs font-medium">● Demo mode</span>}
          </p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {kpis.map((k) => (
          <Card key={k.label} className="p-5">
            <div className="flex items-center justify-between">
              <div className={`h-10 w-10 rounded-lg flex items-center justify-center ${k.color}`}>
                <k.icon className="h-5 w-5" />
              </div>
              <span className="text-xs text-muted-foreground">{k.sub}</span>
            </div>
            <div className="mt-4 text-2xl font-bold text-foreground">{k.value}</div>
            <div className="text-sm text-muted-foreground">{k.label}</div>
          </Card>
        ))}
      </div>

      {/* Main content */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">

        {/* Recent Transactions */}
        <Card className="lg:col-span-3">
          <div className="p-5 border-b flex items-center justify-between">
            <h2 className="font-semibold text-primary">Recent Transactions</h2>
            <Link to="/cases" className="text-xs text-primary hover:underline">
              View all cases →
            </Link>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-muted/50 text-xs text-muted-foreground uppercase tracking-wider">
                <tr>
                  <th className="text-left px-5 py-3 font-medium">Txn ID</th>
                  <th className="text-left px-5 py-3 font-medium">Sender</th>
                  <th className="text-right px-5 py-3 font-medium">Amount</th>
                  <th className="text-right px-5 py-3 font-medium">Score</th>
                  <th className="text-center px-5 py-3 font-medium">Decision</th>
                  <th className="text-right px-5 py-3 font-medium">Time</th>
                </tr>
              </thead>
              <tbody>
                {transactions.slice(0, 8).map((t) => (
                  <tr key={t.txn_id} className="border-t hover:bg-muted/40 cursor-pointer transition-colors">
                    <td className="px-5 py-3 font-mono text-xs text-muted-foreground">
                      {t.txn_id.slice(0, 12)}...
                    </td>
                    <td className="px-5 py-3 font-mono text-xs">{maskVpa(t.sender_vpa)}</td>
                    <td className="px-5 py-3 text-right font-medium">{formatINR(t.amount)}</td>
                    <td className="px-5 py-3 text-right font-semibold">
                      {Math.round(t.composite_score)}/100
                    </td>
                    <td className="px-5 py-3 text-center">
                      <Badge variant={
                        t.decision === "SAFE"   ? "safe"   :
                        t.decision === "REVIEW" ? "review" : "block"
                      }>
                        {t.decision}
                      </Badge>
                    </td>
                    <td className="px-5 py-3 text-right text-xs text-muted-foreground">
                      {timeAgo(t.timestamp)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Live Fraud Alerts */}
        <Card className="lg:col-span-2">
          <div className="p-5 border-b flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-danger animate-pulse" />
            <h2 className="font-semibold text-primary">Live Fraud Alerts</h2>
            <span className="ml-auto text-xs text-muted-foreground">
              {alertsToShow.length} active
            </span>
          </div>
          <div className="p-3 space-y-2 max-h-[440px] overflow-y-auto">
            {alertsToShow.map((a, i) => (
              <div
                key={i}
                className={`p-3 rounded-lg border-l-4 bg-muted/30 hover:bg-muted transition-colors ${
                  a.decision === "BLOCK" ? "border-danger" : "border-warning"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${
                        a.decision === "BLOCK"
                          ? "bg-danger text-danger-foreground"
                          : "bg-warning text-warning-foreground"
                      }`}>
                        {Math.round(a.composite_score)}
                      </span>
                      <span className="text-sm font-mono truncate">
                        {maskVpa(a.sender_vpa)}
                      </span>
                    </div>
                    <div className="mt-1 text-sm font-semibold">{formatINR(a.amount)}</div>
                  </div>
                  <div className="text-right shrink-0 ml-2">
                    <Badge variant={a.decision === "BLOCK" ? "block" : "review"}>
                      {a.decision}
                    </Badge>
                    <div className="text-[10px] text-muted-foreground mt-1">
                      {timeAgo(a.timestamp)}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </AppShell>
  );
}