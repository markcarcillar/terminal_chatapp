from argparse import ArgumentParser

from .client import Client
from .server import Server

class ForExitException(Exception):
    pass

class CommandLineInterface:
    '''
    Command Line Interface for Terminal Chat Application
    '''

    def __init__(self):
        self.parser = ArgumentParser(description=self.__doc__)
        self.parser.add_argument(
            'service',
            choices=['client', 'server'],
            help='Run the program as client or server.'
        )
        self.parser.add_argument(
            '-p',
            '--port',
            default=430,
            type=int,
            help='Server port. Default is 430.'
        )
        self.parser.add_argument(
            '--password',
            default='top_secret',
            help='Password for authorization header. Default is top_secret.'
        )
        self.args = self.parser.parse_args()
    
    def run(self):
        '''
        Runs the program.
        '''
        try:
            if self.args.service == 'server':
                server = Server(self.args.port, self.args.password)
                server.run()
            elif self.args.service == 'client':
                client = Client(self.args.port, self.args.password)
                client.run()
        except KeyboardInterrupt:
            print('\nProgram has been stopped.')