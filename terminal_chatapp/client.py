import asyncio
import json
from random import random

import websockets

from .input import KeyboardThread

class Client:
    '''
    Client API for Terminal Chat Application.
    '''

    def __init__(self, port, password=None):
        self.url = f'ws://localhost:{port}/'
        self.loop = asyncio.get_event_loop()
        self.message = ''
        self.headers = {
            'authorization': 'top_secret' if not password else password
        }
        self.username = ''
    
    async def start_conversation(self):
        '''
        Real function that do the work for 
        running the whole API but you can 
        use `self.run()` method for sync
        code.
        ``
        '''
        async with websockets.connect(
            self.url, 
            extra_headers=self.headers
            ) as websocket:
            print(f'Connects to `{self.url}` server.')
            chat_task = asyncio.create_task(self.chat_forever(websocket))
            receive_task = asyncio.create_task(self.receive_forever(websocket))
            await chat_task
            await receive_task
    
    async def sleepy_head(self):
        '''
        Asyncio sleep for `random() ** 5`.
        '''
        await asyncio.sleep(random() ** 5)
        
    async def chat_forever(self, websocket):
        '''
        Send the `message` to `websocket` server
        every `self.sleepy_head()`.
        '''
        self.keyboard_thread = KeyboardThread(self.set_message, '')
        while True:
            if not self.message == '':
                if not self.username == '':
                    await websocket.send(
                        json.dumps(
                            {
                                'from': self.username,
                                'message': self.message
                            }
                        )
                    )
                    self.message = ''
            await self.sleepy_head()
    
    async def receive_forever(self, websocket):
        '''
        Gets a `message` from `websocket` server 
        every `self.sleepy_head()` and prints it.
        '''
        while True:
            rcv = json.loads(await websocket.recv())
            if rcv['type'] == 'users':
                print('Users Connected:', rcv['users'])
            if rcv['type'] == 'username':
                self.username = rcv['username']
                print('Your username:', rcv['username'])
            if rcv['type'] == 'message':
                print('[Receive]')
                print('From:', rcv['from'])
                print('Message:', rcv['message'])
            await self.sleepy_head()
    
    def set_message(self, message):
        self.message = message
    
    def run(self):
        '''
        Starts chatting and receiving message forever.
        '''
        asyncio.run(self.start_conversation())

