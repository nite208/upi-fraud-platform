import { Link, useRouterState, useNavigate } from "@tanstack/react-router";
import { Shield, LayoutDashboard, FolderOpen, Network, BarChart3, MessageSquare, Settings, Bell, User, UserCog, KeyRound, LogOut, ShieldCheck, X } from "lucide-react";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { getRole, clearRole, ROLE_LABELS, type Role } from "@/lib/auth";

const ALL_NAV = [
  { to: "/dashboard",  label: "Dashboard",  icon: LayoutDashboard },
  { to: "/cases",      label: "Cases",      icon: FolderOpen },
  { to: "/graph",      label: "Graph",      icon: Network },
  { to: "/analytics",  label: "Analytics",  icon: BarChart3 },
  { to: "/investigate",label: "Investigate",icon: MessageSquare },
  { to: "/admin",      label: "Admin",      icon: ShieldCheck },
  { to: "/settings",   label: "Settings",   icon: Settings },
] as const;

const ROLE_NAV: Record<Role, string[]> = {
  admin:         ["/dashboard", "/cases", "/graph", "/analytics", "/investigate", "/admin", "/settings"],
  risk_manager:  ["/dashboard", "/analytics", "/settings"],
  fraud_analyst: ["/dashboard", "/cases", "/investigate"],
  investigator:  ["/dashboard", "/cases", "/graph", "/investigate"],
};

// ── Profile Modal ─────────────────────────────────────────────────────────────
function ProfileModal({ onClose }: { onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-card rounded-xl shadow-xl w-full max-w-md p-6 border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-primary">My Profile</h2>
          <button onClick={onClose} className="p-1 rounded hover:bg-muted">
            <X className="h-5 w-5 text-muted-foreground" />
          </button>
        </div>
        <div className="flex items-center gap-4 mb-6">
          <div className="h-16 w-16 rounded-full bg-secondary flex items-center justify-center">
            <User className="h-8 w-8 text-primary" />
          </div>
          <div>
            <div className="font-semibold text-base">A. Sharma</div>
            <div className="text-sm text-muted-foreground">a.sharma@bank.co.in</div>
            <div className="text-xs text-muted-foreground mt-0.5">Fraud Analyst · ICICI Bank</div>
          </div>
        </div>
        <div className="space-y-3">
          <div>
            <label className="text-xs text-muted-foreground font-medium">Full Name</label>
            <input defaultValue="A. Sharma" className="w-full mt-1 px-3 py-2 border rounded-lg text-sm bg-background" />
          </div>
          <div>
            <label className="text-xs text-muted-foreground font-medium">Email</label>
            <input defaultValue="a.sharma@bank.co.in" className="w-full mt-1 px-3 py-2 border rounded-lg text-sm bg-background" />
          </div>
          <div>
            <label className="text-xs text-muted-foreground font-medium">Department</label>
            <input defaultValue="Fraud Risk Management" className="w-full mt-1 px-3 py-2 border rounded-lg text-sm bg-background" />
          </div>
        </div>
        <div className="flex justify-end gap-2 mt-6">
          <button onClick={onClose} className="px-4 py-2 text-sm border rounded-lg hover:bg-muted">Cancel</button>
          <button onClick={onClose} className="px-4 py-2 text-sm bg-primary text-primary-foreground rounded-lg hover:opacity-90">Save Changes</button>
        </div>
      </div>
    </div>
  );
}

// ── Password Modal ────────────────────────────────────────────────────────────
function PasswordModal({ onClose }: { onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-card rounded-xl shadow-xl w-full max-w-md p-6 border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-primary">Change Password</h2>
          <button onClick={onClose} className="p-1 rounded hover:bg-muted">
            <X className="h-5 w-5 text-muted-foreground" />
          </button>
        </div>
        <div className="space-y-3">
          <div>
            <label className="text-xs text-muted-foreground font-medium">Current Password</label>
            <input type="password" placeholder="••••••••" className="w-full mt-1 px-3 py-2 border rounded-lg text-sm bg-background" />
          </div>
          <div>
            <label className="text-xs text-muted-foreground font-medium">New Password</label>
            <input type="password" placeholder="••••••••" className="w-full mt-1 px-3 py-2 border rounded-lg text-sm bg-background" />
          </div>
          <div>
            <label className="text-xs text-muted-foreground font-medium">Confirm New Password</label>
            <input type="password" placeholder="••••••••" className="w-full mt-1 px-3 py-2 border rounded-lg text-sm bg-background" />
          </div>
        </div>
        <p className="text-xs text-muted-foreground mt-3">Password must be at least 8 characters with one uppercase and one number.</p>
        <div className="flex justify-end gap-2 mt-6">
          <button onClick={onClose} className="px-4 py-2 text-sm border rounded-lg hover:bg-muted">Cancel</button>
          <button onClick={onClose} className="px-4 py-2 text-sm bg-primary text-primary-foreground rounded-lg hover:opacity-90">Update Password</button>
        </div>
      </div>
    </div>
  );
}

