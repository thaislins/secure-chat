from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import sys
from cryptography import rc4, s_des
from utils.args import args_parser

QUIT_MSG, RC4_MSG, SDES_MSG = "\\quit", "\\rc4", "\\s_des"
KEY_MSG = '\\changekey'
BUFSIZE = 1024
ACK = b'msg'
clients = {}
addresses = {}
server_address = ('', 5354) # adress including host and port
server = socket(AF_INET, SOCK_STREAM)
type_crypt = None
name_cryptography = ''
key = ''

def accept_connections():
    """Accepts incoming connections and adds client's address to a dictionary."""
    while True:
        client, client_address = server.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes('\\' + name_cryptography, "utf8")) # Sends cryptography type to client
        client.recv(3)
        client.send(bytes('key' + key, "utf8")) # Sends key value to client
        client.send(bytes(type_crypt.encrypt("Type your name and press enter!"), "utf8"))
        addresses[client] = client_address # Adds client and address to adresses dictionary
        Thread(target=handle_client, args=(client,)).start()

def handle_client(client):  # Takes client socket as argument.
    """Handles client connection by getting a name and storing it in the clients dictionary."""
    name = client.recv(BUFSIZE).decode("utf8")
    client.send(bytes('\\' + name_cryptography, "utf8")) # Sends again in case type has changed after client connected
    welcome = 'Welcome %s! If you want to quit, type \\quit to exit.' % name
    client.send(bytes(type_crypt.encrypt(welcome), "utf8"))
    client.send(bytes(type_crypt.encrypt("This chat is encrypted with " + name_cryptography), "utf8"))
    join_chat = "%s has joined the chat!" % name
    broadcast(join_chat) # Broadcasts that client has joined the chat
    clients[client] = name

    while True:
        try:
            msg_raw = client.recv(BUFSIZE).decode("utf8")
            if msg_raw in [RC4_MSG, SDES_MSG]: # Changes cryptography type in chat
                client.send(ACK)
                crypt_type(msg_raw[1:])
                broadcast(msg_raw, should_encrypt=False)
                broadcast("This chat is encrypted with " + name_cryptography)
                continue
            elif msg_raw.startswith(KEY_MSG): # Changes key value in chat
                client.send(ACK)
                new_key = msg_raw[len(KEY_MSG):].strip()
                broadcast(msg_raw, should_encrypt=False)
                modify_key(new_key)
                broadcast("The key has been altered")
                continue

            msg = type_crypt.decrypt(msg_raw)
            if msg == QUIT_MSG: # Removes client when quit message is received
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
    """Removes client from dictionary and broadcasts this information to remaining clients."""
    del clients[client]
    broadcast("%s has left the chat." % name)
    print("%s:%s has disconnected." % addresses[client])
    client.close()

def broadcast(msg, name="", should_encrypt=True):
    """Broadcasts a message to all the clients."""
    message = msg if not should_encrypt else type_crypt.encrypt(name + str(msg))
    for c in clients:
        c.send(bytes((message), "utf8"))

def modify_key(k):
    """Modifies key in cryptography algorithm."""
    global key
    key = k
    type_crypt.define_key(key)

def crypt_type(name):
    """Defines the current cryptography used in the chat."""
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
    server.bind(server_address) # Binds socket to address
    print('starting up on%s port %s' % server_address) 
    server.listen(32) # Listens for incoming connections
    print("Waiting for connection...")
    accept_thread = Thread(target=accept_connections) 
    accept_thread.start()
    accept_thread.join()
    server.close()

if __name__ == "__main__":
    run(sys.argv[1:])
