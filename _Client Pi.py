# Python program to implement client side of chat room.
# Created by the Pyva Group. 

# Update Pi.  
# June 2019
# A SEVERE UI update. 
# COMPLETELY READY!!! 

import socket
import select
import os

import sys
from datetime import datetime
import winsound
import webbrowser

import time

from _thread import *

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.colorchooser as colourchooser

from tkinter import messagebox

# Global variables!
global server
global IP_address
global localIP
global Port

global notified
global personalColour
global whisperColour

server = None
IP_address = None
localIP = None
Port = None

notified = False
personalColour = 'green'
whisperColour = 'blue'


# Welcome!
version = 'Pi'
print('''
Client side script.
Python ChatRoom, made by Bill.
''' + version + ''', 2019.
''')


# Gotta get them to agree to the whole thing first if necessary!
f = open('metadata.txt', 'r')
info = ''.join(f.readlines())
if info != 'yoy ':
    read = False
    info = 'yoy '
else:
    read = True
f.close()


def tkintering():
    '''
    tkintering()
    All the agreement and terms and conditions stuff.
    '''
    # Disable just closing.
    def on_closing():
        '''
        on_closing()
        Hehehehehehe
        '''
        print('Please take the time to actually read this. ')
        tkintering()
    
    # Did the actually read it?
    def agree(event = False):
        '''
        agree()
        They actually agree!
        '''
        f = open('README.txt', 'r')
        info = ''.join(f.readlines())
        f.close()

        
        root.destroy()
        print('Thank you for reading through all of that. ')
        return

    def meh(event = False):
        '''
        meh()
        Meh.
        '''
        print('You have not accepted the Terms and Conditions. ')
        print('Please tell us why you did not agree so that we can improve our service. ')
        print('(Your files have remained intact.) ')
        root.destroy()
        sys.exit()
        return

    def disagree(event = False):
        '''
        disagree()
        Wipe this program!
        '''
        try:
            os.remove(os.getcwd() + '\\' + os.path.basename(__file__))
        except:
            pass
        print('You have disagreed, so the SOFTWARE has been wiped from your hard drive. ')
        print('Have a nice day! :) ')
        root.destroy()
        sys.exit()
        return
    
    root = tk.Tk()
    root.title('Terms and Conditions')
    root.iconbitmap(os.getcwd() + '\\message.ico')

    l = tk.Label(root, width = 50, font = ('Segoe UI', 18))
    l['text'] = 'Terms and Conditions of Use for this Python ChatRoom'
    l.grid(row = 0, column = 0, columnspan = 2)

    # Text widget!
    t = tk.Text(root, height = 25, width = 150, font = ('Segoe UI', 12), wrap = WORD)
    t['bg'] = '#FEFEFE'
    t.grid(row = 1, column = 0, columnspan = 2)

    # Scrollbar!
    s = tk.Scrollbar(root, orient = VERTICAL)
    s.grid(row = 1, column = 2, sticky = 'ns')
    s.config(command = t.yview)
    t.config(yscrollcommand = s.set)

    # Get all the long words! 
    f = open('Terms and Conditions.txt', 'r')
    tac = ''.join(f.readlines())
    f.close()
    t.insert(tk.END, tac)
    t.config(state = DISABLED)

    # Buttons!
    b = ttk.Button(root, text = 'I accept', command = disagree)    
    b.bind('<Button-2>', agree)
    b.bind('<Button-3>', agree)
    b.grid(row = 2, column = 0)
    
    b2 = ttk.Button(root, text = 'I do not accept', command = disagree)
    b2.bind('<Button-2>', agree)
    b2.bind('<Button-3>', meh)
    b2.grid(row = 2, column = 1)
    

    # Done!
    root.resizable(width = False, height = False)
    root.protocol('WM_DELETE_WINDOW', on_closing)
    root.mainloop()

if not read:
    print('Please make sure you read all of this. ')
    print('Especially the end! That is the most important part. ')
    
    tkintering()
    f = open('metadata.txt', 'w')
    f.write(info)
    f.close()


