import time
from datetime import datetime
from cassandra.cluster import Cluster

def main():
    cassandra_cluster = Cluster(['127.0.0.1'], port=9042)
    session = cassandra_cluster.connect('airtrack_monitoring')
    previous_poll_time = datetime.utcnow()

    try:
        print("Connected to Cassandra (loyalty_program_bookings).")
        while True:
            rows = session.execute("""
                SELECT loyalty_id, flight_id, ticket_price FROM loyalty_program_bookings
                WHERE last_updated > %s ALLOW FILTERING
            """, (previous_poll_time,)) #compare the last updated time with the previous poll time to get only the latest updates
            for row in rows:
                print(f"[Loyalty Booking] Loyalty ID {row.loyalty_id} booked Flight {row.flight_id} for ${row.ticket_price:.2f}.")
            previous_poll_time = datetime.utcnow() #update the poll time to the current time before next run
            time.sleep(2)
    except Exception as e:
        print("Error:", e)
    finally:
        cassandra_cluster.shutdown()

if __name__ == "__main__":
    main()

