# reset-cassandra-schema.ps1
param (
    [string]$CassandraContainerName = "cassandra",
    [string]$SchemaFilePath = ".\cassandra-schema.cql",
    [string]$Keyspace = "airtrack_monitoring"
)

Write-Host "Resetting Cassandra schema..." -ForegroundColor Cyan

# Step 1: Copy the schema file into the container
Write-Host "Copying schema file into Cassandra container..." -ForegroundColor Yellow
docker cp "${SchemaFilePath}" "${CassandraContainerName}:/tmp/schema.cql"

# Step 2: Execute the schema inside the container
Write-Host "Executing schema inside Cassandra container..." -ForegroundColor Yellow
docker exec -i $CassandraContainerName cqlsh -u cassandra -p cassandra -f /tmp/schema.cql

Write-Host "`n✅ Cassandra schema successfully reset for keyspace '$Keyspace'!" -ForegroundColor Green
