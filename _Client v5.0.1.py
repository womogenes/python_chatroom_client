
# Python ChatRoom Client
# v5.0.1, October 2019
# Made by Bill.
# Updates:
# UI fix

# Imports first, always.
import socket
import json
import hashlib

import _thread
import sys
import os
import time

# Encryption libraries.
import secrets
import rsa
import pyaes

# ExTeRnAl ImPoRtS!?
from _ClientUI import *
import Mining

# Stopping errors. 
class DevNull:
    '''
    Placeholder class for stopping all errors.
    '''
    
    def write(self, message):
        '''
        DevNull.write(message)
        Redirects sys.stderr writing to this.
        '''
        pass

# sys.stderr = DevNull()

# Let's make a class for handling sockets!
class Client(tk.Tk):
    '''
    This class handles all the data.
    I mean, like, all the connecting and socket stuff.
    The main advantage of making a class is to keep track of attributes 
        and functions.
    This must be a subclass of tk.Tk because tkinter is so self-centered 
        and requires itself to be the main thread.
    '''

    def __init__(self, port):
        '''
        Client.__init__(port) -> Server
        Makes a new Client object to handle socket stuff.
        
        port is the port of choice.
        I made it 1234 by default, you can do whatever.
        '''
        tk.Tk.__init__(self)
        
        # Load data!
        f = open('data.txt', 'r')
        self.data = json.load(f)
        f.close()

        if not ('publicKey' in self.data and 'privateKey' in self.data):
            print('No keys detected...generating keys. (This may take a while.) ')
            keys = rsa.newkeys(256)
            self.publicKey = keys[0]
            self.privateKey = keys[1]
            self.data['publicKey'] = (self.publicKey.n, self.publicKey.e)
            self.data['privateKey'] = (self.privateKey.n, self.privateKey.e, self.privateKey.d, self.privateKey.p, self.privateKey.q)
        self.save_data()
        self.publicKey = rsa.PublicKey(self.data['publicKey'][0], self.data['publicKey'][1])
        self.privateKey = rsa.PrivateKey(self.data['privateKey'][0], 
                                         self.data['privateKey'][1], 
                                         self.data['privateKey'][2], 
                                         self.data['privateKey'][3], 
                                         self.data['privateKey'][4])
        
        # Attributes.
        self.port = port
        self.ui = ClientUI(self)
        self.username = ''
        self.dead = False
        self.keyLength = 16
        self.rsaKeyLength = 32
        
        # Socket stuff.
        self.pingTime = 0
        self.delay = 0
        self.port = port
        self.localIP = socket.gethostbyname(socket.gethostname())
        self.server = socket.socket()

        # Terms and conditions stuff!
        if not self.data['agreedToTaC']:
            print('Please read the terms and conditions. ')
        else:
            self.ui.configure_login()

        # Alright, do the mainloop now...
        try:
            self.mainloop()
        except:
            return None


    def main_thread(self):
        '''
        Client.main_thread()
        Starts the main thread for the chatroom.
        Handles all requests and puts requests in.
        '''
        # Send a welcome message!
        self.send(self.username + ' is in at ' + str(dt.now())[:-6])
        # Get all info.
        info = self.server.recv(2048)
        info = self.decrypt(info[:-5]).split('\n')
        self.data['money'] = int(info[0])
        self.data['cookies'] = int(info[1])
        self.prevHash = info[2]
        self.hashZeroes = int(info[3])
        self.server.send(b' ')

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
                print('Sorry, the server has broken down at ' + str(dt.now())[:-6])
                self.dead = True
                continue

            for message in message.split(b'\n' * 5):
                if len(message) < self.rsaKeyLength + 1:
                    continue
                
                # Decryption try/catch.
                message = self.decrypt(message)
                if type(message) != str:
                    continue
                
                # Yoy! Message processing.
                messages = message.split('\n')
                
                for line in messages:
                    print(line)
                    if '>' in line:
                        # Lines with usernames may still contain messages.
                        if line.startswith('Server> You have been kicked by ') and line.endswith('. '):
                            self.dead = True
                            break

                        if line == 'Server> Your password has been successfully changed. ':
                            if hasattr(self.ui, 'cpwin'):
                                self.ui.cpwin.destroy()
                        
                        _thread.start_new(self.ui.insert, (line,))

                    else:
                        # Command from the server?
                        if line.startswith('/'):
                            commands = line.split(' ')
                            
                            if commands[0] == '/balance': # Add or subtract money.
                                # (Changing this won't do anything; balances are stored on the server.)
                                prefix = '+' * (int(commands[1]) > 0)
                                print(prefix + commands[1] + ' money. Your current balance is now ' + str(self.data['money']) + '. ')
                                self.data['money'] += int(commands[1])
                                self.save_data()

                            elif commands[0] == '/cookies':
                                self.data['cookies'] += int(commands[1])
                                self.save_data()

                            elif commands[0] == '/newHash': # New hash for the blockchain!
                                self.prevHash = commands[1]

                            elif commands[0] == '/updateLeaderboard':
                                self.ui.updateLeaderboard(' '.join(commands[1:]))

                            elif line.startswith('/ping'):
                                self.delay = time.time() - self.pingTime
                                self.ui.insert('Server> Ping required ' + str(self.delay) + ' seconds. ')

                            elif line.startswith('/e delacc '):
                                self.ui.configure_title(line[10:], self.ui.daTitle)

                            elif line.startswith('/e changepass '):
                                self.ui.configure_title(line[14:], self.ui.cpTitle)

                        else:
                            _thread.start_new(self.ui.insert, (line,))


    def send(self, message, deleteEntry = False):
        '''
        Client.send(message, deleteEntry = False)
        Send a message to the server.
        This does stuff with the UI, could have used lambda, 
            but that would have taken too much space.
        '''
        # First, parse the message for special commands.
        if message == '/ping':
            self.pingTime = time.time()
        
        try:
            key = os.urandom(self.keyLength)
            aes = pyaes.AESModeOfOperationCTR(key)
            aesKey = rsa.encrypt(key, self.serverKey)
            keyAndMessage = aesKey + aes.encrypt(message)
            self.server.send(keyAndMessage + b'\n' * 5)

            if deleteEntry:
                self.ui.entry.delete(0, 'end')
            
        except:
            raise Exception


    def make_account(self, event = None):
        '''
        Client.make_account(event = None)
        Attempt a new account with the credentials provided.
        '''
        self.server = socket.socket()
        
        ip = self.ui.entries[0].get()
        username = self.ui.entries[1].get()
        password = self.ui.entries[2].get()
        confirm = self.ui.entries[3].get()

        if password != confirm:
            self.ui.configure_title('Passwords do not match. ', self.ui.title)
            return

        if len(username) == 0:
            self.ui.configure_title('Please choose an appropriate username. ', self.ui.title)

        if len(password) < 8:
            self.ui.configure_title('Password must be 8 characters or more. ', self.ui.title)

        # Connect to the server.
        self.ui.configure_title('Creating new account...', self.ui.title, self.ui.fg)
        self.ui.configure_cursor('wait')
        try:
            self.server.connect((ip, self.port))
        except:
            self.ui.configure_title('Failed to connect. Please check your IP. ', self.ui.title)
            self.ui.configure_cursor('')
        credentials = str(self.publicKey.n) + '\n' + str(self.publicKey.e) + '\n'
        credentials += username + '\n'
        credentials += hashlib.sha512((password + username).encode()).hexdigest() + '\nnewacc'
        self.server.send(credentials.encode())
            
        message = self.server.recv(2048)
        try:
            serverKey = message.decode().split('\n')
            self.serverKey = rsa.PublicKey(int(serverKey[0]), int(serverKey[1]))
            
        except:
            # I dunno! Let the server tell us.
            message = self.decrypt(message[:-5])
            self.ui.configure_title(message, self.ui.title)
            self.ui.configure_cursor('')
            self.server.close()
            return

        # Start recieving messages.
        self.username = username
        self.ui.configure_cursor('')
        self.ui.configure_chatroom()
        _thread.start_new(self.main_thread, ())
        

    def login(self, event = None):
        '''
        Client.login(event = None)
        Attempts a log-in to the server.
        '''
        # Prevent naughty business!
        if len(self.ui.entries[0].get()) == 0:
            self.ui.configure_title('IP field cannot be blank. ', self.ui.title)
            return

        if len(self.ui.entries[1].get()) == 0:
            self.ui.configure_title('Username field cannot be blank. ', self.ui.title)
            return

        if len(self.ui.entries[2].get()) == 0:
            self.ui.configure_title('Password field cannot be blank. ', self.ui.title)
            return

        # Ok, no funny business, on to the legit stuff.
        self.server = socket.socket()
        self.ui.configure_title('Logging in...', self.ui.title, self.ui.fg)
        self.ui.configure_cursor('wait')
        try:
            self.server.connect((self.ui.entries[0].get(), self.port))
            pk1 = self.publicKey.n
            pk2 = self.publicKey.e
            username = self.ui.entries[1].get()
            password = hashlib.sha512((self.ui.entries[2].get() + username).encode()).hexdigest()
            
            credentials = str(pk1) + '\n' + str(pk2) + '\n' + username + '\n' + password
            self.server.send(credentials.encode())

        except:
            self.ui.configure_title('Failed to connect. Please check your IP. ', self.ui.title)
            self.ui.configure_cursor('')
            return

        print('Attempting login at server with IP ' + self.ui.entries[0].get() + ', ' + str(dt.now())[:-7], end = '... ')
        self.ui.configure_cursor('wait')
        self.username = username

        # Wait for server's public IP to send.
        serverKey = self.server.recv(2048).decode()
        try:
            serverKey = [int(n) for n in serverKey.split('\n')]
            self.serverKey = rsa.PublicKey(serverKey[0], serverKey[1])
            
        except:
            # Probably denied access.
            self.ui.configure_title('Incorrect username or password. Please try again. ', self.ui.title)
            self.ui.configure_cursor('')
            print('Login failed. ')
            return

        # Do the appropriate UI stuff.
        self.ui.configure_cursor('')
        print()
        self.ui.configure_chatroom()
        _thread.start_new(self.main_thread, ())


    def decrypt(self, message):
        '''
        Client.decrypt(message) -> str
        Decrypts a message given in bytes to return a string.
        We use standard a symmetric CTR AES cipher with the key encrypted using RSA.
        '''
        try:
            key = rsa.decrypt(message[:self.rsaKeyLength], self.privateKey)
            aes = pyaes.AESModeOfOperationCTR(key)
            return aes.decrypt(message[self.rsaKeyLength:]).decode()

        except:
            print('Could not decrypt: ' + str(message))
            return 0


    def save_data(self):
        '''
        Client.save_data()
        Saves self.data into data.txt.
        '''
        f = open('data.txt', 'w')
        json.dump(self.data, f)
        f.close()

# Detect if running in IDLE or not.
if 'idlelib' in sys.modules:
    print('Debug info and other information will appear in the new window. ')
    print('This window will no longer host useful information.')
    os.startfile(__file__)
    sys.exit()
    
else:
    client = Client(1235)
    client.server.close()
    print('\nProgram terminated at ' + str(dt.now())[:-6])
    sys.exit()
