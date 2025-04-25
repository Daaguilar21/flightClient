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
    # database='flightclient',
    # user='root',
    # password='davinci13'

    connection = mysql.connector.connect(
    host='127.0.0.1', # or localhost
    database='flightclient',
    user='root',
    password='davinci13',
    auth_plugin='mysql_native_password'
    )
    return connection


def get_customer_and_flight_info(customer_id, flight_id):
    """
    Fetches customer and flight details from  MySQL 
    """
    try:
        connection = buildConnection()
        cursor = connection.cursor(dictionary=True)

        # Fetch customer info
        customer_sql = "SELECT full_name, loyalty_id FROM customers WHERE customer_id = %s"
        cursor.execute(customer_sql, (customer_id,))
        customer = cursor.fetchone()

        # Fetch flight info
        flight_sql = "SELECT origin, destination, departure_time, seat_capacity FROM flights WHERE flight_id = %s"
        cursor.execute(flight_sql, (flight_id,))
        flight = cursor.fetchone()

        return customer, flight
    except mysql.connector.Error as err:
        print("MySQL Error: ", err)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def simulate_booking():
    try:
        conf = {
            'bootstrap.servers': "localhost:9093",  #Kafka server
        }
        producer = Producer(**conf)

        connection = buildConnection()
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            # Randomly select an existing customer_id
            cursor.execute("SELECT customer_id FROM customers ORDER BY RAND() LIMIT 1")
            customer_id = cursor.fetchone()['customer_id']

            # Randomly select a flight with seats available
            cursor.execute("SELECT flight_id, seat_capacity FROM flights WHERE seat_capacity > 0 ORDER BY RAND() LIMIT 1")
            flight = cursor.fetchone()

            if not flight:
                print("No flights available with seats!")
                return

            flight_id = flight['flight_id']

            # fetch customer and flight details
            customer, flight_details = get_customer_and_flight_info(customer_id, flight_id)

            # random seat number 
            seat_number = f"{random.randint(1, 30)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}"

            # Check if seat_number is already taken on this flight
            cursor.execute(
                "SELECT COUNT(*) AS cnt FROM bookings WHERE flight_id = %s AND seat_number = %s",
                (flight_id, seat_number)
            )
            seat_taken = cursor.fetchone()['cnt']

            if seat_taken > 0:
                print(f"Seat {seat_number} on flight {flight_id} is already taken. Skipping this booking.")
                return

            # Simulate booking 
            is_first_class = random.choice([True, False])
            is_flex_ticket = random.choice([True, False])
            ticket_price = round(flight_details['seat_capacity'] * random.uniform(5.5, 7.5), 2)
            booking_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Insert booking into mysql bookings table
            insert_query = """INSERT INTO bookings (flight_id, customer_id, seat_number, booking_time, ticket_price, is_flex_ticket, is_first_class, loyalty_id)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            record = (
                flight_id,
                customer_id,
                seat_number,
                booking_time,
                ticket_price,
                is_flex_ticket,
                is_first_class,
                customer['loyalty_id']
            )
            cursor.execute(insert_query, record)

            # Decrement seat capacity by 1
            update_flight_query = "UPDATE flights SET seat_capacity = seat_capacity - 1 WHERE flight_id = %s"
            cursor.execute(update_flight_query, (flight_id,))

            # Get updated seat capacity
            cursor.execute("SELECT seat_capacity FROM flights WHERE flight_id = %s", (flight_id,))
            new_seat_capacity = cursor.fetchone()['seat_capacity']

            # Build booking event
            booking_event = {
                'customer_id': customer_id,
                'customer_name': customer['full_name'],
                'flight_id': flight_id,
                'origin': flight_details['origin'],
                'destination': flight_details['destination'],
                'seat_number': seat_number,
                'is_first_class': is_first_class,
                'is_flex_ticket': is_flex_ticket,
                'loyalty_id': customer['loyalty_id'],
                'ticket_price': ticket_price,
                'booking_time': booking_time,
                'seats_left': new_seat_capacity  
            }
            event_json = json.dumps(booking_event)

            connection.commit()
            #print("DEBUG PRODUCER EVENT:", booking_event)
            producer.produce("flight_bookings", event_json.encode('utf-8'), callback=acked)
            producer.flush()

            print(f"Booking event produced for customer {customer_id} on flight {flight_id}, seat {seat_number}.")

    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def main():
    while True:
        simulate_booking()
        time.sleep(1)  # Pause for 1 second before the next insert

if __name__ == '__main__':
    main()
