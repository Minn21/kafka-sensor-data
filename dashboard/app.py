# dashboard/app.py
from flask import Flask, render_template, jsonify
import json
import os
import threading
import time
from kafka import KafkaConsumer

app = Flask(__name__)

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
PROCESSED_TOPIC = 'processed_data'
ALERTS_TOPIC = 'alerts'

# Data storage
sensor_data = {}
alerts = []
last_update = time.time()

def kafka_consumer_thread():
    """Background thread to consume Kafka messages"""
    global sensor_data, alerts, last_update
    
    # Initialize consumers
    processed_consumer = KafkaConsumer(
        PROCESSED_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
        auto_offset_reset='latest',
        group_id='dashboard-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    alerts_consumer = KafkaConsumer(
        ALERTS_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
        auto_offset_reset='latest',
        group_id='dashboard-alerts-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    # Process messages from the processed data topic
    for message in processed_consumer:
        data = message.value
        sensor_id = data['sensor_id']
        sensor_data[sensor_id] = data
        last_update = time.time()
        
        # Keep only the 20 most recent alerts
        while len(alerts) > 20:
            alerts.pop(0)

@app.route('/')
def index():
    """Render the main dashboard"""
    return render_template('index.html')

@app.route('/api/sensor-data')
def get_sensor_data():
    """API endpoint to get current sensor data"""
    return jsonify({
        'sensor_data': list(sensor_data.values()),
        'alerts': alerts,
        'last_update': last_update
    })

if __name__ == '__main__':
    # Start Kafka consumer in a background thread
    consumer_thread = threading.Thread(target=kafka_consumer_thread)
    consumer_thread.daemon = True
    consumer_thread.start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)


