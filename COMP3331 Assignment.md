# COMP3331 Assignment

## Files

- `credentials.txt`
  - Server's file only
  - read + write
  - Contains username + password of auth users
  - Username + password on separate lines

```
hans falcon*solo
yoda wise@!man
vader sithlord**
r2d2 do*!@#dedo
c3p0 droid#gold
leia $blasterpistol$
obiwan (jedimaster)
luke light==saber
chewy wookie+aaaawww
palpatine darkside_%$run
```

- This is the database



1. User logs into server
2. Blocking user on auth fails
3. Auto logout on inactivity
4. Handle multiple clients
5. Presence notification, whoelse, whoelsesince
6. Messaging between users
7. Broadcast
8. online messaging
9. offline messaging
10. blacklist
11. peer-peer messaging



## Server

- Use `credentials.txt` has your database

- `server.py <server_port> <block_duration> <timeout>`



1. Client sets up TCP connection with server
2. Username sent to server
3. Check for match in `credentials.txt`
   1. create account if username doesn't exist
   2. send message to client
4. Send confirmation message to client
5. Client sends password
6. Check if correct - send confirmation/error
   1. or create a new account - add it to `credentials.txt`



- Need to keep track of currently online users
  - Have a timer attached so we can log them out on idle
  - prevent logging in twice
- 3 Failed password attempts == blocked for `block_duration` seconds.



https://webcms3.cse.unsw.edu.au/static/uploads/course/COMP3331/21T3/97a15b5ce524cb7b41e83119d0c4fbd6a0cbf3bccfd4898e439696de8a6f9e2c/Assignment.pdf

- spec on page 3 for the different things



## Client

- `client.py <server_port>`



1. Ask for username
2. Send username to server
3. Ask for password
4. Send password



- Client should just print out what the message from the backend is
  - e.g. "Created a new username", "enter a new password"
- **<u>quit if we are blocked</u>**
  - need to clarify what 'quit' means - do we stop the process?



## Report

- `report.pdf`
- Program design
- Data structure design
- Application layer message format
- Description of how system works
- Trade-offs considered/made
- Things that don't work
- Borrowed code



