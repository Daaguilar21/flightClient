#pip install confluent_kafka cassandra-driver
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from confluent_kafka import Consumer, KafkaError
import json

# Cassandra configuration
cassandra_cluster = Cluster(
    ['127.0.0.1'],  # Localhost (change if your IP is different)
    port=9042  # Default Cassandra port
)
session = cassandra_cluster.connect('bp_monitoring')
# Kafka configuration (also try localhost:9092 is 9093 doesn't work)
kafka_conf = {
    'bootstrap.servers': 'localhost:9093',
    'group.id': 'bp_group',
    'auto.offset.reset': 'earliest'
}

# Initialize Consumer
consumer = Consumer(kafka_conf)
consumer.subscribe(['bp'])

def project_into_cassandra(event_data):
    """Inserts the event data into Cassandra."""
    cql = """
    INSERT INTO bp_alerts (patient_name, timestamp, systolic)
    VALUES (%s, %s, %s)
    """
    session.execute(cql, (event_data['patient_name'], event_data['timestamp'],  event_data['systolic']))

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                continue
            else:
                print(msg.error())
                break

        # Deserialize the event data
        event_data = json.loads(msg.value().decode('utf-8'))
        
        # Insert into Cassandra
        if event_data['systolic'] > 160:
            project_into_cassandra(event_data)
            print(f"DEBUG -- DB Alert Projection Service: Inserted event for patient {event_data['patient_name']} into Cassandra... High Blood Pressure Detected!!")
except KeyboardInterrupt:
    pass
finally:
    # Clean up on exit
    consumer.close()
    cassandra_cluster.shutdown()
