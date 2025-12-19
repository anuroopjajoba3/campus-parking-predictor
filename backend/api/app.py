from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append('../..')

# Import ML predictor
try:
    from backend.models.predictor import ParkingPredictor
    predictor = ParkingPredictor()
    print("✅ ML Predictor loaded successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not load ML predictor: {e}")
    predictor = None

# Import auth blueprint
sys.path.append('..')
from auth import auth_bp, token_required, admin_required

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Register authentication blueprint
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# --- UPDATED DATABASE CONFIGURATION FOR RAILWAY ---
# Priority 1: Railway Variables | Priority 2: Local MacBook Default
DB_CONFIG = {
    'host': os.getenv('MYSQLHOST', 'localhost'),
    'user': os.getenv('MYSQLUSER', 'root'),
    'password': os.getenv('MYSQLPASSWORD', 'Verizonsam@9896'),
    'database': os.getenv('MYSQLDATABASE', 'parking_db'),
    'port': int(os.getenv('MYSQLPORT', 3306))
}

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
        "environment": "production" if os.getenv('MYSQLHOST') else "development",
        "database": db_status,
        "ml_models": ml_status
    })

@app.route('/api/lots', methods=['GET'])
def get_parking_lots():
    """Get all parking lots with current occupancy."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT 
            l.lot_id,
            l.name,
            l.capacity,
            l.building_proximity,
            l.type as lot_type,
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
    """Get aggregate statistics for the dashboard."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT COUNT(*) as total_events FROM parking_events")
        total = cursor.fetchone()
        
        cursor.execute("""
            SELECT COALESCE(ROUND(AVG(search_time_minutes), 2), 0) as average_search_time
            FROM parking_events 
            WHERE search_time_minutes IS NOT NULL
        """)
        avg_time = cursor.fetchone()
        
        cursor.execute("""
            SELECT COUNT(DISTINCT e1.registered_user_id) as occupied_spaces
            FROM parking_events e1
            WHERE e1.event_type = 'entry'
            AND e1.registered_user_id IS NOT NULL
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
        print(f"ERROR in /api/stats: {str(e)}")
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
        print(f"ERROR in /api/predict/all: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/report/entry', methods=['POST'])
@token_required
def report_entry(current_user):
    """Record parking entry for an authenticated user."""
    data = request.json
    lot_id = data.get('lot_id')
    search_time = data.get('search_time_minutes', 0)
    weather = data.get('weather', 'sunny')
    temperature = data.get('temperature', 70)
    spot_number = data.get('spot_number')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        day_of_week = datetime.now().weekday()
        
        cursor.execute("""
            INSERT INTO parking_events 
            (lot_id, user_id, event_type, timestamp, search_time_minutes, 
             weather, temperature, day_of_week, registered_user_id, spot_number)
            VALUES (%s, %s, 'entry', NOW(), %s, %s, %s, %s, %s, %s)
        """, (lot_id, current_user['email'], search_time, weather, temperature, 
              day_of_week, current_user['user_id'], spot_number))
        
        conn.commit()
        event_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True, 
            "message": f"Entry recorded for spot {spot_number}",
            "event_id": event_id
        })
    except Error as e:
        print(f"❌ ERROR in /api/report/entry: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/report/exit', methods=['POST'])
@token_required
def report_exit(current_user):
    """Record parking exit for an authenticated user."""
    data = request.json
    lot_id = data.get('lot_id')
    spot_number = data.get('spot_number')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        day_of_week = datetime.now().weekday()
        
        cursor.execute("""
            INSERT INTO parking_events 
            (lot_id, user_id, event_type, timestamp, day_of_week, registered_user_id, spot_number)
            VALUES (%s, %s, 'exit', NOW(), %s, %s, %s)
        """, (lot_id, current_user['email'], day_of_week, current_user['user_id'], spot_number))
        
        conn.commit()
        event_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True, 
            "message": f"Exit recorded from spot {spot_number}",
            "event_id": event_id
        })
    except Error as e:
        print(f"❌ ERROR in /api/report/exit: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/lots/<int:lot_id>/occupied-spots', methods=['GET'])
def get_occupied_spots(lot_id):
    """Get a list of currently occupied spots for a specific lot."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT DISTINCT e1.spot_number
            FROM parking_events e1
            WHERE e1.lot_id = %s
            AND e1.event_type = 'entry'
            AND e1.spot_number IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM parking_events e2
                WHERE e2.lot_id = e1.lot_id
                AND e2.registered_user_id = e1.registered_user_id
                AND e2.spot_number = e1.spot_number
                AND e2.event_type = 'exit'
                AND e2.timestamp > e1.timestamp
            )
        """, (lot_id,))
        
        occupied_spots = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True, 
            "lot_id": lot_id,
            "occupied_spots": [spot['spot_number'] for spot in occupied_spots]
        })
    except Error as e:
        print(f"❌ ERROR in /api/lots/{lot_id}/occupied-spots: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/admin/dashboard', methods=['GET'])
@token_required
@admin_required
def admin_dashboard(current_user):
    """Fetch detailed analytics for the Admin view."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_events,
                COUNT(CASE WHEN event_type = 'entry' THEN 1 END) as total_entries,
                COUNT(CASE WHEN event_type = 'exit' THEN 1 END) as total_exits,
                COALESCE(AVG(search_time_minutes), 0) as avg_search_time
            FROM parking_events
        """)
        stats = cursor.fetchone()
        
        cursor.execute("""
            SELECT COUNT(DISTINCT e1.registered_user_id) as occupied_spaces
            FROM parking_events e1
            WHERE e1.event_type = 'entry'
            AND e1.registered_user_id IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM parking_events e2
                WHERE e2.registered_user_id = e1.registered_user_id
                AND e2.event_type = 'exit'
                AND e2.timestamp > e1.timestamp
            )
        """)
        occupied = cursor.fetchone()
        stats['occupied_spaces'] = occupied['occupied_spaces']
        
        cursor.execute("SELECT SUM(capacity) as total_spaces FROM parking_lots")
        capacity = cursor.fetchone()
        stats['total_spaces'] = capacity['total_spaces']
        
        cursor.execute("""
            SELECT 
                l.lot_id,
                l.name,
                l.capacity,
                l.type,
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
        """)
        lots = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'stats': stats, 'lots': lots})
    except Error as e:
        print(f"ERROR in /api/admin/dashboard: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Railway provides the port via the PORT environment variable
    port = int(os.environ.get("PORT", 5001))
    print(f"🚀 Starting Flask API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)