# 🚀 Digital Footprint Scanner - Professional Edition

## 📋 NEW FEATURES - Company-Grade Platform

### 🎨 **Professional Frontend (Enterprise UI)**

#### Landing Page (`/index-pro`)
- Modern gradient design with smooth animations
- Feature showcase with 6 enterprise-grade capabilities
- Platform carousel showing 15+ scanned platforms
- Step-by-step "How It Works" section
- Call-to-action sections
- Professional footer with links

#### Dashboard (`/dashboard-pro`)
- **Real-time data visualization** with Chart.js
- **Interactive metrics cards** showing:
  - Platforms Found
  - ML Risk Score (0-100%)
  - Exposure Level
  - Anomalies Detected
  
- **Advanced Charts**:
  - Risk Gauge Chart (doughnut chart)
  - Exposure Breakdown (horizontal bar)
  - Platform Categories (radar chart)
  - Anomaly Distribution (vertical bar)
  
- **ML Insights Section** with actionable recommendations
- **Threat Intelligence Report** showing threat patterns
- **Detailed Statistics Table** with all metrics

---

## 🤖 **Machine Learning Integration**

### ML Model Trainer (`analysis/ml_model_trainer.py`)

#### Capabilities:
1. **Data Generation from Groq API**
   - Generates 100+ training samples per run
   - Uses Groq LLM to create diverse digital footprint scenarios
   - Stores data in JSON format for portability

2. **Training Models**
   - **Risk Prediction Model** (RandomForest Regressor)
     - Predicts risk score (0-100)
     - Features: platform count, exposure, consistency, email exposure, etc.
     - Outputs: Risk score, confidence level
   
   - **Threat Classification Model** (Gradient Boosting Classifier)
     - Classifies threat level (LOW, MEDIUM, HIGH, CRITICAL)
     - Enhanced threat detection
     - Multi-class classification

3. **Model Storage**
   - Models saved as JSON + pickle (base64 encoded)
   - Training data persisted in `/data/training_data/`
   - Latest models linked at `/data/models/*_latest.json`

### Training Data Format

```json
[
  {
    "platform_count": 8,
    "exposure_score": 65,
    "username_consistency": 0.85,
    "email_exposure": true,
    "platform_types": ["social", "professional"],
    "anomaly_flags": ["bot_pattern", "privacy_gap"],
    "expected_risk_level": "HIGH",
    "risk_score": 72
  }
]
```

---

## 🔌 **ML API Endpoints**

### **1. Model Training**
```bash
# Train all models
POST /api/ml/train
{
  "num_samples": 150  # Optional
}

# Train risk model only
POST /api/ml/train/risk

# Train threat model only
POST /api/ml/train/threat
```

### **2. Training Data**
```bash
# Generate new training data
POST /api/ml/training-data/generate
{
  "num_samples": 100
}

# List all training data files
GET /api/ml/training-data/list

# Get specific dataset
GET /api/ml/training-data/<filename>
```

### **3. Predictions**
```bash
# Single prediction
POST /api/ml/predict/risk
{
  "platform_count": 6,
  "exposure_score": 45,
  "username_consistency": 0.8,
  "email_exposure": true,
  "platform_types": ["social"],
  "anomaly_flags": []
}

# Batch predictions
POST /api/ml/predict/batch
{
  "scans": [
    { ...scan1 },
    { ...scan2 }
  ]
}
```

### **4. Model Information**
```bash
# List trained models
GET /api/ml/models/list

# Get model info
GET /api/ml/models/info

# ML system health
GET /api/ml/health

# System statistics
GET /api/ml/stats
```

### **5. Enhanced Scan with ML**
```bash
# Run scan with ML predictions
POST /api/scan-ml
{
  "user_input": "username_or_email@domain.com"
}

Response includes:
- ml_risk_score (0-100)
- ml_analysis (feature importance, scores)
- threat_intelligence (threat patterns)
- anomalies (detected anomalies)
```

---

## 📊 **New Dashboard Routes**

| Route | Purpose | Feature |
|-------|---------|---------|
| `/index-pro` | Professional home page | Modern landing with features |
| `/dashboard-pro` | Advanced dashboard | Real-time ML visualization |
| `/api/dashboard-data` | Dashboard data API | Returns all scan data as JSON |
| `/api/ml/train` | Model training | Train ML models |
| `/scan-ml` | ML-enhanced scan | Scan + ML predictions |

---

## 🚀 **Getting Started**

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Application
```bash
python app.py
```

