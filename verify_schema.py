"""
Med24 DB Schema Verifier + Auto-Fixer
Checks if all required columns and tables exist in Neon DB.
If any are missing, prints the exact ALTER TABLE SQL to run.
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

REQUIRED_COLUMNS = {
    "users": [
        ("queries_reset_at", "TIMESTAMPTZ"),
        ("image_queries_month", "INTEGER"),
        ("lab_reports_month", "INTEGER"),
        ("month_reset_at", "TIMESTAMPTZ"),
        ("subscription_plan", "TEXT"),
        ("queries_today", "INTEGER"),
    ]
}

REQUIRED_TABLES = ["users", "chats", "subscriptions", "lab_reports", "response_cache"]

async def verify():
    print(f"\n{'='*55}")
    print("  Med24 AI — Database Schema Verifier")
    print(f"{'='*55}\n")

    try:
        conn = await asyncpg.connect(db_url)
        print("✅ Connected to Neon DB successfully\n")
    except Exception as e:
        print(f"❌ Connection FAILED: {e}")
        return

    # Check tables
    print("── Checking tables ──")
    missing_tables = []
    for table in REQUIRED_TABLES:
        exists = await conn.fetchval(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name=$1 AND table_schema='public')",
            table
        )
        status = "✅" if exists else "❌ MISSING"
        print(f"  {status}  {table}")
        if not exists:
            missing_tables.append(table)

    # Check columns in users table
    print("\n── Checking users table columns ──")
    missing_columns = []
    for table, cols in REQUIRED_COLUMNS.items():
        for col_name, col_type in cols:
            exists = await conn.fetchval(
                "SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name=$1 AND column_name=$2 AND table_schema='public')",
                table, col_name
            )
            status = "✅" if exists else "❌ MISSING"
            print(f"  {status}  users.{col_name} ({col_type})")
            if not exists:
                missing_columns.append((table, col_name, col_type))

    await conn.close()

    # Print fixes
    print()
    if not missing_tables and not missing_columns:
        print("🎉 All tables and columns exist! Schema is correct.\n")
    else:
        print("⚠️  MISSING items found. Run this SQL in your Neon SQL Editor:\n")
        print("```sql")
        if "subscriptions" in missing_tables:
            print("""CREATE TABLE subscriptions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  plan TEXT NOT NULL,
  razorpay_subscription_id TEXT,
  razorpay_payment_id TEXT,
  status TEXT DEFAULT 'active',
  started_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ
);""")
        if "lab_reports" in missing_tables:
            print("""CREATE TABLE lab_reports (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  file_url TEXT,
  parsed_data JSONB,
  interpretation TEXT,
  summary TEXT,
  abnormal_count INTEGER DEFAULT 0,
  confidence FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);""")
        if "chats" in missing_tables:
            print("""CREATE TABLE chats (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  query TEXT NOT NULL,
  query_type TEXT DEFAULT 'general',
  ensemble_response TEXT,
  medgemma_response TEXT,
  meditron_response TEXT,
  medichat_response TEXT,
  confidence FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);""")
        for table, col, typ in missing_columns:
            default = "DEFAULT NOW()" if "TIMESTAMPTZ" in typ else "DEFAULT 0"
            print(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {typ} {default};")
        print("```")

asyncio.run(verify())
