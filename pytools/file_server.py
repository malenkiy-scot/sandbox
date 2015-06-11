import SocketServer

def file_handler(_file_name):
    file_name = _file_name
    
    class TCPHandler(SocketServer.BaseRequestHandler):
        """
        The RequestHandler class for our server.

        It is instantiated once per connection to the server, and must
        override the handle() method to implement communication to the
        client.
        """

        def handle(self):
            # self.request is the TCP socket connected to the client
            with open(file_name, 'rb') as f:
                while True:
                    self.data = f.read(1024)
                    if not self.data:
                        break
                    self.request.sendall(self.data)
                
    return TCPHandler

    
def server(_args):
    # Create the server
    server = SocketServer.TCPServer((_args['host'], _args['port']), file_handler(_args['file_name']))

    # Activate the server; run once
    server.handle_request()


def client(_args):

    import socket
        
    if __name__ == '__main__':
        _args = parse_args()

        # Create a socket (SOCK_STREAM means a TCP socket)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Connect to server
            sock.connect((_args['host'], _args['port']))

            # Receive data from the server and shut down
            with open(_args['file_name'],'wb') as f:
                while True:
                    received = sock.recv(1024)
                    if not received:
                        break
                    f.write(received)            
        finally:
            sock.close()

    
def parse_args():
    """
    Parse command-line parameters
    """
    import argparse

    parser = argparse.ArgumentParser(description='Simple TCP File Server and Client')

    parser.add_argument('mode',
                        metavar='GET_OR_SEND',
                        type=str,
                        choices=['send', 'get'],
                        help="sender or receiver")
                    
    parser.add_argument('file_name',
                        metavar='FILENAME',
                        type=str,
                        help="file to serve")

    parser.add_argument('-H', '--host',
                        metavar='HOSTNAME',
                        type=str,
                        dest='host',
                        help='Hostname. localhost by default',
                        default='localhost',
                        required=False)

    parser.add_argument('-P', '--port',
                        metavar='PORT',
                        dest='port',
                        type=int,
                        help='Port. 22334 by default',
                        default=22334,
                        required=False)

    return vars(parser.parse_args())


if __name__ == "__main__":
    _args = parse_args()

    if _args['mode'] == 'get':
        client(_args)
    elif _args['mode'] == 'send':
        server(_args)
    else:
        raise UserWarning("Unknown mode")
