import logging
import chromadb
from typing import List, Dict, Any, Optional
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logger = logging.getLogger(__name__)

_client     = None
_collection = None

FRAUD_TYPOLOGIES = [
    {
        "id":   "typ_001",
        "text": "Velocity attack: A fraudster sends many small transactions rapidly within minutes. Key signals: high transaction count in 1-5 minute window, amounts below ₹500, multiple different receivers, same device and IP. Common in UPI after OTP compromise.",
        "metadata": {"type": "typology", "fraud_type": "velocity_attack"}
    },
    {
        "id":   "typ_002",
        "text": "Account takeover: Fraudster gains control of victim account via SIM swap or OTP phishing. Key signals: new device ID appearing suddenly, new IP address, large amount to unknown receiver, unusual transaction hour (midnight to 5am), no prior relationship with receiver.",
        "metadata": {"type": "typology", "fraud_type": "account_takeover"}
    },
    {
        "id":   "typ_003",
        "text": "Mule account chain: Stolen funds moved through multiple accounts to obscure origin. Key signals: account receives from many senders, immediately forwards to single receiver, account age less than 30 days, high in-degree vs out-degree ratio in transaction graph.",
        "metadata": {"type": "typology", "fraud_type": "mule_chain"}
    },
    {
        "id":   "typ_004",
        "text": "Large unusual transfer: Single high-value transaction inconsistent with account history. Key signals: amount significantly above sender average, night-time transaction, new receiver, no merchant code (P2P), amount near ₹1 lakh limit.",
        "metadata": {"type": "typology", "fraud_type": "large_unusual"}
    },
    {
        "id":   "typ_005",
        "text": "SIM swap fraud: Attacker ports victim mobile number to new SIM to intercept OTPs. Key signals: device change followed immediately by large transaction, IP change, new UPI app registration, transaction within hours of device change.",
        "metadata": {"type": "typology", "fraud_type": "sim_swap"}
    },
    {
        "id":   "typ_006",
        "text": "Merchant fraud: Fraudulent merchant VPA collects payments for non-existent goods. Key signals: merchant code present, multiple senders to same VPA within hours, receiver VPA newly registered, no prior transaction history for merchant.",
        "metadata": {"type": "typology", "fraud_type": "merchant_fraud"}
    },
    {
        "id":   "rbi_001",
        "text": "RBI guidelines: Banks must report fraud within 24 hours of detection via Fraud Monitoring Return (FMR). Transactions above ₹1 lakh flagged as high-value. Customer liability limited if fraud reported within 3 days. Banks must maintain fraud logs for 5 years.",
        "metadata": {"type": "rbi_guideline"}
    },
    {
        "id":   "rbi_002",
        "text": "RBI UPI fraud categories: Unauthorised electronic fund transfer, phishing, vishing, smishing, SIM swap, account takeover. Banks required to have real-time fraud monitoring for UPI transactions. Cooling period of 24 hours for new payee above ₹50,000.",
        "metadata": {"type": "rbi_guideline"}
    },
    {
        "id":   "fatf_001",
        "text": "FATF money laundering typology - layering phase: Funds moved rapidly through multiple accounts to obscure paper trail. Typical pattern: placement (initial fraud) -> layering (mule chains) -> integration (withdrawal as clean money). Red flags: structuring below reporting thresholds, rapid successive transfers.",
        "metadata": {"type": "fatf_typology"}
    },
    {
        "id":   "invest_001",
        "text": "Investigation checklist for high-risk transactions: 1) Verify device and IP history for sender. 2) Check receiver account age and prior transaction volume. 3) Review sender transaction velocity in past 24 hours. 4) Assess graph connectivity to known fraud accounts. 5) Check if amount matches sender historical average. 6) Verify transaction hour against sender typical behaviour.",
        "metadata": {"type": "investigation_guide"}
    }
]


def get_client():
    global _client
    if _client is None:
        try:
            _client = chromadb.HttpClient(
                host=config.CHROMA_HOST,
                port=config.CHROMA_PORT
            )
            logger.info("✓ ChromaDB client connected")
        except Exception as e:
            logger.warning(f"ChromaDB HTTP failed, using in-memory: {e}")
            _client = chromadb.Client()
    return _client


def get_collection():
    global _collection
    if _collection is None:
        client      = get_client()
        _collection = client.get_or_create_collection(
            name="fraud_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
        # Seed with typologies if empty
        count = _collection.count()
        if count == 0:
            logger.info("Seeding ChromaDB with fraud typologies...")
            _collection.add(
                ids       = [t['id'] for t in FRAUD_TYPOLOGIES],
                documents = [t['text'] for t in FRAUD_TYPOLOGIES],
                metadatas = [t['metadata'] for t in FRAUD_TYPOLOGIES]
            )
            logger.info(f"✓ Seeded {len(FRAUD_TYPOLOGIES)} documents")
    return _collection


def search_similar(query: str, n_results: int = 3,
                   filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search for documents similar to the query."""
    try:
        collection = get_collection()
        where      = {"type": filter_type} if filter_type else None
        results    = collection.query(
            query_texts = [query],
            n_results   = min(n_results, collection.count()),
            where       = where
        )
        docs      = results.get('documents', [[]])[0]
        metadatas = results.get('metadatas', [[]])[0]
        distances = results.get('distances', [[]])[0]

        return [
            {
                'text':      doc,
                'metadata':  meta,
                'relevance': round(1 - dist, 3)
            }
            for doc, meta, dist in zip(docs, metadatas, distances)
        ]
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return []


def add_case_to_store(case_id: str, summary: str,
                      metadata: Dict[str, Any]) -> bool:
    """Add a resolved fraud case to the vector store for future RAG."""
    try:
        collection = get_collection()
        collection.upsert(
            ids       = [f"case_{case_id}"],
            documents = [summary],
            metadatas = [{**metadata, 'type': 'resolved_case'}]
        )
        return True
    except Exception as e:
        logger.error(f"add_case_to_store failed: {e}")
        return False