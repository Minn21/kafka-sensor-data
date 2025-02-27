# consumers/storage_consumer.py
import json
import os
import time
from kafka import KafkaConsumer

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
CONSUMER_GROUP_ID = os.environ.get('CONSUMER_GROUP_ID', 'storage-group')
INPUT_TOPIC = 'sensor_data'

# Initialize Kafka consumer
consumer = KafkaConsumer(
    INPUT_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id=CONSUMER_GROUP_ID,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def main():
    """Main consumer loop"""
    print(f"Starting storage consumer in group '{CONSUMER_GROUP_ID}'")
    print(f"Consuming from '{INPUT_TOPIC}' and storing data")
    
    message_count = 0
    
    try:
        for message in consumer:
            # In a real application, you'd store this in a database
            reading = message.value
            message_count += 1
            
            if message_count % 100 == 0:
                print(f"Stored {message_count} readings so far")
                
    except KeyboardInterrupt:
        print("Consumer stopped by user")
    finally:
        consumer.close()
        print("Consumer closed")

if __name__ == "__main__":
    # Add a small delay to ensure Kafka is ready
    time.sleep(15)
    main()