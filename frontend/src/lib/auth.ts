export type Role = "admin" | "risk_manager" | "fraud_analyst" | "investigator";

export const ROLE_LABELS: Record<Role, string> = {
  admin: "Admin",
  risk_manager: "Risk Manager",
  fraud_analyst: "Fraud Analyst",
  investigator: "Investigator",
};

export const ROLE_HOME: Record<Role, string> = {
  admin: "/admin",
  risk_manager: "/analytics",
  fraud_analyst: "/dashboard",
  investigator: "/graph",
};

export function getRole(): Role | null {
  if (typeof window === "undefined") return null;
  const r = window.localStorage.getItem("fs_role");
  if (r && ["admin", "risk_manager", "fraud_analyst", "investigator"].includes(r)) {
    return r as Role;
  }
  return null;
}

export function setRole(role: Role) {
  window.localStorage.setItem("fs_role", role);
}

export function clearRole() {
  window.localStorage.removeItem("fs_role");
}
