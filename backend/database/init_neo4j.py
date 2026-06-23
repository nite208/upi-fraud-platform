from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI      = "bolt://localhost:7687"
USER     = "neo4j"
PASSWORD = "fraudpass123"

constraints = [
    ("Account VPA uniqueness",
     "CREATE CONSTRAINT account_vpa IF NOT EXISTS FOR (a:Account) REQUIRE a.vpa IS UNIQUE"),
    ("Device ID uniqueness",
     "CREATE CONSTRAINT device_id IF NOT EXISTS FOR (d:Device) REQUIRE d.device_id IS UNIQUE"),
    ("IP address uniqueness",
     "CREATE CONSTRAINT ip_address IF NOT EXISTS FOR (i:IP) REQUIRE i.ip_address IS UNIQUE"),
    ("Merchant VPA uniqueness",
     "CREATE CONSTRAINT merchant_vpa IF NOT EXISTS FOR (m:Merchant) REQUIRE m.vpa IS UNIQUE"),
]

indexes = [
    ("Account risk_score index",
     "CREATE INDEX account_risk IF NOT EXISTS FOR (a:Account) ON (a.risk_score)"),
    ("Account created_at index",
     "CREATE INDEX account_created IF NOT EXISTS FOR (a:Account) ON (a.created_at)"),
    ("FraudRing ring_id index",
     "CREATE INDEX ring_id IF NOT EXISTS FOR (r:FraudRing) ON (r.ring_id)"),
]

try:
    print("Connecting to Neo4j...")
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    driver.verify_connectivity()
    print("✓ Connected\n")

    with driver.session() as session:
        print("Creating constraints:")
        for name, cypher in constraints:
            session.run(cypher)
            print(f"  ✓ {name}")

        print("\nCreating indexes:")
        for name, cypher in indexes:
            session.run(cypher)
            print(f"  ✓ {name}")

        print("\nRunning connectivity test...")
        session.run("MERGE (a:Account {vpa: 'test@setup', risk_score: 0.0})")
        result = session.run("MATCH (a:Account {vpa: 'test@setup'}) RETURN a.vpa AS vpa")
        record = result.single()
        print(f"  ✓ Test node created: {record['vpa']}")
        session.run("MATCH (a:Account {vpa: 'test@setup'}) DELETE a")
        print("  ✓ Test node deleted")

    driver.close()
    print("\n✓ Neo4j schema ready. All constraints and indexes created.")

except Exception as e:
    print(f"\n✗ Error: {e}")
    print("  Make sure fraud_neo4j container is running.")