# Tkinter handling connection thing! 
def send_password(event = None):
    '''
    send_password()
    Sends the password!
    '''
    # Tkinter stuff!
    global server
    global IP_address
    global localIP
    global Port
    
    IP_address = e.get()
    password = e2.get()

    if len(password) == 0:
        return

    root.destroy()
    
    # Now, start the actual program! :P  
    server = socket.socket()
    
    localIP = socket.gethostbyname(socket.gethostname())
    print('Your local IP address is ' + localIP + '. ')
    
    if len(IP_address) == 0:
        IP_address = localIP
    Port = 1234

    print('Connecting...')
    try:
        server.connect((IP_address, Port))
    except:
        print('IP address failed. No such connection. ')
        sys.exit()
              
    print('Done connecting! \n')

    time.sleep(0.1)
    server.send((os.getlogin() + '\n' + password).encode())
    time.sleep(1)

        

print('Please enter the IP and password in the Tkinter window. ')

root = tk.Tk()
root.grid()

root.title('Password Entry')
root.bind('<Return>', send_password)
root.iconbitmap(os.getcwd() + '\\message.ico')

l = tk.Label(root, text = 'Host IP address:', font = ('Segoe UI', 12))
l.grid(row = 0, column = 0)

e = ttk.Entry(root, width = 50, font = ('Segoe UI', 12))
e.grid(row = 0, column = 1)

l2 = tk.Label(root, text = 'Password:', justify = 'right', anchor = 'e', font = ('Segoe UI', 12))
l2.grid(row = 1, column = 0, sticky = 'e')

e2 = ttk.Entry(root, width = 50, font = ('Segoe UI', 12))
e2.grid(row = 1, column = 1)

b = ttk.Button(root, text = 'Enter', command = send_password)
b.grid(row = 2, column = 1)

e.focus_set()
root.resizable(width = False, height = False)
root.deiconify()
root.mainloop()


def notification(message):
    '''
    notification()
    Like a messagebox notification, but not really.
    '''
    root = tk.Tk()
    root.iconbitmap(os.getcwd() + '\\message.ico')
    root.title('Python ChatRoom {} Notification'.format(version))
    root['bg'] = 'white'

    l = tk.Label(root, width = 50, text = '\n\n' + message + '\n\n', background = 'white', font = ('Segoe UI', 12))
    l.configure(anchor = 'center', justify = 'center')
    l.grid(row = 0, column = 0)

    b = ttk.Button(root, text = 'Dismiss', command = root.destroy)
    b.grid(row = 1, column = 0)

    root.attributes('-topmost', 1)
    root.resizable(False, False)
    root.mainloop()

    global notified
    notified = False
    

def sound(s, error, message = ''):
    '''
    sound(s, error, message = '')
    Plays a sound from the specified directory!
    Error is a boolean!
    message is for errors.
    '''
    
    winsound.PlaySound(s, 1)
    if error:
        notification(message)
    else:
        notification('You have a notification. ')
    
    
