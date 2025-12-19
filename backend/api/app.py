from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import sys
import os
import urllib.parse as up

# --- DYNAMIC PATH HANDLING FOR NESTED STRUCTURE ---
# Since app.py is in /backend/api, we need to add the /backend folder 
# to sys.path so it can find 'auth.py' and the 'models' folder.
current_dir = os.path.dirname(os.path.abspath(__file__)) # This is /backend/api
parent_dir = os.path.dirname(current_dir)               # This is /backend
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# --- INTERNAL IMPORTS ---
try:
    # Now that 'parent_dir' is in path, we can import from the backend root
    from models.predictor import ParkingPredictor
    predictor = ParkingPredictor()
    print("✅ ML Predictor loaded successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not load ML predictor: {e}")
    predictor = None

try:
    # Import auth from the /backend directory level
    from auth import auth_bp, token_required, admin_required
except ImportError as e:
    print(f"❌ Critical Error: Could not load auth module: {e}")
    # Fallback to prevent immediate crash if structure varies
    from backend.auth import auth_bp, token_required, admin_required

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Register authentication blueprint
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# --- DYNAMIC DATABASE CONFIGURATION ---
db_url = os.getenv('DATABASE_URL')

if db_url:
    # Parsing Cloud connection string: mysql://user:pass@host:port/dbname
    up.uses_netloc.append("mysql")
    url = up.urlparse(db_url)
    DB_CONFIG = {
        'host': url.hostname,
        'user': url.username,
        'password': url.password,
        'database': url.path[1:], # Removes the leading slash
        'port': url.port or 3306
    }
    print(f"🌐 Cloud Mode: Connected to {url.hostname}")
else:
    # Local MacBook configuration
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Verizonsam@9896',
        'database': 'parking_db',
        'port': 3306
    }
    print("💻 Local Mode: Connected to Localhost")

def get_db_connection():
    """Establishes a connection to the database using configured credentials."""
    return mysql.connector.connect(**DB_CONFIG)

# --- ROUTES ---

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify database and ML status."""
    try:
        conn = get_db_connection()
        conn.close()
        db_status = "connected"
    except Exception as e:
        print(f"Health check error: {e}")
        db_status = "disconnected"
    
    ml_status = "loaded" if predictor else "not loaded"
    
    return jsonify({
        "status": "healthy",
        "environment": "production" if os.getenv('DATABASE_URL') else "development",
        "database": db_status,
        "ml_models": ml_status
    })

@app.route('/api/lots', methods=['GET'])
def get_parking_lots():
    """Get all parking lots with current occupancy based on live events."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT 
            l.lot_id, l.name, l.capacity, l.building_proximity, l.type as lot_type,
            COALESCE(
                (SELECT COUNT(DISTINCT e1.registered_user_id)
                 FROM parking_events e1
                 WHERE e1.lot_id = l.lot_id 
                 AND e1.event_type = 'entry'
                 AND e1.registered_user_id IS NOT NULL
                 AND NOT EXISTS (
                     SELECT 1 FROM parking_events e2
                     WHERE e2.lot_id = e1.lot_id
                     AND e2.registered_user_id = e1.registered_user_id
                     AND e2.event_type = 'exit'
                     AND e2.timestamp > e1.timestamp
                 )), 0
            ) as current_count
        FROM parking_lots l
        ORDER BY l.lot_id
        """
        cursor.execute(query)
        lots = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": lots})
    except Error as e:
        print(f"ERROR in /api/lots: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get aggregate statistics for the dashboard header."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT COUNT(*) as total_events FROM parking_events")
        total = cursor.fetchone()
        
        cursor.execute("""
            SELECT COALESCE(ROUND(AVG(search_time_minutes), 2), 0) as average_search_time
            FROM parking_events WHERE search_time_minutes IS NOT NULL
        """)
        avg_time = cursor.fetchone()
        
        cursor.execute("""
            SELECT COUNT(DISTINCT e1.registered_user_id) as occupied_spaces
            FROM parking_events e1
            WHERE e1.event_type = 'entry'
            AND NOT EXISTS (
                SELECT 1 FROM parking_events e2
                WHERE e2.registered_user_id = e1.registered_user_id
                AND e2.event_type = 'exit'
                AND e2.timestamp > e1.timestamp
            )
        """)
        occupied = cursor.fetchone()
        
        cursor.execute("SELECT COALESCE(SUM(capacity), 0) as total_spaces FROM parking_lots")
        capacity = cursor.fetchone()
        
        stats = {
            'total_events': total['total_events'],
            'average_search_time': avg_time['average_search_time'],
            'occupied_spaces': occupied['occupied_spaces'],
            'total_spaces': capacity['total_spaces']
        }
        
        if stats['total_spaces'] > 0:
            stats['overall_availability'] = round(
                ((stats['total_spaces'] - stats['occupied_spaces']) / stats['total_spaces']) * 100, 1
            )
        else:
            stats['overall_availability'] = 100.0
        
        cursor.close()
        conn.close()
        return jsonify({"success": True, "stats": stats})
    except Error as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/predict/all', methods=['GET'])
def predict_all_lots():
    """Get ML predictions for all parking lots."""
    if not predictor:
        return jsonify({"success": False, "error": "ML predictor not available"}), 503
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

@app.route('/api/report/entry', methods=['POST'])
@token_required
def report_entry(current_user):
    """Record parking entry (authenticated users)."""
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO parking_events 
            (lot_id, user_id, event_type, timestamp, search_time_minutes, weather, temperature, day_of_week, registered_user_id, spot_number)
            VALUES (%s, %s, 'entry', NOW(), %s, %s, %s, %s, %s, %s)
        """, (data.get('lot_id'), current_user['email'], data.get('search_time_minutes', 0), 
              data.get('weather', 'sunny'), data.get('temperature', 70), 
              datetime.now().weekday(), current_user['user_id'], data.get('spot_number')))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Entry recorded"})
    except Error as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/report/exit', methods=['POST'])
@token_required
def report_exit(current_user):
    """Record parking exit (authenticated users)."""
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO parking_events 
            (lot_id, user_id, event_type, timestamp, day_of_week, registered_user_id, spot_number)
            VALUES (%s, %s, 'exit', NOW(), %s, %s, %s)
        """, (data.get('lot_id'), current_user['email'], datetime.now().weekday(), 
              current_user['user_id'], data.get('spot_number')))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Exit recorded"})
    except Error as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/lots/<int:lot_id>/occupied-spots', methods=['GET'])
def get_occupied_spots(lot_id):
    """Get list of currently occupied spots for a parking lot."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT DISTINCT e1.spot_number FROM parking_events e1
            WHERE e1.lot_id = %s AND e1.event_type = 'entry' AND e1.spot_number IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM parking_events e2
                WHERE e2.lot_id = e1.lot_id AND e2.registered_user_id = e1.registered_user_id
                AND e2.spot_number = e1.spot_number AND e2.event_type = 'exit' AND e2.timestamp > e1.timestamp
            )
        """, (lot_id,))
        occupied = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "occupied_spots": [s['spot_number'] for s in occupied]})
    except Error as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    # PORT is provided by Render, defaults to 5001 locally
    port = int(os.environ.get("PORT", 5001))
    print(f"🚀 Starting Flask API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)