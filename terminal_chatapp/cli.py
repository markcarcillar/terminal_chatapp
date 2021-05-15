from argparse import ArgumentParser

from .client import Client
from .server import Server

class ForExitException(Exception):
    pass

class CommandLineInterface:
    '''
    Command Line Interface for Terminal Chat Application.
    '''

    def __init__(self):
        self.parser = ArgumentParser(description=self.__doc__)
        self.parser.add_argument(
            'program',
            choices=['client', 'server'],
            help='Run the program as client or server.'
        )
        self.parser.add_argument(
            '-p',
            '--port',
            default=430,
            type=int,
            help='''
            Server port. This only works for server program.
            Default is 430. 
            '''
        )
        self.parser.add_argument(
            '--url',
            default='ws://localhost:430/',
            help='''
            URL where the client will connect. This only 
            works for client program. Default is 
            "ws://localhost:430/".
            '''
        )
        self.parser.add_argument(
            '--username',
            default='',
            help='''
            Username for username header of client. This only 
            works for client program. If you don't give it a 
            value, the Client Program will create its own
            username. Starting with user then number. Example:
            "user_1234".
            '''
        )
        self.parser.add_argument(
            '--password',
            default='top_secret',
            help='''
            Password for authorization header. 
            Default is `top_secret`.
            '''
        )
        self.args = self.parser.parse_args()
    
    def run(self):
        '''
        Runs the program.
        '''
        try:
            if self.args.program == 'server':
                server = Server(self.args.port, self.args.password)
                server.run()
            elif self.args.program == 'client':
                client = Client(
                    self.args.url, 
                    self.args.username,
                    self.args.password
                )
                client.run()
        except KeyboardInterrupt:
            if self.args.program == 'server':
                print('\nServer has been stopped.')
            elif self.args.program == 'client':
                if client._successfully_connected:
                    print(f'\nDisconnected to the `{client.url}` server.')