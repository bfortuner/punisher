

class DataStore():
    def __init__(self):
        pass

    def save(self):
        pass

    def load(self):
        pass


class CSVStore(DataStore):
    def __init__(self):
        pass


class JSONStore(DataStore):
    def __init__(self):
        pass


class SQLStore(DataStore):
    def __init__(self, endpoint, user, password):
        self.endpoint = endpoint
        self.user = user
        self.password = password

    def get_conn(self):
        return None
