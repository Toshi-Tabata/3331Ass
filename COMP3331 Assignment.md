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



Application Layer Message Format

- Send JSON object sent as bytes
  - object contains information relevant to the request being made
- 







# TODO

- Timeout
  - `ServerHandler` needs dictionary for every user
  - Store username, time since last activity
  - Function to refresh user activity
  - Function to log someone out
- When a user issues a command, check that they are logged in
  - make function for checking - returns boolean
    - sends message that the user is logged out
    - log the user out - will be automatic since we just update the dict
- Create a separate thread for checking user logging in/out
  - create a thread per person that times out/refreshes

- Server should be its own class



- Offline messaging
  - Server has a list that stores all information for a user



```python
- Every user will have access to this dictionary
- When server starts, create one for every user
- when a user logs off, their user is still there, just no value?


{
	user1: {
        
        is_blocked: bool,
        client_socket: class,
        client_obj: class,
        password: password,
    }
}
```

- trade offs with this design
  - Find online history is O(n) since we have check each user against the time frame
    - Could create a second array of tuple with (`user's last online time`, `username`) but that would introduce redundant data which adds the possibility to desync with each other and increase space requirements. Would decrease time complexity to O(log n) though.
  - Use set instead of list for blocked users to reduce complexity from O(n^2^) to O(n) for searching this set.
    - also allows using set difference to find who is logged in and not blocked for simplicity
- Each thread has access
  - Writes their own username + information when they have logged in
  - 





server.py contains the main file -> ClientThread.py contains the client's thread -> ServerHandler.py contains the functions that need to be implemented and information about the client itself



