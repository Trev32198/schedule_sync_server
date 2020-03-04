from DatabaseManager import DatabaseManager
from DatabaseManager import DBError
import socket

# A custom error type for communication problems / problems with data
# from client
class ProtocolError(Exception):
    pass

DB_NAME = "schedule_sync.db"

class ServerCommunicator():
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        self.db_manager = DatabaseManager(DB_NAME)
    def sendToClient(self, text):
        self.connection.sendall(self.encode(text))
    def decode(self, data):
        return data.decode("UTF-8")
    def encode(self, string):
        return string.encode()
    def success(self):
        self.sendToClient("SUCCESS\x04")
        self.connection.close()
    def fail(self):
        self.sendToClient("FAILURE\x04")
        self.connection.close()
        raise ProtocolError
    def authenticate(self):
        if self.authType == "pw":
            self.auth = self.db_manager.checkCredentials(self.username,
                                                         self.authToken)
        else:
            self.auth = self.db_manager.checkCredentials(self.username,
                                                     password=None,
                                                     sqa=self.authToken,
                                                     loginType=self.authType)
        if not self.auth:
            self.fail()
    def getClientCommand(self):
        # Make a buffer for the incoming data
        self.data = b''
        # Keep reading until all data has been read
        # Client should terminate its transmission with a null byte
        while b'\x04' not in self.data:
            self.data += self.connection.recv(4096)
        # Switch from utf-8 bytes to a utf-8 string and eliminate null byte
        self.data = self.decode(self.data).replace("\x04", "")
        # Split data from client into lines
        self.data = self.data.split("\n")
        # There are at least two lines for username, pw, and one for a command
        self.requireArgs(3)
        # First line should be a command
        self.command = self.data[0]
        # Second should be a username
        self.username = self.data[1]
        # Third should be an authentication token (password or 
        # security question answer)
        self.authToken = self.data[2]
        # Test if valid command
        if self.command not in ["CREATE ACCOUNT", "CHANGE PASSWORD",
                                "CHANGE SQ", "DELETE ACCOUNT", "SEARCH USER"]:
            # This is an error, this thread should terminate
            self.fail()
    def requireArgs(self, n):
        if len(self.data) < n:
            self.fail()
    def createAccount(self):
        # Need 5 arguments
        self.requireArgs(5)
        # Fourth line is security question
        self.sq = self.data[3]
        # Fifth line is security question answer
        self.sqa = self.data[4]
        try:
            self.db_manager.createAccount(self.username, self.authToken,
                                          self.sq, self.sqa)
            # If we make it here, we were successful
        except DBError:
            # If we fail, presumably because there's an account with the
            # given name, tell the client and terminate
            self.fail()
    def changePW(self):
        # Need 5 args
        self.requireArgs(5)
        # Fifth line should be a new password
        self.newPW = self.data[4]
        # Change the PW
        self.db_manager.changePW(self.username, self.newPW)
    def changeSQ(self):
        # Need 6 args
        self.requireArgs(6)
        # Fifth line should be a new SQ
        self.newSQ = self.data[4]
        # Sixth line should be a new SQA
        self.newSQA = self.data[5]
        # Change the SQ, SQA
        self.db_manager.changeSQ(self.username, self.newSQ, self.newSQA)
    def deleteAccount(self):
        # If this was successfully called, we already have the needed data
        self.db_manager.deleteAccount(self.username)
    def searchUser(self):
        # Need 5 args
        self.requireArgs(5)
        # Fifth arg is the user to search for
        self.userQuery = self.data[4]
        # Perform the search
        self.sendToClient("\n".join([name[0] for name in self.db_manager.searchAccount(self.userQuery)]) + "\n")
    def handleClient(self):
        print("ServerCommunicator thread started.")
        # First try to get a command and arguments from client
        # Errors in handling of client commands result in the sending
        # of "FAILURE", the closure of the connection, and termination of the
        # current thread
        #try:
        self.getClientCommand()
        if self.command == "CREATE ACCOUNT":
            self.createAccount()
            self.db_manager.terminate()
            self.success()
            return None
        # Other commands all require authentication, in which case the fourth
        # argument is the authType, either password (pw) or security question
        # answer (sqa)
        self.authType = self.data[3]
        # Authenticate first
        self.authenticate()
        if self.command == "CHANGE PASSWORD":
            self.changePW()
        elif self.command == "CHANGE SQ":
            self.changeSQ()
        elif self.command == "DELETE ACCOUNT":
            self.deleteAccount()
        elif self.command == "SEARCH USER":
            self.searchUser()
        # If we make it here, we've handled the client with complete success
        # so it's time to tell them and close the connection
        self.success()
        self.db_manager.terminate()
        #except ProtocolError:
        #    return None
