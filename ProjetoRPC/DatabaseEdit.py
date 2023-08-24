def read_database():
    database = []
    with open("database.txt", "r") as file:
        lines = file.readlines()
        num_entries = len(lines) // 3
        for i in range(num_entries):
            name = lines[i * 3].strip()
            address = lines[i * 3 + 1].strip()
            phone = lines[i * 3 + 2].strip()
            database.append({"name": name, "address": address, "phone": phone})
    return database


def write_database(database):
    with open("database.txt", "w") as file:
        for entry in database:
            file.write(entry["name"] + "\n")
            file.write(entry["address"] + "\n")
            file.write(entry["phone"] + "\n")


def read_data():
    database = []
    with open("dados.txt", "r") as file:
        lines = file.readlines()
        num_entries = len(lines) // 3
        for i in range(num_entries):
            name = lines[i * 3].strip()
            address = lines[i * 3 + 1].strip()
            phone = lines[i * 3 + 2].strip()
            database.append({"name": name, "address": address, "phone": phone})
    return database