import xmlrpc.client

proxy = xmlrpc.client.ServerProxy("http://localhost:8000")


def main():
    proxy.initialize()

    proxy.insert_contact("Ana Maria", "Rua Laranjeiras, 123", "44 9898 8888")
    proxy.insert_contact("Amadeu da Silva", "Av Tororó 34", "9879 9087")

    print(proxy.query_contact("Ana Maria"))

    proxy.update_contact("Amadeu da Silva", "Nova Rua, 56", "1234 5678")
    proxy.update_contact("Denise", "Rua Ipe, 63", "9999 5678")

    print(proxy.query_contact("Amadeu da Silva"))

    proxy.remove_contact("Ana Maria")

    print(proxy.query_contact("Ana Maria"))


if __name__ == "__main__":
    main()
