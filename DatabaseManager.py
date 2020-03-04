import sqlite3

# A custom error class
class DBError(Exception):
    pass

class DatabaseManager():
    def __init__(self, databaseName):
        self.databaseName = databaseName
        self.connection = sqlite3.connect(self.databaseName,
                                          check_same_thread = False)
        self.cursor = self.connection.cursor()
    def terminate(self):
        self.connection.commit()
        self.connection.close()
    def checkCredentials(self, accountName, password, sqa=None, loginType="pw"):
        # Using password to login
        if loginType == "pw":
            self.cursor.execute("SELECT * FROM Users WHERE username = ?" +
                                " AND password = ?;", (accountName, password))
            return bool(len(self.cursor.fetchall()))
        # Using security question and answer to authenticate
        else:
            self.cursor.execute("SELECT * FROM Users WHERE username = ?" +
                                " AND sq_answer = ?;", (accountName, sqa))
            return bool(len(self.cursor.fetchall()))
    def createAccount(self, accountName, password, sq, sqa):
        # First check to see if such an account exists
        self.cursor.execute("SELECT * FROM Users WHERE username = ?;",
                            (accountName, ))
        # If such an account exists
        if len(self.cursor.fetchall()) != 0:
            # Raise our custom error
            raise DBError
        # If no existing account with the specified name exists, make one
        self.cursor.execute("INSERT INTO Users VALUES (?,?,?,?);", (accountName,
                            password, sq, sqa))
    def changePW(self, accountName, newPW):
        self.cursor.execute("UPDATE Users SET password = ? WHERE username = ?;",
                            (newPW, accountName))
    def changeSQ(self, accountName, newSQ, newSQA):
        self.cursor.execute("UPDATE Users SET security_question = ?, sq_answer = ? WHERE " + 
                            "username = ?;", (newSQ, newSQA, accountName))
    def deleteAccount(self, accountName):
        self.cursor.execute("DELETE FROM Users WHERE username = ?;",
                            (accountName, ))
    def searchAccount(self, query):
        self.cursor.execute("SELECT username FROM Users WHERE username LIKE" +
                            " '%' || ? || '%';", (query, ))
        return self.cursor.fetchall()
