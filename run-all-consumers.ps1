Start-Process powershell -ArgumentList "cd '$(Get-Location)'; `$Host.UI.RawUI.WindowTitle = 'Seat Availability Consumer'; python flight_seat_availability_consumer.py"
Start-Process powershell -ArgumentList "cd '$(Get-Location)'; `$Host.UI.RawUI.WindowTitle = 'Concierge Passenger Consumer'; python concierge_passenger_info_consumer.py"
Start-Process powershell -ArgumentList "cd '$(Get-Location)'; `$Host.UI.RawUI.WindowTitle = 'Loyalty Program Consumer'; python loyalty_program_bookings_consumer.py"
Start-Process powershell -ArgumentList "cd '$(Get-Location)'; `$Host.UI.RawUI.WindowTitle = 'Insurance Booking Consumer'; python insurance_booking_records_consumer.py"
