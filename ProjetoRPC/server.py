from xmlrpc.server import SimpleXMLRPCServer
from Agenda import Agenda

agenda = Agenda()


def initialize():
    agenda.initialize()
    return True


def insert_contact(name, address, phone):
    agenda.insert(name, address, phone)
    return True


def query_contact(name):
    result = agenda.query(name)
    if result:
        return result
    else:
        return False


def update_contact(name, address, phone):
    if agenda.update(name, address, phone):
        return True
    else:
        return False


def remove_contact(name):
    if agenda.remove(name):
        return True
    else:
        return False


server = SimpleXMLRPCServer(("localhost", 8000))
server.register_function(initialize)
server.register_function(insert_contact)
server.register_function(query_contact)
server.register_function(update_contact)
server.register_function(remove_contact)

print("Servidor RPC iniciado...")
server.serve_forever()
