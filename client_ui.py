"""
Python ChatRoom Client
    ClientUI.py
v5.0.4, November 2019
"""

# Agh, imports.
import ctypes
import datetime
import hashlib
import sys
import tkinter as tk
import tkinter.ttk as ttk

import _thread


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
        self.whisper_color = "#0051FF"
        self.error_color = "#FF0000"
        self.personal_color = "#33A314"
        self.bg = "#FFFFFF"
        self.fg = "#000000"
        self.save_pass = tk.IntVar()
        self.save_pass.set(int(self.master.data["loginInfo"][0] != ""))
        self.notifications = tk.IntVar()
        self.notifications.set(int(self.master.data["notifications"]))
        self.notified = False
        self.top_levels = set()

        # Set up widget attributes.
        self.da_title = None
        self.cp_title = None
        self.file_menu = None
        self.help_menu = None
        self.stats_menu = None
        self.options_menu = None
        self.acc_menu = None

        self.style = ttk.Style()
        # self.style.theme_use("vista")
        self.configure_style()

        # ctypes hacking?
        if "win" in sys.platform:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
            self.user32 = ctypes.WinDLL("user32", use_last_error=True)
            self.master_id = self.user32.GetForegroundWindow()
            print(self.master_id)

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
        print(f"Your local IP is {self.master.local_ip}. ")
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

        self.file_menu = tk.Menu(self.menubar, tearoff=0, font=self.s_font)
        self.file_menu.add_command(label="Exit (Esc)", command=self.on_closing)
        self.menubar.add_cascade(label="File", menu=self.file_menu)

        self.options_menu = tk.Menu(self.menubar, tearoff=0, font=self.s_font)
        self.options_menu.add_command(
            label="Change Font Size", command=self.configure_font)
        self.menubar.add_cascade(label="Options", menu=self.options_menu)
        self.title = tk.Label(
            self.master, bg=self.bg, width=50,
            text="Log in to the Chatroom", justify="center", font=self.font
        )
        self.button = ttk.Button(
            self.master, text="Log In",
            command=lambda event=None: _thread.start_new(self.master.login, ())
        )
        self.r_button = ttk.Button(
            self.master, width=20, text="Register New Account", command=self.register
        )
        self.save_pass_cb = ttk.Checkbutton(
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
        self.r_button.grid(row=4, column=4, padx=5, pady=5, sticky="e")
        self.save_pass_cb.grid(row=4, column=3, padx=5, pady=5, sticky="w")
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

            if title not in self.chat_boxes and username != "Server":
                self.new_chat(title)
                self.insert(
                    f"Server> This is your private chat with {title}. ", title)
                # Put the appropriate tab into focus.
                self.chats.select(self.chat_frames[title])
            if username == "Server":
                title = "Lobby"

        if title is None:
            title = self.chats.tab(self.chats.select(), "text")

        if substance.startswith("/e ") and username == "Server":
            error = True
            title = self.chats.tab(self.chat_frames[title], "text")
            self.chats.select(self.chat_frames["Lobby"])

        autoscroll = self.scrollbars[self.chats.tab(
            self.chats.select(), "text")].get()[1] == 1

        # Insert text into the listboxes.
        if whisper or error:
            self.chat_boxes[title][1].insert("end", substance[3:])
        else:
            self.chat_boxes[title][1].insert("end", substance)

        self.chat_boxes[title][0].insert("end", username)
        self.chat_boxes[title][2].insert("end", str(datetime.datetime.now()))

        # Based on settings, see the end.
        if autoscroll:
            for i in range(3):
                self.chat_boxes[self.chats.tab(
                    self.chats.select(), "text")][i].see("end")

        # coloring!
        if whisper and username != self.master.username:
            for i in (0, 1):
                self.chat_boxes[title][i].itemconfig(
                    "end", {"fg": self.whisper_color})

        elif error:
            for i in (0, 1):
                self.chat_boxes[title][i].itemconfig(
                    "end", {"fg": self.error_color})

        if username == self.master.username:
            for i in (0, 1):
                self.chat_boxes[title][i].itemconfig(
                    "end", {"fg": self.personal_color})

        # After that, raise notifications if necessary.
        if self.master.focus_get() is None and self.notifications.get() == 1 and not self.notified:
            self.notified = True
            nf_win = tk.Toplevel(self.master)
            self.top_levels.add(nf_win)
            nf_win.attributes("-topmost", True)
            nf_win.resizable(False, False)
            nf_win.title(f"{self.master.title()} Notification")
            nf_win.protocol(
                "WM_DELETE_WINDOW",
                lambda: self.close_notification(nf_win)
            )
            # nf_win.iconbitmap(self.icon_dir)
            nf_win.config(bg=self.bg)
            description = ttk.Label(nf_win, text="You have a new message: ")
            if whisper or error:
                label = tk.Label(
                    nf_win, bg=self.bg, text=f"{username}> {substance[3:]}", font=self.font
                )
                label.config(
                    fg=self.whisper_color if whisper else self.error_color)
            else:
                label = tk.Label(
                    nf_win, bg=self.bg, text=f"{username}> {substance}", font=self.font)

            description.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")
            label.grid(row=1, column=0, padx=20, sticky="w")

            close_button = ttk.Button(
                nf_win, text="Dismiss",
                command=lambda: self.close_notification(nf_win)
            )
            close_button.grid(row=2, column=0, pady=5)

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
        self.master.bind(
            "<Return>",
            lambda event=None: _thread.start_new(self.master.make_account, ())
        )

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
        self.r_button["text"] = "Create New Account"
        self.r_button.configure(command=lambda event=None: _thread.start_new(
            self.master.make_account, ()))
        self.r_button.grid(
            row=5, column=2, padx=5, pady=5, columnspan=2, sticky="e"
        )

    def new_chat(self, title):
        """
        ClientUI.new_chat(title)
        Makes a new chat within the chatroom system.
        We add Lobby first.
        """
        self.chat_frames[title] = tk.Frame(
            self.chats, bg=self.bg, width=100, height=60)
        self.chat_frames[title].columnconfigure(0, weight=0)
        self.chat_frames[title].columnconfigure(1, weight=1)
        self.chat_frames[title].columnconfigure(2, weight=0)
        self.scrollbars[title] = tk.Scrollbar(
            self.chat_frames[title], command=lambda *args: self.onvsb(*args, title=title))

        self.chat_boxes[title] = []
        widths = [20, 60, 30]
        for i in range(3):
            self.chat_boxes[title].append(tk.Listbox(
                self.chat_frames[title], width=widths[i], height=20, font=self.font, relief="flat"))
            self.chat_boxes[title][i].configure(
                bd=0, fg=self.fg, highlightthickness=0, selectmode="browse")
            self.chat_boxes[title][i].configure(
                yscrollcommand=self.scrollbars[title].set)
            self.chat_boxes[title][i].bind(
                "<MouseWheel>", lambda event: self.mouse_wheel(event, title))
            self.chat_boxes[title][i].grid(
                row=0, column=i, padx=5, sticky="we")
        self.chat_boxes[title][2].configure(justify="right")

        self.scrollbars[title].grid(row=0, column=3, sticky="ns")
        self.chat_frames[title].grid()
        self.chats.add(self.chat_frames[title], text=title)

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
        self.help_menu = tk.Menu(self.menubar, tearoff=0, font=self.s_font)
        self.help_menu.add_command(label="IP Info", command=self.ip_info)
        self.help_menu.add_command(
            label="Terms and Conditions",
            command=lambda: self.text_window(
                "Terms and Conditions", "Terms and Conditions.txt")
        )
        self.help_menu.add_command(
            label="API Documentation",
            command=lambda: self.text_window("API Documentation", "api.txt")
        )
        self.menubar.add_cascade(label="Help", menu=self.help_menu)

        self.stats_menu = tk.Menu(self.menubar, tearoff=0, font=self.s_font)
        self.stats_menu.add_command(
            label="Leaderboard", command=self.create_leaderboard)
        self.menubar.add_cascade(label="Statistics", menu=self.stats_menu)

        for color_name in ("whisper", "error", "personal"):
            self.options_menu.add_command(
                label=f"Edit {color_name.title()} color",
                command=lambda: self.edit_color(color_name)
            )

        self.options_menu.add_separator()
        self.options_menu.add_checkbutton(
            label="Notifications", variable=self.notifications,
            command=self.configure_notification
        )

        self.acc_menu = tk.Menu(self.menubar, tearoff=0, font=self.s_font)
        self.acc_menu.add_command(
            label="Delete Account", command=self.del_account)
        self.acc_menu.add_command(
            label="Change Password", command=self.change_password)
        self.menubar.add_cascade(label="Account", menu=self.acc_menu)

        # Chat management system!
        self.chats = ttk.Notebook(self.master)
        self.chat_frames = {}
        self.chat_boxes = {}
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

        self.chats.grid(
            ow=2, column=0, padx=5, pady=5, columnspan=2, sticky="new"
        )
        self.entry.grid(
            row=3, column=1, padx=(0, 5), pady=5, columnspan=2, sticky="swe"
        )
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
        self.style.configure(
            "TLabel", foreground=self.fg, background=self.bg, font=self.font
        )
        self.style.configure("TButton", font=self.s_font)
        self.style.configure("TNotebook.Tab", font=self.s_font)
        self.style.configure("TSpinbox", font=self.s_font)

        for widget in self.master.winfo_children():
            if type(widget) in [ttk.Entry, tk.Listbox, tk.Label]:
                widget.config(font=self.font)

        for menu in (
            self.file_menu, self.options_menu, self.help_menu,
            self.stats_menu, self.options_menu, self.acc_menu
        ):
            try:
                menu.config(font=self.s_font)
            except:
                pass

        for window in self.top_levels:
            try:
                for widget in window.winfo_children():
                    if type(widget) in [ttk.Entry, tk.Listbox, tk.Label]:
                        widget.config(font=self.font)
                    if type(widget) in [Spinbox]:
                        widget.config(font=self.s_font)
            except:
                self.widget.remove(widget)

        if hasattr(self, "chat_boxes"):
            for title in self.chat_boxes:
                for i in range(3):
                    self.chat_boxes[title][i].config(font=self.font)

    def configure_title(self, message, widget, color=None):
        """
        ClientUI.loginerror(message, window, color = None)
        Changes the login title in given window.
        """
        if color is None:
            color = self.error_color

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
        self.top_levels.add(self.cfwin)
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
        self.font_label = ttk.Label(self.cfwin, text="Font size: ")

        self.font_label.grid(row=1, column=0, padx=5, pady=5, sticky="ne")
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

        self.master.send(f"/w {prefix} {self.entry.get()}", True)

    def on_closing(self):
        """
        self.on_closing()
        This is the protocol for when the "x" button is pressed.
        """
        if tk.messagebox.askyesno(
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
            self.chat_boxes[title][i].yview(*args)

    def mouse_wheel(self, event, title):
        """
        ClientUI.mouse_wheel(event, title)
        Scrolls listboxes in unison.
        """
        for i in range(3):
            self.chat_boxes[title][i].yview(
                "scroll", -event.delta // 20, "units")

        return "break"

    def edit_color(self, color):
        """
        ClientUI.edit_color(color)
        Personalizes a color!
        """
        # TODO: remove duplication
        if color == "whisper":
            self.whisper_color = tk.colorchooser.askcolor(
                parent=self.master, title="Choose color of Whispers")[1]
        elif color == "error":
            self.error_color = tk.colorchooser.askcolor(
                parent=self.master, title="Choose color of Errors")[1]
        elif color == "personal":
            self.personal_color = tk.colorchooser.askcolor(
                parent=self.master, title="Choose Your Personal color")[1]

    def close_notification(self, notification_window):
        """
        ClientUI.close_notification(notification_window)
        Stupid lambdas...can't be multi-line. :(
        Also closes the window.
        """
        self.notified = False
        notification_window.destroy()
        del notification_window

    def ip_info(self):
        """
        ClientUI.ip_info()
        Brings up a new window with ip information!
        """
        ip_info_win = tk.Toplevel(self.master, bg=self.bg)
        self.top_levels.add(ip_info_win)
        ip_info_win.transient(self.master)
        ip_info_win.title(f"{ip_info_win.title()} IP Info")
        # ip_info_win.iconbitmap(self.icon_dir)
        ip_info_win.grid_rowconfigure(0, weight=1)
        ip_info_win.grid_columnconfigure(0, weight=1)
        close_button = ttk.Button(
            ip_info_win, text="Close", command=ip_info_win.destroy)
        close_button.grid(row=1, column=0, pady=(0, 5))

        label = ttk.Label(ip_info_win)
        label.config(justify="left")
        server_info = self.master.server.getpeername()
        label["text"] = "\n".join((
            f"Local IP: {self.master.local_ip}, Port: {self.master.port}",
            f"Server IP: {server_info[0]}, Port: {server_info[1]}"
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
            command=lambda event=None: self.accept_tac()
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
        self.top_levels.add(win)
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
        close_button = ttk.Button(win, text="Close", command=win.destroy)
        close_button.grid(row=1, column=0, pady=(0, 5))

        f = open(file, "r")
        words = f.read()
        f.close()
        text.insert("end", words)
        text.config(state="disabled")

    def accept_tac(self):
        """
        ClientUI.accept_tac(winToDestroy)
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
        self.top_levels.add(self.leaderboard)
        self.leaderboard.transient(self.master)
        self.leaderboard.title("Mining Leaderboard")
        # self.leaderboard.iconbitmap(self.icon_dir)
        self.leaderboard.grid_rowconfigure(0, weight=1)
        self.leaderboard.grid_columnconfigure(0, weight=2)
        self.leaderboard.grid_columnconfigure(1, weight=3)
        self.leaderboard.grid_columnconfigure(2, weight=2)
        close_button = ttk.Button(
            self.leaderboard, text="Close", command=self.leaderboard.destroy)
        update_button = ttk.Button(
            self.leaderboard, width=19, text="Update Leaderboard",
            command=lambda event=None: self.master.send("/requestLeaderboard")
        )

        self.lb_ranks = tk.Listbox(self.leaderboard)
        self.lb_names = tk.Listbox(self.leaderboard)
        self.lb_coins = tk.Listbox(self.leaderboard)
        for x in [self.lb_ranks, self.lb_names, self.lb_coins]:
            x.config(
                width=20, height=20, font=self.font,
                relief="solid", bd=0, highlightthickness=0, fg="#000000"
            )

        self.lb_ranks.grid(row=0, column=0, padx=(
            10, 10), pady=5, sticky="news")
        self.lb_names.grid(row=0, column=1, pady=5, sticky="news")
        self.lb_coins.grid(row=0, column=2, padx=(
            10, 10), pady=5, sticky="news")
        close_button.grid(row=1, column=1, pady=5, columnspan=1)
        update_button.grid(row=1, column=0, pady=5, columnspan=1)

        self.lb_ranks.insert(0, "Rank")
        self.lb_names.insert(0, "User")
        self.lb_coins.insert(0, "Coins")
        for i in (self.lb_ranks, self.lb_names, self.lb_coins):
            i.config(state="disabled")
        self.master.send("/requestLeaderboard")

    def update_leaderboard(self, raw_str):
        """
        ClientUI.update_leaderboard(raw_str)
        Updates the leaderboard with a raw string.
        """
        if not hasattr(self, "lb_ranks"):
            self.create_leaderboard()
        info = [
            i.split(",")
            for i in raw_str.split(" ")
        ]
        for i in (self.lb_ranks, self.lb_names, self.lb_coins):
            i.config(state="normal")
            i.delete(1, "end")

        for i in range(len(info)):
            self.lb_ranks.insert("end", i + 1)
            self.lb_names.insert("end", info[i][0])
            self.lb_coins.insert("end", info[i][1])

        for i in (self.lb_ranks, self.lb_names, self.lb_coins):
            i.config(state="disabled")

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
            if len(self.da_pass_entry.get()) == 0:
                return
            self.master.send("/delacc " + hashlib.sha512(
                (self.da_pass_entry.get() + self.master.username).encode()).hexdigest())
            self.da_pass_entry.delete(0, "end")
            self.da_pass_entry.focus_set()

        self.dawin = tk.Toplevel(self.master)
        self.top_levels.add(self.dawin)
        self.dawin.transient(self.master)
        self.dawin.title("Delete your account")
        self.dawin.config(bg=self.bg)
        self.dawin.grid_columnconfigure(2, weight=1)

        # self.dawin.iconbitmap(self.icon_dir)
        self.da_title = tk.Label(
            self.dawin, text="To confirm deletion, please enter your password below. ",
            font=self.font, fg=self.fg, bg=self.bg
        )
        self.da_pass_entry = ttk.Entry(self.dawin, width=50, font=self.font)
        self.da_pass_entry.config(show="•")
        self.da_pass_entry.focus_set()
        self.del_button = ttk.Button(
            self.dawin, width=17,  text="Delete Account", command=try_del_account)

        ttk.Label(self.dawin, text="Password: ").grid(
            row=1, column=1, padx=(5, 0))

        self.da_title.grid(row=0, column=2, padx=5, pady=5)
        self.da_pass_entry.grid(row=1, column=2, padx=5, pady=5, sticky="we")
        self.del_button.grid(row=2, column=2, padx=5, pady=5)
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
        self.top_levels.add(self.cpwin)
        self.cpwin.transient(self.master)
        self.cpwin.title("Delete your account")
        self.cpwin.config(bg=self.bg)
        self.cpwin.grid_columnconfigure(2, weight=1)

        # self.cpwin.iconbitmap(self.icon_dir)
        self.cp_title = tk.Label(
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

        self.cp_title.grid(row=0, column=2, padx=5, pady=5, columnspan=2)
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
