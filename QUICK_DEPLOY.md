# 🚀 RENDER DEPLOYMENT QUICK START

## Prerequisites
- GitHub account with your code pushed
- Render account (free at render.com)
- Groq API key

---

## ⚡ 5-Minute Deploy

### Step 1: Prepare GitHub
```bash
# Make sure everything is committed
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### Step 2: Deploy to Render
1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Render will auto-detect `render.yaml`:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn -w 2 -b 0.0.0.0:$PORT app:app`
5. Click **"Create Web Service"**

### Step 3: Add Environment Variables
In Render Dashboard → Settings → Environment Variables:

```
GROQ_API_KEY = your-groq-api-key-here
SECRET_KEY = generate-a-random-32-char-secret-key
FLASK_ENV = production
FLASK_DEBUG = False
SESSION_TYPE = filesystem
```

Optional:
```
ABSTRACT_API_KEY = your-abstract-api-key
GOOGLE_CLIENT_ID = your-google-client-id
GOOGLE_CLIENT_SECRET = your-google-client-secret
```

### Step 4: Monitor Deployment
Render will:
- Build your app (~3-5 minutes)
- Install dependencies
- Start the server
- Show you the live URL

Your app will be at: `https://your-app-name.onrender.com`

---

## ✅ Verify Deployment

Test your live app:

```bash
# Test health
curl https://your-app-name.onrender.com/

# Test API
curl -X POST https://your-app-name.onrender.com/api/chat-with-ai \
  -H "Content-Type: application/json" \
  -d '{"message":"How can I protect my privacy?","scan_context":{}}'
```

---

## 📊 Expected Performance

| Metric | Value |
|--------|-------|
| First Deploy | 3-5 minutes |
| Startup Time | 1-2 seconds |
| Cold Start | 30-60 sec (free tier) |
| Memory | 512MB (free) |
| CPU | 0.5 vCPU (free) |

---

## 💡 Tips

1. **Free tier is perfect for testing** - No credit card needed
2. **Upgrade to Starter ($7/mo)** - For production (no cold starts)
3. **Sessions are ephemeral** - Restarted on deploy, this is normal
4. **Check logs anytime** - Dashboard → Logs tab for debugging

---

## 🔗 Resources

- **Render Dashboard:** https://dashboard.render.com
- **Render Docs:** https://render.com/docs
- **Your App URL:** `https://your-app-name.onrender.com`
GOOGLE_REDIRECT_URI = https://your-project-name.vercel.app/callback
FLASK_ENV = production
SESSION_TYPE = filesystem
```

To generate SECRET_KEY, run:
```python
import secrets
print(secrets.token_hex(16))  # Copy this value
```

### Step 5: Deploy
Click **"Deploy"** button and wait for:
```
✅ Build Complete
✅ Deployment Live
```

Your app is now at: `https://your-project-name.vercel.app`

---

## 🔐 Update Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select your project
3. Go to **APIs & Services** → **OAuth 2.0 Credentials**
4. Click your OAuth 2.0 Client ID (Web Application)
5. Under **Authorized redirect URIs**, add:
   ```
   https://your-project-name.vercel.app/callback
   ```
6. Click **Save**
7. Download the updated JSON file to replace `client_secret.json`

---

## ✅ Test on Vercel

1. Visit your deployed URL: `https://your-project-name.vercel.app`
2. Enter an email or username
3. Watch it scan in real-time
4. Verify platforms are detected
5. Check AI assistant responds quickly

---

## 🐛 Troubleshooting

### Build Fails
**Check:** Requirements.txt has all dependencies
```bash
pip freeze > requirements.txt
git push
# Redeploy
```

### OAuth Login Error
**Solution:** Verify redirect URI in Google Cloud matches Vercel URL exactly

### No Results Displaying
**Solution:** Ensure session folder has write permissions
- Vercel has `/tmp` available
- Check `SESSION_TYPE=filesystem` in environment variables

### Slow Scans
**Solution:** Check timeout settings
- Increase `SCAN_TIMEOUT` in environment variables if needed
- Verify Groq API key is valid

---

## 📊 Monitoring

View your deployment logs in Vercel:
1. Select your project
2. Go to **"Deployments"**
3. Click latest deployment
4. Check **"Functions"** tab for logs

---

## 🎉 Done!

Your Digital Footprint Scanner is now live on Vercel! 🚀

Share the link: `https://your-project-name.vercel.app`
