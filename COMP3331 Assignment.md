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
        client_thread: class,
        password: password,
        queue: [queue of messages to be sent to client],
        blacklist: set()
    }
}

- need access to the thread for specific information

- who is online
- log on time for each user
- last active time
- offline message queue
- 
```

- trade offs with this design
  - Find online history is O(n) since we have check each user against the time frame
    - Could create a second array of tuple with (`user's last online time`, `username`) but that would introduce redundant data which adds the possibility to desync with each other and increase space requirements. Would decrease time complexity to O(log n) though.
  - Use set instead of list for blocked users to reduce complexity from O(n^2^) to O(n) for searching this set.
    - also allows using set difference to find who is logged in and not blocked for simplicity
  
  

### Message response

```
{
from_server: boolean - might not need
from: "<username>"

message: string
}

dictionary encoded as a json string, with line separators of "\r\n" to determine the ending of one message and the start of another
```





server.py contains the main file -> ClientThread.py contains the client's thread -> ServerHandler.py contains the functions that need to be implemented and information about the client itself



## P2P

Requirements

- Both users are online
- user isn't blocked
- close connection when one of the users disconnects
- user don't time out if they're using private commands
  - i.e. need to send something to the backend whenever a message is being sent
  - ping the server to show that this user is alive





1. `startprivate user2`
   1. if blocked, just return "can't start because user is blocked"
2. `Server: User1 wants to start a private chat. y/n`
   1. `n` == send message to user1 that they didn't want to
   2. y == start transmission
   3. Note that you need to hijack the existing input()
3. `Server to user1: Connection has been established with user2`





1. Client1 sends request to server to create a connection with Client2 using `startprivate Client2`.  (same way all server messages are handledq)
2. Server sends message to `Client2` after error checking asking to create a connection with the given username, address and port (using ServerHandlers.py's `handle_startprivate`)
3. `Client2` responds with y/n. If y, client creates a thread to listen on that port
4. Server  relays this + address + port. If y:
5. `Client1`  starts listening for this address + port
6. `private` will get routed through the normal ClientMethods handler





1. `startprivate username`
2. `handle_startprivate()` in ServerHandlers.py - done
3. `startprivate_response()` in ClientMethods.py
4. y gets sent to server + setup the socket for themselves 
5. `handle_startprivate_accept()` sends information back to Client1
6. `startprivate_init()` in client1 to create their own socket
7. 



h: startprivate j

j starts their server

h gets info about server

h connects to server





- TODO: when logging out, send a message to any peers we're connected to, to disconnect them





## Assumptions

- Password cannot be empty
- Username cannot be empty

- "private <user\> <message\> command sending an error message" is overwritten by a connection not existing
  - the command still fails when a connection doesn't exist or is offline, but the reason will end up being "You need to start a private session with a user first" since a connection needs to be set up first
  - technically fulfils requirements so I left it



