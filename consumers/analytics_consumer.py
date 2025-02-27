# consumers/analytics_consumer.py
import json
import os
import time
from kafka import KafkaConsumer, KafkaProducer
from collections import defaultdict

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
CONSUMER_GROUP_ID = os.environ.get('CONSUMER_GROUP_ID', 'analytics-group')
INPUT_TOPIC = 'sensor_data'
OUTPUT_TOPIC = 'processed_data'

# Initialize Kafka consumer
consumer = KafkaConsumer(
    INPUT_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id=CONSUMER_GROUP_ID,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Initialize Kafka producer for processed data
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Analytics state
window_size = 60  # seconds
sensor_readings = defaultdict(list)
last_process_time = time.time()

def process_window():
    """Process the current window of data and produce analytics results"""
    current_time = time.time()
    results = []
    
    # Process each sensor's data
    for sensor_id, readings in sensor_readings.items():
        if not readings:
            continue
            
        # Extract sensor type and location from the first reading
        sensor_type = readings[0]['sensor_type']
        location = readings[0]['location']
        
        # Calculate basic statistics
        values = [r['value'] for r in readings]
        avg_value = sum(values) / len(values)
        min_value = min(values)
        max_value = max(values)
        
        # Count anomalies
        anomaly_count = sum(1 for r in readings if r['is_anomaly'])
        
        # Create result record
        result = {
            'sensor_id': sensor_id,
            'sensor_type': sensor_type,
            'location': location,
            'window_start': current_time - window_size,
            'window_end': current_time,
            'avg_value': round(avg_value, 2),
            'min_value': round(min_value, 2),
            'max_value': round(max_value, 2),
            'reading_count': len(readings),
            'anomaly_count': anomaly_count
        }
        results.append(result)
    
    # Send results to the processed_data topic
    for result in results:
        producer.send(OUTPUT_TOPIC, value=result)
    
    # Clear the window
    sensor_readings.clear()
    
    return len(results)

def main():
    """Main consumer loop"""
    global last_process_time
    
    print(f"Starting analytics consumer in group '{CONSUMER_GROUP_ID}'")
    print(f"Consuming from '{INPUT_TOPIC}' and producing to '{OUTPUT_TOPIC}'")
    
    try:
        for message in consumer:
            # Get the sensor reading
            reading = message.value
            sensor_id = reading['sensor_id']
            
            # Add to the current window
            sensor_readings[sensor_id].append(reading)
            
            # Check if it's time to process the window
            current_time = time.time()
            if current_time - last_process_time >= window_size:
                processed_count = process_window()
                print(f"Processed window with {processed_count} sensor results")
                last_process_time = current_time
                
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