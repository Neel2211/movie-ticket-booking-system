Movie Ticket Booking System 

Customer 
    | 
    v 
Booking Service 
    | 
    +-------> Show Service 
    |               | 
    |               v 
    |           Reserve Seat 
    | 
    +-------> Payment Service 
    |               | 
    |               v 
    |       Process Payment 
    | 
    +-------> Notification Service 
                    | 
                    v 
                Send Confirmation


Successful Booking

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


Failed Booking

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
Payment Failure
 |
 v
Release Seat
 |
 v
Cancel Booking