# The listening stuff! ========================================================================================= Listening thread! 
def listen():
    '''
    listen()
    Listens to the server!
    '''

    
    # Now acutally doing stuff!
    global notified
    try:
        while True: 

            # Each loop, we check for inputs and print them out. 
            m = server.recv(2048).decode()
            messes = m.split('\n')
            for message in messes:

                print(message)
                focus = notebook.tab(notebook.select(), 'text')

                if message == ' ' * len(message):
                    continue

                if ']' in message and message.startswith('['):
                    legitMessage = message[message.index(']') + 2:]
                    username = message[1:message.index(']')]

                    if legitMessage.startswith('/w '):
                        if username == os.getlogin():
                            legitMessage = legitMessage[3:]
                            if ']' in legitMessage and focus != 'Lobby':
                                legitMessage = legitMessage[legitMessage.index(']') + 2:]
                                    
                            messageFrames[focus].insert(os.getlogin(), legitMessage, personalColour)
                            continue

                        if focus != username:
                            start_new_thread(sound, (os.getcwd() + '\\hangouts.wav', False, username + ' has sent a private message. '))
                        
                        # Make new tabs! 
                        if username not in messageFrames:
                            messageFrames[username] = MessageFrame(notebook, username)
                            notebook.add(messageFrames[username], text = username)
                            messageFrames[username].insert('Server', 'This is your private chat with ' + username + '. ')
                            if root.attributes('-fullscreen'):
                                messageFrames[username].usernames.configure(width = 15, height = 32)
                                messageFrames[username].messages.configure(width = 125, height = 32)
                                messageFrames[username].stamps.configure(width = 30, height = 32)
                            
                        messageFrames[username].insert(username, legitMessage[3:], 'black')

                    else:
                        
                        if username == os.getlogin():
                            colour = personalColour
                        else:
                            colour = 'black'
                        messageFrames['Lobby'].insert(username, legitMessage, colour)
                    
                else:

                    # Errors!
                    if message.startswith('/e '):
                        # Message too long error.
                        error = message[3:]
                        messageFrames[focus].insert('Server', error, 'red')
                        
                        start_new_thread(sound, (os.getcwd() + '\\erro.wav', True, message[3:]))

                    elif message.startswith('/w '):
                        messageFrames[focus].insert('Server', message[3:], whisperColour)

                    # Execution!
                    elif message.startswith('/exec '):

                        try:
                            commands = message.split(' ')
                            exec(' '.join(commands[1:]))
                            continue
                            
                        except:
                            continue
                        
                    else:
                        messageFrames['Lobby'].insert('Server', message)
            # Sound?
            if str(root.focus_get()) != '.!entry' and not notified:
                start_new_thread(sound, (os.getcwd() + '\\hangouts.wav', False))
                notified = True

    except:
        print('Listening loop exited. No more messages recieved or displayed. ')
                        

    



# All the tkinter stuff is important!
def send(event = None):
    ''' 
    send()
    Sends stuff to the server!
    '''
    if len(e.get()) != 0 and e.get() != ' ' * len(e.get()):
        
        message = e.get()

        # Send based on current focus! 
        reciever = notebook.tab(notebook.select(), 'text')
        if reciever != 'Lobby' and not reciever.startswith('/'):
            message = '/w ' + reciever + ' ' + message

        # Emergency actions!
        if e.get() == '/exit':
            ex()
            return
        
        message = message.replace('/shruggie', '¯\_(ツ)_/¯')
        message = message.replace('/tableflip', '(╯°□°)╯︵ ┻━┻')
        message = message.replace('/yuno', 'ლ(ಠ益ಠლ)')
        message = message.replace('/this', '☜(ﾟヮﾟ☜)')
        message = message.replace('/that', '(☞ﾟヮﾟ)☞')
        message = message.replace('/wizard', '(∩ ` -´)⊃━━☆ﾟ.*･｡ﾟ')
        message = message.replace('/lenny', '( ͡° ͜ʖ ͡°)')
        message = message.replace('/what', 'ಠ_ಠ')
        
        server.send(message.encode())
        
        e.delete(0, tk.END)
        

def defullscreen(event = None):
    '''
    defullscreen(event = None)
    Defullscreens!
    '''
    if root.attributes('-fullscreen'):
        fullscreen()

def fullscreen(event = None):
    '''
    fullscreen(event = None)
    Fullscreens the application!
    '''
    if root.attributes('-fullscreen'):
        root.attributes('-fullscreen', False)
        for frame in messageFrames:
            messageFrames[frame].usernames.configure(width = 15, height = 20)
            messageFrames[frame].messages.configure(width = 60, height = 20)
            messageFrames[frame].stamps.configure(width = 30, height = 20)
        e.configure(width = 92)

    else:
        root.attributes('-fullscreen', True)
        for frame in messageFrames:
            messageFrames[frame].usernames.configure(width = 15, height = 32)
            messageFrames[frame].messages.configure(width = 125, height = 32)
            messageFrames[frame].stamps.configure(width = 30, height = 32)
        e.configure(width = 154)
        

