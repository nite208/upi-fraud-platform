import { createFileRoute } from "@tanstack/react-router";
import { AppShell, Badge, Card } from "@/components/AppShell";
import { Bot, Send, FileText, User } from "lucide-react";
import { useState } from "react";
import { formatINR, maskVpa } from "@/lib/mockData";

export const Route = createFileRoute("/investigate")({
  head: () => ({ meta: [{ title: "Investigate — FraudShield" }] }),
  component: Investigate,
});

type Msg = { role: "user" | "ai"; text: string; time: string };

function nowIST() {
  const d = new Date();
  const hh = String(d.getHours()).padStart(2, "0");
  const mm = String(d.getMinutes()).padStart(2, "0");
  return `${hh}:${mm} IST`;
}

const RESPONSES = [
  "Based on the retrieved knowledge sources, this transaction pattern aligns with RBI's velocity-attack typology (KB doc `rbi_guideline_2021`). The sender's account age (3 days) combined with amount escalation is a strong indicator. Want me to attach the evidence pack to the case?",
  "I searched the last 24h of alerts and found 3 similar cases sharing the same receiver bank + hour-of-day signature. Two are already confirmed as mule activity in RING-014. Should I link them?",
  "Top SHAP drivers here: `receiver_age_days` (0.31), `sender_p95_ratio` (0.24), and `graph_mule_hops` (0.19). The GNN embedding for this receiver sits in the 97th percentile of the fraud cluster. Shall I draft a SAR under RBI Master Direction §4.3?",
];

const initial: Msg[] = [
  { role: "user", text: "Explain transaction TXN20250703001 in plain language.", time: "10:42 IST" },
  { role: "ai", text: "**TXN20250703001** was blocked because it matches a classic velocity attack pattern:\n\n1. Sender opened UPI handle 3 days ago (`sender_txn_count=3`, unusually low)\n2. Amount ₹2,45,000 is 8.2× the sender's 30-day p95\n3. Receiver `shop9x@paytm` is 1 hop from 2 confirmed mule accounts\n4. Hour of day (10:42 IST) coincides with active layering window observed in RING-014\n\nRecommend confirming as fraud and filing SAR under RBI Master Direction on Digital Payment Security 2021, Section 4.3.", time: "10:42 IST" },
];

const prompts = ["Explain this transaction", "Show similar cases", "Generate SAR draft", "Which features drove the decision?"];

