from pymongo import MongoClient

class DatabaseManager:
    def __init__(self, database_name, host, port):
        self.database_name = database_name
        self.host = host
        self.port = port
        self.client = MongoClient(host, port)
        self.db = self.client[database_name]

    def close_connection(self):
        self.client.close()

