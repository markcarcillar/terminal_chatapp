# Terminal Chat Application

Communicate using terminal.


## Requirements
1. [Python 3+](https://www.python.org/)
2. [Python websockets](https://github.com/aaugustin/websockets)


## Installation

By the main repo:
```
$ git clone https://github.com/clediscover/terminal_chatapp/
$ cd terminal_chatapp
$ sudo python3 setup.py install
```

By pip:
```
$ pip install terminal_chatapp
```


## What is Terminal Chat Application? What does it have? and How does it work?

This project has two program, **server** and **client**. The server is used to **open a connection**. The client is the one that will **connect to the server**. All the client that is connected to the server can receive a message from any other client. The server only accepts a connection if its authorized and will reject the request if not. It authorized the request using the authorization header, by checking if its value is the same with the password that is used to run the server. Also it checks the username header, if the username is already registered on the server (meaning other client is using the username and is connected), the server will reject the request.

The client connects with authorization and username header. Authorization header is used as authentication on the server. Username header is used to give an identity to the client. For instance, if the client sends a message to the server. The client username is used to know where the message comes from.

> ### Important
> 
> Running the server program requires root or administrator previledged.


## Basic Usage

### Run the program as server
Run this on terminal to start running the server.
```
$ sudo python3 -m terminal_chatapp server
```
This will run the server from this project. By default it opens connection on **ws://localhost:430/**. You can also choose your own port by using the `-p` flag. Example: `$ sudo python3 -m terminal_chatapp server -p 123`. This example will open the server on **ws://localhost:123/**. Also it is important to know that by default, the password of the server is `top_secret`. You should change it if you don't want an unathorized person to connect to your server. You can change it by using the `--password` flag. Example: `$ sudo python3 -m terminal_chatapp server --password mysupertoppass`.

### Run the program as client
Run this on terminal to connect to the server.
```
$ python3 -m terminal_chatapp client
```
By default it will connect to **ws://localhost:430/** with an authorization header of `"top_secret"` and username header of `"user_1234"`, the number to username header is randomly selected. If you want to change where you want to connect, use `--url` flag. Example: `$ python3 -m terminal_chatapp client --url ws://mychatapp.com:123/`. This will connect to **ws://mychatapp.com:123/**.


For more information on the Command Line Interface (CLI) of server and client program, just run `python3 -m terminal_chatapp -h` or `python3 -m terminal_chatapp --help`. This will show all the available and valid arguments.