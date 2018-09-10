#!/usr/bin/env python3
"""Script for Tkinter GUI chat client."""
import socket
from threading import Thread
import tkinter as tk
from tkinter import messagebox
import s_des

type_cryptography = s_des

def receive():
    """Handles receiving of messages."""
    while True:
        try:
            msg = type_cryptography.decode(client_socket.recv(BUFSIZ).decode("utf8"))
            msg_list.insert(tk.END, msg)
        except OSError:  # Possibly client has left the chat.
            break


def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.
    client_socket.send(bytes(type_cryptography.encode(msg), "utf8"))
    if msg == "{quit}":
        client_socket.close()
        top.quit()

def on_closing(event=None):
    """This function is to be called when the window is closed."""
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        my_msg.set("{quit}")
        send()

top = tk.Tk()
top.title("Secure Chat")

messages_frame = tk.Frame(top)
my_msg = tk.StringVar()  # For the messages to be sent.
scrollbar = tk.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = tk.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.config(command=msg_list.yview)
scrollbar.grid(column=9)
msg_list.grid(row=0, column=0)
messages_frame.grid(row=0, column=0, padx=20, pady=20, columnspan=10, rowspan=10)

entry_field = tk.Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.grid(row=10, column=4, pady=5)
send_button = tk.Button(top, text="Send", command=send)
send_button.grid(row=11, column=4, pady=10)

options = [
"RC4",
"S-DES"
] #etc

variable = tk.StringVar(top)
variable.set(options[0]) # default value

crytography_text = tk.Label(top, text="Cryptography Algorithm:")
crytography_text.grid(row=1, column=10, padx=10)

w = tk.OptionMenu(top, variable, *options)
w.grid(row=2, column=10)

top.protocol("WM_DELETE_WINDOW", on_closing)

#----Now comes the sockets part----
BUFSIZ = 1024
client_address = (socket.gethostbyname(socket.gethostname()), 5354)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(client_address)

receive_thread = Thread(target=receive)
receive_thread.start()
tk.mainloop() 