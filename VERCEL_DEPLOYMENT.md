# 🚀 VERCEL DEPLOYMENT GUIDE - Digital Footprint Scanner

## Prerequisites

1. **GitHub Account** - Repository hosting
2. **Vercel Account** - Free at https://vercel.com
3. **Groq API Key** - From https://console.groq.com/
4. **Google OAuth Credentials** - From https://console.cloud.google.com/

---

## Step 1: Prepare Your Repository

### 1.1 Push to GitHub

```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Ready for Vercel deployment"

# Add remote (replace with your repo)
git remote add origin https://github.com/YOUR_USERNAME/digital-footprint-scanner.git

# Push to main branch
git branch -M main
git push -u origin main
```

### 1.2 Create `.gitignore`

Create `.gitignore` in root:
```
__pycache__/
*.pyc
.env
.env.local
.env.*.local
.flask_session/
venv/
.venv/
node_modules/
.vercel/
dist/
build/
```

---

## Step 2: Configure Google OAuth for Vercel

### 2.1 Update Redirect URI

In Google Cloud Console:
1. Go to **APIs & Services** → **Credentials**
2. Click your OAuth 2.0 app
3. Update **Authorized redirect URIs**:
   ```
   https://your-project.vercel.app/callback
   http://localhost:3000/callback
   ```
4. Download updated `client_secret.json`

### 2.2 Update Redirect URI in Code

The app already uses environment variable, but ensure:
- `.env` for local: `GOOGLE_REDIRECT_URI=http://127.0.0.1:5000/callback`
- Vercel will use: `GOOGLE_REDIRECT_URI=https://your-project.vercel.app/callback`

---

## Step 3: Deploy to Vercel

### 3.1 Connect Repository

1. Go to **vercel.com/dashboard**
2. Click **"Add New..."** → **"Project"**
3. Select **"Import Git Repository"**
4. Choose your `digital-footprint-scanner` repo
5. Click **"Import"**

### 3.2 Configure Environment Variables

In Vercel deployment settings, add:

```
GROQ_API_KEY = your_groq_api_key
SECRET_KEY = generate_random_key_here
GOOGLE_REDIRECT_URI = https://your-project.vercel.app/callback
GOOGLE_CLIENT_SECRETS_FILE = client_secret.json (or upload as secret)
FLASK_ENV = production
FLASK_DEBUG = False
SCAN_TIMEOUT = 5
MAX_PLATFORMS = 15
GROQ_MAX_TOKENS = 512
GROQ_TEMPERATURE = 0.3
```

### 3.3 Deploy

1. Review build settings (should auto-detect Flask)
2. Click **"Deploy"**
3. Wait for deployment to complete

---

## Step 4: Verify Deployment

### 4.1 Test in Browser

```
https://your-project.vercel.app/
```

### 4.2 Check Logs

In Vercel dashboard:
1. Go to your project
2. Click **"Deployments"**
3. Click latest deployment
4. Check **"Logs"** tab for errors

---

## Troubleshooting

### Issue: "Module not found" errors

**Fix:**
```bash
# Ensure requirements.txt is in root
pip freeze > requirements.txt

# Commit and push
git add requirements.txt
git commit -m "Update requirements.txt"
git push
```

### Issue: "GROQ_API_KEY not set"

**Fix:**
1. In Vercel dashboard, go to **Settings** → **Environment Variables**
2. Add `GROQ_API_KEY` with your key
3. Redeploy

### Issue: OAuth redirect fails

**Fix:**
1. Update `GOOGLE_REDIRECT_URI` in Vercel env vars
2. Update Google Cloud OAuth settings
3. Redeploy

### Issue: "Session storage failed"

**Fix:**
This is expected on Vercel (filesystem not persistent). Already handled in code with fallback.

---

## Performance on Vercel

### Expected Performance
- **Scan Time**: 15-20 seconds (same as local)
- **AI Response**: 5-8 seconds (same as local)
- **Cold Start**: ~5-10 seconds (first request)

### Optimize Further

To reduce cold starts, use:
```
- Vercel Pro tier
- Reduce Python dependencies
- Use async/await patterns
```

---

## Production Best Practices

### 1. Security

```bash
# Generate secure SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```

Use this in Vercel env vars.

### 2. Monitor Logs

```bash
# View real-time logs
vercel logs digital-footprint-scanner
```

### 3. Set Up Domains

1. In Vercel, go to **Settings** → **Domains**
2. Add your custom domain
3. Update `GOOGLE_REDIRECT_URI` to use custom domain

### 4. Scale

For high traffic:
- Upgrade to Vercel Pro
- Increase `MAX_PLATFORMS` back to 20-25
- Consider caching scan results

---

## File Structure for Vercel

```
digital-footprint-scanner/
├── api/
│   └── index.py              # Vercel serverless function (optional)
├── vercel.json               # ✅ Vercel config
├── app.py                    # ✅ Flask app (Vercel entrypoint)
├── requirements.txt          # ✅ Python dependencies
├── .env.example              # ✅ Environment template
├── config.py
├── routes.py
├── scanner/
├── ai_engine/
├── analysis/
├── templates/
├── static/
├── .gitignore
└── README.md
```

---

## Verification Checklist

- ✅ `vercel.json` exists in root
- ✅ `requirements.txt` in root (not in subdirectory)
- ✅ `.env` in `.gitignore`
- ✅ `client_secret.json` handled securely
- ✅ Environment variables set in Vercel
- ✅ `GOOGLE_REDIRECT_URI` updated for Vercel domain
- ✅ No hardcoded localhost URLs
- ✅ All imports are absolute (not relative beyond package)

---

## Useful Commands

### View Deployment Status
```bash
vercel --cwd d:\MY\ PROJECT\digital-footprint-scanner
```

### Redeploy Latest
```bash
vercel --cwd d:\MY\ PROJECT\digital-footprint-scanner --prod
```

### View Environment Variables
```bash
vercel env list
```

### Clear Vercel Cache
```bash
vercel --cwd d:\MY\ PROJECT\digital-footprint-scanner --prod --force
```

---

## Next Steps

1. ✅ Deploy to Vercel (this guide)
2. ✅ Test OAuth login
3. ✅ Run a scan
4. ✅ Check AI response
5. ✅ Monitor logs
6. ✅ Celebrate! 🎉

---

**Your scanner is now production-ready on Vercel!** 🚀
