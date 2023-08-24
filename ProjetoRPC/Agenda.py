from DatabaseEdit import read_database, write_database, read_data


class Agenda:
    def __init__(self):
        self.database = read_database()

    def initialize(self):
        self.database = []
        self.database = read_data()

    def insert(self, name, address, phone):
        self.database.append({"name": name, "address": address, "phone": phone})
        write_database(self.database)

    def query(self, name):
        for entry in self.database:
            if entry["name"] == name:
                return entry
        return None

    def update(self, name, address, phone):
        for entry in self.database:
            if entry["name"] == name:
                entry["address"] = address
                entry["phone"] = phone
                write_database(self.database)
                return True
        return False

    def remove(self, name):
        for entry in self.database:
            if entry["name"] == name:
                self.database.remove(entry)
                write_database(self.database)
                return True
        return False
