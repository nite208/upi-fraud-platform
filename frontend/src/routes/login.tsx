import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { Shield, Mail, Lock } from "lucide-react";
import { useState } from "react";
import { setRole, ROLE_HOME, ROLE_LABELS, type Role } from "@/lib/auth";

export const Route = createFileRoute("/login")({ component: Login });

const ROLES: Role[] = ["fraud_analyst", "investigator", "risk_manager", "admin"];

function Login() {
  const navigate = useNavigate();
  const [role, setRoleLocal] = useState<Role>("fraud_analyst");

  return (
    <div className="min-h-screen bg-secondary flex items-center justify-center px-4 diagonal-pattern">
      <div className="w-full max-w-md">
        <Link to="/" className="flex flex-col items-center gap-3 mb-8">
          <div className="h-14 w-14 rounded-xl bg-primary flex items-center justify-center shadow-lg shadow-primary/30">
            <Shield className="h-8 w-8 text-primary-foreground" />
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-primary">FraudShield</div>
            <div className="text-xs text-muted-foreground">UPI Risk Intelligence Platform</div>
          </div>
        </Link>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            setRole(role);
            navigate({ to: ROLE_HOME[role] });
          }}
          className="bg-card rounded-lg border shadow-lg p-8"
        >
          <h1 className="text-xl font-semibold text-primary">Sign in to your workspace</h1>
          <p className="text-sm text-muted-foreground mt-1">Enterprise SSO or credentials</p>

          <div className="mt-6 space-y-4">
            <div>
              <label className="text-sm font-medium text-foreground">Email</label>
              <div className="mt-1 relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input type="email" required defaultValue="analyst@bank.co.in" className="w-full pl-9 pr-3 py-2 rounded-lg border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary" />
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-foreground">Password</label>
              <div className="mt-1 relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input type="password" required defaultValue="••••••••" className="w-full pl-9 pr-3 py-2 rounded-lg border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary" />
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-foreground">Role</label>
              <div className="mt-1 grid grid-cols-2 gap-2">
                {ROLES.map((r) => (
                  <button
                    type="button"
                    key={r}
                    onClick={() => setRoleLocal(r)}
                    className={`text-xs py-2 rounded-md border transition-colors ${role === r ? "bg-primary text-primary-foreground border-primary" : "bg-background hover:bg-muted"}`}
                  >
                    {ROLE_LABELS[r]}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <button type="submit" className="mt-6 w-full bg-primary text-primary-foreground py-2.5 rounded-lg font-medium hover:bg-primary/90">
            Sign In
          </button>
          <p className="mt-4 text-xs text-center text-muted-foreground">Protected by FraudShield • ISO 27001 certified</p>
        </form>
      </div>
    </div>
  );
}
