from flask import Flask, jsonify, render_template
from pixhawk_data import PixhawkData
import os

app = Flask(__name__)

# Get connection settings from environment variables or use defaults
connection_string = os.environ.get('PIXHAWK_CONNECTION', 'COM7')
baud_rate = int(os.environ.get('PIXHAWK_BAUD', 115200))

pixhawk = PixhawkData(connection_string, baud_rate)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    try:
        data = pixhawk.get_data()
        if data:
            return jsonify(data)
        return jsonify({'error': 'No valid data received from Pixhawk Cube Orange+'})
    except Exception as e:
        return jsonify({'error': f'Error fetching data from Pixhawk Cube Orange+: {str(e)}'})

@app.route('/connect')
def connect():
    success = pixhawk.connect()
    if success:
        return jsonify({'status': 'Connected successfully to Pixhawk Cube Orange+'})
    else:
        return jsonify({'status': 'Connection to Pixhawk Cube Orange+ failed'}), 500

@app.route('/system_status')
def system_status():
    try:
        # Implement a method in PixhawkData to get system status
        status = pixhawk.get_system_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': f'Error fetching system status: {str(e)}'})

if __name__ == '__main__':
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(debug=debug, host=host, port=port)