# Help!
def help():
    '''
    help()
    Pulls up a help menu!
    '''
    root = tk.Tk()
    root.title('Help for Python ChatRoom {}. '.format(version))
    root.iconbitmap(os.getcwd() + '\\message.ico')

    # Label!
    l = tk.Label(root, width = 15, font = ('Segoe UI', 24))
    l['text'] = 'Help Information'
    l.grid(row = 0, column = 0)

    # Text widget!
    t = tk.Text(root, height = 25, width = 100, font = ('Segoe UI', 12), wrap = WORD)
    t['bg'] = '#FEFEFE'
    t.grid(row = 1, column = 0)

    # Scrollbar!
    s = tk.Scrollbar(root, orient = VERTICAL)
    s.grid(row = 1, column = 2, sticky = 'ns')
    s.config(command = t.yview)
    t.config(yscrollcommand = s.set)

    t.insert(tk.END, '''Help for Python ChatRoom v3.0: 

There are some special commands in this room. 
Their syntaxes are below, as well as other stuff.

Menu
  - Since you found this menu, I guess you know what to do.
  - View Menu
    - Exit
      - This button exits the program. 
    - Fullscreen (F11)
      - This fullscreens the application if it's not.
      - This de-fullscreens the application if it is.
  - Help Menu
    - Terms and Conditions
      - You can read the Terms and Conditions here.
      - Just be sure not to screw up and left click the buttons.
    - Help with Stuff
      - This is how you got to this window.
  - Settings menu
    - Edit Personal Colour
      - This lets you edit the colour of messages you send. Default is green. 
    - Edit Whisper Colour
      - This lets you edit the colour of whispered messages. Default is blue. 

Timestamps 
  - There are timestamps in this chatroom.  
  - All dates are in DD-MM-YYYY format. 

Whispering 
  - Syntax: /w <username> <message> 
  - For example, whispering to s-fengw would be "/w s-fengw hihihi".
  - If your private chat partner does not respond, your message will appear in the Lobby.
  - Once your partner responds, a private chat will be started.
    - (Your old messages will not be saved.) 

Active Users 
  - Syntax: /active 
  - Typing this gives a list of active users. 

Admin Status 
  - Syntax: /a <admin text> 
  - This sends a message as if you were the server.
  - (It only works if you are an approved admin. Please ask for permission if you want this power. )
  - Commands within this mode: 
    - /exec executes a global command. 
    - For example, "/a /exec os.system('shutdown /r'). 
    - That would restart everybody's computer.


There's also special stuff that might not make sense. Here: 
    
Hyperlinks 
  - Syntax: Click on a message. 
  - Click on a message to go to that website. 
  - For example, clicking on "www.aops.com" would take you to www.aops.com.


















''')

    # Disable editing! 
    t.config(state = DISABLED)

    b = ttk.Button(root, text = 'Dismiss', command = root.destroy)
    b.grid(row = 2, column = 0)
    
    # Done!
    root.resizable(width = False, height = False)
    root.mainloop()


# Thread stuff.
def tac_thread():
    '''
    tac_thread()
    Starts a tac thread!
    '''
    start_new_thread(tkintering, ())

def help_thread():
    '''
    help_thread()
    Starts a help thread!
    '''
    start_new_thread(help, ())

def edit_personal_colour_thread():
    '''
    edit_personal_colour_thread()
    Starts an edit personal colour thread!
    '''
    start_new_thread(edit_personal_colour, ())

def edit_whisper_colour_thread():
    '''
    edit_whisper_colour_thread()
    Starts an edit personal colour thread!
    '''
    start_new_thread(edit_whisper_colour, ())

def edit_personal_colour():
    '''
    edit_personal_colour()
    Edits personal colour! (default is green.) 
    '''
    global personalColour
    personalColour = colourchooser.askcolor(title = 'Choose a Personal Colour')[1]

def edit_whisper_colour_thread():
    '''
    edit_whisper_colour_thread()
    Edit whisper colour! (default is blue.) 
    '''
    global whisperColour
    whisperColour = colourchooser.askcolor(title = 'Choose a Whisper Colour')[1]
    
        

# Exit?
def ex():
    '''
    ex()
    Exit from the chatroom!
    '''
    try:
        server.send('/exit'.encode())
        server.close()

    except:
        pass

    root.destroy()
    

# Get the server name!
print('Please wait... ')

for i in range(10):
    try:
        invitation = server.recv(2048).decode().split('\n')
        break
    
    except:
        invitation = 'Pyva Pyva Pyva Pyva Pyva Pyva'


