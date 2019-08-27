
# Python ChatRoom Client
#   ClientUI.py
# v4.1.2, August 2019

# Agh, imports.
import ctypes
import sys
import _thread
import time

from datetime import datetime as dt

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import tkinter.colorchooser as colourchooser

class ClientUI():
    '''
    This uses tkinter to make a nice UI for the chatroom.
    It has lots of methods.
    There is only ONE WINDOW because we are super OP at this.
    '''

    def __init__(self, master, data):
        '''
        ClientUI.__init__(master, data) -> ClientUI
        Makes a new ClientUI.
        Master describes the above Client class associated with this one.
        '''
        # Set up attributes.
        self.font = ('Segoe UI', 13)
        self.sFont = (self.font[0], self.font[1] - 2)
        self.bFont = (self.font[0], self.font[1] + 5)
        self.iconDir = 'pyva.ico'
        self.data = data
        self.master = master
        self.prefix = ''
        self.whisperColour = '#0051FF'
        self.errorColour = '#FF0000'

        # Set up tkinter styling!
        self.style = ttk.Style()
        # Try changing the themes to one of these, if you like.
        # ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
        self.style.theme_use('vista')
        self.style.configure('.', background = '#FFFFFF')
        self.style.configure('TCheckbutton', font = self.font)
        self.style.configure('TLabel', font = self.bFont)
        self.style.configure('TButton', font = self.sFont)
        self.style.configure('TNotebook.Tab', font = self.sFont)

        # ctypes hacking?
        if 'win' in sys.platform:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
            self.user32 = ctypes.WinDLL('user32', use_last_error = True)
            self.masterID = self.user32.GetForegroundWindow()
            print(self.masterID)

        # Master attributes.
        self.master.iconbitmap(self.iconDir)
        self.master.resizable(True, True)
        self.master['bg'] = 'white'
        self.master.protocol('WM_DELETE_WINDOW', lambda event = None: _thread.start_new(self.on_closing, ()))
        self.master.bind('<Return>', lambda event = None: _thread.start_new(self.master.login, ()))
        self.master.bind('<Escape>', lambda event = None: _thread.start_new(self.on_closing, ()))
        for widget in self.master.winfo_children():
            widget.grid_forget()
            del widget
        if not self.master.data['agreedToTaC']:
            self.tac_info(True)
        self.master.resizable(False, False)


    def configure_login(self):
        '''
        ClientUI.configure_login()
        Configures the login screen!
        This is a necessary function for the terms and conditions stuff.
        '''
        print('Your local IP is ' + self.master.localIP + '. ')
        print('Please sign in with the new window. ')
        
        # Set up as login frame first.
        self.master.title('Python ChatRoom ' + self.data['version'])
        self.master.resizable(True, True)
        for widget in self.master.winfo_children():
            widget.grid_forget()
            del widget
        self.master.bind('<Return>', lambda event = None: _thread.start_new(self.master.login, ()))
        self.menubar = tk.Menu(self.master, relief = 'sunken')
        
        self.fileMenu = tk.Menu(self.menubar, tearoff = 0)
        self.fileMenu.add_command(label = 'Exit (Esc)', command = self.on_closing, font = self.sFont)
        self.menubar.add_cascade(label = 'File', menu = self.fileMenu)

        self.master.config(menu = self.menubar)
        
        self.title = tk.Label(self.master, width = 50, bg = '#FFFFFF', text = 'Log in to the Chatroom', font = self.font)
        self.button = ttk.Button(self.master, text = 'Log In', command = lambda event = None: _thread.start_new(self.master.login, ()))
        self.rButton = ttk.Button(self.master, width = 20, text = 'Register New Account', command = self.register)
        
        self.entries = []
        for i in range(3):
            self.entries.append(ttk.Entry(self.master, width = 60, font = self.font))
        self.entries[0].focus_set()
        self.entries[2].configure(show = '•')

        self.labels = []
        for i in ['IP Address: ', 'Username: ', 'Password: ']:
            self.labels.append(tk.Label(self.master, bg = '#FFFFFF', text = i, font = self.font))

        # Gridding!
        for i in range(3):
            self.entries[i].grid(row = i + 1, column = 2, padx = 5, columnspan = 2)
            self.labels[i].grid(row = i + 1, column = 0, padx = 5, pady = 5, columnspan = 2, sticky = 'e')
        self.button.grid(row = 4, column = 2, padx = 5, pady = 5, sticky = 'w')
        self.rButton.grid(row = 4, column = 2, padx = 5, pady = 5, columnspan = 2, sticky = 'e')
        self.title.grid(row = 0, column = 2, pady = (5, 0))


    def insert(self, message, title = 'Lobby'):
        '''
        ClientUI.insert(message, title = 'Lobby')
        Inserts a new message in the given tab.
        If title is not Lobby, we don't get to choose.
        '''
        if '>' in message:
            index = message.index('>')
            username = message[:index]
        else:
            index = -2
            username = ''
        substance = message[index + 2:]

        # Check for whispers and errors, and format appropriately.
        whisper = False
        error = False
        if substance.startswith('/w ') and username.lower() != 'Server' and title == 'Lobby':
            whisper = True
            # If we whisper to somebody else, have it be in the same chat.
            if substance.startswith('/w To:') and username == self.master.username:
                title = substance.split(' ')[1][3:]
                substance = ' '.join(substance.split(' ')[2:])
                whisper = False
                
            else:
                # Otherwise, somebody else has whispered to us.
                title = username
                
            if title not in self.chatBoxes:
                self.new_chat(title)
                self.insert('Server> This is your private chat with ' + title + '. ', title)
            self.chats.select(self.chatFrames[title]) # Put the appropriate tab into focus.

        if substance.startswith('/e ') and username == 'Server':
            error = True
            title = self.chats.tab(self.chatFrames[title], 'text')
            self.chats.select(self.chatFrames['Lobby'])

        # Insert text into the listboxes.
        if whisper or error:
            self.chatBoxes[title][1].insert('end', substance[3:])
        else:
            self.chatBoxes[title][1].insert('end', substance)
        
        self.chatBoxes[title][0].insert('end', username)
        self.chatBoxes[title][2].insert('end', str(dt.now()))

        # Colouring!
        if whisper and username != self.master.username:
            self.chatBoxes[title][0].itemconfig('end', {'fg': self.whisperColour})
            self.chatBoxes[title][1].itemconfig('end', {'fg': self.whisperColour})

        elif error:
            self.chatBoxes[title][0].itemconfig('end', {'fg': self.errorColour})
            self.chatBoxes[title][1].itemconfig('end', {'fg': self.errorColour})

        # Based on settings, see the end.
        if username in [self.master.username, 'Server']:
            prefix = self.chats.tab(self.chats.select(), 'text')
            for i in range(3):
                self.chatBoxes[prefix][i].see('end')


    def register(self, event = None):
        '''
        ClientUI.register(event = None)
        Make a new account!
        '''
        # Configure the chatroom.
        self.title['text'] = 'Please enter the IP and your new account info. '
        self.title['fg'] = '#000000'
        self.title.grid()
        self.button['text'] = 'Back'
        self.button.configure(command = self.configure_login)
        self.button.grid(row = 5, column = 2)
        self.master.bind('<Return>', lambda event = None: _thread.start_new(self.master.make_account, ()))
        
        self.entries[0].focus_set()
        self.entries.append(ttk.Entry(self.master, width = self.entries[0]['width'], show = self.entries[2]['show'], font = self.font))
        self.labels.append(tk.Label(self.master, bg = '#FFFFFF', text = 'Confirm Password: ', font = self.font))
        self.entries[3].grid(row = 4, column = 2, columnspan = 2)
        self.labels[3].grid(row = 4, column = 0, padx = 5, pady = 5, columnspan = 2, sticky = 'e')

        # Now make the proper stuff.
        self.rButton['text'] = 'Create New Account'
        self.rButton.configure(command = lambda event = None: _thread.start_new(self.master.make_account, ()))
        self.rButton.grid(row = 5, column = 2, padx = 5, pady = 5, columnspan = 2, sticky = 'e')


    def new_chat(self, title):
        '''
        ClientUI.new_chat(title)
        Makes a new chat within the chatroom system.
        We add Lobby first.
        '''
        self.chatFrames[title] = tk.Frame(self.chats, bg = '#FFFFFF', width = 100, height = 60)
        self.chatFrames[title].columnconfigure(0, weight = 0)
        self.chatFrames[title].columnconfigure(1, weight = 1)
        self.chatFrames[title].columnconfigure(2, weight = 0)
        self.scrollbars[title] = tk.Scrollbar(self.chatFrames[title], command = lambda *args: self.onvsb(*args, title = title))
        
        self.chatBoxes[title] = []
        widths = [20, 60, 30]
        for i in range(3):
            self.chatBoxes[title].append(tk.Listbox(self.chatFrames[title], width = widths[i], height = 20, font = self.font, relief = 'flat'))
            self.chatBoxes[title][i].configure(bd = 0, fg = '#000000', highlightthickness = 0, selectmode = 'browse', takefocus = False)
            self.chatBoxes[title][i].configure(yscrollcommand = self.scrollbars[title].set)
            self.chatBoxes[title][i].bind('<MouseWheel>', lambda event: self.mouse_wheel(event, title))
            self.chatBoxes[title][i].grid(row = 0, column = i, padx = 5, sticky = 'we')
        self.chatBoxes[title][2].configure(justify = 'right')

        self.scrollbars[title].grid(row = 0, column = 3, sticky = 'ns')
        self.chatFrames[title].grid()
        self.chats.add(self.chatFrames[title], text = title)
        

    def configure_chatroom(self):
        '''
        ClientUI.configure_chatroom()
        Changes the layout to the chatroom!
        '''
        # First, dismantle everything.
        for widget in self.master.winfo_children():
            widget.grid_forget()
        self.master.resizable(True, True)
        self.master.grid_rowconfigure(0, weight = 1)
        self.master.grid_columnconfigure(0, weight = 1)
        self.master.grid_columnconfigure(1, weight = 1)

        # Add new menu stuff!        
        self.helpMenu = tk.Menu(self.menubar, tearoff = 0)
        self.helpMenu.add_command(label = 'IP Info', command = self.ip_info, font = self.sFont)
        self.helpMenu.add_command(label = 'Terms and Conditions', command = self.tac_info, font = self.sFont)
        self.menubar.add_cascade(label = 'Help', menu = self.helpMenu)

        self.statsMenu = tk.Menu(self.menubar, tearoff = 0)
        self.statsMenu.add_command(label = 'Leaderboard', command = self.createLeaderboard, font = self.sFont)
        self.menubar.add_cascade(label = 'Statistics', menu = self.statsMenu)

        self.optionsMenu = tk.Menu(self.menubar, tearoff = 0)
        self.optionsMenu.add_command(label = 'Edit Whisper Colour', command = lambda: self.edit_colour('whisper'), font = self.sFont)
        self.optionsMenu.add_command(label = 'Edit Error Colour', command = lambda: self.edit_colour('error'), font = self.sFont)
        self.menubar.add_cascade(label = 'Options', menu = self.optionsMenu)

        # Chat management system!
        self.chats = ttk.Notebook(self.master)     
        self.chatFrames = {}
        self.chatBoxes = {}
        self.scrollbars = {}
        self.entry = ttk.Entry(self.master, width = 103, font = self.font)
        self.entry.focus_set()
        
        self.master.bind('<Return>', self.send)

        self.new_chat('Lobby')
        self.new_chat(self.master.username)
        self.insert('Server> This is a private place to take notes. ', self.master.username)

        self.chats.grid(row = 2, column = 0, padx = 5, pady = 5, columnspan = 2, sticky = 'news')
        self.entry.grid(row = 3, column = 0, padx = 5, pady = 5, columnspan = 2, sticky = 'we')


    def logintitle(self, message, colour = None):
        '''
        ClientUI.loginerror(message, colour = None)
        Changes the login title.
        '''
        if colour == None:
            colour = self.errorColour
        self.title['fg'] = colour
        self.title['text'] = message
        self.title.grid(row = 0, column = 2)


    def configure_cursor(self, cursor):
        '''
        ClientUI.configure_cursor(cursor)
        Changes the cursor type, when loading, for example.
        '''
        self.master.config(cursor = cursor)
        for widget in self.master.winfo_children():
            if '.!entry' in str(widget):
                if cursor == 'wait':
                    widget.config(cursor = cursor)
                elif cursor == '':
                    widget.config(cursor = 'ibeam')
            else:
                widget.config(cursor = cursor)

        # Disable buttons and entry widgets.
        for widget in self.master.winfo_children():
            if type(widget) in [ttk.Button, ttk.Entry]:
                if cursor == '':
                    widget.config(state = 'normal')
                elif cursor == 'wait':
                    widget.config(state = 'disabled')


    def send(self, event = None):
        '''
        ClientUI.send(event = None)
        Handle for pressing Enter.
        This takes into account which chat we are currently on.
        '''
        if len(self.entry.get()) == 0:
            return

        prefix = self.chats.tab(self.chats.select(), 'text')
        
        if prefix == 'Lobby' or self.entry.get().startswith('/'):
            self.master.send(self.entry.get())
            return

        else:
            self.master.send('/w ' + prefix + ' ' + self.entry.get())

    
    def on_closing(self):
        '''
        self.on_closing()
        This is the protocol for when the 'x' button is pressed.
        '''
        if messagebox.askyesno('Python Chatroom ' + self.data['version'], 'Are you sure you want to exit? '):
            self.master.dead = True
            try:
                self.master.send('/exit', False)
            except:
                pass
            try:
                self.master.destroy()
            except:
                pass
        

    def onvsb(self, *args, title):
        '''
        ClientUI.onvsb(*args, title)
        This is a necessary handle for scrolling listboxes together.
        '''
        for i in range(3):
            self.chatBoxes[title][i].yview(*args)


    def mouse_wheel(self, event, title):
        '''
        ClientUI.mouse_wheel(event, title)
        Scrolls listboxes in unison.
        '''
        for i in range(3):
            self.chatBoxes[title][i].yview('scroll', -event.delta // 20, 'units')

        return 'break'


    def edit_colour(self, colour):
        '''
        ClientUI.edit_colour(colour)
        Personalizes a colour!
        '''
        if colour == 'whisper':
            self.whisperColour = colourchooser.askcolor(parent = self.master, title = 'Choose Colour of Whispers')[1]
        elif colour == 'error':
            self.errorColour = colourchooser.askcolor(parent = self.master, title = 'Choose Colour of Errors')[1]


    def ip_info(self):
        '''
        ClientUI.ip_info()
        Brings up a new window with ip information!
        '''
        ipInfoWin = tk.Toplevel(self.master, bg = '#FFFFFF')
        ipInfoWin.title(ipInfoWin.title() + ' IP Information')
        ipInfoWin.iconbitmap(self.iconDir)
        ipInfoWin.grid_rowconfigure(0, weight = 1)
        ipInfoWin.grid_columnconfigure(0, weight = 1)
        closeButton = ttk.Button(ipInfoWin, text = 'Close', command = ipInfoWin.destroy)
        closeButton.grid(row = 1, column = 0, pady = (0, 5))
        
        label = tk.Label(ipInfoWin, bg = '#FFFFFF', font = self.font)
        label.config(justify = 'left')
        serverInfo = self.master.server.getpeername()
        label['text'] = 'Local IP: ' + self.master.localIP + ', Port: ' + str(self.master.port) + \
                        '\nServer IP: ' + serverInfo[0] + ', Port: ' + str(serverInfo[1])
        label.grid(row = 0, column = 0, padx = 200, pady = 20, sticky = 'nsew')
        
        
    def tac_info(self, agreeTo = False):
        '''
        ClientUI.tac_info(agreeTo = False)
        Brings up a new window with terms and conditions.
        If agreeTo is True, we make buttons for that.
        '''
        if agreeTo:
            master = self.master
            agree = tk.BooleanVar()
            agree.set(False)
            ttk.Label(master, text = 'I made it short for you. Please read it. ').grid(row = 1, column = 0, pady = 5)
            checkButton = ttk.Checkbutton(master, text = 'I agree to these Terms and Conditions. ', variable = agree, onvalue = 1, offvalue = 0)
            nextButton = ttk.Button(master, text = 'Continue', state = 'disabled', command = lambda event = None: self.accept_TaC())
            checkButton.config(command = lambda: self.nextButtonState(nextButton, agree))
            checkButton.grid(row = 2, column = 0)
            nextButton.grid(row = 3, column = 0, pady = 10)
        else:
            tacInfoWin = tk.Toplevel(self.master, bg = '#FFFFFF')
            master = tacInfoWin
            tacInfoWin.title(tacInfoWin.title() + ' Terms and Conditions')
            tacInfoWin.iconbitmap(self.iconDir)
            tacInfoWin.grid_rowconfigure(0, weight = 1)
            tacInfoWin.grid_columnconfigure(0, weight = 1)
            tacInfoWin.grid_columnconfigure(1, weight = 0)
            closeButton = ttk.Button(tacInfoWin, text = 'Close', command = master.destroy)
            closeButton.grid(row = 1, column = 0, pady = (0, 5))

        master.title('Terms and Conditions')
        text = tk.Text(master, bg = '#FFFFFF', font = self.font, wrap = 'word', relief = 'solid')
        scrollbar = tk.Scrollbar(master, command = text.yview)
        text.configure(yscrollcommand = scrollbar.set)
        text.grid(row = 0, column = 0, padx = (5, 3), pady = 5, sticky = 'nesw')
        scrollbar.grid(row = 0, column = 1, sticky = 'ns')
        
        f = open('Terms and Conditions.txt', 'r')
        tac = f.read()
        f.close()

        text.insert('end', tac)
        text.configure(state = 'disabled')


    def accept_TaC(self):
        '''
        ClientUI.accept_TaC(winToDestroy)
        Accept the Terms and Conditions and set the variable.
        '''
        self.master.data['agreedToTaC'] = True
        self.master.save_data()
        self.configure_login()

    
    def nextButtonState(self, button, var):
        '''
        ClientUI.nextButtonState(button, var)
        Handle for configuring buttons.
        '''
        if not var.get():
            button.config(state = 'disabled')
        else:
            button.config(state = 'normal')
        

    def createLeaderboard(self):
        '''
        ClientUI.leaderboard(update = False)
        Create a new window for the leaderboard.
        '''
        self.leaderboard = tk.Toplevel(self.master, bg = '#FFFFFF')
        self.leaderboard.title('Mining Leaderboard')
        self.leaderboard.iconbitmap(self.iconDir)
        self.leaderboard.grid_rowconfigure(0, weight = 1)
        self.leaderboard.grid_columnconfigure(0, weight = 2)
        self.leaderboard.grid_columnconfigure(1, weight = 3)
        self.leaderboard.grid_columnconfigure(2, weight = 2)
        closeButton = ttk.Button(self.leaderboard, text = 'Close', command = self.leaderboard.destroy)
        updateButton = ttk.Button(self.leaderboard, width = 19, text = 'Update Leaderboard', command = lambda event = None: self.master.send('/requestLeaderboard', False))
        
        self.lbRanks = tk.Listbox(self.leaderboard)
        self.lbNames = tk.Listbox(self.leaderboard)
        self.lbCoins = tk.Listbox(self.leaderboard)
        for x in [self.lbRanks, self.lbNames, self.lbCoins]:
            x.config(width = 20, height = 20, font = self.font, relief = 'solid', bd = 0, highlightthickness = 0, fg = '#000000')
        
        self.lbRanks.grid(row = 0, column = 0, padx = (5, 10), pady = 5, sticky = 'news')
        self.lbNames.grid(row = 0, column = 1, pady = 5, sticky = 'news')
        self.lbCoins.grid(row = 0, column = 2, padx = (10, 5), pady = 5, sticky = 'news')
        closeButton.grid(row = 1, column = 1, pady = 5, columnspan = 1)
        updateButton.grid(row = 1, column = 0, pady = 5, columnspan = 1)

        self.lbRanks.insert(0, 'Rank')
        self.lbNames.insert(0, 'User')
        self.lbCoins.insert(0, 'Coins')
        
        self.lbRanks.config(state = 'disabled')
        self.lbNames.config(state = 'disabled')
        self.lbCoins.config(state = 'disabled')
        self.master.send('/requestLeaderboard', False)
        
        
    def updateLeaderboard(self, rawStr):
        '''
        ClientUI.updateLeaderboard(rawStr)
        Updates the leaderboard with a raw string.
        '''
        if not hasattr(self, 'lbRanks'):
            self.createLeaderboard()
        rawInfo = rawStr.split(' ')
        info = [] 
        for i in rawInfo:
            info.append(i.split(','))

        self.lbRanks.config(state = 'normal')
        self.lbNames.config(state = 'normal')
        self.lbCoins.config(state = 'normal')
        self.lbRanks.delete(1, 'end')
        self.lbNames.delete(1, 'end')
        self.lbCoins.delete(1, 'end')
        
        for i in range(len(info)):
            self.lbRanks.insert('end', i + 1)
            self.lbNames.insert('end', info[i][0])
            self.lbCoins.insert('end', info[i][1])
        self.lbRanks.config(state = 'disabled')
        self.lbNames.config(state = 'disabled')
        self.lbCoins.config(state = 'disabled')










    















## 
