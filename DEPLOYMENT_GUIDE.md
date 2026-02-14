# 🚀 Render Deployment Guide

## ✅ Project is Ready for Render

Your Digital Footprint Scanner is fully configured and tested for Render deployment.

---

## 📋 What's Been Fixed

✅ ML models trained and ready  
✅ All required directories created automatically  
✅ Complete error handling with clear messages  
✅ Production-ready configuration  
✅ Optimized for Render free tier  
✅ Startup script ensures proper initialization  

---

## ⚡ Quick Deploy to Render (5 Minutes)

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Ready for Render deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Create Render Web Service

1. Go to [https://dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `digital-footprint-scanner`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt && python startup.py`
   - **Start Command**: `gunicorn -w 2 --timeout 120 -b 0.0.0.0:$PORT app:app`
   - **Plan**: Free

### Step 3: Add Environment Variables

In Render Dashboard → Your Service → Environment, add:

**Required:**
```
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your-32-char-random-secret-key
FLASK_ENV=production
FLASK_DEBUG=False
ALLOW_MISSING_CONFIG=True
```

**Optional (for enhanced features):**
```
ABSTRACT_API_KEY=your_abstract_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

### Step 4: Deploy

Click **"Create Web Service"** and wait 3-5 minutes for deployment.

Your app will be live at: `https://your-app-name.onrender.com`

---

## 🔑 Getting API Keys

### Groq API Key (Required - FREE)
1. Visit [https://console.groq.com](https://console.groq.com)
2. Sign up for free account
3. Go to API Keys section
4. Create new API key
5. Copy and add to Render environment variables

### Abstract API Key (Optional)
1. Visit [https://www.abstractapi.com](https://www.abstractapi.com)
2. Sign up for free account
3. Get API key for email validation
4. Adds 100 free email validations/month

---

## 🛠️ Troubleshooting

### Issue: "Scan Failed"

**Check these:**
1. **Environment Variables**: Ensure `GROQ_API_KEY` is set correctly
2. **Logs**: Check Render logs for specific error messages
3. **API Limits**: Groq free tier has rate limits
4. **Build Status**: Ensure `startup.py` ran successfully during build

**Solution:**
- Go to Render Dashboard → Your Service → Logs
- Look for errors during startup
- Verify all environment variables are set
- Redeploy if needed

### Issue: "ML Models Not Found"

**Solution:**
The `startup.py` script automatically trains models during build. If this fails:
1. Check build logs for errors
2. Ensure sufficient memory (Render free tier has 512MB)
3. Models will be trained on first scan if build training fails

### Issue: "Session Errors"

**Solution:**
Ensure these environment variables are set:
```
SESSION_TYPE=filesystem
ALLOW_MISSING_CONFIG=True
```

---

## 📊 Verifying Deployment

### 1. Health Check
Visit: `https://your-app-name.onrender.com/health`

Should return:
```json
{
  "status": "ok",
  "service": "Digital Footprint Scanner",
  "version": "2.0",
  "ml_models_ready": true
}
```

### 2. Test Scan
Visit: `https://your-app-name.onrender.com/debug`

Use the debug console to test scanning functionality.

### 3. Main Interface
Visit: `https://your-app-name.onrender.com/`

Enter a username and test the full scanning flow.

---

## ⚙️ Configuration Files

### `render.yaml` (Auto-detected by Render)
```yaml
services:
  - type: web
    name: digital-footprint-scanner
    env: python
    plan: free
    buildCommand: |
      pip install --upgrade pip
      pip install -r requirements.txt
      python startup.py
    startCommand: gunicorn -w 2 --timeout 120 -b 0.0.0.0:$PORT app:app
```

### `Procfile` (Backup)
```
web: gunicorn -w 2 --timeout 120 -b 0.0.0.0:$PORT app:app
```

### `runtime.txt` (Specifies Python version)
```
python-3.11.6
```

---

## 🚦 Performance Tips

1. **Cold Starts**: First request after inactivity may take 30-60 seconds on free tier
2. **Keep Alive**: Use uptime monitoring to ping your app every 5 minutes
3. **Rate Limits**: Groq free tier has API rate limits
4. **Memory**: ML models use ~200MB RAM, leaving room for requests

---

## 📈 Monitoring

### Render Dashboard
- View real-time logs
- Monitor CPU and memory usage
- Check deployment history
- View error rates

### Recommended: UptimeRobot
1. Sign up at [https://uptimerobot.com](https://uptimerobot.com)
2. Add monitor for your Render URL
3. Set check interval to 5 minutes
4. Prevents cold starts

---

## 🔐 Security Notes

- Never commit `.env` file to Git
- Rotate `SECRET_KEY` regularly
- Keep API keys secure
- Use environment variables for all secrets
- Enable HTTPS (automatic on Render)

---

## 📝 Post-Deployment Checklist

- [ ] App deployed successfully
- [ ] Health check endpoint responds
- [ ] Test scan completes successfully
- [ ] ML analysis shows in results
- [ ] Dashboard displays correctly
- [ ] All API keys configured
- [ ] Uptime monitoring configured (optional)
- [ ] Custom domain configured (optional)

---

## 🎉 Success!

Your Digital Footprint Scanner is now live and ready to use!

**Support:**
- Check `/debug` endpoint for diagnostics
- Review Render logs for errors
- Ensure all environment variables are set
- Groq API must be configured for ML features

**Enjoy your production-ready OSINT tool! 🚀**