// ── Main AppShell ─────────────────────────────────────────────────────────────
export function AppShell({ children }: { children: ReactNode }) {
  const pathname  = useRouterState({ select: (s) => s.location.pathname });
  const navigate  = useNavigate();
  const [role, setRoleState]         = useState<Role | null>(null);
  const [menuOpen, setMenuOpen]      = useState(false);
  const [showProfile, setShowProfile]   = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => { setRoleState(getRole()); }, []);

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setMenuOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  const allowed  = role ? ROLE_NAV[role] : ROLE_NAV.fraud_analyst;
  const nav      = ALL_NAV.filter((n) => allowed.includes(n.to));
  const roleLabel = role ? ROLE_LABELS[role] : "Fraud Analyst";

  const logout = () => { clearRole(); navigate({ to: "/login" }); };

  return (
    <div className="min-h-screen bg-background">
      {/* Modals */}
      {showProfile  && <ProfileModal  onClose={() => setShowProfile(false)}  />}
      {showPassword && <PasswordModal onClose={() => setShowPassword(false)} />}

      {/* Header */}
      <header className="h-14 border-b bg-card flex items-center justify-between px-6 sticky top-0 z-20">
        <Link to="/dashboard" className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
            <Shield className="h-5 w-5 text-primary-foreground" />
          </div>
          <span className="font-semibold text-primary tracking-tight">FraudShield</span>
          <span className="text-xs text-muted-foreground ml-1 hidden sm:inline">UPI Risk Intelligence</span>
        </Link>
        <div className="flex items-center gap-4">
          <button className="relative p-2 rounded-md hover:bg-muted">
            <Bell className="h-5 w-5 text-muted-foreground" />
            <span className="absolute top-1 right-1 h-2 w-2 bg-accent rounded-full" />
          </button>
          <div className="relative" ref={menuRef}>
            <button
              onClick={() => setMenuOpen((o) => !o)}
              className="flex items-center gap-2 rounded-md hover:bg-muted px-2 py-1"
            >
              <div className="h-8 w-8 rounded-full bg-secondary flex items-center justify-center">
                <User className="h-4 w-4 text-primary" />
              </div>
              <div className="hidden sm:block text-sm text-left">
                <div className="font-medium leading-tight">A. Sharma</div>
                <div className="text-xs text-muted-foreground leading-tight">{roleLabel}</div>
              </div>
            </button>
            {menuOpen && (
              <div className="absolute right-0 top-11 w-52 bg-card border rounded-lg shadow-lg py-1 z-30">
                <button
                  onClick={() => { setMenuOpen(false); setShowProfile(true); }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-muted text-left"
                >
                  <UserCog className="h-4 w-4 text-muted-foreground" /> My Profile
                </button>
                <button
                  onClick={() => { setMenuOpen(false); setShowPassword(true); }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-muted text-left"
                >
                  <KeyRound className="h-4 w-4 text-muted-foreground" /> Change Password
                </button>
                <div className="my-1 border-t" />
                <button
                  onClick={logout}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-muted text-left text-red-600"
                >
                  <LogOut className="h-4 w-4" /> Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Body */}
      <div className="flex">
        <aside className="w-56 border-r bg-sidebar min-h-[calc(100vh-3.5rem)] p-3 sticky top-14 self-start">
          <nav className="space-y-1">
            {nav.map((item) => {
              const active = pathname === item.to ||
                (item.to !== "/dashboard" && pathname.startsWith(item.to));
              const Icon = item.icon;
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                    active
                      ? "bg-sidebar-active text-primary font-medium"
                      : "text-sidebar-foreground hover:bg-sidebar-hover"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </aside>
        <main className="flex-1 p-6 min-w-0">{children}</main>
      </div>
    </div>
  );
}

export function Badge({ children, variant = "default" }: {
  children: ReactNode;
  variant?: "safe" | "review" | "block" | "default" | "primary"
}) {
  const styles = {
    safe:    "bg-success/10 text-success border-success/20",
    review:  "bg-warning/10 text-warning border-warning/20",
    block:   "bg-danger/10 text-danger border-danger/20",
    primary: "bg-secondary text-primary border-primary/20",
    default: "bg-muted text-muted-foreground border-border",
  }[variant];
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${styles}`}>
      {children}
    </span>
  );
}

export function Card({ children, className = "" }: {
  children: ReactNode;
  className?: string
}) {
  return <div className={`bg-card rounded-lg border shadow-sm ${className}`}>{children}</div>;
}