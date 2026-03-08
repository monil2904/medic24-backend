-- ============================================================
-- Med24 AI — Safe Schema Migration (Run in Neon SQL Editor)
-- All statements use IF NOT EXISTS so it's safe to run even
-- if tables/columns already exist.
-- ============================================================

-- 1. Ensure users table has all required columns
ALTER TABLE users ADD COLUMN IF NOT EXISTS queries_reset_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE users ADD COLUMN IF NOT EXISTS image_queries_month INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS lab_reports_month INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS month_reset_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_plan TEXT DEFAULT 'free';
ALTER TABLE users ADD COLUMN IF NOT EXISTS queries_today INTEGER DEFAULT 0;

-- 2. Create subscriptions table (for /auth/upgrade endpoint and Razorpay webhook)
CREATE TABLE IF NOT EXISTS subscriptions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  plan TEXT NOT NULL,
  razorpay_subscription_id TEXT,
  razorpay_payment_id TEXT,
  status TEXT DEFAULT 'active',
  started_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);

-- 3. Create lab_reports table (to persist AI lab report analysis)
CREATE TABLE IF NOT EXISTS lab_reports (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  file_url TEXT,
  parsed_data JSONB,
  interpretation TEXT,
  summary TEXT,
  abnormal_count INTEGER DEFAULT 0,
  confidence FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_lab_reports_user_id ON lab_reports(user_id);

-- 4. Create chats table (for chat history)
CREATE TABLE IF NOT EXISTS chats (
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
);
CREATE INDEX IF NOT EXISTS idx_chats_user_id ON chats(user_id);
CREATE INDEX IF NOT EXISTS idx_chats_created_at ON chats(created_at DESC);

-- 5. Create response_cache table (to avoid duplicate AI API calls)
CREATE TABLE IF NOT EXISTS response_cache (
  query_hash TEXT PRIMARY KEY,
  query TEXT,
  ensemble_response TEXT,
  confidence FLOAT,
  cached_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '24 hours'
);

-- Verify all columns exist in users
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users' 
  AND table_schema = 'public'
  AND column_name IN (
    'queries_reset_at', 'image_queries_month', 
    'lab_reports_month', 'month_reset_at',
    'subscription_plan', 'queries_today'
  )
ORDER BY column_name;
