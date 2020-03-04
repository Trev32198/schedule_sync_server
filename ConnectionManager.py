from ServerCommunicator import ServerCommunicator
import socket
import threading

class ConnectionManager():
    def __init__(self, port):
        self.port = port
        # Create a TCP server socket and start listening
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind(('', self.port))
        self.serverSocket.listen()
        # Begin accepting connections
        while True:
            # Accept a connection and store the connection and address
            connection, address = self.serverSocket.accept()
            print("Connection from " + str(address))
            # Create new ServerCommunicator for the connection
            sc = ServerCommunicator(connection, address)
            # TODO: Spawn new handler thread for the connection and keep
            # listening
            # Need to call sc.handleClient(), but on an independent thread
            threading.Thread(target=sc.handleClient).start()
