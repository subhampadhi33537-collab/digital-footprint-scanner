# 🚀 VERCEL DEPLOYMENT QUICK START

## Prerequisites
- GitHub account with your code pushed
- Vercel account (free at vercel.com)
- Google OAuth credentials
- Groq API key

---

## ⚡ 5-Minute Deploy

### Step 1: Prepare GitHub
```bash
# Make sure everything is committed
git add .
git commit -m "Ready for Vercel deployment"
git push origin main
```

### Step 2: Import Project to Vercel
1. Go to https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**
3. Select **"Import Git Repository"**
4. Paste your repo URL or select from list
5. Click **"Import"**

### Step 3: Configure Build Settings
When Vercel shows the configuration screen:
- **Framework:** Python
- **Root Directory:** `.` (default)
- Click **"Environment Variables"** and skip for now

### Step 4: Add Environment Variables
Click the **"Environment Variables"** section and add:

```
GROQ_API_KEY = sk-proj-xxxxxxxxxxxxxxxxxxxxx
SECRET_KEY = generate-a-random-32-char-string
GOOGLE_CLIENT_ID = your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET = your-google-client-secret
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
