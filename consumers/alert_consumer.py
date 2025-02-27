# consumers/alert_consumer.py
import json
import os
import time
from kafka import KafkaConsumer, KafkaProducer

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
CONSUMER_GROUP_ID = os.environ.get('CONSUMER_GROUP_ID', 'alert-group')
INPUT_TOPIC = 'sensor_data'
OUTPUT_TOPIC = 'alerts'

# Initialize Kafka consumer
consumer = KafkaConsumer(
    INPUT_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id=CONSUMER_GROUP_ID,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Initialize Kafka producer for alerts
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def process_reading(reading):
    """Check if reading needs an alert and send if necessary"""
    if reading['is_anomaly']:
        alert = {
            'sensor_id': reading['sensor_id'],
            'sensor_type': reading['sensor_type'],
            'location': reading['location'],
            'value': reading['value'],
            'timestamp': reading['timestamp'],
            'severity': 'HIGH' if abs(reading['value']) > 1.3 * get_normal_max(reading['sensor_type']) else 'MEDIUM',
            'message': f"Anomaly detected for {reading['sensor_type']} sensor at {reading['location']}"
        }
        producer.send(OUTPUT_TOPIC, value=alert)
        return True
    return False

def get_normal_max(sensor_type):
    """Get the normal maximum value for a sensor type"""
    if sensor_type == 'temperature':
        return 35.0
    elif sensor_type == 'humidity':
        return 70.0
    elif sensor_type == 'pressure':
        return 1020.0
    return 100.0  # Default

def main():
    """Main consumer loop"""
    print(f"Starting alert consumer in group '{CONSUMER_GROUP_ID}'")
    print(f"Consuming from '{INPUT_TOPIC}' and producing alerts to '{OUTPUT_TOPIC}'")
    
    alert_count = 0
    
    try:
        for message in consumer:
            # Process the reading
            reading = message.value
            if process_reading(reading):
                alert_count += 1
                if alert_count % 10 == 0:
                    print(f"Processed {alert_count} alerts so far")
                
    except KeyboardInterrupt:
        print("Consumer stopped by user")
    finally:
        consumer.close()
        producer.close()
        print("Consumer and producer closed")

if __name__ == "__main__":
    # Add a small delay to ensure Kafka is ready
    time.sleep(15)
    main()