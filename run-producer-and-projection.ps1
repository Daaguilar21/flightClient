# Change directory and set window title, then run producer
Start-Process powershell -ArgumentList "cd '$(Get-Location)'; `$Host.UI.RawUI.WindowTitle = 'Flight Bookings Producer'; python bookings-producer.py"

# Change directory and set window title, then run projector
Start-Process powershell -ArgumentList "cd '$(Get-Location)'; `$Host.UI.RawUI.WindowTitle = 'Bookings Projector (Kafka to Cassandra)'; python bookings-projector.py"
