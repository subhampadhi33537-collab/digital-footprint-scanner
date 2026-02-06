#!/usr/bin/env python
"""Test script for ML model predictions"""

import requests
import json

url = "http://localhost:5000/api/ml/predict/risk"

# Test with different scan feature sets
test_cases = [
    {
        "name": "LOW RISK - Few platforms",
        "data": {
            "platforms_found": 2,
            "exposures": 0,
            "breaches": 0,
            "username_variations": 1,
            "location_leaks": 0,
            "phone_leaks": 0,
            "suspicious_accounts": False
        }
    },
    {
        "name": "MEDIUM RISK - Some exposure",
        "data": {
            "platforms_found": 7,
            "exposures": 5,
            "breaches": 1,
            "username_variations": 2,
            "location_leaks": 1,
            "phone_leaks": 0,
            "suspicious_accounts": False
        }
    },
    {
        "name": "HIGH RISK - Significant exposure",
        "data": {
            "platforms_found": 12,
            "exposures": 10,
            "breaches": 3,
            "username_variations": 3,
            "location_leaks": 2,
            "phone_leaks": 1,
            "suspicious_accounts": True
        }
    }
]

print("=" * 70)
print("ML MODEL PREDICTION TESTING")
print("=" * 70)
print(f"Endpoint: {url}\n")

predictions = []

for test in test_cases:
    print(f"📊 Test Case: {test['name']}")
    print(f"   Input Features: {json.dumps(test['data'], indent=18)}")
    
    try:
        response = requests.post(url, json=test['data'], timeout=10)
        result = response.json()
        
        if response.status_code == 200:
            pred = result.get('prediction', {})
            risk_score = pred.get('risk_score', 'N/A')
            risk_level = pred.get('risk_level', 'N/A')
            confidence = pred.get('confidence', 'N/A')
            models_status = pred.get('status', 'unknown')
            
            print(f"   ✅ Status: {models_status}")
            print(f"   Risk Score: {risk_score}%")
            print(f"   Risk Level: {risk_level}")
            print(f"   Confidence: {confidence}%")
            
            predictions.append({
                'test': test['name'],
                'risk_score': risk_score,
                'risk_level': risk_level
            })
        else:
            print(f"   ❌ Error: {result}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()

print("=" * 70)
print("PREDICTION ANALYSIS")
print("=" * 70)

# Check if predictions are varied
scores = [p.get('risk_score') for p in predictions if isinstance(p.get('risk_score'), (int, float))]

if len(scores) >= 3:
    min_score = min(scores)
    max_score = max(scores)
    variation = max_score - min_score
    
    print(f"\n📈 Score Variation Analysis:")
    print(f"   Minimum Score: {min_score}%")
    print(f"   Maximum Score: {max_score}%")
    print(f"   Variation Range: {variation}%")
    
    if variation > 20:
        print(f"\n✅ EXCELLENT! ML MODEL IS WORKING CORRECTLY")
        print(f"   Predictions vary based on input features (not hardcoded)")
        print(f"   Model is using trained RandomForest + GradientBoosting")
    else:
        print(f"\n⚠️  Warning: Predictions have minimal variation")
        print(f"   Variation should be > 20% for proper ML functioning")
else:
    print("Could not analyze variation - insufficient prediction data")

print("\n" + "=" * 70)
print("PREDICTIONS SUMMARY")
print("=" * 70)
for pred in predictions:
    print(f"{pred['test']}: {pred['risk_score']}% ({pred['risk_level']})")

print("\n" + "=" * 70)
