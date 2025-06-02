A demonstration project for processing simulated IoT sensor data through an Apache Kafka pipeline.

## Overview

This project demonstrates a complete real-time data pipeline using Apache Kafka for processing sensor data. It simulates IoT temperature, humidity, and pressure sensors generating data, which is then processed by multiple consumer applications for different purposes.

### Key Components

- **3-node Kafka Cluster**: A fault-tolerant distributed messaging system
- **Zookeeper**: Coordinates the Kafka cluster
- **Producer**: Generates simulated sensor readings
- **Multiple Consumers**: Process the data for different purposes
- **Web Dashboard**: Visualizes the processed data in real-time

## Architecture

The system uses a classic producer-consumer architecture with Kafka as the central message broker:

```
Sensor Data Simulator (Producer) → Kafka → Multiple Consumers → Analytics Dashboard
```

Data flows through the following pipeline:
1. The producer generates simulated sensor readings
2. Messages are published to Kafka topics with partitioning based on sensor ID
3. Three independent consumer applications process the data:
   - Alert Consumer: Detects anomalies and generates alerts
   - Analytics Consumer: Calculates statistics in time windows
   - Storage Consumer: Simulates persistence (would connect to a database in production)
4. The dashboard application displays processed data and alerts

## Prerequisites

- Docker and Docker Compose
- Git (for cloning the repository)

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Minn21/kafka-sensor-project.git
cd kafka-sensor-project
```

### 2. Start the Services

```bash
docker-compose up -d
```

This will:
- Start the Zookeeper service
- Launch a 3-node Kafka cluster
- Create the required Kafka topics
- Start the producer and consumer services
- Launch the web dashboard

### 3. Access the Dashboard

Open your browser and navigate to:

```
http://localhost:5000
```

You should see the dashboard displaying real-time sensor data and alerts.

## Project Structure

```
kafka-sensor-project/
├── docker-compose.yml             # Service configuration
├── producers/
│   ├── sensor_simulator.py        # Generates simulated sensor data
│   ├── Dockerfile                 # Container definition for producer
│   └── requirements.txt           # Python dependencies
├── consumers/
│   ├── alert_consumer.py          # Processes data for anomaly detection
│   ├── analytics_consumer.py      # Calculates statistics in time windows
│   ├── storage_consumer.py        # Simulates data persistence
│   ├── Dockerfile.alert           # Container for alert consumer
│   ├── Dockerfile.analytics       # Container for analytics consumer
│   ├── Dockerfile.storage         # Container for storage consumer
│   └── requirements.txt           # Python dependencies
└── dashboard/
    ├── app.py                     # Flask web application
    ├── templates/
    │   └── index.html             # Dashboard UI
    ├── Dockerfile                 # Container for web dashboard
    └── requirements.txt           # Python dependencies
```

## Key Kafka Concepts Demonstrated

This project demonstrates several key Kafka concepts:

1. **Multi-broker Cluster**: A 3-node Kafka cluster showing horizontal scaling
2. **Replication**: Messages are replicated across brokers for fault tolerance
3. **Partitioning**: Data is distributed across partitions using sensor IDs as keys
4. **Consumer Groups**: Different applications process the same data independently
5. **Real-time Processing**: Data flows through the system with minimal latency

## Exploring the System

### Useful Kafka Commands

Here are some useful commands to explore the Kafka cluster:

```bash
# List all topics
docker exec kafka-1 kafka-topics --bootstrap-server kafka-1:29092 --list

# Describe a specific topic
docker exec kafka-1 kafka-topics --bootstrap-server kafka-1:29092 --describe --topic sensor_data

# List consumer groups
docker exec kafka-1 kafka-consumer-groups --bootstrap-server kafka-1:29092 --list

# Check consumer group lag
docker exec kafka-1 kafka-consumer-groups --bootstrap-server kafka-1:29092 --describe --group alert-group
```

### Testing Fault Tolerance

To demonstrate Kafka's fault tolerance:

```bash
# Stop one broker
docker stop kafka-2

# System should continue functioning
# Check the dashboard to confirm data still flows

# Restart the broker
docker start kafka-2
```

## Shutting Down

When you're done exploring:

```bash
docker-compose down
```

To clean up completely (including volumes):

```bash
docker-compose down -v
```