function Investigate() {
  const [messages, setMessages] = useState<Msg[]>(initial);
  const [input, setInput] = useState("");
  const [turn, setTurn] = useState(0);
  const [thinking, setThinking] = useState(false);

  const send = (text?: string) => {
    const t = (text ?? input).trim();
    if (!t || thinking) return;
    const userMsg: Msg = { role: "user", text: t, time: nowIST() };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setThinking(true);
    const reply = RESPONSES[turn % RESPONSES.length];
    setTurn((n) => n + 1);
    setTimeout(() => {
      setMessages((m) => [...m, { role: "ai", text: reply, time: nowIST() }]);
      setThinking(false);
    }, 900);
  };

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-primary flex items-center gap-3">
          <Bot className="h-7 w-7 text-accent" />
          AI Investigation Assistant
        </h1>
        <p className="text-sm text-muted-foreground">Powered by Llama 3.1 8B via Groq · Grounded on internal SOPs and RBI guidelines</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-10 gap-6">
        <Card className="lg:col-span-7 flex flex-col" >
          <div className="flex-1 p-5 space-y-4 overflow-y-auto" style={{ minHeight: 500, maxHeight: 600 }}>
            {messages.map((m, i) => (
              <div key={i} className={`flex gap-3 ${m.role === "user" ? "flex-row-reverse" : ""}`}>
                <div className={`h-8 w-8 shrink-0 rounded-full flex items-center justify-center ${m.role === "user" ? "bg-primary text-primary-foreground" : "bg-accent/10 text-accent"}`}>
                  {m.role === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                </div>
                <div className={`max-w-[80%] ${m.role === "user" ? "text-right" : ""}`}>
                  <div className={`rounded-lg px-4 py-3 text-sm whitespace-pre-line ${m.role === "user" ? "bg-primary text-primary-foreground" : "bg-card border"}`}>
                    {m.text}
                  </div>
                  <div className="text-[10px] text-muted-foreground mt-1 px-1">{m.time}</div>
                </div>
              </div>
            ))}
            {thinking && (
              <div className="flex gap-3">
                <div className="h-8 w-8 shrink-0 rounded-full flex items-center justify-center bg-accent/10 text-accent">
                  <Bot className="h-4 w-4" />
                </div>
                <div className="rounded-lg px-4 py-3 text-sm bg-card border inline-flex items-center gap-2">
                  <span className="text-muted-foreground">Thinking</span>
                  <span className="inline-flex gap-1">
                    <span className="h-1.5 w-1.5 rounded-full bg-accent animate-bounce" style={{ animationDelay: "0ms" }} />
                    <span className="h-1.5 w-1.5 rounded-full bg-accent animate-bounce" style={{ animationDelay: "150ms" }} />
                    <span className="h-1.5 w-1.5 rounded-full bg-accent animate-bounce" style={{ animationDelay: "300ms" }} />
                  </span>
                </div>
              </div>
            )}
          </div>

          <div className="border-t p-4">
            <div className="flex flex-wrap gap-2 mb-3">
              {prompts.map((p) => (
                <button key={p} onClick={() => send(p)} className="text-xs px-3 py-1.5 rounded-full border bg-background hover:bg-muted text-foreground">
                  {p}
                </button>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && send()}
                placeholder="Ask about a transaction or fraud pattern..."
                className="flex-1 text-sm px-4 py-2.5 border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <button onClick={() => send()} disabled={thinking} className="bg-primary text-primary-foreground px-4 rounded-lg flex items-center gap-2 text-sm font-medium hover:bg-primary/90 disabled:opacity-60">
                <Send className="h-4 w-4" /> Send
              </button>
            </div>
          </div>
        </Card>

        <div className="lg:col-span-3 space-y-6">
          <Card>
            <div className="p-4 border-b"><h2 className="font-semibold text-primary text-sm">Transaction Context</h2></div>
            <div className="p-4 space-y-2 text-sm">
              {[
                ["Txn ID", "TXN20250703001"],
                ["Sender", maskVpa("rahul123@okicici")],
                ["Receiver", maskVpa("shop9x@paytm")],
                ["Amount", formatINR(245000)],
                ["Score", "92/100"],
                ["Decision", <Badge variant="block">BLOCK</Badge>],
              ].map(([k, v], i) => (
                <div key={i} className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">{k}</span>
                  <span className="font-medium">{v}</span>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <div className="p-4 border-b">
              <h2 className="font-semibold text-primary text-sm">Knowledge Sources</h2>
              <p className="text-[11px] text-muted-foreground mt-0.5">Retrieved from ChromaDB · 4 docs</p>
            </div>
            <div className="divide-y">
              {[
                { title: "RBI Master Direction 2021", tag: "regulation", score: 0.94 },
                { title: "Velocity Attack Typology", tag: "sop", score: 0.91 },
                { title: "Mule Chain Detection Playbook", tag: "playbook", score: 0.87 },
                { title: "SAR Filing Template v3", tag: "template", score: 0.82 },
              ].map((d) => (
                <div key={d.title} className="p-3 hover:bg-muted/40 cursor-pointer">
                  <div className="flex items-start gap-2">
                    <FileText className="h-4 w-4 text-muted-foreground shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <div className="text-xs font-medium truncate">{d.title}</div>
                      <div className="mt-1 flex items-center gap-2">
                        <Badge variant="primary">{d.tag}</Badge>
                        <span className="text-[10px] text-muted-foreground">score {d.score}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
