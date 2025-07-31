# 🔒 Security Architecture for RAG Application

## Overview
This document outlines our multi-layered security approach to protect API keys, user data, and system integrity.

## 🔑 API Key Security

### 1. **Environment Variable Hierarchy**

```
┌─────────────────────────────────────────────────────────────┐
│                    NEVER EXPOSED TO CLIENT                   │
├─────────────────────────────────────────────────────────────┤
│ Backend Only (Railway Environment Variables):                │
│ • SUPABASE_SERVICE_KEY     - Full database access          │
│ • TOGETHER_API_KEY         - LLM API access                │
│ • OPENAI_API_KEY          - Alternative LLM                │
│ • DATABASE_URL            - Direct DB connection           │
│ • REDIS_PASSWORD          - Cache access                   │
│ • JWT_SECRET              - Token signing                  │
│ • ENCRYPTION_KEY          - Data encryption                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    SAFE FOR CLIENT EXPOSURE                  │
├─────────────────────────────────────────────────────────────┤
│ Frontend Only (Vercel Environment Variables):               │
│ • NEXT_PUBLIC_SUPABASE_URL     - Public API endpoint       │
│ • NEXT_PUBLIC_SUPABASE_ANON_KEY - Public anon key         │
│ • NEXT_PUBLIC_API_URL          - Backend URL               │
└─────────────────────────────────────────────────────────────┘
```

### 2. **Key Storage Best Practices**

#### Development
```bash
# .env.local (Frontend) - NEVER commit
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...  # Safe to expose

# .env (Backend) - NEVER commit
SUPABASE_SERVICE_KEY=eyJ...  # NEVER expose to frontend
TOGETHER_API_KEY=xxx        # NEVER expose to frontend
```

#### Production
- **Vercel**: Environment variables set in dashboard
- **Railway**: Environment variables set in dashboard
- **GitHub Actions**: Secrets stored in repository settings

## 🛡️ Security Layers

### Layer 1: API Gateway Pattern
```
Frontend → Backend API → External Services
   ↓          ↓              ↓
No API keys  All keys     Never exposed
             stored here
```

All sensitive API calls go through our backend:
```python
# ❌ NEVER do this in frontend
const response = await fetch('https://api.together.xyz/inference', {
  headers: { 'Authorization': 'Bearer YOUR_API_KEY' }
});

# ✅ Always proxy through backend
const response = await fetch('/api/chat', {
  headers: { 'Authorization': `Bearer ${userToken}` }
});
```

### Layer 2: Authentication & Authorization

#### Supabase RLS (Row Level Security)
Every database table has RLS policies:
```sql
-- Users can only access their own data
CREATE POLICY "Users own data" ON documents
  FOR ALL USING (auth.uid() = user_id);
```

#### JWT Token Validation
```python
# Backend validates every request
@app.middleware("http")
async def validate_request(request: Request, call_next):
    token = extract_token(request)
    if not token or not validate_jwt(token):
        return JSONResponse({"error": "Unauthorized"}, 401)
    return await call_next(request)
```

### Layer 3: Input Validation & Sanitization

#### Request Validation
```python
from pydantic import BaseModel, validator

class ChatRequest(BaseModel):
    message: str
    conversation_id: str
    
    @validator('message')
    def validate_message(cls, v):
        # Prevent injection attacks
        if len(v) > 10000:
            raise ValueError('Message too long')
        # Remove any potential scripts
        v = bleach.clean(v, tags=[], strip=True)
        return v.strip()
```

#### File Upload Security
```python
ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.docx', '.md'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def validate_file(file: UploadFile):
    # Check file extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("File type not allowed")
    
    # Check file size
    if file.size > MAX_FILE_SIZE:
        raise ValueError("File too large")
    
    # Scan file content (basic check)
    content = file.file.read(1024)
    if has_malicious_content(content):
        raise ValueError("Suspicious file content")
```

### Layer 4: Rate Limiting & DDoS Protection

#### API Rate Limiting
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_user_id)

@app.post("/api/chat")
@limiter.limit("10/minute")  # 10 requests per minute
async def chat_endpoint(request: Request):
    pass

@app.post("/api/documents/upload")
@limiter.limit("5/hour")  # 5 uploads per hour
async def upload_endpoint(request: Request):
    pass
```

#### Vercel/Railway Protection
- Automatic DDoS protection
- Web Application Firewall (WAF)
- SSL/TLS encryption

### Layer 5: Data Encryption

#### At Rest
```python
# Encrypt sensitive data before storage
from cryptography.fernet import Fernet

def encrypt_document(content: str) -> str:
    cipher = Fernet(settings.ENCRYPTION_KEY)
    return cipher.encrypt(content.encode()).decode()

def decrypt_document(encrypted: str) -> str:
    cipher = Fernet(settings.ENCRYPTION_KEY)
    return cipher.decrypt(encrypted.encode()).decode()
