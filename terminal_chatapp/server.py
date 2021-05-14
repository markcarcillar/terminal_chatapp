import asyncio
import json
import secrets

import websockets

class Server:
    '''
    Server API for Terminal Chat Application.
    '''

    def __init__(self, port, password=None):
        self.port = int(port)
        self.password = 'top_secret' if not password else password
        self.loop = asyncio.get_event_loop()
        self.users = set()
        self.usernames = []
    
    def users_event(self):
        return json.dumps({'type': 'users', 'users': len(self.users)})
    
    def username_event(self, username):
        return json.dumps({'type': 'username', 'username': username})
    
    def message_event(self, _from, message):
        return json.dumps({'type': 'message', 'from': _from, 'message': message})
    
    def new_username(self, websocket):
        username = 'user_' + secrets.token_hex(10)
        while  username in self.usernames:
            username = 'user_' + secrets.token_hex(5)
        websocket._username = username
        return username
    
    async def notify_users(self, message):
        if self.users:
            await asyncio.wait(
                [
                    user.send(message)
                    for user in self.users
                ]
            )

    async def register(self, websocket, path):
        new_username = self.new_username(websocket)
        # Give the username to the websocket that is being registered
        await websocket.send(self.username_event(new_username))

        self.users.add(websocket)
        self.usernames.append(new_username)
        
        print(
            '[Connected]', 
            new_username,
            f'{websocket.remote_address[0]}:{websocket.remote_address[1]}',
            sep='\n'
        )
        print('[Path]', path)
        await self.notify_users(self.users_event())
    
    async def unregister(self, websocket, path):
        self.users.remove(websocket)
        self.usernames.remove(websocket._username)
        print(
            '[Disconnected]',
            websocket._username,
            f'{websocket.remote_address[0]}:{websocket.remote_address[1]}',
            sep='\n'
        )
        print('[Path]', path)
        await self.notify_users(self.users_event())
    
    def is_authorized(self, websocket):
        headers = dict(
            [header for header in websocket.request_headers.raw_items()]
        )
        if not 'authorization' in headers:
            return False
        if not headers['authorization'] == self.password:
            return False
        return True
    
    async def server(self, websocket, path):
        # if not self.is_authorized(websocket):
        #     try:
        #         await websocket.close()
        #     except:
        #         pass
        await self.register(websocket, path)
        try:
            async for message in websocket:
                message = json.loads(message)
                if message:
                    print(
                        '[Message]', 
                        message['from'], 
                        message['message'],
                        sep='\n'
                    )
                    await self.notify_users(
                        self.message_event(
                            message['from'], 
                            message['message']
                        )
                    )
        finally:
            await self.unregister(websocket, path)
        
    def run(self):
        '''
        Start running the server.
        '''
        print(f'Starts server at `ws://localhost:{self.port}/`.')
        self.loop.run_until_complete(
            websockets.serve(self.server, 'localhost', self.port)
        )
        self.loop.run_forever()