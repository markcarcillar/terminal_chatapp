import asyncio
import json
import secrets

import websockets

from .event import (
    message_event, 
    users_event
)


class Server:
    '''
    Server API for Terminal Chat Application.
    '''

    def __init__(self, port, password='top_secret'):
        self.port = int(port)
        self.password = password
        self.loop = asyncio.get_event_loop()
        self.users = set()
        self.usernames = []
    
    
    async def server(self, websocket, path):
        '''
        The main handler of the websocket request.

        This first register the websocket to the server, 
        if it successful, it will allow the websocket 
        to receive a message from any websocket 
        that is connected to the server.
        '''
        
        # Register the websocket request to server. 
        # If registering is not successful, reject 
        # the request.
        is_registered = await self.register(websocket, path)
        if not is_registered:
            await websocket.close(
                1008,
                'Invalid authorization header or username header is already registered on the server.'
            )
            # Show the websocket remote address 
            # that is rejected to console
            print(
                '[Rejected]', 
                f'{websocket.remote_address[0]}:{websocket.remote_address[1]}'
            )
            return
        
        try:
            # When there is a message from
            # from any websocket, send the 
            # message to all websocket that 
            # is connected to the server.
            async for message in websocket:
                message = json.loads(message)
                if message:
                    await self.notify_all_user(
                        message_event(
                            message['from'],
                            message['message']
                        )
                    )
        finally:
            # Before the websocket disconnect to the server
            # unregister them.
            await self.unregister(websocket, path)


    async def register(self, websocket, path):
        '''
        First it checks if the websocket is authorized,
        if not, it returns False. Then it register
        the websocket to the server by adding the 
        websocket to `self.users` and its username 
        to `self.usernames`. If the websocket does 
        not have username, it will only add the 
        websocket to `self.users`. If the websocket 
        username is already registered, this will 
        return False, as we don't want a duplicate 
        username.

        It returns True if registering the websocket 
        is successful, otherwise False.
        '''
        # Check if the websocket is authorized, if not
        # return False
        if not self.is_authorized(websocket):
            return False

        # Add the websocket to `self.users` and websocket
        # username to `self.usernames` if it has.
        # If the websocket username is already registered,
        # return False.
        username = self.get_username_header(websocket)
        if username is not None:
            if username in self.usernames:
                return False
            self.usernames.append(username)
        self.users.add(websocket)
        
        
        # Notify the users how many user is connected to the
        # websocket server.
        await self.notify_all_user(users_event(len(self.users)))
        
        # Show who connects to the websocket server.
        print('[Connected]')
        print('Username:', 'No username' if username is None else username)
        print(
            'Address:', 
            f'{websocket.remote_address[0]}:{websocket.remote_address[1]}'
        )
        print('[Path]', path)

        # Successfully registered.
        return True
        

    async def unregister(self, websocket, path):
        '''
        Unregisters the websocket to the server by 
        removing the websocket to `self.users` and 
        its username to `self.usernames`. If
        the websocket does not have username,
        it will only remove the websocket to 
        `self.users`.
        '''
        # Remove the websocket to `self.users` and websocket
        # username to `self.usernames` if it has.
        username = self.get_username_header(websocket)
        if username is not None:
            self.usernames.remove(username)
        self.users.remove(websocket)

        await self.notify_all_user(users_event(len(self.users)))
        
        # Show who disconnects to the websocket server.
        print('[Disconnected]')
        print('Username:', 'No username' if username is None else username)
        print(
            'Address:', 
            f'{websocket.remote_address[0]}:{websocket.remote_address[1]}'
        )
        print('[Path]', path)
    

    async def notify_all_user(self, message):
        '''
        If `self.users` is not empty, send the
        message to all `self.users`.
        '''
        if self.users:
            await asyncio.wait(
                [
                    user.send(message)
                    for user in self.users
                ]
            )
    

    def is_authorized(self, websocket):
        '''
        Validates the websocket authorization header 
        if its value is equal to `self.password`.
        It returns True if equal, if not or the 
        websocket does not have a authorization 
        header it returns False.
        '''
        headers = self.get_headers(websocket)
        if not 'authorization' in headers:
            return False
        if not headers['authorization'] == self.password:
            return False
        return True
        

    def get_headers(self, websocket):
        '''
        Returns the headers as dict from websocket.
        '''
        return dict([header for header in websocket.request_headers.raw_items()])
    

    def get_username_header(self, websocket):
        '''
        Returns the username from websocket header.
        If not found or username is an empty 
        string, it returns None.
        '''
        headers = self.get_headers(websocket)
        if not 'username' in headers:
            return None
        if headers['username'] == '':
            return None
        return headers['username']
    

    def run(self):
        '''
        Start running the server.
        '''
        print(f'Server starts at `ws://localhost:{self.port}/`.')
        self.loop.run_until_complete(
            websockets.serve(self.server, 'localhost', self.port)
        )
        self.loop.run_forever()