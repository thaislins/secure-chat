import socket
from threading import Thread
import tkinter as tk
from tkinter import messagebox
from ..cryptography import rc4, s_des

name_cryptography = ''
type_crypt = None
quit_msg, rc4_msg, sdes_msg = "{quit}", "{rc4}", "{s_des}"
key = ''

#tkinter variables
top = tk.Tk()
messages_frame = tk.Frame(top)
my_msg = tk.StringVar()  # For the messages to be sent.
scrollbar = tk.Scrollbar(messages_frame)  # To navigate through past messages.
msg_list = tk.Listbox(messages_frame, height=20, width=60, yscrollcommand=scrollbar.set)

def receive():
    """Handles receiving of messages."""
    # Receive cryptography name and the welcome message
    welcome_message = ""
    for i in range(3):
        msg = client_socket.recv(BUFSIZ).decode("utf8")
        if msg in [rc4_msg, sdes_msg]:
            client_socket.send(b'ack')
            crypt_type(msg[1:-1])
        elif msg[:3] == "key":
            modify_key(msg[3:])
        else:
            welcome_message = msg
    welcome_message = type_crypt.decode(welcome_message)
    msg_list.insert(tk.END, welcome_message)

    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")

            if msg in [rc4_msg, sdes_msg]:
                crypt_type(msg[1:-1])
            else:
                msg = type_crypt.decode(msg)
                msg_list.insert(tk.END, msg)
        except OSError:  # Possibly client has left the chat.
            break

def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.
    message = type_crypt.encode(msg)
    if msg in [rc4_msg, sdes_msg]:
        client_socket.send(bytes(msg, "utf8"))
        client_socket.recv(3)
    elif msg == quit_msg:
        client_socket.send(bytes(message,"utf8"))
        client_socket.close()
        top.quit()
    else:
        client_socket.send(bytes(message,"utf8"))

def on_closing(event=None):
    """This function is to be called when the window is closed."""
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        my_msg.set(quit_msg)
        send()

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

def setup_tk():
    global top, scrollbar, msg_list, messages_frame
    top.title("Secure Chat")

    scrollbar.config(command=msg_list.yview)
    scrollbar.grid(column=9)
    msg_list.grid(row=0, column=0)
    messages_frame.grid(row=0, column=0, padx=20, pady=20, columnspan=10, rowspan=10)

    entry_field = tk.Entry(top, textvariable=my_msg)
    entry_field.bind("<Return>", send)
    entry_field.grid(row=10, column=4, pady=5)
    send_button = tk.Button(top, text="Send", command=send)
    send_button.grid(row=11, column=4, pady=10)

    crytography_text = tk.Label(top, text="Instructions")
    crytography_text.grid(row=1, column=10, padx=10)

    label1 = tk.Label(top, text="{quit} - Quit Program")
    label1.grid(row=2, column=10)
    label2 = tk.Label(top, text="{rc4} - Modify encryption algorithm to RC4")
    label2.grid(row=3, column=10)
    label3 = tk.Label(top, text="{s_des} - Modify encryption algorithm to S-DES")
    label3.grid(row=4, column=10, padx=7)
    #w = tk.OptionMenu(top, variable, *options)
    #w.grid(row=2, column=10)
    top.protocol("WM_DELETE_WINDOW", on_closing)
#----Now comes the sockets part----
setup_tk()
BUFSIZ = 1024
client_address = (socket.gethostbyname(socket.gethostname()), 5354)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(client_address)

receive_thread = Thread(target=receive)
receive_thread.start()
tk.mainloop()
