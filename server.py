from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import sys
import rc4
import s_des
from args import args_parser

clients = {}
addresses = {}
bufsize = 1024
server_address = ('', 5354)
quit_msg, rc4_msg, sdes_msg = "{quit}", "{rc4}", "{s_des}"
server = socket(AF_INET, SOCK_STREAM)
type_crypt = None
name_cryptography = ''
key = ''

def accept_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = server.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes('{' + name_cryptography + '}', "utf8"))
        client.recv(3)
        client.send(bytes('key' + key, "utf8"))
        client.send(bytes(type_crypt.encode("Type your name and press enter!"), "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()

def handle_client(client):  # Takes client socket as argument.
    name = type_crypt.decode(client.recv(bufsize).decode("utf8"))
    client.send(bytes(type_crypt.encode("This chat is encrypted with " + name_cryptography), "utf8"))
    welcome = 'Welcome %s! If you want to quit, type {quit} to exit.' % name
    client.send(bytes(type_crypt.encode(welcome), "utf8"))
    join_chat = "%s has joined the chat!" % name
    broadcast(join_chat)
    clients[client] = name

    while True:
        try:
            msg_raw = client.recv(bufsize).decode("utf8")
            if msg_raw in [rc4_msg, sdes_msg]:
                client.send(b'ack')
                crypt_type(msg_raw[1:-1])
                broadcast(msg_raw)
                broadcast("This chat is encrypted with " + name_cryptography)
                continue

            msg = type_crypt.decode(msg_raw)
            if msg == quit_msg:
                remove_client(client, name)
                break
            elif msg != '':
                broadcast(msg, name+": ")
        except BrokenPipeError:
            remove_client(client,name)
            break
        except ConnectionResetError:
            break

def remove_client(client, name):
    del clients[client]
    broadcast("%s has left the chat." % name)
    print("%s:%s has disconnected." % addresses[client])
    client.close()

def broadcast(msg, name=""):
    """Broadcasts a message to all the clients."""
    message = msg if msg in [rc4_msg, sdes_msg] else type_crypt.encode(name + str(msg))
    for c in clients:
        c.send(bytes((message), "utf8"))

def modify_key(k):
    global key
    key = k
    type_crypt.define_key(key)

def crypt_type(name):
    global type_crypt
    global name_cryptography
    name_cryptography = name
    type_crypt = rc4.RC4() if name == 'rc4' else s_des.SDES()
    if key != '': type_crypt.define_key(key)

def run(args):
    # Parse CLI arguments
    args = args_parser(args)
    arg_alg = args.algorithm
    arg_key = args.key

    crypt_type(arg_alg)
    modify_key(arg_key)
    server.bind(server_address)
    print('starting up on%s port %s' % server_address)
    server.listen(5)
    print("Waiting for connection...")
    accept_thread = Thread(target=accept_connections)
    accept_thread.start()
    accept_thread.join()
    server.close()

if __name__ == "__main__":
    run(sys.argv[1:])
