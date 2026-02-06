# Vercel Deployment Guide - Digital Footprint Scanner

## 🚀 Quick Deploy to Vercel

Your Flask app is now configured for Vercel serverless deployment!

### Prerequisites
- GitHub account
- Vercel account (sign up at https://vercel.com)
- Git repository

### Step 1: Push to GitHub

```bash
git add -A
git commit -m "Configure for Vercel deployment"
git push origin main
```

### Step 2: Deploy to Vercel

#### Option A: Via Vercel Dashboard (Easiest)
1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Vercel auto-detects `vercel.json` configuration
4. Add environment variables (see below)
5. Click "Deploy"

#### Option B: Via Vercel CLI
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

### Step 3: Configure Environment Variables

In Vercel Dashboard → Settings → Environment Variables, add:

**Required:**
```
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your_random_secret_key_here
```

**Optional:**
```
ABSTRACT_API_KEY=your_abstract_api_key
FLASK_ENV=production
ALLOW_MISSING_CONFIG=true
```

### Step 4: Done! 🎉

Your app will be live at:
```
https://your-project-name.vercel.app
```

## 📁 Project Structure for Vercel

```
digital-footprint-scanner/
├── api/
│   ├── index.py          # Main Vercel entry point
│   └── ml_endpoints.py   # ML API endpoints
├── templates/            # HTML templates
├── static/              # CSS, JS, images
├── scanner/             # OSINT scanning modules
├── analysis/            # Risk & ML analysis
├── ai_engine/           # Groq AI integration
├── config.py            # Configuration
├── routes.py            # Flask routes
├── vercel.json          # Vercel configuration
└── requirements.txt     # Python dependencies
```

## ⚙️ Key Configuration Files

### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

### api/index.py
- Main Flask app initialization
- All routes registered
- Session management configured
- CORS enabled for API access

## 🔧 Local Testing

```bash
# Install dependencies
python -m pip install -r requirements.txt

# Run locally
python app.py

# Or use Flask development server
flask run
```

Access at: `http://localhost:5000`

## 🌐 Features Available

✅ **All Original Features Work:**
- OSINT Scanning across 50+ platforms
- Real-time progress tracking
- ML-powered risk analysis
- AI chatbot (Groq integration)
- Threat intelligence
- Analytics dashboard
- Google OAuth (optional)

## 📊 Vercel Serverless Benefits

| Feature | Render | Vercel |
|---------|--------|--------|
| Deploy Speed | 5-10 min | 30 sec |
| Cold Start | ~2-3 sec | ~1 sec |
| Free Tier | Limited hours | Unlimited |
| SSL | Included | Included |
| Custom Domain | Yes | Yes |
| Automatic Scaling | Manual | Automatic |

## 🐛 Troubleshooting

### Build Fails?
Check `vercel.json` syntax and ensure Python 3.11+ is specified.

### Import Errors?
Verify all modules are in `requirements.txt` and paths are correct in `api/index.py`.

### Session Issues?
Sessions use `/tmp/.flask_session` on Vercel. For production, consider Redis.

### API Not Working?
- Check CORS settings in `api/index.py`
- Verify environment variables are set
- Review Vercel function logs

## 📈 Production Optimization

### 1. Add Redis for Sessions (Recommended)
```python
SESSION_TYPE = 'redis'
SESSION_REDIS = redis.from_url(os.getenv('REDIS_URL'))
```

### 2. Enable Caching
```python
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
```

### 3. Add Rate Limiting
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: request.remote_addr)
```

### 4. Environment Variables Best Practices
- Never commit `.env` file
- Use Vercel's encrypted env vars
- Rotate API keys regularly

## 🔒 Security Checklist

- ✅ SECRET_KEY is strong and unique
- ✅ CORS configured properly
- ✅ ALLOW_MISSING_CONFIG only in development
- ✅ API keys in environment variables
- ✅ Input validation on all forms
- ✅ HTTPS enforced (Vercel default)

## 📝 Deployment Commands

```bash
# Check deployment status
vercel ls

# View logs
vercel logs

# Promote deployment to production
vercel --prod

# Remove deployment
vercel rm [deployment-url]

# Check domains
vercel domains ls
```

## 🎯 Next Steps

1. **Custom Domain:** Settings → Domains → Add
2. **Analytics:** Enable Vercel Analytics
3. **Monitoring:** Set up Sentry or similar
4. **API Documentation:** Add Swagger/OpenAPI
5. **Testing:** Add pytest for automated tests

## 💡 Tips

- Use Vercel's preview deployments for testing
- Set up automatic deployments from `main` branch
- Monitor function execution time (10s limit on free tier)
- Use edge functions for faster global response

## 🆘 Need Help?

- **Vercel Docs:** https://vercel.com/docs
- **Flask Docs:** https://flask.palletsprojects.com
- **GitHub Issues:** Create issue in your repo

---

**Ready to deploy?**
```bash
git push origin main
```

Then import on Vercel! 🚀
