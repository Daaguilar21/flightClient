#pip install mysql-connector-python confluent_kafka
#pip install mysql-connector-python

#you might need to reset to the older password style for this to work:
#ALTER USER 'root'@'localhost'
#IDENTIFIED WITH mysql_native_password BY 'your_password';

import json
from confluent_kafka import Producer
import mysql.connector
from mysql.connector import Error
import random
from datetime import datetime
import time

def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        print("Message produced: %s" % (str(msg)))

def buildConnection():
    # connection = mysql.connector.connect(
    # host='127.0.0.1', # or localhost
    # database='bloodpressure',
    # user='root',
    # password='davinci13'

    connection = mysql.connector.connect(
    host='127.0.0.1', # or localhost
    database='bloodpressure',
    user='root',
    password='davinci13',
    auth_plugin='mysql_native_password'
    )

    return connection


def get_patient_and_machine_info(patient_id, machine_id):
    """
    Fetches patient and machine details from the MySQL database.
    """
    try:
        # Connect to the database
        connection = buildConnection()
        cursor = connection.cursor(dictionary=True)

        # SQL to fetch patient details
        patient_sql = "SELECT first_name, last_name FROM patients WHERE patient_id = %s"
        cursor.execute(patient_sql, (patient_id,))
        patient = cursor.fetchone()

        # SQL to fetch machine details
        machine_sql = "SELECT machine_id, location FROM machines WHERE machine_id = %s"
        cursor.execute(machine_sql, (machine_id,))
        machine = cursor.fetchone()

        return patient, machine
    except mysql.connector.Error as err:
        print("MySQL Error: ", err)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()



def collect_bp_measurement():
    try:
        # Kafka configuration
        conf = {
            'bootstrap.servers': "localhost:9093",  # Change this to your Kafka server configuration
        }
        # Create Producer instance
        producer = Producer(**conf)
        # Connect to the MySQL database
        connection = buildConnection()
        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)

            cursor = connection.cursor()

            # Assuming machine_id values range from 1 to 10 and patient_id values range from 1 to 10
            machine_id = random.randint(1, 10)
            patient_id = random.randint(1, 10)
            systolic_pressure = random.randint(110, 400)  # Example systolic range
            diastolic_pressure = random.randint(70, 90)  # Example diastolic range
            pulse_rate = random.randint(60, 100)  # Example pulse rate range
            reading_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Insert command
            insert_query = """INSERT INTO readings (machine_id, patient_id, systolic_pressure, diastolic_pressure, pulse_rate, reading_time) 
                              VALUES (%s, %s, %s, %s, %s, %s)"""
            record = (machine_id, patient_id, systolic_pressure, diastolic_pressure, pulse_rate, reading_time)
            cursor.execute(insert_query, record)
            patient, machine = get_patient_and_machine_info(patient_id, machine_id)

            blood_pressure_event = {
                'patient_id': patient_id,
                'patient_name': f"{patient['first_name']} {patient['last_name']}",
                'machine_id': machine['machine_id'],
                'machine_location': machine['location'],
                'systolic': systolic_pressure,
                'diastolic': diastolic_pressure,
                'pulse': 70,
                'timestamp': '2024-03-29 12:34:56'
            }
            event_json = json.dumps(blood_pressure_event) # serialize the data to an event.
            connection.commit()
            producer.produce("bp", event_json.encode('utf-8'), callback=acked)

# Wait for any outstanding messages to be delivered
            producer.flush()

            print("Event pushed to topic 'bp'.")
            print(f"New reading inserted: Machine ID: {machine_id}, Patient ID: {patient_id}, Systolic Pressure: {systolic_pressure}, "
                  f"Diastolic Pressure: {diastolic_pressure}, Pulse Rate: {pulse_rate}, Reading Time: {reading_time}")

    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()

def main():
    while True:
        collect_bp_measurement()
        time.sleep(1)  # Pause for 1 second before the next insert

if __name__ == '__main__':
    main()
