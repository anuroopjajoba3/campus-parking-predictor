import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, accuracy_score, classification_report
import xgboost as xgb
import pickle
import os

print("📚 Loading training data...")
df = pd.read_csv('ml_models/training/parking_data.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])

print(f"✅ Loaded {len(df)} records")

# Feature engineering
def create_features(df):
    """Create features for ML model"""
    df = df.copy()
    
    # Time-based features (cyclical encoding)
    df['hour_sin'] = np.sin(2 * np.pi * df['hour_of_day'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour_of_day'] / 24)
    df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
    
    # One-hot encode weather
    weather_dummies = pd.get_dummies(df['weather'], prefix='weather')
    df = pd.concat([df, weather_dummies], axis=1)
    
    # Lag features (previous hour's occupancy)
    df = df.sort_values(['lot_id', 'timestamp'])
    df['prev_hour_occupancy'] = df.groupby('lot_id')['occupancy_rate'].shift(1)
    df['prev_2hour_occupancy'] = df.groupby('lot_id')['occupancy_rate'].shift(2)
    
    # Rolling average
    df['rolling_avg_occupancy'] = df.groupby('lot_id')['occupancy_rate'].transform(
        lambda x: x.rolling(window=3, min_periods=1).mean()
    )
    
    # Fill NaN values
    df = df.fillna(df.mean(numeric_only=True))
    
    return df

print("🔧 Creating features...")
df = create_features(df)

# Define features and targets
feature_columns = [
    'lot_id', 'hour_of_day', 'day_of_week', 'is_weekend', 'is_exam_week',
    'temperature', 'capacity', 'hour_sin', 'hour_cos', 'day_sin', 'day_cos',
    'prev_hour_occupancy', 'prev_2hour_occupancy', 'rolling_avg_occupancy'
]

# Add weather columns
weather_cols = [col for col in df.columns if col.startswith('weather_')]
feature_columns.extend(weather_cols)

X = df[feature_columns]
y_occupancy = df['occupancy_rate']
y_search_time = df['search_time_minutes']
y_found_parking = df['found_parking']

# Split data
X_train, X_test, y_occ_train, y_occ_test = train_test_split(
    X, y_occupancy, test_size=0.2, random_state=42
)
_, _, y_search_train, y_search_test = train_test_split(
    X, y_search_time, test_size=0.2, random_state=42
)
_, _, y_found_train, y_found_test = train_test_split(
    X, y_found_parking, test_size=0.2, random_state=42
)

print("\n" + "="*70)
print("MODEL 1: OCCUPANCY PREDICTION (Regression)")
print("="*70)
occupancy_model = xgb.XGBRegressor(
    n_estimators=200,
    learning_rate=0.1,
    max_depth=5,
    random_state=42
)
occupancy_model.fit(X_train, y_occ_train)
y_occ_pred = occupancy_model.predict(X_test)
mae = mean_absolute_error(y_occ_test, y_occ_pred)
print(f"✅ Mean Absolute Error: {mae:.3f}")
print(f"📊 Average Actual Occupancy: {y_occ_test.mean():.3f}")
print(f"🎯 Accuracy: {(1 - mae) * 100:.1f}%")

print("\n" + "="*70)
print("MODEL 2: SEARCH TIME PREDICTION (Regression)")
print("="*70)
search_time_model = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    random_state=42
)
search_time_model.fit(X_train, y_search_train)
y_search_pred = search_time_model.predict(X_test)
mae_search = mean_absolute_error(y_search_test, y_search_pred)
print(f"✅ Mean Absolute Error: {mae_search:.2f} minutes")
print(f"📊 Average Actual Search Time: {y_search_test.mean():.2f} minutes")

print("\n" + "="*70)
print("MODEL 3: PARKING AVAILABLE (Classification)")
print("="*70)
parking_classifier = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42
)
parking_classifier.fit(X_train, y_found_train)
y_found_pred = parking_classifier.predict(X_test)
accuracy = accuracy_score(y_found_test, y_found_pred)
print(f"✅ Classification Accuracy: {accuracy*100:.1f}%")
print("\n📋 Classification Report:")
print(classification_report(y_found_test, y_found_pred))

# Feature importance
print("\n" + "="*70)
print("TOP 10 MOST IMPORTANT FEATURES")
print("="*70)
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': occupancy_model.feature_importances_
}).sort_values('importance', ascending=False)
print(feature_importance.head(10))

# Save models
print("\n💾 Saving models...")
os.makedirs('ml_models/saved_models', exist_ok=True)

with open('ml_models/saved_models/occupancy_model.pkl', 'wb') as f:
    pickle.dump(occupancy_model, f)

with open('ml_models/saved_models/search_time_model.pkl', 'wb') as f:
    pickle.dump(search_time_model, f)

with open('ml_models/saved_models/parking_classifier.pkl', 'wb') as f:
    pickle.dump(parking_classifier, f)

with open('ml_models/saved_models/feature_columns.pkl', 'wb') as f:
    pickle.dump(feature_columns, f)

print("✅ All models saved successfully!")
print(f"📁 Models saved to: ml_models/saved_models/")
