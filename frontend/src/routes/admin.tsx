import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { AppShell, Badge, Card } from "@/components/AppShell";
import { useEffect, useState } from "react";
import { getRole, ROLE_LABELS, type Role } from "@/lib/auth";
import { Plus, Trash2, Pencil, X } from "lucide-react";

export const Route = createFileRoute("/admin")({
  head: () => ({ meta: [{ title: "Admin — FraudShield" }] }),
  component: Admin,
});

type UserRow = {
  id: string;
  name: string;
  email: string;
  role: Role;
  status: "Active" | "Suspended";
  lastLogin: string;
};

const SEED: UserRow[] = [
  { id: "u1", name: "A. Sharma", email: "a.sharma@bank.co.in", role: "admin", status: "Active", lastLogin: "Today 09:14" },
  { id: "u2", name: "P. Iyer", email: "p.iyer@bank.co.in", role: "risk_manager", status: "Active", lastLogin: "Today 08:02" },
  { id: "u3", name: "R. Verma", email: "r.verma@bank.co.in", role: "fraud_analyst", status: "Active", lastLogin: "Yesterday 22:41" },
  { id: "u4", name: "S. Nair", email: "s.nair@bank.co.in", role: "investigator", status: "Active", lastLogin: "Yesterday 19:20" },
  { id: "u5", name: "K. Rao", email: "k.rao@bank.co.in", role: "fraud_analyst", status: "Suspended", lastLogin: "Jun 28, 14:11" },
];

function Admin() {
  const navigate = useNavigate();
  const [ready, setReady] = useState(false);
  const [users, setUsers] = useState<UserRow[]>(SEED);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", role: "fraud_analyst" as Role, password: "" });

  useEffect(() => {
    const r = getRole();
    if (r !== "admin") {
      navigate({ to: "/login" });
      return;
    }
    setReady(true);
  }, [navigate]);

  if (!ready) return null;

  const addUser = (e: React.FormEvent) => {
    e.preventDefault();
    setUsers((u) => [
      ...u,
      { id: `u${u.length + 1}`, name: form.name, email: form.email, role: form.role, status: "Active", lastLogin: "—" },
    ]);
    setForm({ name: "", email: "", role: "fraud_analyst", password: "" });
    setOpen(false);
  };

  return (
    <AppShell>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-primary">Admin Panel — User Management</h1>
          <p className="text-sm text-muted-foreground">Manage analyst accounts, roles, and access</p>
        </div>
        <button
          onClick={() => setOpen(true)}
          className="inline-flex items-center gap-2 bg-accent text-white px-4 py-2 rounded-lg text-sm font-medium hover:opacity-90"
        >
          <Plus className="h-4 w-4" /> Add Analyst
        </button>
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-muted/50 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-4 py-3 text-left">Name</th>
                <th className="px-4 py-3 text-left">Email</th>
                <th className="px-4 py-3 text-left">Role</th>
                <th className="px-4 py-3 text-left">Status</th>
                <th className="px-4 py-3 text-left">Last Login</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-muted/30">
                  <td className="px-4 py-3 font-medium">{u.name}</td>
                  <td className="px-4 py-3 text-muted-foreground">{u.email}</td>
                  <td className="px-4 py-3"><Badge variant="primary">{ROLE_LABELS[u.role]}</Badge></td>
                  <td className="px-4 py-3">
                    {u.status === "Active" ? (
                      <Badge variant="safe">● Active</Badge>
                    ) : (
                      <Badge variant="block">● Suspended</Badge>
                    )}
                  </td>
                  <td className="px-4 py-3 text-xs text-muted-foreground">{u.lastLogin}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-2">
                      <button className="p-1.5 rounded hover:bg-muted" title="Edit"><Pencil className="h-4 w-4 text-muted-foreground" /></button>
                      <button
                        onClick={() => setUsers((list) => list.filter((x) => x.id !== u.id))}
                        className="p-1.5 rounded hover:bg-muted"
                        title="Remove"
                      >
                        <Trash2 className="h-4 w-4 text-danger" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {open && (
        <div className="fixed inset-0 z-40 bg-black/40 flex items-center justify-center px-4">
          <div className="bg-card rounded-lg shadow-xl border w-full max-w-md">
            <div className="flex items-center justify-between px-5 py-4 border-b">
              <h2 className="font-semibold text-primary">Add Analyst</h2>
              <button onClick={() => setOpen(false)} className="p-1 rounded hover:bg-muted"><X className="h-4 w-4" /></button>
            </div>
            <form onSubmit={addUser} className="p-5 space-y-4">
              <div>
                <label className="text-xs font-medium">Name</label>
                <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="mt-1 w-full text-sm px-3 py-2 border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary" />
              </div>
              <div>
                <label className="text-xs font-medium">Email</label>
                <input required type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="mt-1 w-full text-sm px-3 py-2 border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary" />
              </div>
              <div>
                <label className="text-xs font-medium">Role</label>
                <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value as Role })} className="mt-1 w-full text-sm px-3 py-2 border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary">
                  <option value="fraud_analyst">Fraud Analyst</option>
                  <option value="investigator">Investigator</option>
                  <option value="risk_manager">Risk Manager</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-medium">Password</label>
                <input required type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} className="mt-1 w-full text-sm px-3 py-2 border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary" />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button type="button" onClick={() => setOpen(false)} className="px-4 py-2 text-sm rounded-md border hover:bg-muted">Cancel</button>
                <button type="submit" className="px-4 py-2 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90">Create User</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppShell>
  );
}