```

#### In Transit
- All API calls use HTTPS
- WebSocket connections use WSS
- Database connections use SSL

### Layer 6: Monitoring & Auditing

#### Security Monitoring
```python
# Log all security events
@app.middleware("http")
async def security_logger(request: Request, call_next):
    # Log request details
    log_security_event({
        "ip": request.client.host,
        "path": request.url.path,
        "method": request.method,
        "user_id": get_user_id(request),
        "timestamp": datetime.utcnow()
    })
    
    response = await call_next(request)
    
    # Alert on suspicious patterns
    if response.status_code == 401:
        alert_security_team(request)
    
    return response
```

## 🚨 Security Checklist

### Development Phase
- [ ] Never commit .env files
- [ ] Use .gitignore properly
- [ ] Rotate keys regularly
- [ ] Use different keys for dev/staging/prod
- [ ] Enable 2FA on all service accounts

### Pre-Deployment
- [ ] Security audit of all endpoints
- [ ] Penetration testing
- [ ] Dependency vulnerability scan
- [ ] OWASP compliance check
- [ ] Data privacy compliance (GDPR/CCPA)

### Production
- [ ] Enable all Supabase RLS policies
- [ ] Set up monitoring alerts
- [ ] Configure backup encryption
- [ ] Enable audit logging
- [ ] Set up incident response plan

## 🔐 Environment Configuration

### Safe Frontend Configuration (.env.local)
```bash
# These can be exposed to the browser
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
NEXT_PUBLIC_API_URL=https://api.yourapp.com
```

### Secure Backend Configuration (.env)
```bash
# NEVER expose these to frontend
SUPABASE_SERVICE_KEY=eyJ...
DATABASE_URL=postgresql://...
TOGETHER_API_KEY=xxx
OPENAI_API_KEY=sk-xxx
JWT_SECRET=your-256-bit-secret
ENCRYPTION_KEY=your-encryption-key
REDIS_PASSWORD=xxx

# Security settings
RATE_LIMIT_ENABLED=true
CORS_ORIGINS=https://yourapp.com,https://www.yourapp.com
SESSION_TIMEOUT=3600
MAX_FILE_SIZE=52428800
```

## 🛑 Common Security Mistakes to Avoid

### 1. **API Key Exposure**
```javascript
// ❌ NEVER do this
const API_KEY = "sk-1234567890";

// ✅ Always use environment variables
const API_KEY = process.env.SECRET_API_KEY;
```

### 2. **Direct Database Access**
```javascript
// ❌ NEVER expose database queries to frontend
const users = await supabase.from('users').select('*');

// ✅ Always use RLS and authenticated queries
const { data, error } = await supabase
  .from('documents')
  .select('*')
  .eq('user_id', user.id);
```

### 3. **Unvalidated Input**
```python
# ❌ NEVER trust user input
query = f"SELECT * FROM users WHERE id = {user_input}"

# ✅ Always validate and sanitize
user_id = validate_uuid(user_input)
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

## 🔄 Key Rotation Strategy

### Quarterly Rotation
1. Generate new keys in provider dashboards
2. Update in production environment variables
3. Deploy new version
4. Revoke old keys after verification

### Emergency Rotation
If a key is compromised:
1. Immediately revoke the compromised key
2. Generate new key
3. Update all environments
4. Audit access logs
5. Notify affected users if necessary

## 📊 Security Monitoring

### Real-time Alerts
- Failed authentication attempts > 5 in 5 minutes
- Unusual API usage patterns
- File upload anomalies
- Rate limit violations
- 500 errors spike

### Weekly Reviews
- Security logs analysis
- User access patterns
- API usage by endpoint
- Error rate trends
- Performance metrics

## 🚀 Deployment Security

### CI/CD Security
```yaml
# .github/workflows/deploy.yml
name: Secure Deploy
on:
  push:
    branches: [main]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      # Scan for secrets
      - name: Secret Scanning
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          
      # Dependency vulnerability scan
      - name: Security Audit
        run: |
          npm audit --audit-level=moderate
          pip-audit
          
      # SAST scanning
      - name: CodeQL Analysis
        uses: github/codeql-action/analyze@v2
```

### Production Hardening
- Enable Vercel's Web Application Firewall
- Configure Railway's security policies
- Set up Cloudflare for additional DDoS protection
- Enable Supabase's advanced security features

## 🆘 Incident Response Plan

### If API Keys are Exposed
1. **Immediate**: Rotate all affected keys
2. **Within 1 hour**: Audit access logs
3. **Within 24 hours**: Notify users if data affected
4. **Within 48 hours**: Complete security review
5. **Within 1 week**: Implement additional safeguards

### Security Contact
Create security@yourapp.com for vulnerability reports