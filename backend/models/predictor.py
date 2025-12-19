import pickle
import pandas as pd
import numpy as np
from datetime import datetime
import os

class ParkingPredictor:
    def __init__(self):
        # Get absolute path to models
        # current_dir is backend/models
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # project_root is the main campus-parking-predictor folder
        # We go up two levels from backend/models to reach the root
        project_root = os.path.dirname(os.path.dirname(current_dir))
        model_path = os.path.join(project_root, 'ml_models', 'saved_models')
        
        print(f"🔄 Loading ML models from: {model_path}")
        
        # Helper to safely join paths
        def get_path(filename):
            return os.path.join(model_path, filename)

        try:
            # Standard pickle loading preserved from original code
            with open(get_path('occupancy_model.pkl'), 'rb') as f:
                self.occupancy_model = pickle.load(f)
            with open(get_path('search_time_model.pkl'), 'rb') as f:
                self.search_time_model = pickle.load(f)
            with open(get_path('parking_classifier.pkl'), 'rb') as f:
                self.parking_classifier = pickle.load(f)
            with open(get_path('feature_columns.pkl'), 'rb') as f:
                self.feature_columns = pickle.load(f)
            print("✅ Models loaded successfully")
        except FileNotFoundError as e:
            # Matches the error seen in your Render logs
            print(f"⚠️ Warning: Model files not found at {model_path}: {e}")
            raise e
    
    def prepare_features(self, lot_id, timestamp, weather='sunny', temperature=70,
                        is_exam_week=False, capacity=150, prev_occupancy=0.5):
        # All original feature engineering preserved
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        is_weekend = day_of_week >= 5
        
        features = {
            'lot_id': lot_id, 'hour_of_day': hour, 'day_of_week': day_of_week,
            'is_weekend': is_weekend, 'is_exam_week': is_exam_week,
            'temperature': temperature, 'capacity': capacity,
            'hour_sin': np.sin(2 * np.pi * hour / 24),
            'hour_cos': np.cos(2 * np.pi * hour / 24),
            'day_sin': np.sin(2 * np.pi * day_of_week / 7),
            'day_cos': np.cos(2 * np.pi * day_of_week / 7),
            'prev_hour_occupancy': prev_occupancy,
            'prev_2hour_occupancy': prev_occupancy,
            'rolling_avg_occupancy': prev_occupancy,
        }
        
        for w in ['sunny', 'rainy', 'cloudy']:
            features[f'weather_{w}'] = 1 if weather == w else 0
        
        df = pd.DataFrame([features])
        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = 0
        
        return df[self.feature_columns]
    
    def predict(self, lot_id, timestamp=None, **kwargs):
        # All original prediction logic and rounding preserved
        if timestamp is None:
            timestamp = datetime.now()
        
        X = self.prepare_features(lot_id, timestamp, **kwargs)
        occupancy = max(0.0, min(1.0, float(self.occupancy_model.predict(X)[0])))
        search_time = max(0, float(self.search_time_model.predict(X)[0]))
        parking_available = bool(self.parking_classifier.predict(X)[0])
        confidence = float(self.parking_classifier.predict_proba(X)[0][1])
        
        return {
            'lot_id': lot_id,
            'timestamp': timestamp.isoformat(),
            'occupancy_rate': round(occupancy, 3),
            'availability': round(1 - occupancy, 3),
            'search_time_minutes': round(search_time, 1),
            'parking_available': parking_available,
            'confidence': round(confidence, 3)
        }