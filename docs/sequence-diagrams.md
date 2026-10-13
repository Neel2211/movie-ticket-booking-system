SUCCESS FLOW 

User 
 | 
 v 
Booking Service 
 | 
 v 
Reserve Seat 
 | 
 v 
Process Payment 
 | 
 v 
Payment Success 
 |
 v 
Confirm Booking 
 | 
 v 
Send Notification


FAILURE FLOW User 
 |
 v 
Booking Service 
 | 
 v 
Reserve Seat 
 |
 v 
Process Payment
 | 
 v 
Payment Failure 
 | 
 v 
Release Seat 
 | 
 v
Cancel Booking