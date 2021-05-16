import asyncio
import json
from random import random
from secrets import choice
from string import digits

import websockets

from .input import NonBlockingInput
from .event import create_message_event
from .security import Security


class Client:
    '''
    Client API for Terminal Chat Application.
    '''

    def __init__(
        self, 
        cryptography_key, 
        cryptography_digest_count=3, 
        url='ws://localhost:1719/', 
        username='', 
        password='top_secret'
        ):

        self.url = url
        self.loop = asyncio.get_event_loop()

        # For cryptography of messages of client, 
        # authorization and username header.
        self.security = Security(
            cryptography_key,
            cryptography_digest_count
        )

        # Set a message as an empty string since
        # this API is using a callback API for 
        # `input()` function.
        self.message = ''

        # Setup the credentials of client for connecting to server.
        self.username = username if username else self.create_username()
        self.headers = {
            'authorization': self.security.encrypt(password).decode(), 
            'username': self.security.encrypt(self.username).decode()
        }

        # Have an access to this Client API if connecting to the
        # server is successful. This should not be change by other
        # API.
        self._successfully_connected = False
    

    async def start_conversation(self):
        '''
        Real function that do the work for running the 
        whole `Client` API but you can use the `self.run()` 
        method for synchronous code.

        It connects to the websocket server (`self.url`)
        with an encrypted authorization and username header. 
        If the request to the server is rejected, this will 
        stop the program and show why client can't connect to 
        the server. Otherwise, if the request is accepted, 
        it will create a task for `self.chat_forever()` and 
        `self.receive_forever()` method and run them 
        concurrently. This is to allow the client to send 
        and receive a message at the same time.
        '''
        async with websockets.connect(
            self.url,
            extra_headers=self.headers
            ) as websocket:
            # Literally sleep for random milliseconds to ensure
            # that client request is accepted by the server. 
            # If not, it will just raise the 
            # `websockets.exceptions.ConnectionClosedError`
            # showing the status code and reason why client can't 
            # connect to the server.
            await self.sleepy_head()
            await websocket.ensure_open()

            # Show to console that connecting to server is successful
            # and set `self._successfully_connected` to True.
            self._successfully_connected = True
            print(f'Connected to `{self.url}` server.')
            print(f'You are connected as `{self.username}`.')

            # Run the `chat_forever()` and `receive_forever()`
            # concurrently.
            chat_task = asyncio.create_task(self.chat_forever(websocket))
            receive_task = asyncio.create_task(self.receive_forever(websocket))
            await chat_task
            await receive_task
        

    async def chat_forever(self, websocket):
        '''
        Have an input to the console so that,
        the client can type and send a message 
        to the websocket server. The message 
        is encrypted using the `self.security`
        before it sends to the websocket server.
        '''
        self.keyboard_thread = NonBlockingInput(self._set_message, '')
        while True:
            if not self.message == '':
                # Send the message as encrypted 
                # with `self.security`.
                self.message = self.security.encrypt(
                    create_message_event(self.username, self.message)
                ).decode()
                await websocket.send(self.message)
                self.message = ''
            await self.sleepy_head()
    

    async def receive_forever(self, websocket):
        '''
        Gets a message from the `websocket` server 
        every `self.sleepy_head()` and decrypts it
        using `self.security`.

        If event type is `users`, it shows how many 
        user is connected to the server. If event 
        type is `message`, it shows the message sender 
        username and its message content, but if the
        message sender is this client, it does not
        show the message.
        '''
        while True:
            rcv = await websocket.recv()
            rcv = json.loads(self.security.decrypt(rcv))
            if rcv['type'] == 'users':
                print('Users Connected:', rcv['users'])
            elif rcv['type'] == 'message':
                # Only show the message if it comes
                # from other websocket.
                if not self.username == rcv['from']:
                    print('[Receive]')
                    print('From:', rcv['from'])
                    print('Message:', rcv['message'])
            await self.sleepy_head()
    

    async def sleepy_head(self):
        '''
        Asyncio sleep for `random() ** 5`.
        '''
        await asyncio.sleep(random() ** 5)
    

    def create_username(self):
        '''
        Returns a random username started at `user_` 
        then random 4 numbers. For instance, `user_1234`.
        '''
        return 'user_' + ''.join(choice(digits) for _ in range(4))
    

    def _set_message(self, message):
        '''
        It set the `self.message` to `message` parameter.

        This method is used as callback on `NonBlockingInput` 
        from `self.chat_forever()` method and should not be 
        use by other API.
        '''
        self.message = message
    
    
    def run(self):
        '''
        Starts the client program.
        '''
        asyncio.run(self.start_conversation())