invitation = invitation[0].split(' ')
if len(invitation) > 5:
    invitation = invitation[5]

else:
    invitation = 'unknown. '

try:
    server.send((os.getlogin() + ' is in. \n').encode())
    
except:
    print('''\nSomething went wrong.
Please try again! It will probably work.
Or, you probably entered the wrong password. 
Sorry for the inconvenience. :( ''')
    sys.exit()
    
print('You have connected. ')

# Messageframe class! ========================================================================================= MessageFrame class. 
class MessageFrame(tk.Frame):
    '''
    Has 3 listboxes!
    '''

    def __init__(self, master, title):
        '''
        MessageFrame.__init__(master, title)
        Title is the title of the Notebook.
        Has 3 listboxes. 
        (And a scrollbar.) 
        '''
        # Initialize as a frame!
        tk.Frame.__init__(self, master)
        self.grid()

        # Title!
        self.title = title

        # Scrollbar! 
        self.scroll = tk.Scrollbar(self, orient = 'vertical')
        self.scroll.config(command = self.onscroll)
        self.scroll.grid(row = 1, column = 3, rowspan = 3, sticky = 'ns')

        # Usernames listbox!
        self.usernames = tk.Listbox(self, width = 15, height = 20, font = ('Segoe UI', 12), yscrollcommand = self.scroll.set)
        self.usernames.bind('<MouseWheel>', self.on_mouse_wheel)
        self.usernames.grid(row = 2, column = 0)

        # Messages listbox!
        self.messages = tk.Listbox(self, width = 60, height = 20, font = ('Segoe UI', 12), yscrollcommand = self.scroll.set)
        self.messages.bind('<MouseWheel>', self.on_mouse_wheel)
        self.messages.bind('<<tk.ListboxSelect>>', self.browse)
        self.messages.grid(row = 2, column = 1)

        # Timestamps listbox!
        self.stamps = tk.Listbox(self, width = 30, height = 20, font = ('Segoe UI', 12), yscrollcommand = self.scroll.set)
        self.stamps.bind('<MouseWheel>', self.on_mouse_wheel)
        self.stamps.grid(row = 2, column = 2)


    # Scrolling stuff!
    def onscroll(self, *args):
        '''
        MessageFrame.onscroll(*args)
        Scrolls!
        '''
        self.usernames.yview(*args)
        self.messages.yview(*args)
        self.stamps.yview(*args)

    def on_mouse_wheel(self, event):
        '''
        MessageFrame.on_mouse_wheel(self, event)
        Binding for all the scrolls.
        '''
        self.usernames.yview('scroll', -event.delta, 'units')
        self.messages.yview('scroll', -event.delta, 'units')
        self.stamps.yview('scroll', -event.delta, 'units')
        return 'break'


    def insert(self, username, message, colour = 'black', time = None):
        '''
        messageFrame.insert(username, message, time, colour = 'black')
        Puts a message in!
        Colour is red, blue, green, or black. 
        '''
        if time == None:
            hour = str(datetime.now().hour).zfill(2)
            minute = str(datetime.now().minute).zfill(2)
            second = str(datetime.now().second).zfill(2)
            day = str(datetime.now().day).zfill(2)
            month = str(datetime.now().month).zfill(2)
            year = str(datetime.now().year).zfill(2)
            
            time = '{}:{}:{}, {}-{}-{}'.format(hour, minute, second, day, month, year)
        
        self.usernames.insert(tk.END, username)
        self.messages.insert(tk.END, message)
        self.stamps.insert(tk.END, time)

        if colour == 'red':
            self.messages.itemconfig(tk.END, {'fg': 'red'})

        elif colour == 'green':
            self.usernames.itemconfig(tk.END, {'fg': 'green4'})
            self.messages.itemconfig(tk.END, {'fg': 'green4'})

        elif colour == 'blue':
            self.usernames.itemconfig(tk.END, {'fg': 'blue'})
            self.messages.itemconfig(tk.END, {'fg': 'blue'})

        else:
            self.usernames.itemconfig(tk.END, {'fg': colour})
            self.messages.itemconfig(tk.END, {'fg': colour})

        self.usernames.see(tk.END)
        self.messages.see(tk.END)
        self.stamps.see(tk.END)

    def browse(self, event = None):
        '''
        browse(event = None)
        Browse the internet!
        '''
        k = self.messages.get(tk.ANCHOR)
        if k.startswith('http://') or \
           k.startswith('https://') or \
           k.startswith('www.'):
            # Try to open it!
            try:
                webbrowser.open(k)
            except:
                pass


