import time
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
#https://cassandra.apache.org/_/quickstart.html
def main():
    # Configure the connection:
    cassandra_cluster = Cluster(['127.0.0.1'], port=9042)
    session = cassandra_cluster.connect('bp_monitoring')

    # Connect to the cluster:
    try:
        session = cassandra_cluster.connect()
        print("Connected to Cassandra cluster.")
        while True:
            rows = session.execute("SELECT patient_name FROM bp_monitoring.bp_alerts;")
            for row in rows:
                print(f'WARNING!! SEND AMBULANCE TO: {row.patient_name} RIGHT AWAY!!!!')
            time.sleep(2)
    except Exception as e:
        print("Failed to connect to Cassandra cluster:", e)
    finally:
        cluster.shutdown()

if __name__ == "__main__":
    main()