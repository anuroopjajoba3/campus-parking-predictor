import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_synthetic_parking_data(num_days=90, lots=5):
    """
    Generate realistic parking data for training
    Simulates 90 days of parking patterns
    """
    data = []
    start_date = datetime.now() - timedelta(days=num_days)
    
    for day in range(num_days):
        current_date = start_date + timedelta(days=day)
        day_of_week = current_date.weekday()  # 0=Monday, 6=Sunday
        is_weekend = day_of_week >= 5
        
        # Generate hourly data for each lot
        for hour in range(6, 23):  # 6 AM to 11 PM
            timestamp = current_date.replace(hour=hour, minute=0, second=0)
            
            for lot_id in range(1, lots + 1):
                # Base occupancy depends on time and day
                if is_weekend:
                    base_occupancy = 0.2  # Weekends less busy
                else:
                    # Peak hours: 9-11 AM and 2-4 PM
                    if 9 <= hour <= 11:
                        base_occupancy = 0.85  # Morning rush
                    elif 14 <= hour <= 16:
                        base_occupancy = 0.75  # Afternoon peak
                    elif 12 <= hour <= 14:
                        base_occupancy = 0.60  # Lunch time
                    elif 8 <= hour <= 9 or 16 <= hour <= 17:
                        base_occupancy = 0.70  # Transition times
                    else:
                        base_occupancy = 0.30  # Off-peak
                
                # Add randomness
                occupancy = base_occupancy + np.random.normal(0, 0.1)
                occupancy = max(0.0, min(1.0, occupancy))  # Clamp to [0, 1]
                
                # Weather impact
                weather = random.choice(['sunny', 'sunny', 'sunny', 'rainy', 'cloudy'])
                if weather == 'rainy':
                    occupancy = min(1.0, occupancy * 1.2)  # More drivers in rain
                
                # Temperature impact
                temperature = random.randint(30, 85)
                if temperature < 40 or temperature > 80:
                    occupancy = min(1.0, occupancy * 1.1)  # Extreme temps
                
                # Exam week impact (last week of month)
                is_exam_week = (day % 30) >= 26
                if is_exam_week:
                    occupancy = min(1.0, occupancy * 1.3)
                
                # Calculate derived features
                capacity_map = {1: 150, 2: 200, 3: 100, 4: 50, 5: 30}
                capacity = capacity_map[lot_id]
                current_count = int(occupancy * capacity)
                availability = 1 - occupancy
                
                # Search time (inversely proportional to availability)
                if availability > 0.3:
                    search_time = random.randint(1, 3)
                elif availability > 0.1:
                    search_time = random.randint(3, 8)
                else:
                    search_time = random.randint(8, 15)
                
                data.append({
                    'timestamp': timestamp,
                    'lot_id': lot_id,
                    'hour_of_day': hour,
                    'day_of_week': day_of_week,
                    'is_weekend': is_weekend,
                    'is_exam_week': is_exam_week,
                    'weather': weather,
                    'temperature': temperature,
                    'capacity': capacity,
                    'current_count': current_count,
                    'occupancy_rate': occupancy,
                    'availability': availability,
                    'search_time_minutes': search_time,
                    'found_parking': availability > 0.05
                })
    
    df = pd.DataFrame(data)
    return df

if __name__ == '__main__':
    print("🔄 Generating synthetic parking data...")
    df = generate_synthetic_parking_data(num_days=90, lots=5)
    
    # Save to CSV
    output_file = 'ml_models/training/parking_data.csv'
    df.to_csv(output_file, index=False)
    
    print(f"✅ Generated {len(df)} records")
    print(f"📁 Saved to: {output_file}")
    print(f"\n📊 Data Preview:")
    print(df.head(10))
    print(f"\n📈 Statistics:")
    print(df.describe())
    print(f"\n📅 Date Range: {df['timestamp'].min()} to {df['timestamp'].max()}")
