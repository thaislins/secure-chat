from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import sys
import rc4
import s_des

clients = {}
addresses = {}
bufsize = 1024
server_address = ('', 5354)
quit_msg = '{quit}'
server = socket(AF_INET, SOCK_STREAM)
type_cryptography = s_des

def accept_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = server.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes(type_cryptography.encode("Type your name and press enter!"), "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()

def handle_client(client):  # Takes client socket as argument.
    name = type_cryptography.decode(client.recv(bufsize).decode("utf8"))
    welcome = 'Welcome %s! If you want to quit, type {quit} to exit.' % name
    client.send(bytes(type_cryptography.encode(welcome), "utf8"))
    join_chat = "%s has joined the chat!" % name
    broadcast(join_chat)
    clients[client] = name

    while True:
        try:
            msg = type_cryptography.decode(client.recv(bufsize).decode("utf8"))
            if msg == quit_msg:
                remove_client(client, name)
                break
            elif msg != '':
                broadcast(msg, name+": ")
        except BrokenPipeError:
            remove_client(client,name)
            break

def remove_client(client, name):
    del clients[client]
    broadcast("%s has left the chat." % name)
    print("%s:%s has disconnected." % addresses[client])
    client.close()

def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    for c in clients:
        c.send(bytes(type_cryptography.encode(prefix + str(msg)), "utf8"))

def crypt_type(type):
    global type_cryptography
    type_cryptography = rc4 if sys.argv[1] == 'rc4' else s_des

def run():
    if len(sys.argv) == 2 and (sys.argv[1] == 'rc4' or sys.argv[1] == 's_des'):
        crypt_type(sys.argv[1])
        print(type_cryptography)
        server.bind(server_address)
        print('starting up on%s port %s' % server_address)
        server.listen(2)
        print("Waiting for connection...")
        accept_thread = Thread(target=accept_connections)
        accept_thread.start()
        accept_thread.join()
        server.close()
    else:
        print('Missing Arguments or Wrong Input! Input type is:')
        print('server.py #algorithm_name')
        print('Options for algorithm_name include:')
        print('1. rc4      2. s_des')
        
if __name__ == "__main__":
    run()