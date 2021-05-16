from argparse import ArgumentParser

from .client import Client
from .server import Server


class CommandLineInterface:
    '''
    Command Line Interface for Terminal Chat Application.
    '''

    def __init__(self):
        # Top level parser for client and server program.
        parser = ArgumentParser(
            prog='Terminal Chat Application',
            description=self.__doc__
        )
        
        # Subparser for client and server program.
        subparser = parser.add_subparsers(
            help='Choose a program between client and server.',
            dest='program'
        )

        # Server program parser.
        server_parser = subparser.add_parser(
            'server', 
            prog='Server Program',
            help='Run the program as server.'
        )
        server_parser.add_argument(
            '-p',
            '--port',
            default=1719,
            type=int,
            help='''
            Server port. Default is 1719. 
            '''
        )
        server_parser.add_argument(
            '--password',
            default='top_secret',
            help='''
            Password for authorization header. 
            Default is `top_secret`.
            '''
        )
        server_parser.add_argument(
            '-cdc',
            '--cryptography-digest-count',
            default=3,
            type=int,
            help='''
            Digest count for cryptography of server 
            and client program. Max of 5 and min of 1.
            ''',
            dest='digest_count'
        )

        # Client program parser.
        client_parser = subparser.add_parser(
            'client',
            prog='Client Program',
            help='Run the program as client.'
        )
        client_parser.add_argument(
            'cryptography_key',
            default='ws://localhost:1719/',
            help='''
            Cryptography key for cryptography of server 
            and client program.
            '''
        )
        client_parser.add_argument(
            '--url',
            default='ws://localhost:1719/',
            help='''
            URL where the client will connect. Default is 
            "ws://localhost:1719/".
            ''',
            dest='websocket_url'
        )
        client_parser.add_argument(
            '--username',
            default='',
            help='''
            Username for username header of client. If you don't 
            use this optional arg, the Client Program will create 
            its own username. Starting with user then number. 
            Example: "user_1234".
            '''
        )
        client_parser.add_argument(
            '--password',
            default='top_secret',
            help='''
            Password for authorization header. 
            Default is `top_secret`.
            '''
        )
        client_parser.add_argument(
            '-cdc',
            '--cryptography-digest-count',
            default=3,
            type=int,
            help='''
            Digest count for cryptography of server 
            and client program. Max of 5 and min of 1.
            ''',
            dest='digest_count'
        )
        
        self.args = parser.parse_args()
        
        # Validates if digest count for cryptography
        # is in between 1-5. If not raise
        # `parser.error()`.
        if not self.args.digest_count in range(1, 6):
            # Chooce which parser to use. If client
            # or server program.
            error_info = f'Invalid digest count for cryptography. It should be in between of 1-5 but got "{self.args.digest_count}".'
            if self.args.program == 'server':
                raise server_parser.error(error_info)
            raise client_parser.error(error_info)
    
    
    def run(self):
        '''
        Runs the program.
        '''
        try:
            # Run the program as server
            if self.args.program == 'server':
                server = Server(
                    port=self.args.port, 
                    password=self.args.password,
                    cryptography_digest_count=self.args.digest_count
                )
                server.run()

            # Run the program as client
            elif self.args.program == 'client':
                client = Client(
                    cryptography_key=self.args.cryptography_key,
                    cryptography_digest_count=self.args.digest_count,
                    url=self.args.websocket_url,
                    username=self.args.username,
                    password=self.args.password
                )
                
                client.run()
        except KeyboardInterrupt:
            if self.args.program == 'server':
                print('\nServer has been stopped.')
            elif self.args.program == 'client':
                if client._successfully_connected:
                    print(f'\nDisconnected to the `{client.url}` server.')