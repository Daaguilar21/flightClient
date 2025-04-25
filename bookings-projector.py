# pip install confluent_kafka cassandra-driver

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from confluent_kafka import Consumer, KafkaError
import json
from datetime import datetime


# Cassandra configuration
cassandra_cluster = Cluster(
    ['127.0.0.1'],  # Localhost 
    port=9042
)
session = cassandra_cluster.connect('airtrack_monitoring')  #keyspace

# Kafka configuration
kafka_conf = {
    'bootstrap.servers': 'localhost:9093',
    'group.id': 'flight_booking_group',
    'auto.offset.reset': 'earliest'
}

# Initialize Kafka Consumer
consumer = Consumer(kafka_conf)
consumer.subscribe(['flight_bookings'])

def project_into_cassandra(event_data):
    """Insert qualifying events into corresponding Cassandra tables"""

    # change booking_time from event to align with .cql schema timestamp type (originaly comes as string)
    booking_time = datetime.strptime(event_data['booking_time'], "%Y-%m-%d %H:%M:%S")
    last_updated = datetime.utcnow()

    # CONSUMER 1 - Flight Seat Availability
    if 'seats_left' in event_data and event_data['seats_left'] < 200: #check for scarcity, repreented by 200 seats left
        session.execute("""
            INSERT INTO flight_seat_availability (flight_id, seat_number, is_first_class, is_booked, seats_left, booking_time, last_updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            event_data['flight_id'],
            event_data['seat_number'],
            event_data['is_first_class'],
            True,
            event_data['seats_left'],
            booking_time,
            last_updated
        ))
        print(f"[flight_seat_availability] Inserted seat {event_data['seat_number']} for flight {event_data['flight_id']}.")

    # CONSUMER 2 - Concierge Passenger Info
    if event_data['is_first_class']: #check if booking is VIP, i.e. is_first_class
        session.execute("""
            INSERT INTO concierge_passenger_info (flight_id, customer_id, full_name, seat_number, loyalty_id, booking_time, is_first_class, last_updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            event_data['flight_id'],
            event_data['customer_id'],
            event_data['customer_name'],
            event_data['seat_number'],
            event_data['loyalty_id'],
            booking_time,
            event_data['is_first_class'],
            last_updated
        ))
        print(f"[concierge_passenger_info] Inserted customer {event_data['customer_id']}.")

    # CONSUMER 3 - Loyalty Program Bookings
    if event_data['loyalty_id']: #check if booking is loyalty program member, i.e. has loyalty_id
        session.execute("""
            INSERT INTO loyalty_program_bookings (loyalty_id, booking_time, flight_id, ticket_price, is_first_class, last_updated)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            event_data['loyalty_id'],
            booking_time,
            event_data['flight_id'],
            event_data['ticket_price'],
            event_data['is_first_class'],
            last_updated
        ))
        print(f"[loyalty_program_bookings] Inserted loyalty ID {event_data['loyalty_id']}.")

    # CONSUMER 4 - Insured Flight Records
    if event_data['is_flex_ticket']: #check if booking is insured, i.e. is_flex_ticket
        session.execute("""
            INSERT INTO insurance_booking_records (customer_id, flight_id, booking_time, ticket_price, is_flex_ticket, seat_number, last_updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            event_data['customer_id'],
            event_data['flight_id'],
            booking_time,
            event_data['ticket_price'],
            event_data['is_flex_ticket'],
            event_data['seat_number'],
            last_updated
        ))
        print(f"[insurance_booking_records] Inserted customer {event_data['customer_id']}.")


# Main consumer loop
try:
    print("Kafka Consumer Started: Listening to 'flight_bookings' topic...")
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

        # Deserialize Kafka message
        event_data = json.loads(msg.value().decode('utf-8'))

        # Project into Cassandra with filtering
        project_into_cassandra(event_data)

except KeyboardInterrupt:
    pass
finally:
    # Clean up connections
    consumer.close()
    cassandra_cluster.shutdown()
    print("Kafka Consumer and Cassandra connection closed.")
