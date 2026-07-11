"""
seed_demo.py — Seeds FraudShield with 10 realistic demo transactions.

Covers all 3 decision outcomes (SAFE / REVIEW / BLOCK) plus the 4 fraud
scenarios described in the PRD: mule-chain forwarding, SIM-swap style
device/IP change, OTP-hijack pattern, and a velocity burst attack — so an
interviewer sees the full range of the platform's behaviour in one run.

Usage:
    python scripts/seed_demo.py
    python scripts/seed_demo.py --api http://localhost:8000
"""
import argparse
import random
import sys
import time
import uuid
from datetime import datetime, timezone

import httpx

try:
    import redis
except ImportError:
    redis = None


API_BASE_DEFAULT = "http://localhost:8000/api/v1"
REDIS_URL_DEFAULT = "redis://localhost:6379/0"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_txn_id() -> str:
    return str(uuid.uuid4())


def base_txn(**overrides) -> dict:
    txn = {
        "txn_id": new_txn_id(),
        "sender_vpa": "rahul.sharma@okaxis",
        "receiver_vpa": "amit.traders@ybl",
        "amount": 500.0,
        "timestamp": now_iso(),
        "device_id": "device-" + uuid.uuid4().hex[:10],
        "ip_address": f"49.36.{random.randint(1,254)}.{random.randint(1,254)}",
        "gps_lat": 19.0760,
        "gps_lng": 72.8777,
        "upi_app": "PhonePe",
        "merchant_code": None,
        "remarks": "",
    }
    txn.update(overrides)
    return txn


# ── The 10 demo scenarios ─────────────────────────────────────────────────────
def build_scenarios() -> list[dict]:
    scenarios = []

    # 1. SAFE — everyday small grocery payment
    scenarios.append({
        "label": "Everyday grocery payment (expect SAFE)",
        "txn": base_txn(
            sender_vpa="priya.iyer@okhdfcbank",
            receiver_vpa="dmart.store123@ybl",
            amount=842.0,
            merchant_code="5411",
            upi_app="GPay",
        ),
    })

    # 2. SAFE — regular monthly rent payment to a known receiver
    scenarios.append({
        "label": "Recurring rent payment (expect SAFE)",
        "txn": base_txn(
            sender_vpa="ananya.reddy@oksbi",
            receiver_vpa="landlord.vk@ybl",
            amount=18000.0,
            upi_app="BHIM",
        ),
    })

    # 3. REVIEW — new receiver + slightly odd hour + round amount
    scenarios.append({
        "label": "New receiver, round amount, late night (expect REVIEW)",
        "txn": base_txn(
            sender_vpa="karan.mehta@okicici",
            receiver_vpa="unknownvpa9931@ybl",
            amount=25000.0,
            gps_lat=28.6139, gps_lng=77.2090,
        ),
    })

    # 4. REVIEW — merchant category the user has no history with
    scenarios.append({
        "label": "First-time high-value merchant category (expect REVIEW)",
        "txn": base_txn(
            sender_vpa="sneha.kapoor@okaxis",
            receiver_vpa="crypto.exchange.xyz@ybl",
            amount=45000.0,
            merchant_code="6051",
        ),
    })

    # 5. BLOCK — impossible travel: same sender, two cities, minutes apart
    fast_travel_sender = "vikram.singh@okhdfcbank"
    scenarios.append({
        "label": "Impossible travel — Mumbai txn (expect SAFE/REVIEW)",
        "txn": base_txn(
            sender_vpa=fast_travel_sender,
            receiver_vpa="cafe.local@ybl",
            amount=350.0,
            gps_lat=19.0760, gps_lng=72.8777,
        ),
    })
    scenarios.append({
        "label": "Impossible travel — Delhi txn 2 min later (expect BLOCK)",
        "txn": base_txn(
            sender_vpa=fast_travel_sender,
            receiver_vpa="unknown.receiver77@ybl",
            amount=48000.0,
            gps_lat=28.6139, gps_lng=77.2090,
            device_id="device-" + uuid.uuid4().hex[:10],  # device also changed
        ),
    })

    # 6. BLOCK — OTP-hijack pattern: brand-new device + new IP + new receiver + high amount
    scenarios.append({
        "label": "OTP-hijack pattern: new device/IP/receiver (expect BLOCK)",
        "txn": base_txn(
            sender_vpa="deepak.nair@okaxis",
            receiver_vpa="firsttime.payee555@ybl",
            amount=95000.0,
            device_id="device-" + uuid.uuid4().hex[:10],
            ip_address="103.211.45.88",
        ),
    })

    # 7. BLOCK — blacklisted VPA (hard rule override, no ML needed)
    blacklisted_vpa = "known.fraud.vpa@ybl"
    scenarios.append({
        "label": "Blacklisted VPA hard-block (expect BLOCK, hard_rule)",
        "txn": base_txn(
            sender_vpa="ritu.malhotra@oksbi",
            receiver_vpa=blacklisted_vpa,
            amount=2000.0,
        ),
    })

    # 8-9-10. Velocity / mule-chain burst — same sender, 3 rapid transfers
    # to 3 different receivers within seconds (mule fund-forwarding pattern)
    mule_sender = "compromised.acct@okicici"
    for i, amt in enumerate([15000.0, 14500.0, 15500.0], start=1):
        scenarios.append({
            "label": f"Velocity/mule-chain burst txn {i}/3 (expect escalating REVIEW/BLOCK)",
            "txn": base_txn(
                sender_vpa=mule_sender,
                receiver_vpa=f"mule.link{i}@ybl",
                amount=amt,
                device_id="device-shared-mule001",
            ),
        })

    return scenarios, blacklisted_vpa


