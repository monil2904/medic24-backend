-- Users table (our own auth — no external service)
CREATE TABLE users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT,  -- NULL for Google OAuth users
  google_id TEXT,      -- NULL for email/password users
  subscription_plan TEXT DEFAULT 'free',
  queries_today INTEGER DEFAULT 0,
  image_queries_month INTEGER DEFAULT 0,
  lab_reports_month INTEGER DEFAULT 0,
  queries_reset_at TIMESTAMPTZ DEFAULT NOW(),
  month_reset_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_google_id ON users(google_id);

-- Chat history
CREATE TABLE chats (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  query TEXT NOT NULL,
  query_type TEXT DEFAULT 'text',
  ensemble_response TEXT,
  medgemma_response TEXT,
  meditron_response TEXT,
  medichat_response TEXT,
  confidence FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chats_user_id ON chats(user_id);
CREATE INDEX idx_chats_created_at ON chats(created_at DESC);

-- Response cache (saves AI API calls for repeated questions)
CREATE TABLE response_cache (
  query_hash TEXT PRIMARY KEY,
  query TEXT,
  ensemble_response TEXT,
  confidence FLOAT,
  cached_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '24 hours'
);

-- Subscriptions (Razorpay payment tracking)
CREATE TABLE subscriptions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  plan TEXT NOT NULL,
  razorpay_subscription_id TEXT,
  razorpay_payment_id TEXT,
  status TEXT DEFAULT 'active',
  started_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ
);

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);

-- Lab reports
CREATE TABLE lab_reports (
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

CREATE INDEX idx_lab_reports_user_id ON lab_reports(user_id);
