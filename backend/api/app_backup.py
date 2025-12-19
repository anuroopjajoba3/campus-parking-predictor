from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv
import sys

# Add parent directory to path for ML models
sys.path.append('../..')
from backend.models.predictor import ParkingPredictor

load_dotenv(dotenv_path='../../.env')

app = Flask(__name__)
CORS(app)

# Initialize ML Predictor
try:
    predictor = ParkingPredictor()
    print("✅ ML Predictor loaded successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not load ML models: {e}")
    predictor = None

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        conn = get_db_connection()
        conn.close()
        ml_status = "loaded" if predictor else "not loaded"
        return jsonify({"status": "healthy", "database": "connected", "ml_models": ml_status})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

# Get all parking lots
@app.route('/api/lots', methods=['GET'])
def get_lots():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT l.lot_id, l.name, l.capacity, l.latitude, l.longitude,
                   l.building_proximity, l.type, c.current_count, 
                   c.availability_percentage, c.last_updated, c.trend
            FROM parking_lots l
            LEFT JOIN current_occupancy c ON l.lot_id = c.lot_id
            ORDER BY l.name
        """)
        lots = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": lots, "count": len(lots)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Report parking entry
@app.route('/api/report/entry', methods=['POST'])
def report_entry():
    try:
        data = request.json
        user_id = data.get('user_id')
        lot_id = data.get('lot_id')
        search_time = data.get('search_time_minutes', 0)
        weather = data.get('weather', 'unknown')
        temperature = data.get('temperature', 70)
        
        if not user_id or not lot_id:
            return jsonify({"success": False, "error": "user_id and lot_id required"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO parking_events 
            (lot_id, user_id, event_type, timestamp, search_time_minutes, weather, temperature, day_of_week)
            VALUES (%s, %s, 'entry', NOW(), %s, %s, %s, DAYOFWEEK(NOW()))
        """, (lot_id, user_id, search_time, weather, temperature))
        
        cursor.execute("""
            UPDATE current_occupancy 
            SET current_count = LEAST(current_count + 1, capacity),
                last_updated = NOW(),
                availability_percentage = ((capacity - LEAST(current_count + 1, capacity)) / capacity) * 100,
                trend = 'increasing'
            WHERE lot_id = %s
        """, (lot_id,))
        
        conn.commit()
        
        cursor.execute("""
            SELECT current_count, capacity, availability_percentage 
            FROM current_occupancy WHERE lot_id = %s
        """, (lot_id,))
        occupancy = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Entry recorded",
            "occupancy": {
                "current_count": occupancy[0],
                "capacity": occupancy[1],
                "availability": occupancy[2]
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Report parking exit
@app.route('/api/report/exit', methods=['POST'])
def report_exit():
    try:
        data = request.json
        user_id = data.get('user_id')
        lot_id = data.get('lot_id')
        
        if not user_id or not lot_id:
            return jsonify({"success": False, "error": "user_id and lot_id required"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO parking_events 
            (lot_id, user_id, event_type, timestamp, day_of_week)
            VALUES (%s, %s, 'exit', NOW(), DAYOFWEEK(NOW()))
        """, (lot_id, user_id))
        
        cursor.execute("""
            UPDATE current_occupancy 
            SET current_count = GREATEST(current_count - 1, 0),
                last_updated = NOW(),
                availability_percentage = ((capacity - GREATEST(current_count - 1, 0)) / capacity) * 100,
                trend = 'decreasing'
            WHERE lot_id = %s
        """, (lot_id,))
        
        conn.commit()
        
        cursor.execute("""
            SELECT current_count, capacity, availability_percentage 
            FROM current_occupancy WHERE lot_id = %s
        """, (lot_id,))
        occupancy = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Exit recorded",
            "occupancy": {
                "current_count": occupancy[0],
                "capacity": occupancy[1],
                "availability": occupancy[2]
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Get current occupancy for all lots
@app.route('/api/occupancy/current', methods=['GET'])
def get_current_occupancy():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT l.lot_id, l.name, l.capacity, l.latitude, l.longitude,
                   c.current_count, c.availability_percentage, c.last_updated, c.trend
            FROM parking_lots l
            JOIN current_occupancy c ON l.lot_id = c.lot_id
            ORDER BY c.availability_percentage DESC
        """)
        
        occupancy = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "data": occupancy})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Get parking statistics
@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT COUNT(*) as total FROM parking_events")
        total_events = cursor.fetchone()['total']
        
        cursor.execute("SELECT AVG(search_time_minutes) as avg_time FROM parking_events WHERE search_time_minutes IS NOT NULL")
        avg_search = cursor.fetchone()['avg_time'] or 0
        
        cursor.execute("SELECT SUM(current_count) as occupied, SUM(capacity) as total FROM current_occupancy")
        occupancy = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "stats": {
                "total_events": total_events,
                "total_user_reports": 0,
                "average_search_time": round(avg_search, 2),
                "total_spaces": occupancy['total'],
                "occupied_spaces": occupancy['occupied'],
                "overall_availability": round(((occupancy['total'] - occupancy['occupied']) / occupancy['total']) * 100, 1)
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ML PREDICTION ENDPOINTS
@app.route('/api/predict/all', methods=['GET'])
def predict_all_lots():
    """Predict parking for all lots"""
    if not predictor:
        return jsonify({"success": False, "error": "ML models not loaded"}), 500
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT lot_id, name, capacity FROM parking_lots")
        lots = cursor.fetchall()
        cursor.close()
        conn.close()
        
        predictions = []
        for lot in lots:
            pred = predictor.predict(lot_id=lot['lot_id'], capacity=lot['capacity'])
            pred['lot_name'] = lot['name']
            predictions.append(pred)
        
        return jsonify({"success": True, "predictions": predictions})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict_parking():
    """Predict parking availability for a specific lot"""
    if not predictor:
        return jsonify({"success": False, "error": "ML models not loaded"}), 500
    
    try:
        data = request.json
        lot_id = data.get('lot_id')
        
        if not lot_id:
            return jsonify({"success": False, "error": "lot_id required"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM parking_lots WHERE lot_id = %s", (lot_id,))
        lot = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not lot:
            return jsonify({"success": False, "error": "Lot not found"}), 404
        
        timestamp_str = data.get('timestamp')
        timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.now()
        
        prediction = predictor.predict(
            lot_id=lot_id,
            timestamp=timestamp,
            capacity=lot['capacity'],
            weather=data.get('weather', 'sunny'),
            temperature=data.get('temperature', 70)
        )
        
        prediction['lot_name'] = lot['name']
        return jsonify({"success": True, "prediction": prediction})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5001))
    print(f"🚀 Starting Flask API on http://localhost:{port}")
    print(f"📊 Database: {os.getenv('DB_NAME')}")
    app.run(debug=True, port=port, host='0.0.0.0')