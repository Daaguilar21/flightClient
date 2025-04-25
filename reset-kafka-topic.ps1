# reset-kafka-topic.ps1
param (
    [string]$KafkaContainerName = "finalproject-kafka-1",
    [string]$TopicName = "flight_bookings",
    [string]$BootstrapServer = "localhost:9093"
)

Write-Host "Deleting Kafka topic '$TopicName' from container '$KafkaContainerName'..." -ForegroundColor Cyan
docker exec -i $KafkaContainerName kafka-topics.sh --bootstrap-server $BootstrapServer --delete --topic $TopicName

Start-Sleep -Seconds 2  # Small pause to ensure delete finishes

Write-Host "Recreating Kafka topic '$TopicName'..." -ForegroundColor Cyan
docker exec -i $KafkaContainerName kafka-topics.sh --bootstrap-server $BootstrapServer --create --topic $TopicName --partitions 1 --replication-factor 1

Write-Host "`n✅ Kafka topic '$TopicName' successfully reset!" -ForegroundColor Green
