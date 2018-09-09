from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import sys

clients = {}
addresses = {}
bufsize = 1024
server_address = ('', 5354)
quit_msg = '{quit}'
server = socket(AF_INET, SOCK_STREAM)

def accept_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = server.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes("Type your name and press enter!", "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):  # Takes client socket as argument.
    name = client.recv(bufsize).decode("utf8")
    welcome = 'Welcome %s! If you want to quit, type {quit} to exit.' % name
    client.send(bytes(welcome, "utf8"))
    broadcast_msg(bytes("%s has joined the chat!" % name, "utf8"))
    clients[client] = name

    while True:
        msg = client.recv(bufsize)
        if msg != bytes(quit_msg, "utf8"):
            broadcast_msg(msg, name+": ")
        else:
            remove_client(client, name)
            break

def remove_client(client, name):
    broadcast_msg(bytes("%s has left the chat." % name, "utf8"))
    print("%s:%s has disconnected." % addresses[client])
    client.close()
    del clients[client]

def broadcast_msg(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    for c in clients:
        c.send(bytes(prefix, "utf8")+msg)

def run():
    server.bind(server_address)
    print('starting up on%s port %s' % server_address)
    server.listen(2)
    print("Waiting for connection...")
    accept_thread = Thread(target=accept_connections)
    accept_thread.start()
    accept_thread.join()
    server.close()

if __name__ == "__main__":
    run()