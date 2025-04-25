-- Connect to your Cassandra container
-- docker exec -it my-cassandra cqlsh

DROP KEYSPACE IF EXISTS airtrack_monitoring;

CREATE KEYSPACE IF NOT EXISTS airtrack_monitoring
WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};

USE airtrack_monitoring;


-- Flight Availability Websites
CREATE TABLE IF NOT EXISTS flight_seat_availability (
    flight_id int,
    seat_number text,
    is_first_class boolean,
    is_booked boolean,
    seats_left int,           
    booking_time timestamp,
    last_updated timestamp,  
    PRIMARY KEY ((flight_id), seat_number)
);

-- Concierge Services (VIP / First Class passengers)
CREATE TABLE IF NOT EXISTS concierge_passenger_info (
    flight_id int,
    customer_id int,
    full_name text,
    seat_number text,
    loyalty_id text,
    booking_time timestamp,
    is_first_class boolean,
    last_updated timestamp,  
    PRIMARY KEY ((flight_id), customer_id)
);

-- Loyalty Program Systems (Track bookings for mileage/tier upgrades)
CREATE TABLE IF NOT EXISTS loyalty_program_bookings (
    loyalty_id text,
    booking_time timestamp,
    flight_id int,
    ticket_price decimal,
    is_first_class boolean,
    last_updated timestamp,  
    PRIMARY KEY ((loyalty_id), booking_time)
) WITH CLUSTERING ORDER BY (booking_time DESC);

-- Insurance  Providers (check active, live flight policies)
CREATE TABLE IF NOT EXISTS insurance_booking_records (
    customer_id int,
    flight_id int,
    booking_time timestamp,
    ticket_price decimal,
    is_flex_ticket boolean,
    seat_number text,
    last_updated timestamp,  
    PRIMARY KEY ((customer_id), flight_id)
);
