"""
Test script to verify your ML models are working
Run this first to make sure everything loads correctly
"""

import sys
import os
import json

# Add ML_MODELS to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    print("🔍 Testing ML Model Loading...")
    print("-" * 40)
    
    # Test importing your modules
    print("📂 Importing trajectory_predictor...")
    from ML_MODELS.trajectory_predictor import TrajectoryPredictor
    
    print("📂 Importing data_collector...")
    from ML_MODELS.data_collector import DataCollector
    
    print("📂 Importing ml_utils...")
    from ML_MODELS import ml_utils
    
    print("✅ All modules imported successfully!\n")
    
    # Test loading the model
    print("🤖 Loading trained model...")
    predictor = TrajectoryPredictor(model_path='ML_MODELS/trained_model.h5')
    
    if predictor.model is not None:
        print("✅ Model loaded successfully!")
        print(f"   Model type: {type(predictor.model)}")
    else:
        print("⚠️ Model not loaded, using fallback mode")
    
    # Test making a prediction
    print("\n🔮 Testing prediction...")
    test_history = [
        {'x': 50, 'y': 50, 'vx': 2, 'vy': 1, 'timestamp': 1},
        {'x': 55, 'y': 48, 'vx': 5, 'vy': -2, 'timestamp': 2},
        {'x': 60, 'y': 45, 'vx': 5, 'vy': -3, 'timestamp': 3},
    ]
    
    predictions = predictor.predict_trajectory(test_history)
    print(f"   Predictions: {predictions}")
    
    print("\n✅ ML Test Complete!")
    print("=" * 40)
    print("Now run: python app.py")
    print("Then open your dashboard to see ML outputs!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 Troubleshooting:")
    print("1. Make sure all ML files are in ML_MODELS/")
    print("2. Check that trained_model.h5 exists")
    print("3. Verify paths are correct")