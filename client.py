
# Python Chatroom Client
# Made by womogenes.

# Imports first, always.
import socket
import json
import hashlib

import _thread
import sys
import os
import time
import tkinter as tk
from datetime import datetime

# Encryption libraries.=
import rsa
import pyaes

# ExTeRnAl ImPoRtS!?
import client_ui
import Mining


# Stopping errors.
class DevNull:
    """
    Placeholder class for stopping all errors.
    """

    def write(self, message):
        """
        DevNull.write(message)
        Redirects sys.stderr writing to this.
        """
        pass

# sys.stderr = DevNull()

# Let's make a class for handling sockets!


class Client(tk.Tk):
    """
    This class handles all the data.
    I mean, like, all the connecting and socket stuff.
    The main advantage of making a class is to keep track of attributes
        and functions.
    This must be a subclass of tk.Tk because tkinter is so self-centered
        and requires itself to be the main thread.
    """
    login_data = "data.txt"

    def __init__(self, port):
        """
        Client.__init__(port) -> Server
        Makes a new Client object to handle socket stuff.

        port is the port of choice.
        I made it 1235 by default, you can do whatever.
        """
        tk.Tk.__init__(self)

        # Load data!
        if not os.path.exists(self.login_data):
            with open(self.login_data, "w") as f:
                json.dump({
                    "version": "v5.0.5", "agreedToTaC": True, "fontSize": 11,
                    "notifications": False, "loginInfo": ["", "", ""],
                    "money": 0, "cookies": 0}, f)
        with open(self.login_data, "r") as f:
            self.data = json.load(f)

        print("Generating encryption keys...")
        keys = rsa.newkeys(256)
        self.public_key = keys[0]
        self.private_key = keys[1]

        # Attributes.
        self.port = port
        self.ui = client_ui.ClientUI(self)
        self.username = ""
        self.dead = False
        self.key_length = 16
        self.rsa_key_length = 32

        # Socket stuff.
        self.pingTime = time.time()
        self.delay = 0
        self.port = port
        self.local_ip = socket.gethostbyname(socket.gethostname())
        self.server = socket.socket()

        # Terms and conditions stuff!
        if not self.data["agreedToTaC"]:
            print("Please read the terms and conditions. ")
        else:
            self.ui.configure_login()

        # Alright, do the mainloop now...
        try:
            self.mainloop()
        except:
            return None

    def main_thread(self):
        """
        Client.main_thread()
        Starts the main thread for the chatroom.
        Handles all requests and puts requests in.
        """
        # Send a welcome message!
        self.send(f"{self.username} is in at {str(datetime.now())[:-6]}")
        # Get all info.
        info = self.server.recv(2048)
        info = self.decrypt(info[:-5]).split("\n")
        self.data["money"] = int(info[0])
        self.data["cookies"] = int(info[1])
        self.prev_hash = info[2]
        self.hash_zeros = int(info[3])
        self.server.send(b" ")

        # Mine away!
        _thread.start_new(Mining.mine, (self,))

        while True:
            # Check for deadness.
            if self.dead:
                try:
                    self.destroy()
                except:
                    pass
                return

            # Accept messages from the server.
            try:
                message = self.server.recv(2048)

            except:
                print(
                    f"Sorry, the server has broken down at {str(datetime.now())[:-6]}")
                self.dead = True
                continue

            for message in message.split(b"\n" * 5):
                if len(message) < self.rsa_key_length + 1:
                    continue

                # Decryption try/catch.
                message = self.decrypt(message)
                if type(message) != str:
                    continue

                # Yoy! Message processing.
                for line in message.split("\n"):
                    print(line)
                    if ">" in line:
                        # Lines with usernames may still contain messages.
                        if line.startswith("Server> You have been kicked by ") and line.endswith(". "):
                            self.dead = True
                            break

                        if line.startswith("Server> /w Your password has been successfully changed."):
                            if hasattr(self.ui, "cpwin"):
                                self.ui.cpwin.destroy()

                        _thread.start_new(self.ui.insert, (line,))

                    else:
                        # Command from the server?
                        if line.startswith("/"):
                            commands = line.split(" ")

                            # Add or subtract money.
                            if commands[0] == "/balance":
                                # (Changing this won't do anything; balances are stored on the server.)
                                prefix = "+" * (int(commands[1]) > 0)
                                print(
                                    f"{prefix}{commands[1]} money. Your current balance is now {self.data['money']}. ")
                                self.data["money"] += int(commands[1])
                                self.save_data()

                            elif commands[0] == "/cookies":
                                self.data["cookies"] += int(commands[1])
                                self.save_data()

                            # New hash for the blockchain!
                            elif commands[0] == "/newHash":
                                self.prev_hash = commands[1]

                            elif commands[0] == "/update_leaderboard":
                                self.ui.update_leaderboard(
                                    " ".join(commands[1:]))

                            elif line.startswith("/ping"):
                                self.delay = time.time() - self.pingTime
                                self.pingTime = time.time()
                                self.ui.insert(
                                    f"Server> Ping required {self.delay * 1000} milliseconds. ")

                            elif line.startswith("/e delacc "):
                                self.ui.configure_title(
                                    line[10:], self.ui.da_title)

                            elif line.startswith("/e changepass "):
                                self.ui.configure_title(
                                    line[14:], self.ui.cp_title)

                        else:
                            _thread.start_new(self.ui.insert, (line,))

    def send(self, message, delete_entry=False):
        """
        Client.send(message, delete_entry = False)
        Send a message to the server.
        This does stuff with the UI, could have used lambda,
            but that would have taken too much space.
        """
        # First, parse the message for special commands.
        if message.startswith("/ping"):
            self.pingTime = time.time()

        try:
            key = os.urandom(self.key_length)
            aes = pyaes.AESModeOfOperationCTR(key)
            aes_key = rsa.encrypt(key, self.server_key)
            key_and_message = aes_key + aes.encrypt(message)
            self.server.send(key_and_message + b"\n" * 5)

            if delete_entry:
                self.ui.entry.delete(0, "end")

        except:
            raise Exception

    def make_account(self, event=None):
        """
        Client.make_account(event=None)
        Attempt a new account with the credentials provided.
        """
        self.server = socket.socket()

        ip = self.ui.entries[0].get()
        username = self.ui.entries[1].get()
        password = self.ui.entries[2].get()
        confirm = self.ui.entries[3].get()

        if password != confirm:
            self.ui.configure_title("Passwords do not match. ", self.ui.title)
            return

        if len(username) == 0:
            self.ui.configure_title(
                "Please choose an appropriate username. ", self.ui.title)

        if len(password) < 8:
            self.ui.configure_title(
                "Password must be 8 characters or more. ", self.ui.title)

        # Connect to the server.
        self.ui.configure_title("Creating new account...", self.ui.title, self.ui.fg)
        # self.ui.configure_cursor("wait")
        try:
            self.server.connect((ip, self.port))
        except:
            self.ui.configure_title(
                "Failed to connect. Please check your IP. ", self.ui.title)
            # self.ui.configure_cursor("")
        credentials = f"{self.public_key.n}\n{self.public_key.e}\n"
        credentials += f"{username}\n"
        credentials += f"{hashlib.sha512((password + username).encode()).hexdigest()}\nnewacc"
        self.server.send(credentials.encode())

        message = self.server.recv(2048)
        try:
            server_key = message.decode().split("\n")
            self.server_key = rsa.PublicKey(
                int(server_key[0]), int(server_key[1]))

        except:
            # I dunno! Let the server tell us.
            message = self.decrypt(message[:-5])
            self.ui.configure_title(message, self.ui.title)
            # self.ui.configure_cursor("")
            self.server.close()
            return

        # Start recieving messages.
        self.username = username
        # self.ui.configure_cursor("")
        self.ui.configure_chatroom()
        _thread.start_new(self.main_thread, ())

    def login(self, event=None):
        """
        Client.login(event = None)
        Attempts a log-in to the server.
        """
        # Prevent naughty business!
        if len(self.ui.entries[0].get()) == 0:
            self.ui.configure_title(
                "IP field cannot be blank. ", self.ui.title)
            return

        if len(self.ui.entries[1].get()) == 0:
            self.ui.configure_title(
                "Username field cannot be blank. ", self.ui.title)
            return

        if len(self.ui.entries[2].get()) == 0:
            self.ui.configure_title(
                "Password field cannot be blank. ", self.ui.title)
            return

        # Ok, no funny business, on to the legit stuff.
        self.server = socket.socket()
        self.ui.configure_title("Logging in...", self.ui.title, self.ui.fg)
        # self.ui.configure_cursor("wait")
        try:
            self.server.connect((self.ui.entries[0].get(), self.port))
            pk1 = self.public_key.n
            pk2 = self.public_key.e
            username = self.ui.entries[1].get()
            password = hashlib.sha512(
                (self.ui.entries[2].get() + username).encode()).hexdigest()

            credentials = "\n".join((str(pk1), str(pk2), username, password))
            self.server.send(credentials.encode())

        except:
            self.ui.configure_title(
                "Failed to connect. Please check your IP. ", self.ui.title)
            # self.ui.configure_cursor("")
            return

        print(
            f"Attempting login at server with IP {self.ui.entries[0].get()}, {str(datetime.now())[:-7]}",
            end="... "
        )
        # self.ui.configure_cursor("wait")
        self.username = username

        # Wait for server's public IP to send.
        server_key = self.server.recv(2048).decode()
        try:
            server_key = [int(n) for n in server_key.split("\n")]
            self.server_key = rsa.PublicKey(server_key[0], server_key[1])

        except:
            # Probably denied access.
            self.ui.configure_title(
                "Incorrect username or password. Please try again. ", self.ui.title)
            # self.ui.configure_cursor("")
            print("Login failed. ")
            return

        # Do the appropriate UI stuff.
        # self.ui.configure_cursor("")
        print()
        self.ui.configure_chatroom()
        _thread.start_new(self.main_thread, ())

    def decrypt(self, message):
        """
        Client.decrypt(message) -> str
        Decrypts a message given in bytes to return a string.
        We use standard a symmetric CTR AES cipher with the key encrypted using RSA.
        """
        try:
            key = rsa.decrypt(message[:self.rsa_key_length], self.private_key)
            aes = pyaes.AESModeOfOperationCTR(key)
            return aes.decrypt(message[self.rsa_key_length:]).decode()

        except:
            print(f"Could not decrypt: {message}")
            return 0

    def save_data(self):
        """
        Client.save_data()
        Saves self.data into data.txt.
        """
        with open(login_data, "w") as f:
            json.dump(self.data, f)


# Detect if running in IDLE or not.
if "idlelib" in sys.modules:
    print("Debug info and other information will appear in the new window. ")
    print("This window will no longer host useful information.")
    os.startfile(__file__)
    sys.exit()

else:
    client = Client(1235)
    client.server.close()
    print(f"\nProgram terminated at {str(datetime.now())[:-6]}")
    sys.exit()
