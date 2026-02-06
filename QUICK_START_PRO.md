# 🚀 Quick Start - Professional ML Edition

## ⚡ 5-Minute Setup

### 1. Install ML Dependencies (2 min)
```bash
pip install -r requirements.txt
```

**Or just the new packages**:
```bash
pip install scikit-learn numpy joblib groq
```

### 2. Start Application (1 min)
```bash
python app.py
```

You'll see:
```
✅ Environment & configuration validated
🚀 Starting AI-Powered Digital Footprint Scanner
...
```

### 3. Access Professional Dashboard (30 sec)
Open browser:
- **Landing Page**: http://localhost:5000/index-pro
- **Dashboard**: http://localhost:5000/dashboard-pro

### 4. Train ML Models (Optional - 20 sec)

**Option A: One-Command Training**
```bash
curl -X POST http://127.0.0.1:5000/api/ml/train
```

**Option B: Python Script**
```python
from analysis.ml_model_trainer import get_ml_trainer
trainer = get_ml_trainer()
result = trainer.train_all_models()
print(f"✅ Models trained: {result}")
```

### 5. Run Enhanced Scan (15 sec)
```bash
curl -X POST http://127.0.0.1:5000/scan-ml \
  -H "Content-Type: application/json" \
  -d '{"user_input": "testuser@gmail.com"}'
```

---

## 📊 View Results

After running a scan:

1. **Dashboard auto-loads** with real data
2. **Charts render** showing:
   - Risk gauge
   - Exposure breakdown
   - Platform categories
   - Anomaly distribution
3. **ML insights** display with predictions
4. **Threat report** shows detected threats

---

## 🎯 API Commands

### Check System Health
```bash
curl http://127.0.0.1:5000/api/ml/health
```

### Get Statistics
```bash
curl http://127.0.0.1:5000/api/ml/stats
```

### List Models
```bash
curl http://127.0.0.1:5000/api/ml/models/list
```

### Generate Training Data
```bash
curl -X POST http://127.0.0.1:5000/api/ml/training-data/generate \
  -H "Content-Type: application/json" \
  -d '{"num_samples": 100}'
```

---

## 📁 Key Files

| File | Purpose | Size |
|------|---------|------|
| `analysis/ml_model_trainer.py` | ML core engine | 470 lines |
| `api/ml_endpoints.py` | API endpoints | 400+ lines |
| `templates/index-pro.html` | Landing page | 700+ lines |
| `templates/dashboard-pro.html` | Dashboard UI | 400+ lines |
| `static/js/dashboard-pro.js` | Dashboard logic | 600+ lines |

---

## 🔧 Environment Setup

No new `.env` variables required! But you can add:

```bash
# Optional ML settings
ML_TRAINING_ENABLED=True
ML_AUTO_TRAIN=False
ML_MAX_TREES=100
```

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] `python app.py` runs without errors
- [ ] http://localhost:5000/index-pro loads
- [ ] http://localhost:5000/dashboard-pro loads
- [ ] `/api/ml/health` returns `{"status": "healthy"}`
- [ ] `/api/ml/train` trains models successfully
- [ ] Scan results appear on dashboard

---

## 🚀 Next Steps

1. **Deploy**: Push to Vercel (same as before)
2. **Customize**: Edit templates for your branding
3. **Monitor**: Check `/api/ml/stats` regularly
4. **Retrain**: Update models as needed

---

## 📚 Full Documentation

See these files for complete details:

- `ML_FEATURES_GUIDE.md` - Complete ML guide
- `UPGRADE_SUMMARY.md` - What's been added
- `README.md` - Original project info

---

**Your professional ML-powered platform is ready!** 🎉
