# 🔐 Secure Supabase Setup Guide

## Step 1: Create Supabase Project

1. **Go to [Supabase Dashboard](https://supabase.com/dashboard)**
2. **Click "New Project"**
3. **Fill in details:**
   - **Name**: `rag-app-production` 
   - **Database Password**: Generate a strong password (save in password manager!)
   - **Region**: Choose closest to your users
   - **Plan**: Free (upgrade later as needed)

4. **Wait for project creation** (~2 minutes)

## Step 2: Secure Your Project Settings

### Database Security
1. **Go to Settings → Database**
2. **Enable "Connection Pooling"** (better performance)
3. **Note down connection string** (save securely!)

### API Security
1. **Go to Settings → API**
2. **Copy these values securely:**
   ```
   Project URL: https://[PROJECT_ID].supabase.co
   Anon Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (SAFE for frontend)
   Service Role Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (NEVER expose!)
   ```

3. **⚠️ CRITICAL: The Service Role Key has FULL database access - treat like a password!**

### Row Level Security (RLS)
1. **Go to Authentication → Settings**
2. **Enable "Enable Row Level Security for all tables"**
3. **Set Site URL**: `https://your-app.vercel.app` (update later)
4. **Set Redirect URLs**: Add both:
   - `http://localhost:3000` (development)
   - `https://your-app.vercel.app` (production)

## Step 3: Configure Authentication Providers

### Enable Email/Password Auth
1. **Go to Authentication → Settings**
2. **Enable Email provider**
3. **Set "Confirm email" to enabled**
4. **Set email templates** (optional, use defaults for now)

### Enable Google OAuth (Optional)
1. **Go to Authentication → Settings → External OAuth**
2. **Enable Google provider**
3. **You'll need Google OAuth credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create new project or select existing
   - Enable Google+ API
   - Create OAuth 2.0 credentials
   - Add authorized redirect URIs:
     ```
     https://[PROJECT_ID].supabase.co/auth/v1/callback
     ```
   - Copy Client ID and Client Secret to Supabase

### Enable GitHub OAuth (Optional)
1. **Go to your GitHub Settings → Developer settings → OAuth Apps**
2. **Create new OAuth App:**
   - Application name: `RAG App`
   - Homepage URL: `https://your-app.vercel.app`
   - Authorization callback URL: `https://[PROJECT_ID].supabase.co/auth/v1/callback`
3. **Copy Client ID and Client Secret to Supabase**

## Step 4: Run Database Migrations

### Option A: Using Supabase Dashboard (Recommended for now)
1. **Go to SQL Editor in Supabase Dashboard**
2. **Copy contents of `supabase/migrations/20240101000000_initial_schema.sql`**
3. **Paste and run the SQL**
4. **Copy contents of `supabase/migrations/20240101000001_storage_buckets.sql`**
5. **Paste and run the SQL**

### Option B: Using Supabase CLI (Advanced)
```bash
# Install Supabase CLI
npm install -g supabase

# Login to Supabase
supabase login

# Link to your project
supabase link --project-ref YOUR_PROJECT_ID

# Run migrations
supabase db push
```

## Step 5: Verify Security Settings

### Test RLS Policies
1. **Go to Table Editor**
2. **Try to access tables without authentication** - should be blocked
3. **Create a test user via Auth → Users**
4. **Verify user can only see their own data**

### Test Storage Policies
1. **Go to Storage**
2. **Verify buckets were created**: `documents`, `avatars`
3. **Test upload permissions**

## Step 6: Set Up Environment Variables

### For Local Development
1. **Create `.env` file in backend:**
   ```bash
   cp .env.example .env
   # Edit with your actual values
   ```

2. **Create `.env.local` file in frontend:**
   ```bash
   cp frontend/.env.local.example frontend/.env.local
   # Edit with your actual values
   ```

### For Production Deployment

#### Railway (Backend)
1. **Go to Railway Dashboard**
2. **Select your project**
3. **Go to Variables tab**
4. **Add all backend environment variables**

#### Vercel (Frontend)
1. **Go to Vercel Dashboard**
2. **Select your project**
3. **Go to Settings → Environment Variables**
4. **Add all frontend environment variables**

## Step 7: Test Security

### Security Checklist
- [ ] RLS is enabled on all tables
- [ ] Service role key is only in backend environment
- [ ] Anon key is only used in frontend
- [ ] Storage policies prevent unauthorized access
- [ ] Auth providers are configured correctly
- [ ] Redirect URLs are set properly
- [ ] Database connection uses SSL
- [ ] No secrets are committed to git

### Test Authentication Flow
1. **Start local development**
2. **Try to sign up/sign in**
3. **Verify JWT tokens are working**
4. **Test protected routes**
5. **Verify data isolation between users**

## Step 8: Monitoring & Alerts

### Enable Monitoring
1. **Go to Settings → Monitoring**
2. **Set up email alerts for:**
   - High error rates
   - Unusual traffic patterns
   - Database connection issues
   - Storage quota warnings

### Regular Security Tasks
- [ ] **Weekly**: Review auth logs for suspicious activity
- [ ] **Monthly**: Rotate service role key
- [ ] **Monthly**: Review user access patterns
- [ ] **Quarterly**: Security audit of all policies

## 🚨 Security Incident Response

### If Service Role Key is Compromised
1. **Immediately go to Settings → API**
2. **Click "Reset Service Role Key"**
3. **Update environment variables in all deployments**
4. **Review access logs for suspicious activity**
5. **Audit all database changes in past 30 days**

### If Database is Compromised
1. **Enable database audit logging**
2. **Change all user passwords**
3. **Review and tighten RLS policies**
4. **Consider temporary access restrictions**

## 📞 Support Contacts

- **Supabase Support**: [https://supabase.com/support](https://supabase.com/support)
- **Security Issues**: security@supabase.com
- **Status Page**: [https://status.supabase.com](https://status.supabase.com)

## 🔄 Next Steps

After Supabase is set up:
1. Test local development environment
2. Set up Railway backend
3. Set up Vercel frontend
4. Configure CI/CD pipeline
5. Deploy to staging for testing
6. Deploy to production

Remember: **Security is not a feature, it's a foundation!** 🛡️