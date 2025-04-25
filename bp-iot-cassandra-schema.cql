
-- docker exec -it my-cassandra cqlsh

CREATE KEYSPACE IF NOT EXISTS bp_monitoring
WITH replication = {
    'class': 'SimpleStrategy', 
    'replication_factor': 1  -- Adjust based on your cluster setup
};

USE bp_monitoring;

CREATE TABLE IF NOT EXISTS readings (
    patient_id int,
    timestamp timestamp,
    patient_name text,
    machine_id int,
    machine_location text,
    systolic int,
    diastolic int,
    pulse int,
    PRIMARY KEY ((patient_id), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

CREATE TABLE IF NOT EXISTS bp_alerts (
    patient_name text,
    timestamp timestamp,
    systolic int,
    PRIMARY KEY ((patient_name), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
