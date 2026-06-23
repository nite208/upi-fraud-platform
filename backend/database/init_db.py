import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Connect to localhost (we're outside Docker)
conn_params = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "frauddb",
    "user":     "frauduser",
    "password": "fraudpass123"
}

schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")

try:
    print("Connecting to TimescaleDB...")
    conn = psycopg2.connect(**conn_params)
    conn.autocommit = True
    cur = conn.cursor()

    print("Reading schema.sql...")
    with open(schema_path, "r") as f:
        sql = f.read()

    print("Applying schema...")
    cur.execute(sql)

    # Verify tables were created
    cur.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = [row[0] for row in cur.fetchall()]

    print("\n✓ Tables created:")
    for t in tables:
        print(f"  ✓ {t}")

    cur.close()
    conn.close()
    print("\n✓ All done. Database ready.")

except psycopg2.OperationalError as e:
    print(f"\n✗ Connection failed: {e}")
    print("  Make sure fraud_timescaledb container is running.")
except Exception as e:
    print(f"\n✗ Error: {e}")