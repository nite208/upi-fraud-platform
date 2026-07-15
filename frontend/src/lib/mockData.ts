export type Decision = "SAFE" | "REVIEW" | "BLOCK";
export type CaseStatus = "Open" | "In Progress" | "Closed";

export interface Transaction {
  id: string;
  sender: string;
  receiver: string;
  amount: number;
  score: number;
  decision: Decision;
  time: string;
  hour: number;
  isNewReceiver: boolean;
  senderTxnCount: number;
  receiverCount: number;
}

export interface Case {
  id: string;
  txnId: string;
  score: number;
  status: CaseStatus;
  analyst: string;
  slaMinutes: number;
  fraudType: string;
}

export const formatINR = (n: number) =>
  "₹" + n.toLocaleString("en-IN");

export const maskVpa = (vpa: string) => {
  const [name, handle] = vpa.split("@");
  if (!handle) return vpa;
  return name.slice(0, 3) + "***@" + handle;
};

export const transactions: Transaction[] = [
  { id: "TXN20250703001", sender: "rahul123@okicici", receiver: "shop9x@paytm", amount: 245000, score: 92, decision: "BLOCK", time: "10:42 IST", hour: 10, isNewReceiver: true, senderTxnCount: 3, receiverCount: 47 },
  { id: "TXN20250703002", sender: "priya@ybl", receiver: "amit.k@okhdfcbank", amount: 4500, score: 12, decision: "SAFE", time: "10:38 IST", hour: 10, isNewReceiver: false, senderTxnCount: 128, receiverCount: 12 },
  { id: "TXN20250703003", sender: "vikas.m@okaxis", receiver: "cash4u@ybl", amount: 89000, score: 78, decision: "REVIEW", time: "10:31 IST", hour: 10, isNewReceiver: true, senderTxnCount: 8, receiverCount: 63 },
  { id: "TXN20250703004", sender: "neha22@okicici", receiver: "grocery@paytm", amount: 1200, score: 8, decision: "SAFE", time: "10:22 IST", hour: 10, isNewReceiver: false, senderTxnCount: 210, receiverCount: 5 },
  { id: "TXN20250703005", sender: "sanjay@ybl", receiver: "quickpay@okaxis", amount: 55000, score: 65, decision: "REVIEW", time: "10:15 IST", hour: 10, isNewReceiver: true, senderTxnCount: 14, receiverCount: 29 },
];

export const cases: Case[] = [
  { id: "CASE-2451", txnId: "TXN20250703001", score: 92, status: "Open", analyst: "A. Sharma", slaMinutes: 18, fraudType: "velocity_attack" },
  { id: "CASE-2450", txnId: "TXN20250703003", score: 78, status: "In Progress", analyst: "R. Iyer", slaMinutes: 124, fraudType: "mule_chain" },
  { id: "CASE-2449", txnId: "TXN20250703005", score: 65, status: "Open", analyst: "M. Khan", slaMinutes: 45, fraudType: "large_unusual" },
  { id: "CASE-2448", txnId: "—", score: 42, status: "Closed", analyst: "S. Patel", slaMinutes: 0, fraudType: "account_takeover" },
];

export const shapValues = [
  { feature: "is_new_receiver", value: 0.34, direction: "fraud" },
  { feature: "amount", value: 0.28, direction: "fraud" },
  { feature: "sender_txn_count", value: -0.19, direction: "normal" },
  { feature: "hour", value: 0.15, direction: "fraud" },
  { feature: "receiver_count", value: 0.12, direction: "fraud" },
];

export const scoreDistribution = [
  { bucket: "0-10", count: 4820, decision: "SAFE" },
  { bucket: "10-20", count: 3120, decision: "SAFE" },
  { bucket: "20-30", count: 1840, decision: "SAFE" },
  { bucket: "30-40", count: 920, decision: "SAFE" },
  { bucket: "40-50", count: 410, decision: "REVIEW" },
  { bucket: "50-60", count: 260, decision: "REVIEW" },
  { bucket: "60-70", count: 180, decision: "REVIEW" },
  { bucket: "70-80", count: 95, decision: "BLOCK" },
  { bucket: "80-90", count: 62, decision: "BLOCK" },
  { bucket: "90-100", count: 41, decision: "BLOCK" },
];

export const decisionBreakdown = [
  { name: "SAFE", value: 11110, color: "#2E7D32" },
  { name: "REVIEW", value: 850, color: "#F57F17" },
  { name: "BLOCK", value: 198, color: "#C62828" },
];

export const fraudTypeDist = [
  { type: "velocity_attack", count: 84, color: "#C62828" },
  { type: "account_takeover", count: 51, color: "#FF6B00" },
  { type: "mule_chain", count: 38, color: "#1A237E" },
  { type: "large_unusual", count: 25, color: "#F57F17" },
];

export const muleAccounts = [
  { vpa: "cash4u@ybl", score: 94, inDeg: 32, outDeg: 4 },
  { vpa: "quickpay@okaxis", score: 87, inDeg: 28, outDeg: 6 },
  { vpa: "shop9x@paytm", score: 81, inDeg: 47, outDeg: 9 },
  { vpa: "fastmoney@ybl", score: 76, inDeg: 21, outDeg: 3 },
];
