
# Python ChatRoom Client
#   ClientUI.py
# v5.0.4, November 2019

# Agh, imports.
import ctypes
import sys
import _thread

import hashlib

from datetime import datetime as dt

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import tkinter.colorchooser as colorchooser


class ClientUI():
    """
    This uses tkinter to make a nice UI for the chatroom.
    It has lots of methods.
    There is only ONE WINDOW because we are super OP at this.
    """

    def __init__(self, master):
        """
        ClientUI.__init__(master) -> ClientUI
        Makes a new ClientUI.
        Master describes the above Client class associated with this one.
        """
        # Set up attributes.
        self.master = master
        self.font = ("Segoe UI", self.master.data["fontSize"])
        self.s_font = (self.font[0], self.font[1] - 2)
        self.b_font = (self.font[0], self.font[1] + 5)
        self.icon_dir = "pyva.ico"
        self.prefix = ""
        self.whispercolor = "#0051FF"
        self.errorcolor = "#FF0000"
        self.personalcolor = "#33A314"
        self.bg = "#FFFFFF"
        self.fg = "#000000"
        self.save_pass = tk.IntVar()
        self.save_pass.set(int(self.master.data["loginInfo"][0] != ""))
        self.notifications = tk.IntVar()
        self.notifications.set(int(self.master.data["notifications"]))
        self.notified = False
        self.toplevels = set()

        # Set up widget attributes.
        self.daTitle = None
        self.cpTitle = None
        self.fileMenu = None
        self.helpMenu = None
        self.statsMenu = None
        self.optionsMenu = None
        self.accMenu = None

        self.style = ttk.Style()
        # self.style.theme_use("vista")
        self.configure_style()

        # ctypes hacking?
        if "win" in sys.platform:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
            self.user32 = ctypes.WinDLL("user32", use_last_error=True)
            self.masterID = self.user32.GetForegroundWindow()
            print(self.masterID)

        # Master attributes.
        # self.master.iconbitmap(self.icon_dir)
        self.master.resizable(True, True)
        self.master["bg"] = "white"
        self.master.protocol(
            "WM_DELETE_WINDOW", lambda event=None: _thread.start_new(self.on_closing, ()))
        self.master.bind(
            "<Return>", lambda event=None: _thread.start_new(self.master.login, ()))
        self.master.bind(
            "<Escape>", lambda event=None: _thread.start_new(self.on_closing, ()))
        for widget in self.master.winfo_children():
            if not type(widget) == tk.Toplevel():
                widget.grid_forget()
                del widget
        if not self.master.data["agreedToTaC"]:
            self.tac_info()
        self.master.resizable(False, False)

    def configure_login(self):
        """
        ClientUI.configure_login()
        Configures the login screen!
        This is a necessary function for the terms and conditions stuff.
        """
        print(f"Your local IP is {self.master.localIP}. ")
        print("Please sign in with the new window. ")

        # Set up as login frame first.
        self.master.title(f"Python ChatRoom {self.master.data['version']}")
        self.master.resizable(True, True)
        for widget in self.master.winfo_children():
            if not type(widget) == tk.Toplevel:
                widget.grid_forget()
            del widget
        self.master.bind(
            "<Return>", lambda event=None: _thread.start_new(self.master.login, ()))
        self.menubar = tk.Menu(self.master, relief="sunken")
        self.master.config(menu=self.menubar)

        self.fileMenu = tk.Menu(self.menubar, tearoff=0, font=self.s_font)
        self.fileMenu.add_command(label="Exit (Esc)", command=self.on_closing)
        self.menubar.add_cascade(label="File", menu=self.fileMenu)

        self.optionsMenu = tk.Menu(self.menubar, tearoff=0, font=self.s_font)
        self.optionsMenu.add_command(
            label="Change Font Size", command=self.configure_font)
        self.menubar.add_cascade(label="Options", menu=self.optionsMenu)
        self.title = tk.Label(
            self.master, bg=self.bg, width=50,
            text="Log in to the Chatroom", justify="center", font=self.font
        )
        self.button = ttk.Button(
            self.master, text="Log In",
            command=lambda event=None: _thread.start_new(self.master.login, ())
        )
        self.rButton = ttk.Button(
            self.master, width=20, text="Register New Account", command=self.register
        )
        self.savePassCB = ttk.Checkbutton(
            self.master, text="Remember Me", variable=self.save_pass
        )

        self.entries = [
            ttk.Entry(self.master, width=60, font=self.font)
            for _ in range(3)
        ]
        self.entries[0].focus_set()
        self.entries[2].configure(show="•")

        self.labels = []
        for i in ["IP Address: ", "Username: ", "Password: "]:
            self.labels.append(ttk.Label(self.master, text=i))

        for i in range(3):
            self.entries[i].grid(row=i + 1, column=2, padx=5, columnspan=3)
            self.labels[i].grid(
                row=i + 1, column=0, padx=5,
                pady=5, columnspan=2, sticky="e"
            )

        # Gridding!
        info = self.master.data["loginInfo"]
        for i in range(3):
            self.entries[i].insert(0, info[i])

        self.button.grid(row=4, column=2, padx=5, pady=5, sticky="w")
        self.rButton.grid(row=4, column=4, padx=5, pady=5, sticky="e")
        self.savePassCB.grid(row=4, column=3, padx=5, pady=5, sticky="w")
        self.title.grid(
            row=0, column=1, padx=10, pady=10, columnspan=4, sticky="ew"
        )

    def insert(self, message, title=None):
        """
        ClientUI.insert(message, title = None)
        Inserts a new message in the given tab.
        If title is not None, we don't get to choose.
        """
        if ">" in message:
            index = message.index(">")
            username = message[:index]
        else:
            index = -2
            username = ""
        substance = message[index + 2:]

        # Check for whispers and errors, and format appropriately.
        whisper = False
        error = False
        if substance.startswith("/w ") and title is None:
            whisper = True
            # If we whisper to somebody else, have it be in the same chat.
            if substance.startswith("/w To:") and username == self.master.username:
                title = substance.split(" ")[1][3:]
                substance = " ".join(substance.split(" ")[2:])
                whisper = False

            else:
                # Otherwise, somebody else has whispered to us.
                title = username

            if title not in self.chatBoxes and username != "Server":
                self.new_chat(title)
                self.insert(
                    f"Server> This is your private chat with {title}. ", title)
                # Put the appropriate tab into focus.
                self.chats.select(self.chatFrames[title])
            if username == "Server":
                title = "Lobby"

        if title is None:
            title = self.chats.tab(self.chats.select(), "text")

        if substance.startswith("/e ") and username == "Server":
            error = True
            title = self.chats.tab(self.chatFrames[title], "text")
            self.chats.select(self.chatFrames["Lobby"])

        autoscroll = self.scrollbars[self.chats.tab(
            self.chats.select(), "text")].get()[1] == 1

        # Insert text into the listboxes.
        if whisper or error:
            self.chatBoxes[title][1].insert("end", substance[3:])
        else:
            self.chatBoxes[title][1].insert("end", substance)

        self.chatBoxes[title][0].insert("end", username)
        self.chatBoxes[title][2].insert("end", str(dt.now()))

        # Based on settings, see the end.
        if autoscroll:
            for i in range(3):
                self.chatBoxes[self.chats.tab(
                    self.chats.select(), "text")][i].see("end")

        # coloring!
        if whisper and username != self.master.username:
            self.chatBoxes[title][0].itemconfig(
                "end", {"fg": self.whispercolor})
            self.chatBoxes[title][1].itemconfig(
                "end", {"fg": self.whispercolor})

        elif error:
            self.chatBoxes[title][0].itemconfig("end", {"fg": self.errorcolor})
            self.chatBoxes[title][1].itemconfig("end", {"fg": self.errorcolor})

        if username == self.master.username:
            self.chatBoxes[title][0].itemconfig(
                "end", {"fg": self.personalcolor})
            self.chatBoxes[title][1].itemconfig(
                "end", {"fg": self.personalcolor})

        # After that, raise notifications if necessary.
        if self.master.focus_get() is None and self.notifications.get() == 1 and not self.notified:
            self.notified = True
            nfWin = tk.Toplevel(self.master)
            self.toplevels.add(nfWin)
            nfWin.attributes("-topmost", True)
            nfWin.resizable(False, False)
            nfWin.title(self.master.title() + " Notification")
            nfWin.protocol(
                "WM_DELETE_WINDOW",
                lambda: self.close_notification(nfWin)
            )
            # nfWin.iconbitmap(self.icon_dir)
            nfWin.config(bg=self.bg)
            description = ttk.Label(nfWin, text="You have a new message: ")
            if whisper or error:
                label = tk.Label(
                    nfWin, bg=self.bg, text=f"{username}> {substance[3:]}", font=self.font
                )
                label.config(
                    fg=self.whispercolor if whisper else self.errorcolor)
            else:
                label = tk.Label(
                    nfWin, bg=self.bg, text=f"{username}> {substance}", font=self.font)

            description.grid(row=0, column=0, padx=20,
                             pady=(20, 0), sticky="w")
            label.grid(row=1, column=0, padx=20, sticky="w")

            closeButton = ttk.Button(
                nfWin, text="Dismiss", command=lambda: self.close_notification(nfWin))
            closeButton.grid(row=2, column=0, pady=5)

    def register(self, event=None):
        """
        ClientUI.register(event = None)
        Make a new account!
        """
        # Configure the chatroom.
        self.title["text"] = "Please enter the IP and your new account info. "
        self.title["fg"] = "#000000"
        self.title["width"] = self.title["width"] + 20
        self.title.grid(columnspan=3)
        self.button["text"] = "Back"
        self.button.configure(command=self.configure_login)
        self.button.grid(row=5, column=2)
        self.master.bind("<Return>", lambda event=None: _thread.start_new(
            self.master.make_account, ()))

        self.entries[0].focus_set()
        self.entries.append(ttk.Entry(
            self.master, width=self.entries[0]["width"],
            show=self.entries[2]["show"], font=self.font
        ))
        self.labels.append(ttk.Label(self.master, text="Confirm Password: "))
        self.entries[3].grid(row=4, column=2, columnspan=3)
        self.labels[3].grid(row=4, column=0, padx=5,
                            pady=5, columnspan=2, sticky="e")

        # Now make the proper stuff.
        self.rButton["text"] = "Create New Account"
        self.rButton.configure(command=lambda event=None: _thread.start_new(
            self.master.make_account, ()))
        self.rButton.grid(
            row=5, column=2, padx=5, pady=5, columnspan=2, sticky="e"
        )

    def new_chat(self, title):
        """
        ClientUI.new_chat(title)
        Makes a new chat within the chatroom system.
        We add Lobby first.
        """
        self.chatFrames[title] = tk.Frame(
            self.chats, bg=self.bg, width=100, height=60)
        self.chatFrames[title].columnconfigure(0, weight=0)
        self.chatFrames[title].columnconfigure(1, weight=1)
        self.chatFrames[title].columnconfigure(2, weight=0)
        self.scrollbars[title] = tk.Scrollbar(
            self.chatFrames[title], command=lambda *args: self.onvsb(*args, title=title))

        self.chatBoxes[title] = []
        widths = [20, 60, 30]
        for i in range(3):
            self.chatBoxes[title].append(tk.Listbox(
                self.chatFrames[title], width=widths[i], height=20, font=self.font, relief="flat"))
            self.chatBoxes[title][i].configure(
                bd=0, fg=self.fg, highlightthickness=0, selectmode="browse")
            self.chatBoxes[title][i].configure(
                yscrollcommand=self.scrollbars[title].set)
            self.chatBoxes[title][i].bind(
                "<MouseWheel>", lambda event: self.mouse_wheel(event, title))
            self.chatBoxes[title][i].grid(row=0, column=i, padx=5, sticky="we")
        self.chatBoxes[title][2].configure(justify="right")

        self.scrollbars[title].grid(row=0, column=3, sticky="ns")
        self.chatFrames[title].grid()
        self.chats.add(self.chatFrames[title], text=title)

    def configure_chatroom(self):
        """
        ClientUI.configure_chatroom()
        Changes the layout to the chatroom!
        """
        # Remember data if necessary.
        if self.save_pass.get() == 1:
            for i in range(3):
                self.master.data["loginInfo"][i] = self.entries[i].get()
            self.master.save_data()

        else:
            for i in range(3):
                self.master.data["loginInfo"][i] = ""
            self.master.save_data()

        # First, dismantle everything.
        for widget in self.master.winfo_children():
            if type(widget) == tk.Toplevel:
                widget.destroy()
            else:
                widget.grid_forget()
        self.master.resizable(True, True)

        # Add new menu stuff!
        self.helpMenu = tk.Menu(self.menubar, tearoff=0, font=self.s_font)
        self.helpMenu.add_command(label="IP Info", command=self.ip_info)
        self.helpMenu.add_command(
            label="Terms and Conditions",
            command=lambda: self.text_window(
                "Terms and Conditions", "Terms and Conditions.txt")
        )
        self.helpMenu.add_command(
            label="API Documentation",
            command=lambda: self.text_window("API Documentation", "api.txt")
        )
        self.menubar.add_cascade(label="Help", menu=self.helpMenu)

        self.statsMenu = tk.Menu(self.menubar, tearoff=0, font=self.s_font)
        self.statsMenu.add_command(
            label="Leaderboard", command=self.create_leaderboard)
        self.menubar.add_cascade(label="Statistics", menu=self.statsMenu)

        # TODO: get rid of duplication
        self.optionsMenu.add_command(
            label="Edit Whisper color", command=lambda: self.edit_color("whisper"))
        self.optionsMenu.add_command(
            label="Edit Error color", command=lambda: self.edit_color("error"))
        self.optionsMenu.add_command(
            label="Edit Personal color", command=lambda: self.edit_color("personal"))

        self.optionsMenu.add_separator()
        self.optionsMenu.add_checkbutton(
            label="Notifications", variable=self.notifications, command=self.configure_notifications)

        self.accMenu = tk.Menu(self.menubar, tearoff=0, font=self.s_font)
        self.accMenu.add_command(
            label="Delete Account", command=self.del_account)
        self.accMenu.add_command(
            label="Change Password", command=self.change_password)
        self.menubar.add_cascade(label="Account", menu=self.accMenu)

        # Chat management system!
        self.chats = ttk.Notebook(self.master)
        self.chatFrames = {}
        self.chatBoxes = {}
        self.scrollbars = {}
        self.entry = ttk.Entry(self.master, width=103, font=self.font)
        self.entry.focus_set()

        self.master.bind("<Return>", self.send)

        self.new_chat("Lobby")
        self.new_chat(self.master.username)
        self.insert(
            "Server> This is a private place to take notes. ",
            self.master.username
        )

        self.chats.grid(row=2, column=0, padx=5, pady=5,
                        columnspan=2, sticky="new")
        self.entry.grid(row=3, column=1, padx=(0, 5),
                        pady=5, columnspan=2, sticky="swe")
        ttk.Label(
            self.master, text=f"{self.master.username}>"
        ).grid(row=3, column=0, padx=(5, 0), pady=5)

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)

    def configure_style(self):
        """
        ClientUI.configure_style()
        Configues the style of the application.
        """
        self.style.configure(".", foreground=self.fg, background=self.bg)
        self.style.configure("TCheckbutton", font=self.font)
        self.style.configure("TLabel", foreground=self.fg,
                             background=self.bg, font=self.font)
        self.style.configure("TButton", font=self.s_font)
        self.style.configure("TNotebook.Tab", font=self.s_font)
        self.style.configure("TSpinbox", font=self.s_font)

        for widget in self.master.winfo_children():
            if type(widget) in [ttk.Entry, tk.Listbox, tk.Label]:
                widget.config(font=self.font)

        for menu in [self.fileMenu, self.optionsMenu, self.helpMenu, self.statsMenu, self.optionsMenu, self.accMenu]:
            try:
                menu.config(font=self.s_font)
            except:
                pass

        for window in self.toplevels:
            try:
                for widget in window.winfo_children():
                    if type(widget) in [ttk.Entry, tk.Listbox, tk.Label]:
                        widget.config(font=self.font)
                    if type(widget) in [Spinbox]:
                        widget.config(font=self.s_font)
            except:
                self.widget.remove(widget)

        if hasattr(self, "chatBoxes"):
            for title in self.chatBoxes:
                for i in range(3):
                    self.chatBoxes[title][i].config(font=self.font)

    def configure_title(self, message, widget, color=None):
        """
        ClientUI.loginerror(message, window, color = None)
        Changes the login title in given window.
        """
        if color is None:
            color = self.errorcolor

        if True:  # try:
            widget.config(fg=color)
            widget.config(text=message)
            widget.grid(row=0, column=2)

        else:  # except:
            print(message)

    def configure_cursor(self, cursor):
        """
        ClientUI.configure_cursor(cursor)
        Changes the cursor type, when loading, for example.
        """
        self.master.config(cursor=cursor)
        for widget in self.master.winfo_children():
            if ".!entry" in str(widget):
                if cursor == "wait":
                    widget.config(cursor=cursor)
                elif cursor == "":
                    widget.config(cursor="ibeam")
            else:
                widget.config(cursor=cursor)

        # Disable buttons and entry widgets.
        for widget in self.master.winfo_children():
            if type(widget) in [ttk.Button, ttk.Entry]:
                if cursor == "":
                    widget.config(state="normal")
                elif cursor == "wait":
                    widget.config(state="disabled")

    def configure_font(self):
        """
        ClientUI.configure_font()
        Changes font size.
        """
        def font_apply():
            """
            font_apply()
            Changes the font size and saves it.
            """
            size = int(self.spinbox.get())
            self.master.data["fontSize"] = size
            self.font = (self.font[0], size)
            self.s_font = (self.s_font[0], size - 2)
            self.b_font = (self.b_font[0], size + 5)
            self.configure_style()
            self.master.save_data()

        self.cfwin = tk.Toplevel(self.master)
        self.toplevels.add(self.cfwin)
        self.cfwin.transient(self.master)
        self.cfwin.resizable(False, False)
        self.cfwin.title("Choose the font size")
        # self.cfwin.iconbitmap(self.icon_dir)
        self.cfwin.config(bg=self.bg)
        self.spinbox = Spinbox(
            self.cfwin, width=10, from_=1, to_=72, wrap=True, font=self.s_font
        )
        self.spinbox.set(self.font[1])
        self.applybutton = ttk.Button(
            self.cfwin, text="Apply", command=font_apply)
        self.closebutton = ttk.Button(
            self.cfwin, text="Close", command=self.cfwin.destroy)
        self.fontLabel = ttk.Label(self.cfwin, text="Font size: ")

        self.fontLabel.grid(row=1, column=0, padx=5, pady=5, sticky="ne")
        self.spinbox.grid(row=1, column=1, padx=5, pady=5, sticky="e")
        self.applybutton.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.closebutton.grid(row=2, column=1, padx=5, pady=5, sticky="e")

    def configure_notifications(self):
        """
        ClientUI.configure_notifications()
        LAMBDAS. I HATE LAMBDAS.
        Saves notification data.
        """
        self.master.data["notifications"] = bool(self.notifications.get())
        self.master.save_data()

    def send(self, event=None):
        """
        ClientUI.send(event = None)
        Handle for pressing Enter.
        This takes into account which chat we are currently on.
        """
        if len(self.entry.get()) == 0:
            return

        prefix = self.chats.tab(self.chats.select(), "text")

        if prefix == "Lobby" or self.entry.get().startswith("/"):
            self.master.send(self.entry.get(), True)
            return

        else:
            self.master.send(f"/w {prefix} {self.entry.get()}", True)

    def on_closing(self):
        """
        self.on_closing()
        This is the protocol for when the "x" button is pressed.
        """
        if messagebox.askyesno(
            f"Python Chatroom {self.master.data['version']}",
            "Are you sure you want to exit? "
        ):
            self.master.dead = True
            try:
                self.master.send("/exit")
            except:
                pass
            try:
                self.master.destroy()
            except:
                pass

    def onvsb(self, *args, title):
        """
        ClientUI.onvsb(*args, title)
        This is a necessary handle for scrolling listboxes together.
        """
        for i in range(3):
            self.chatBoxes[title][i].yview(*args)

    def mouse_wheel(self, event, title):
        """
        ClientUI.mouse_wheel(event, title)
        Scrolls listboxes in unison.
        """
        for i in range(3):
            self.chatBoxes[title][i].yview(
                "scroll", -event.delta // 20, "units")

        return "break"

    def edit_color(self, color):
        """
        ClientUI.edit_color(color)
        Personalizes a color!
        """
        # TODO: remove duplication
        if color == "whisper":
            self.whispercolor = colorchooser.askcolor(
                parent=self.master, title="Choose color of Whispers")[1]
        elif color == "error":
            self.errorcolor = colorchooser.askcolor(
                parent=self.master, title="Choose color of Errors")[1]
        elif color == "personal":
            self.personalcolor = colorchooser.askcolor(
                parent=self.master, title="Choose Your Personal color")[1]

    def close_notification(self, notificationWindow):
        """
        ClientUI.close_notification(notificationWindow)
        Stupid lambdas...can't be multi-line. :(
        Also closes the window.
        """
        self.notified = False
        notificationWindow.destroy()
        del notificationWindow

    def ip_info(self):
        """
        ClientUI.ip_info()
        Brings up a new window with ip information!
        """
        ipInfoWin = tk.Toplevel(self.master, bg=self.bg)
        self.toplevels.add(ipInfoWin)
        ipInfoWin.transient(self.master)
        ipInfoWin.title(f"{ipInfoWin.title()} IP Info")
        # ipInfoWin.iconbitmap(self.icon_dir)
        ipInfoWin.grid_rowconfigure(0, weight=1)
        ipInfoWin.grid_columnconfigure(0, weight=1)
        closeButton = ttk.Button(
            ipInfoWin, text="Close", command=ipInfoWin.destroy)
        closeButton.grid(row=1, column=0, pady=(0, 5))

        label = ttk.Label(ipInfoWin)
        label.config(justify="left")
        serverInfo = self.master.server.getpeername()
        label["text"] = "\n".join((
            f"Local IP: {self.master.localIP}, Port: {self.master.port}",
            f"Server IP: {serverInfo[0]}, Port: {serverInfo[1]}"
        ))
        label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    def tac_info(self):
        """
        ClientUI.tac_info()
        Brings up a new window with terms and conditions.
        If agreeTo is True, we make buttons for that.
        """
        agree = tk.BooleanVar()
        agree.set(False)
        tk.Label(
            self.master, bg=self.bg,
            text="I made it short for you. Please read it. ", font=self.b_font
        ).grid(row=1, column=0, pady=5)
        check_button = ttk.Checkbutton(
            self.master, text="I agree to these Terms and Conditions. ", variable=agree)
        next_button = ttk.Button(
            self.master, text="Continue", state="disabled",
            command=lambda event=None: self.accept_TaC()
        )
        check_button.config(
            command=lambda: self.next_button_state(next_button, agree)
        )
        check_button.grid(row=2, column=0)
        next_button.grid(row=3, column=0, pady=10)

        self.master.title("Terms and Conditions")
        text = tk.Text(self.master, fg=self.fg, bg=self.bg,
                       font=self.font, wrap="word", relief="solid")
        scrollbar = tk.Scrollbar(self.master, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        text.grid(row=0, column=0, padx=(5, 3), pady=5, sticky="nesw")
        scrollbar.grid(row=0, column=1, sticky="ns")

        f = open("Terms and Conditions.txt", "r")
        tac = f.read()
        f.close()

        text.insert("end", tac)
        text.configure(state="disabled")

    def text_window(self, title, file):
        """
        ClientUI.text_window(title, file)
        Displays a window full of text!
        """
        win = tk.Toplevel()
        self.toplevels.add(win)
        # win.iconbitmap(self.icon_dir)
        win.transient(self.master)
        win.config(bg=self.bg)
        win.grid_rowconfigure(0, weight=1)
        win.grid_columnconfigure(0, weight=1)
        win.grid_columnconfigure(1, weight=1)
        win.title(f"{self.master.title()} {title}")

        text = tk.Text(win, font=self.font, wrap="word", relief="solid")
        scrollbar = tk.Scrollbar(win, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        text.grid(row=0, column=0, padx=(5, 3), pady=5, sticky="nesw")
        scrollbar.grid(row=0, column=1, sticky="ns")
        closeButton = ttk.Button(win, text="Close", command=win.destroy)
        closeButton.grid(row=1, column=0, pady=(0, 5))

        f = open(file, "r")
        words = f.read()
        f.close()
        text.insert("end", words)
        text.config(state="disabled")

    def accept_TaC(self):
        """
        ClientUI.accept_TaC(winToDestroy)
        Accept the Terms and Conditions and set the variable.
        """
        self.master.data["agreedToTaC"] = True
        self.master.save_data()
        self.configure_login()

    def next_button_state(self, button, var):
        """
        ClientUI.next_button_state(button, var)
        Handle for configuring buttons.
        """
        state = "normal" if var.get() else "disabled"
        button.config(state=state)

    def create_leaderboard(self):
        """
        ClientUI.leaderboard(update=False)
        Create a new window for the leaderboard.
        """
        self.leaderboard = tk.Toplevel(self.master, bg=self.bg)
        self.toplevels.add(self.leaderboard)
        self.leaderboard.transient(self.master)
        self.leaderboard.title("Mining Leaderboard")
        # self.leaderboard.iconbitmap(self.icon_dir)
        self.leaderboard.grid_rowconfigure(0, weight=1)
        self.leaderboard.grid_columnconfigure(0, weight=2)
        self.leaderboard.grid_columnconfigure(1, weight=3)
        self.leaderboard.grid_columnconfigure(2, weight=2)
        closeButton = ttk.Button(
            self.leaderboard, text="Close", command=self.leaderboard.destroy)
        updateButton = ttk.Button(
            self.leaderboard, width=19, text="Update Leaderboard",
            command=lambda event=None: self.master.send("/requestLeaderboard")
        )

        self.lbRanks = tk.Listbox(self.leaderboard)
        self.lbNames = tk.Listbox(self.leaderboard)
        self.lbCoins = tk.Listbox(self.leaderboard)
        for x in [self.lbRanks, self.lbNames, self.lbCoins]:
            x.config(width=20, height=20, font=self.font,
                     relief="solid", bd=0, highlightthickness=0, fg="#000000")

        self.lbRanks.grid(row=0, column=0, padx=(
            10, 10), pady=5, sticky="news")
        self.lbNames.grid(row=0, column=1, pady=5, sticky="news")
        self.lbCoins.grid(row=0, column=2, padx=(
            10, 10), pady=5, sticky="news")
        closeButton.grid(row=1, column=1, pady=5, columnspan=1)
        updateButton.grid(row=1, column=0, pady=5, columnspan=1)

        self.lbRanks.insert(0, "Rank")
        self.lbNames.insert(0, "User")
        self.lbCoins.insert(0, "Coins")

        self.lbRanks.config(state="disabled")
        self.lbNames.config(state="disabled")
        self.lbCoins.config(state="disabled")
        self.master.send("/requestLeaderboard")

    def updateLeaderboard(self, rawStr):
        """
        ClientUI.updateLeaderboard(rawStr)
        Updates the leaderboard with a raw string.
        """
        if not hasattr(self, "lbRanks"):
            self.create_leaderboard()
        rawInfo = rawStr.split(" ")
        info = []
        for i in rawInfo:
            info.append(i.split(","))

        self.lbRanks.config(state="normal")
        self.lbNames.config(state="normal")
        self.lbCoins.config(state="normal")
        self.lbRanks.delete(1, "end")
        self.lbNames.delete(1, "end")
        self.lbCoins.delete(1, "end")

        for i in range(len(info)):
            self.lbRanks.insert("end", i + 1)
            self.lbNames.insert("end", info[i][0])
            self.lbCoins.insert("end", info[i][1])
        self.lbRanks.config(state="disabled")
        self.lbNames.config(state="disabled")
        self.lbCoins.config(state="disabled")

    def del_account(self):
        """
        ClientUI.del_account()
        Delete one's account from the server.
        This requires one's password.
        """
        def try_del_account(event=None):
            """
            try_del_account(event = None)
            Inconvenient handle for return.
            """
            if len(self.daPassEntry.get()) == 0:
                return
            self.master.send("/delacc " + hashlib.sha512(
                (self.daPassEntry.get() + self.master.username).encode()).hexdigest())
            self.daPassEntry.delete(0, "end")
            self.daPassEntry.focus_set()

        self.dawin = tk.Toplevel(self.master)
        self.toplevels.add(self.dawin)
        self.dawin.transient(self.master)
        self.dawin.title("Delete your account")
        self.dawin.config(bg=self.bg)
        self.dawin.grid_columnconfigure(2, weight=1)

        # self.dawin.iconbitmap(self.icon_dir)
        self.daTitle = tk.Label(
            self.dawin, text="To confirm deletion, please enter your password below. ",
            font=self.font, fg=self.fg, bg=self.bg
        )
        self.daPassEntry = ttk.Entry(self.dawin, width=50, font=self.font)
        self.daPassEntry.config(show="•")
        self.daPassEntry.focus_set()
        self.delButton = ttk.Button(
            self.dawin, width=17,  text="Delete Account", command=try_del_account)

        ttk.Label(self.dawin, text="Password: ").grid(
            row=1, column=1, padx=(5, 0))

        self.daTitle.grid(row=0, column=2, padx=5, pady=5)
        self.daPassEntry.grid(row=1, column=2, padx=5, pady=5, sticky="we")
        self.delButton.grid(row=2, column=2, padx=5, pady=5)
        self.dawin.bind("<Return>", try_del_account)

    def change_password(self):
        """
        ClientUI.change_password()
        Authentication system for changing passwords.
        """
        def try_change_pass(event=None):
            """
            try_change_pass(event = None)
            Inconvenient handle for return.
            """
            if len(self.cp_pass_entry.get()) * len(self.cp_new_pass_entry.get()) == 0:
                return
            oldpass = hashlib.sha512(
                (self.cp_pass_entry.get() + self.master.username).encode()).hexdigest()
            newpass = hashlib.sha512(
                (self.cp_new_pass_entry.get() + self.master.username).encode()).hexdigest()
            self.master.data["loginInfo"][2] = ""
            self.master.save_data()
            creds = ("/newpass " + oldpass + " " + newpass).encode()
            self.master.send(creds)
            self.cp_pass_entry.delete(0, "end")
            self.cp_new_pass_entry.delete(0, "end")
            self.cp_pass_entry.focus_set()

        self.cpwin = tk.Toplevel(self.master)
        self.toplevels.add(self.cpwin)
        self.cpwin.transient(self.master)
        self.cpwin.title("Delete your account")
        self.cpwin.config(bg=self.bg)
        self.cpwin.grid_columnconfigure(2, weight=1)

        # self.cpwin.iconbitmap(self.icon_dir)
        self.cpTitle = tk.Label(
            self.cpwin, text="To change your password, please enter your info below. ",
            font=self.font, fg=self.fg, bg=self.bg
        )
        self.cp_pass_entry = ttk.Entry(
            self.cpwin, width=50, font=self.font, show="•"
        )
        self.cp_new_pass_entry = ttk.Entry(
            self.cpwin, width=50, font=self.font, show="•"
        )
        self.cp_pass_entry.focus_set()
        self.cp_button = ttk.Button(
            self.cpwin, width=17,  text="Change Password", command=try_change_pass)

        ttk.Label(self.cpwin, text="Old Password: ").grid(
            row=1, column=1, padx=(5, 0))
        ttk.Label(self.cpwin, text="New Password: ").grid(
            row=2, column=1, padx=(5, 0))

        self.cpTitle.grid(row=0, column=2, padx=5, pady=5, columnspan=2)
        self.cp_pass_entry.grid(row=1, column=2, padx=5, pady=5, sticky="we")
        self.cp_new_pass_entry.grid(
            row=2, column=2, padx=5, pady=5, sticky="we")
        self.cp_button.grid(row=3, column=2, padx=5, pady=5, columnspan=2)
        self.cpwin.bind("<Return>", try_change_pass)


class Spinbox(ttk.Entry):
    """Just in case. :)"""

    def __init__(self, master=None, **kw):

        ttk.Entry.__init__(self, master, "ttk::spinbox", **kw)

    def set(self, value):
        self.tk.call(self._w, "set", value)
