import asyncio
import json
from random import random
from secrets import choice
from string import digits

import websockets

from .input import NonBlockingInput
from .event import message_event

class Client:
    '''
    Client API for Terminal Chat Application.
    '''

    def __init__(self, url='ws://localhost:430/', username='', password='top_secret'):
        self.url = url
        self.loop = asyncio.get_event_loop()
        self.message = ''
        self.username = username if username else self.create_username()
        self.headers = {
            'authorization': password, 
            'username': self.username
        }
        self._successfully_connected = False
    

    async def start_conversation(self):
        '''
        Real function that do the work for running the 
        whole `Client` API but you can use the `self.run()` 
        method for synchronous code.

        It connects to the websocket server (`self.url`)
        with an authorization and username header to 
        headers. If the request to the server is rejected,
        this will stop the program and show why we can't
        connect to the server. Otherwise, if the request
        is accepted, it will create a task for 
        `self.chat_forever()` and `self.receive_forever()` 
        method and run them concurrently. This is to allow 
        the client to send and receive a message at the same 
        time.
        '''
        async with websockets.connect(
            self.url,
            extra_headers=self.headers
            ) as websocket:
            # Literally sleep for random milliseconds to ensure
            # that we are connected to the server. If we are not
            # connected, it will just raise the 
            # `websockets.exceptions.ConnectionClosedError`
            # showing the status code and reason why we can't 
            # connect to the server.
            await self.sleepy_head()
            await websocket.ensure_open()

            # Connection is successful.
            self._successfully_connected = True
            print(f'Connects to `{self.url}` server.')
            print(f'You are connected as `{self.username}`.')
            chat_task = asyncio.create_task(self.chat_forever(websocket))
            receive_task = asyncio.create_task(self.receive_forever(websocket))
            await chat_task
            await receive_task
        

    async def chat_forever(self, websocket):
        '''
        Have an input to the console so that,
        the client can type and send a message 
        to the websocket server.
        '''
        self.keyboard_thread = NonBlockingInput(self._set_message, '')
        while True:
            if not self.message == '':
                await websocket.send(
                    message_event(self.username, self.message)
                )
                self.message = ''
            await self.sleepy_head()
    

    async def receive_forever(self, websocket):
        '''
        Gets a message from the `websocket` server 
        every `self.sleepy_head()`. If event type
        is `users`, it shows how many user is 
        connected to the server. If event type is 
        `message`, it prints the message sender 
        username and its message content, but if the
        message sender is this client, it does not
        show the message.
        '''
        while True:
            rcv = json.loads(await websocket.recv())
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
        Returns a random username started at `user_` then numbers.
        '''
        return 'user_' + ''.join(choice(digits) for _ in range(4))
    

    def _set_message(self, message):
        '''
        It set the `self.message` to `message` parameter.

        This method is used as callback on `NonBlockingInput` 
        from `self.chat_forever()` method.
        '''
        self.message = message
    
    
    def run(self):
        '''
        Starts chatting and receiving message forever
        to the websocket server (`self.url`).
        '''
        asyncio.run(self.start_conversation())

