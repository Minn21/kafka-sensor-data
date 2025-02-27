# producers/sensor_simulator.py
import json
import time
import random
import os
from datetime import datetime
from kafka import KafkaProducer

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
TOPIC_NAME = 'sensor_data'
SENSOR_COUNT = int(os.environ.get('SENSOR_COUNT', 10))
SIMULATION_INTERVAL_MS = int(os.environ.get('SIMULATION_INTERVAL_MS', 500))

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda v: v.encode('utf-8')
)

# Sensor types and their normal ranges
SENSOR_TYPES = {
    'temperature': {'min': 15.0, 'max': 35.0, 'unit': '°C'},
    'humidity': {'min': 30.0, 'max': 70.0, 'unit': '%'},
    'pressure': {'min': 980.0, 'max': 1020.0, 'unit': 'hPa'},
}

# Create sensor IDs and assign types
sensors = []
for i in range(SENSOR_COUNT):
    sensor_type = random.choice(list(SENSOR_TYPES.keys()))
    sensors.append({
        'id': f'sensor-{i+1}',
        'type': sensor_type,
        'location': f'zone-{random.randint(1, 5)}',
        'parameters': SENSOR_TYPES[sensor_type]
    })

def generate_reading(sensor):
    """Generate a realistic sensor reading with occasional anomalies"""
    params = sensor['parameters']
    # 5% chance of an anomaly
    if random.random() < 0.05:
        # Generate a value outside the normal range
        anomaly_factor = random.choice([-1, 1]) * random.uniform(1.1, 1.5)
        if random.random() < 0.5:
            value = params['min'] * anomaly_factor
        else:
            value = params['max'] * anomaly_factor
        is_anomaly = True
    else:
        # Generate a normal value
        value = random.uniform(params['min'], params['max'])
        is_anomaly = False
    
    return {
        'sensor_id': sensor['id'],
        'sensor_type': sensor['type'],
        'location': sensor['location'],
        'value': round(value, 2),
        'unit': params['unit'],
        'timestamp': datetime.now().isoformat(),
        'is_anomaly': is_anomaly
    }

def main():
    """Main simulation loop"""
    print(f"Starting sensor data simulation with {SENSOR_COUNT} sensors")
    print(f"Sending data to Kafka topic '{TOPIC_NAME}' at {KAFKA_BOOTSTRAP_SERVERS}")
    
    try:
        while True:
            for sensor in sensors:
                reading = generate_reading(sensor)
                # Use sensor_id as the key for partitioning
                future = producer.send(
                    TOPIC_NAME,
                    key=reading['sensor_id'],
                    value=reading
                )
                # Log successful sends
                record_metadata = future.get(timeout=10)
                print(f"Sent reading from {reading['sensor_id']} to partition {record_metadata.partition}")
                
            # Introduce a small delay to control the rate
            time.sleep(SIMULATION_INTERVAL_MS / 1000)
    except KeyboardInterrupt:
        print("Simulation stopped by user")
    finally:
        producer.flush()
        producer.close()
        print("Producer closed")

if __name__ == "__main__":
    # Add a small delay to ensure Kafka is ready
    time.sleep(10)
    main()