def seed_blacklist(redis_url: str, vpa: str):
    if redis is None:
        print("  (redis-py not installed — skipping blacklist seed; "
              "pip install redis to enable the blacklist demo case)")
        return
    try:
        r = redis.from_url(redis_url, decode_responses=True)
        r.sadd("blacklist:vpa", vpa)
        print(f"  Seeded blacklist:vpa with '{vpa}' in Redis")
    except Exception as e:
        print(f"  WARNING: could not seed Redis blacklist ({e}). "
              f"The BLOCK-by-blacklist demo case may show REVIEW/SAFE instead.")


def main():
    parser = argparse.ArgumentParser(description="Seed FraudShield demo data")
    parser.add_argument("--api", default=API_BASE_DEFAULT,
                        help="Base API URL, e.g. http://localhost:8000/api/v1")
    parser.add_argument("--redis", default=REDIS_URL_DEFAULT,
                        help="Redis URL for seeding the blacklist entry")
    parser.add_argument("--delay", type=float, default=1.5,
                        help="Seconds to wait between requests (0 for the "
                             "3-txn velocity burst at the end)")
    args = parser.parse_args()

    scenarios, blacklisted_vpa = build_scenarios()

    print(f"FraudShield demo seeder — target API: {args.api}\n")
    print("Step 1: seeding blacklist entry in Redis...")
    seed_blacklist(args.redis, blacklisted_vpa)

    print(f"\nStep 2: posting {len(scenarios)} transactions...\n")

    results = []
    with httpx.Client(timeout=15) as client:
        for idx, sc in enumerate(scenarios, start=1):
            txn = sc["txn"]
            is_burst = "burst" in sc["label"]
            try:
                resp = client.post(f"{args.api}/transactions", json=txn)
                if resp.status_code in (200, 202):
                    data = resp.json()
                    decision = data.get("decision", "?")
                    score = data.get("composite_score", "?")
                    ms = data.get("processing_ms", "?")
                    print(f"[{idx:2d}/10] {sc['label']}")
                    print(f"         txn_id={txn['txn_id'][:8]}...  "
                          f"decision={decision:6s}  score={score}  "
                          f"({ms} ms)")
                    results.append((sc["label"], decision, score))
                else:
                    print(f"[{idx:2d}/10] {sc['label']}")
                    print(f"         HTTP {resp.status_code}: {resp.text[:200]}")
                    results.append((sc["label"], f"HTTP {resp.status_code}", None))
            except httpx.ConnectError:
                print(f"ERROR: could not reach {args.api}. "
                      f"Is the backend running (uvicorn on :8000)?")
                sys.exit(1)
            except Exception as e:
                print(f"[{idx:2d}/10] {sc['label']}")
                print(f"         ERROR: {e}")
                results.append((sc["label"], "ERROR", None))

            time.sleep(0.2 if is_burst else args.delay)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for label, decision, score in results:
        print(f"  {decision!s:10s}  score={str(score):8s}  {label}")

    blocked = sum(1 for _, d, _ in results if d == "BLOCK")
    review = sum(1 for _, d, _ in results if d == "REVIEW")
    safe = sum(1 for _, d, _ in results if d == "SAFE")
    print(f"\n  {safe} SAFE, {review} REVIEW, {blocked} BLOCK out of {len(results)} transactions")
    print("\nDemo data ready. Open the dashboard and cases queue to show it live.")


if __name__ == "__main__":
    main()