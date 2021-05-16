import asyncio
import json

import websockets
from cryptography.fernet import Fernet

from .event import (
    create_message_event, 
    create_users_event
)
from .security import Security


class Server:
    '''
    Server API for Terminal Chat Application.
    '''

    def __init__(
        self, 
        port, 
        password='top_secret', 
        cryptography_digest_count=3
        ):

        self.port = int(port)
        self.password = password
        self.loop = asyncio.get_event_loop()
        
        # For cryptography of messages of client, 
        # authorization and username header.
        self.cryptography_key = Fernet.generate_key().decode()
        self.security = Security(
            self.cryptography_key,
            cryptography_digest_count
        )

        # For clients that is connected
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
            
            # Show to console what remote address is rejected.
            print(
                '[Rejected]', 
                f'{websocket.remote_address[0]}:{websocket.remote_address[1]}'
            )
            return

        try:
            # When there is a message from
            # any websocket, decrypt the 
            # message, and send it to all 
            # websocket that is connected 
            # to the server.
            # If message can't be decrypted,
            # close the connection since,
            # only a valid websocket can send
            # a right encrypted message.
            async for message in websocket:
                message = self.security.decrypt(message)
                if message is None:
                    await websocket.close(
                        1008,
                        'Invalid message. Make sure it is encrypted with the same cryptography key from the server.'
                    )
                    break
                message = json.loads(message)
                if message:
                    await self.notify_all_user(
                        create_message_event(
                            message['from'],
                            message['message']
                        )
                    )
        finally:
            # Before or after the websocket disconnect to the server
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
        await self.notify_all_user(create_users_event(len(self.users)))
        
        # Show to console who connect to the 
        # websocket server.
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

        await self.notify_all_user(create_users_event(len(self.users)))
        
        # Show to console who disconnect
        # to the websocket server.
        print('[Disconnected]')
        print('Username:', 'No username' if username is None else username)
        print(
            'Address:', 
            f'{websocket.remote_address[0]}:{websocket.remote_address[1]}'
        )
        print('[Path]', path)
    

    async def notify_all_user(self, message):
        '''
        If `self.users` is not empty, encrypt the
        `message`, decode it as unicode, and send it 
        to all `self.users`.
        '''
        if self.users:
            message = self.security.encrypt(message).decode()
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
        
        It returns True if authorization header
        and `self.password` are equal. If websocket does
        not have authorization header or it can't be
        decrypted with `self.security`, it will return
        False.
        '''
        headers = self.get_headers(websocket)
        if not 'authorization' in headers:
            return False

        # Decrypt the websocket authorization header.
        websocket_password = self.security.decrypt(
            headers['authorization']
        )

        # If authorization header can't be decrypted,
        # return False.
        if websocket_password is None:
            return False

        if not websocket_password.decode() == self.password:
            return False
        return True
        

    def get_username_header(self, websocket):
        '''
        Encrypts the username from websocket header
        and return it. If not found, username is 
        an empty string, or username header can't be
        decrypted with `self.security`, it returns 
        None.
        '''
        headers = self.get_headers(websocket)
        if not 'username' in headers:
            return None

        # Decrypt the websocket username.
        websocket_username = self.security.decrypt(
            headers['username']
        )

        # If websocket username can't be decrypted
        # return None
        if websocket_username is None:
            return None

        if websocket_username.decode() == '':
            return None
        return websocket_username.decode()


    def get_headers(self, websocket):
        '''
        Returns the headers as dict from websocket.
        '''
        return dict([header for header in websocket.request_headers.raw_items()])
    

    def run(self):
        '''
        Start running the server.
        '''
        print(f'Server starts at `ws://localhost:{self.port}/`.')

        # Show the cryptography key of server to console
        # as client needs it for cryptography of authorization
        # and username headers, and messages of client.
        print('[Cryptography Key]')
        print('Please copy the following key below, you will need it for connecting to this server:')
        print(f'Key: {self.cryptography_key}')
        
        # Run the server forever.
        self.loop.run_until_complete(
            websockets.serve(self.server, 'localhost', self.port)
        )
        self.loop.run_forever()