### 3. Train Models (First Time)
```bash
# Method A: Using Python
from analysis.ml_model_trainer import get_ml_trainer

trainer = get_ml_trainer()
results = trainer.train_all_models()
print(results)

# Method B: Using API
curl -X POST http://127.0.0.1:5000/api/ml/train
```

### 4. Access Dashboards
- **Professional Home**: http://127.0.0.1:5000/index-pro
- **Professional Dashboard**: http://127.0.0.1:5000/dashboard-pro
- **Run Scan with ML**: POST to `/scan-ml` endpoint

---

## 📁 **Project Structure**

```
digital-footprint-scanner/
├── analysis/
│   ├── ml_model_trainer.py       # NEW: ML training engine
│   ├── ml_risk_engine.py         # ML risk scoring
│   ├── anomaly_detector.py       # Anomaly detection
│   ├── threat_intel.py           # Threat analysis
│   └── ...
├── api/
│   └── ml_endpoints.py           # NEW: ML REST API
├── templates/
│   ├── index-pro.html            # NEW: Professional home
│   ├── dashboard-pro.html        # NEW: Professional dashboard
│   └── ...
├── static/
│   ├── js/
│   │   └── dashboard-pro.js      # NEW: Dashboard logic
│   ├── css/
│   └── ...
├── data/
│   ├── models/                   # NEW: Trained ML models
│   │   ├── risk_model_latest.json
│   │   ├── threat_model_latest.json
│   │   └── ...
│   ├── training_data/            # NEW: Training datasets
│   │   ├── training_data_*.json
│   │   └── ...
│   └── scans/
├── app.py                        # UPDATED: With ML blueprint
├── routes.py                     # UPDATED: New routes
├── config.py                     # Configuration
└── requirements.txt              # UPDATED: ML packages
```

---

## 🔧 **Configuration**

Add to `.env`:
```bash
# ML Model Training
ML_TRAINING_ENABLED=True
ML_AUTO_TRAIN=False  # Set to True for auto-training

# Model Parameters
ML_MAX_TREES=100
ML_LEARNING_RATE=0.1
ML_TEST_SIZE=0.2
```

---

## 📈 **Model Performance**

### Training Results Example
```json
{
  "risk_model": {
    "status": "success",
    "model_type": "risk_prediction",
    "train_score": 0.847,    // R² score
    "test_score": 0.823,
    "samples_used": 150
  },
  "threat_model": {
    "status": "success",
    "model_type": "threat_classification",
    "train_score": 0.891,    // Accuracy
    "test_score": 0.865,
    "samples_used": 150
  }
}
```

---

## 💡 **Features Breakdown**

### Frontend Features
✅ Modern, responsive design  
✅ Dark mode (Tailwind CSS)  
✅ Interactive charts (Chart.js)  
✅ Real-time data updates  
✅ Smooth animations  
✅ Mobile-responsive  

### ML Features
✅ Automated data generation from Groq API  
✅ Risk prediction (0-100 score)  
✅ Threat classification (4 levels)  
✅ Model persistence (JSON format)  
✅ Batch predictions  
✅ Model versioning  

### API Features
✅ REST endpoints for training  
✅ Prediction endpoints  
✅ Model management  
✅ Training data management  
✅ System health checks  
✅ Statistics and monitoring  

---

## 🔐 **Security & Privacy**

- ✅ No data storage (except training data in `/data/`)
- ✅ Privacy-first architecture
- ✅ Ethical OSINT scanning
- ✅ OAuth 2.0 authentication ready
- ✅ Session-based data isolation

---

## 📦 **Dependencies Added**

- `scikit-learn==1.3.2` - Machine learning models
- `numpy==1.24.3` - Numerical computing
- `joblib==1.3.2` - Model persistence
- `groq==0.5.0` - Groq API integration

---

## 🎯 **Next Steps**

1. **Deploy Dashboard**: Access `/index-pro` for landing page
2. **Train Models**: POST to `/api/ml/train` to train ML models
3. **Run Enhanced Scans**: Use `/scan-ml` endpoint
4. **Monitor System**: Check `/api/ml/health` for status
5. **Analyze Results**: View results in `/dashboard-pro`

---

## 📞 **Support**

For issues or questions:
1. Check logs in console output
2. Verify `.env` configuration
3. Ensure ML dependencies installed
4. Check `/api/ml/health` endpoint

---

**✨ Your Digital Footprint Scanner is now enterprise-grade with advanced ML capabilities! ✨**
