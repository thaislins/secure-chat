import socket
from threading import Thread
import tkinter as tk
from tkinter import messagebox
from cryptography import rc4, s_des

name_cryptography = ''
bufsize = 1024
type_crypt = None
quit_msg, rc4_msg, sdes_msg = "{quit}", "{rc4}", "{s_des}"
change_key_msg = '\changekey'
key = ''
client_address = (socket.gethostbyname(socket.gethostname()), 5354)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
nameMsg = True

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
    for _ in range(3):
        msg = client_socket.recv(bufsize).decode("utf8")
        if msg in [rc4_msg, sdes_msg]:
            client_socket.send(b'ack')
            crypt_type(msg[1:-1])
        elif msg[:3] == "key":
            modify_key(msg[3:])
        else:
            welcome_message = msg
            name_message(True)
    welcome_message = type_crypt.decrypt(welcome_message)
    msg_list.insert(tk.END, welcome_message)

    while True:
        try:
            msg = client_socket.recv(bufsize).decode("utf8")

            if msg in [rc4_msg, sdes_msg]:
                crypt_type(msg[1:-1])
            elif msg.startswith(change_key_msg):
                new_key = msg[len(change_key_msg):].strip()
                modify_key(new_key)
            else:
                msg = type_crypt.decrypt(msg)
                msg_list.insert(tk.END, msg)
        except OSError:  # Possibly client has left the chat.
            break

def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.
    message = type_crypt.encrypt(msg)
    if msg in [rc4_msg, sdes_msg] or msg.startswith(change_key_msg):
        client_socket.send(bytes(msg, "utf8"))
        client_socket.recv(3)
    elif nameMsg == True:
        client_socket.send(bytes(msg, "utf8"))
        name_message(False)
    elif msg == quit_msg:
        client_socket.send(bytes(message,"utf8"))
        client_socket.close()
        top.quit()
    else:
        client_socket.send(bytes(message,"utf8"))

def name_message(msg):
    global nameMsg
    nameMsg = msg

def on_closing(event=None):
    """This function is called when the window is closed."""
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        my_msg.set(quit_msg)
        send()

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

def setup_tk():
    """Setup tkinter GUI."""
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

    label_quit = tk.Label(top, text="{quit} - Quit Program")
    label_quit.grid(row=2, column=10)
    label_rc4 = tk.Label(top, text="{rc4} - Modify encryption algorithm to RC4")
    label_rc4.grid(row=3, column=10)
    label_sdes = tk.Label(top, text="{s_des} - Modify encryption algorithm to S-DES")
    label_sdes.grid(row=4, column=10, padx=15)
    label_key = tk.Label(top, text="\changekey <key> - Define a new key")
    label_key.grid(row=5, column=10)

    top.protocol("WM_DELETE_WINDOW", on_closing)

def run():
    setup_tk()
    client_socket.connect(client_address)
    receive_thread = Thread(target=receive)
    receive_thread.start()
    tk.mainloop()

if __name__ == "__main__":
    run()
