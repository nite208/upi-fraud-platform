import { createFileRoute, Link } from "@tanstack/react-router";
import { Shield, Zap, Network, Brain, ArrowRight, Inbox, Bell, CheckCircle2 } from "lucide-react";

export const Route = createFileRoute("/")({ component: Landing });

function Landing() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-9 w-9 rounded-lg bg-primary flex items-center justify-center">
              <Shield className="h-5 w-5 text-primary-foreground" />
            </div>
            <div>
              <div className="font-bold text-primary tracking-tight leading-tight">FraudShield</div>
              <div className="text-[10px] text-muted-foreground leading-tight">UPI Risk Intelligence</div>
            </div>
          </div>
          <Link to="/login" className="bg-primary text-primary-foreground px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90">
            Access Platform
          </Link>
        </div>
      </header>

      <section className="diagonal-pattern">
        <div className="max-w-7xl mx-auto px-6 py-24 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-secondary text-primary text-xs font-medium mb-8 border border-primary/10">
            <span className="h-2 w-2 rounded-full bg-accent pulse-dot" />
            Live • Processing 12,158 UPI transactions today
          </div>
          <div className="mx-auto mb-8 h-24 w-24 rounded-2xl bg-primary flex items-center justify-center shadow-xl shadow-primary/20 rotate-3 hover:rotate-0 transition-transform">
            <Shield className="h-14 w-14 text-primary-foreground" />
          </div>
          <h1 className="text-5xl md:text-6xl font-extrabold text-primary tracking-tight max-w-4xl mx-auto leading-tight">
            India's Most Advanced UPI Fraud Intelligence Platform
          </h1>
          <p className="mt-6 text-lg text-muted-foreground max-w-2xl mx-auto">
            Real-time transaction scoring, graph-based mule detection, and LLM-assisted investigation for India's leading banks.
          </p>
          <div className="mt-10 flex items-center justify-center gap-4">
            <Link to="/login" className="inline-flex items-center gap-2 bg-primary text-primary-foreground px-6 py-3 rounded-lg font-medium hover:bg-primary/90 shadow-lg shadow-primary/20">
              Access Platform <ArrowRight className="h-4 w-4" />
            </Link>
            <a href="#features" className="text-primary font-medium px-6 py-3 hover:underline">Learn more</a>
          </div>

          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-4 max-w-3xl mx-auto">
            {[
              { v: "₹2.3Cr", l: "Fraud Prevented Monthly" },
              { v: "99.2%", l: "Detection Accuracy" },
              { v: "< 150ms", l: "Real-time Scoring" },
            ].map((s) => (
              <div key={s.l} className="bg-card border rounded-lg p-6 shadow-sm">
                <div className="text-3xl font-bold text-primary">{s.v}</div>
                <div className="text-sm text-muted-foreground mt-1">{s.l}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="how" className="max-w-7xl mx-auto px-6 py-24">
        <div className="text-center mb-14">
          <div className="text-xs font-semibold text-accent uppercase tracking-wider">How it works</div>
          <h2 className="text-3xl font-bold text-primary mt-2">From transaction to resolved case</h2>
        </div>
        <div className="grid md:grid-cols-4 gap-6">
          {[
            { icon: Inbox, title: "Transaction Ingested", desc: "Every UPI event streams into FraudShield in real time from the NPCI switch." },
            { icon: Brain, title: "AI Scores in <150ms", desc: "XGBoost + Graph Neural Network ensemble emit a calibrated risk score." },
            { icon: Bell, title: "Alert Fires to Analyst", desc: "High-risk events open a case with SHAP evidence and mule-chain context." },
            { icon: CheckCircle2, title: "Case Resolved", desc: "Analyst confirms, files SAR, and feedback retrains the model overnight." },
          ].map((s, i) => (
            <div key={s.title} className="bg-card border rounded-lg shadow-sm overflow-hidden">
              <div className="bg-primary text-primary-foreground px-5 py-3 flex items-center gap-2">
                <s.icon className="h-5 w-5" />
                <div className="font-semibold text-sm">Step {i + 1}</div>
              </div>
              <div className="p-5">
                <h3 className="font-semibold text-primary">{s.title}</h3>
                <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{s.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section id="features" className="max-w-7xl mx-auto px-6 pb-24">
        <div className="text-center mb-14">
          <div className="text-xs font-semibold text-accent uppercase tracking-wider">Platform capabilities</div>
          <h2 className="text-3xl font-bold text-primary mt-2">Built for the scale of Indian UPI</h2>
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            { icon: Zap, title: "Real-time Detection", desc: "Sub-150ms XGBoost + Random Forest ensemble scoring on every UPI transaction, with adaptive thresholds per corridor.", color: "text-accent bg-accent/10" },
            { icon: Network, title: "Graph Intelligence", desc: "GNN-powered mule account detection surfacing fraud rings, layering patterns and money-laundering chains.", color: "text-primary bg-secondary" },
            { icon: Brain, title: "AI Investigation", desc: "Llama 3.1 grounded on RBI guidelines and internal SOPs — explanations, SAR drafts, and case notes on demand.", color: "text-success bg-success/10" },
          ].map((f) => (
            <div key={f.title} className="bg-card border rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className={`h-12 w-12 rounded-lg flex items-center justify-center ${f.color}`}>
                <f.icon className="h-6 w-6" />
              </div>
              <h3 className="mt-4 font-semibold text-primary text-lg">{f.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="border-t bg-card">
        <div className="max-w-7xl mx-auto px-6 py-8 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <Shield className="h-4 w-4 text-primary" />
            <span>© 2026 FraudShield</span>
          </div>
          <div>Powered by XGBoost + Graph Neural Networks</div>
        </div>
      </footer>
    </div>
  );
}