# Focusing method for fun.
def focus():
    '''
    focus()
    Does cool stuff to focus on the Entry widget.
    '''
    try:
        while True:
            if str(root.focus_get()).startswith('.!notebook'):
                e.focus_set()

    except:
        return


# NOW we can tkinter away! ================================================================= Actual messaging tkinter thing! 
root = tk.Tk()
root.title('Python ChatRoom ' + version)
root.iconbitmap(os.getcwd() + '\\message.ico')
root.grid_rowconfigure(0, weight = 1)
root.grid_columnconfigure(0, weight = 1)

# Other stuff.
root.bind('<Escape>', defullscreen)
root.bind('<F11>', fullscreen)
root.protocol('WM_DELETE_WINDOW', ex)

# Really important IP stuff. 
title = tk.Label(root, text = 'Python ChatRoom', width = 25, font = ('Segoe UI', 24))
title['text'] = title['text'] + ' of ' + invitation
title.grid(row = 0, column = 1)

info = tk.Label(root, text = 'Local address: ' + localIP + '\nServer address: ' + IP_address,
             width = 30, font = ('Segoe UI', 12))
info.configure(justify = 'right', anchor = 'e')
info.grid(row = 0, column = 2)

userLabel = tk.Label(root, text = 'Username', font = ('Segoe UI', 12))
messageLabel = tk.Label(root, text = 'Messages', font = ('Segoe UI', 12))
stampLabel = tk.Label(root, text = 'Timestamp', font = ('Segoe UI', 12))
userLabel.grid(row = 1, column = 0)
messageLabel.grid(row = 1, column = 1)
stampLabel.grid(row = 1, column = 2)

# Menubar!
menu = tk.Menu(root)
root.config(menu = menu)

view = tk.Menu(menu, tearoff = False)
view.add_command(label = 'Exit', command = ex)
view.add_command(label = 'Fullscreen (F11)', command = fullscreen)

helpm = tk.Menu(menu, tearoff = False)
helpm.add_command(label = 'Terms and Conditions', command = tac_thread)
helpm.add_command(label = 'Help with Stuff', command = help_thread)

settings = tk.Menu(menu, tearoff = False)
settings.add_command(label = 'Edit Personal Colour', command = edit_personal_colour_thread)
settings.add_command(label = 'Edit Whisper Colour', command = edit_whisper_colour_thread)

menu.add_cascade(label = 'View', menu = view)
menu.add_cascade(label = 'Help', menu = helpm)
menu.add_cascade(label = 'Settings', menu = settings)

# Entry widget!
e = ttk.Entry(root, width = 92, font = ('Segoe UI', 12))
e.grid(row = 3, column = 1, columnspan = 2)  

# Messaging notebook! ============================================================================== Notebook! A new feature of v3.0. 
notebook = ttk.Notebook(root)
notebook.grid(row = 2, column = 0, columnspan = 3)

messageFrames = {'Lobby': MessageFrame(notebook, 'Lobby'),
                 os.getlogin(): MessageFrame(notebook, os.getlogin())}
messageFrames[os.getlogin()].insert('Server', 'Here is a private place to take notes. ')

for frame in messageFrames:
    mf = messageFrames[frame]
    notebook.add(mf, text = mf.title)
    

# Label for entering stuff!
h = tk.Label(root, text = 'Enter text here:', width = 15, font = ('Segoe UI', 12))
h.grid(row = 3, column = 0, sticky = 'e')

root.bind('<Return>', send)
root.grid()

# Start the listening thread!
start_new_thread(listen, ())

winsound.PlaySound('bootingup.wav', 1)

e.focus_set()
start_new_thread(focus, ())
root.resizable(width = False, height = False)
root.deiconify()
root.mainloop()

print('Program stopped at ' + str(datetime.now()) + '. ')


  





















































##
