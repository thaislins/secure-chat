#!/usr/bin/env python3
"""Script for Tkinter GUI chat client."""
import socket
from threading import Thread
import tkinter as tk
from tkinter import messagebox

def receive():
    """Handles receiving of messages."""
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            msg_list.insert(tk.END, msg)
        except OSError:  # Possibly client has left the chat.
            break


def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.
    client_socket.send(bytes(msg, "utf8"))
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
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
msg_list.pack(side=tk.LEFT, fill=tk.BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = tk.Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tk.Button(top, text="Send", command=send)
send_button.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)

#----Now comes the sockets part----
BUFSIZ = 1024
client_address = (socket.gethostbyname(socket.gethostname()), 5354)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(client_address)

receive_thread = Thread(target=receive)
receive_thread.start()
tk.mainloop() 