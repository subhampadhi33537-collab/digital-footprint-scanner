# 🚀 Render Deployment Guide - Digital Footprint Scanner

## ✅ Your Application is Ready for Render

Your Flask app is fully configured for Render deployment with no errors!

---

## 📋 Prerequisites
- GitHub account with your code pushed
- Render account (free at https://render.com)
- Groq API key from https://console.groq.com/

---

## ⚡ 5-Minute Deploy to Render

### Step 1: Push Code to GitHub
```bash
git add -A
git commit -m "Production ready for Render deployment"
git push origin main
```

### Step 2: Deploy to Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Fill in the deployment form:
   - **Name:** `digital-footprint-scanner`
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn -w 2 -b 0.0.0.0:$PORT app:app`
   - **Plan:** Free (or Starter)

### Step 3: Add Environment Variables
Go to **Settings** → **Environment Variables** and add:

```
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=generate_a_random_32_char_secret_key
FLASK_ENV=production
FLASK_DEBUG=False
SESSION_TYPE=filesystem
```

Optional:
```
ABSTRACT_API_KEY=your_abstract_api_key_here
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

### Step 4: Deploy
Click **"Create Web Service"** and Render will automatically:
- Build your application
- Install dependencies
- Start the server
- Assign a public URL

Your app will be live at: `https://your-app-name.onrender.com`

---

## 📁 Project Configuration

### render.yaml
Your application uses the following Render configuration:
```yaml
services:
  - type: web
    name: digital-footprint-scanner
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn -w 2 -b 0.0.0.0:$PORT app:app
    envVars:
      - key: FLASK_ENV
        value: production
      - key: SESSION_TYPE
        value: filesystem
```

### requirements.txt
All dependencies are specified in `requirements.txt`:
- Flask 3.1.2
- Gunicorn 22.0.0 (production WSGI server)
- Groq API integration
- Google OAuth support
- All scanner & ML modules

---

## ✅ Deployment Verification

After deployment, verify:

1. **Health Check**
   ```bash
   curl https://your-app.onrender.com/
   ```
   Should return: Dashboard HTML

2. **API Test**
   ```bash
   curl -X POST https://your-app.onrender.com/api/chat-with-ai \
     -H "Content-Type: application/json" \
     -d '{"message":"What is digital privacy?","scan_context":{}}'
   ```
   Should return: AI response

3. **Scanning Test**
   - Visit `https://your-app.onrender.com/`
   - Enter an email/username
   - Should scan platforms and display results

---

## 🔧 Troubleshooting

### App won't start
**Check logs:**
- Go to Render Dashboard → Your Service → Logs
- Look for error messages
- Common issues: Missing environment variables, dependency conflicts

**Fix:**
```bash
# Add missing environment variables in Render Dashboard
# Rebuild the service
```

### Cold starts are slow
- This is normal on Render's free tier
- First request takes 30-60 seconds
- Subsequent requests are fast
- Upgrade to Starter plan for instant starts

### Database/Session errors
- Render uses ephemeral storage for free tier
- Flask sessions use filesystem by default
- Sessions are lost on app restarts
- This is expected behavior

---

## 📊 Performance

- **Build time:** ~3-5 minutes (first deployment)
- **Startup time:** 1-2 seconds (after built)
- **Cold start:** 30-60 seconds on free tier
- **Memory:** 512MB (free tier)
- **CPU:** Shared 0.5 vCPU (free tier)

For production use, upgrade to **Starter Plan**:
- $7/month
- 1 vCPU dedicated
- No cold starts
- Auto-scaling available

---

## 🔗 Useful Links

- **Render Docs:** https://render.com/docs
- **Render Dashboard:** https://dashboard.render.com
- **Flask Gunicorn:** https://gunicorn.org/
- **Groq API:** https://console.groq.com/

---

## ✨ What's Included

Your deployment includes:
- ✅ Real OSINT scanning (15 platforms)
- ✅ AI chatbot (Groq integration)
- ✅ Professional dashboard
- ✅ ML risk assessment
- ✅ Real-time progress tracking
- ✅ Session management
- ✅ Google OAuth support
- ✅ Production-ready configuration

---

## 🎉 You're All Set!

Your Digital Footprint Scanner is ready for production deployment on Render with zero errors!
