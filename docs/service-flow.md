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
