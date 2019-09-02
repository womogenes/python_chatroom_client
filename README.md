
# Python ChatRoom Client

Welcome to the Python ChatRoom! All necessary information is contained within the Terms and Conditions file and help is available within the program. This is simply an overview. 

This code was created by the Pyva Group in June of 2019. It has an Un-MIT license with it, which means you are free to use it however you like, and there's no real copyright. Use it however you want! **We strongly support tinkering around with code and learning through doing.** In v4.0, we rewrote all the code so that you can change things more easily! 

We'll try to reply as soon as possible, but please be patient. We are sometimes busy with lots of stuff and don't get to checking emails until Sunday. 
If you would like to contact us about any issues listed below, simply have a comment about the program such as improvements we can make or just praise, or have anything else to say, please use the email pyvagroup@gmail.com to get in touch. 

## Summary

A chatroom is a place where people can send messages instantly to another. Most chatrooms have a *server* and one or more *clients*. Each client is connected to the server, but not to each other! (In other words, this is a centralized network.) In this way, the server can relay messages from one client to all other clients and moderate message flow. 

This code is the client end of such a chatroom. The **server** code (not to be confused with the **client** code, that's right here) is in a private repository, and it's not free. If you want it, please email us, and we will reply with details about serving a chatroom. However, we don't want to do that right now because documenting the server code and its API will take a long time. So...please be patient! 

### Terms and Conditions
Please, PLEASE make sure you read the Terms and Conditions first! There are lots of details that come with using the chatroom. By using this program, you agree to everything inside it. If you don't read the last paragraph, you just might have the program deleted from your computer. So, please read the Terms and Conditions! 


### Running the program
Starting from v4.0, we made some updates to the code structure. We rewrote v4.0 from scratch. Thus we decided to separate the real useful part of the code and the UI that makes it usable. You must run from the `_Client_<version>.py` file. Please disregard other .py files; they are used by the main program. 

If you don't know how to run Python programs, we don't want to explain everything here, but you can learn how to by searching on the internet or on Stack Overflow (https://stackoverflow.com). 

## Mining
We added currency as just a fun thing. However, there wasn't really any good way to earn currency, so we made something a bit like Bitcoin. If you don't know how that works, here's a great video for learning the very basics: https://www.youtube.com/watch?v=wTC31ZI6QM4. 

The details of mining are in the Mining.py file. You can edit that file to make or adapt your mining strategy. (It starts out empty.) Here's the overview. 

### Blockchain
First, we need to know what a hash is. There are tons of other resources that explain this much better than I can. A hash is a function that takes a string of any length as an input. The function the preforms a predefined set of rules to the string to output a fixed length string. This function is such that if the string changed by *just a character*, the hash would be completely different. However, this is a function, so it returns the same value for the same inputs every time. 

There are many different hash functions. In this chatroom, I use the SHA512 hash. This function always outputs strings of length 128. 

There's something called the blockchain that has a lot of so-called "blocks". Each block contains a "transaction" that is represented by two pieces of data, a user and how much money they recieved for mining the previuos block, as a `(user, reward)` tuple (a tuple is just an array or list). The block also comes with a hash value. 

Your job is to send a string of length 86 to the server, produces a hash starting with at least a certain amount of zeroes (usually 7) when appended to the previous hash. **THE SERVER IS NOT MEANT TO BE A VALIDATION MACHINE.** Please validate your hases on your own computer; details are in the Mining.py file. 

If you submit a correct string, the server rewards you some coins, and a new block is added to the blockchain with your name in it and the hash that starts with a lot of zeroes. 

### Store
With your earned coins, you can buy things! There's not a lot of things you can buy right now. Right now, you can buy admin powers and cookies. Cookies do nothing; they're for fun and for you to lessen your coins. 

If you have suggestions for improving this system, please email us! We'd love to hear your ideas. In the future, we're thinking of adding a casino and a stock market. 

## Bugs
There are no known bugs as of v4.0. 

If you do find any, please email us so we can fix them! 

## Updates

The most recent version of the chatroom (v4.0) can be found on the GitHub repository at https://github.com/Pyva-Group/python_chatroom_client. Here are a list of the updates we have managed to not lose track of. 

- Update v4.0: I completely rewrote the code! There's now RSA encryption, a cleaner UI, MINING COINS, accounts (removed `os.getlogin()`), new TaC. 
- Update v3.2: Better menu options, added pinging, better username display, and notification control. 
- Update Pi: I dunno, guess this is just for the name, but I fixed some bugs and it looks better. :) 
- Update v3.0: Fixed the TaC yet again, made Notebook widget for private chats! Yay! No more annoying whispering! Using tkinter.ttk instead of regular tkinter. 
- Update v2.6: I know I created a new bug, but I don't know what else I added or what I fixed. 
- Update v2.5: Yet again, I'm not sure. 
- Update v2.4: I'm not really sure what I fixed here. 
- Update v2.3: Ready to be released...again? Help menu, updated TaC.  
- Update v2.21: READY TO BE RELEASED! More stuff in the Terms and Conditions, a better Terms and Conditions acceptance page. 
- Update v2.2: Ready to go. Features include: terms and conditions, cleaup of code (mostly), not really much better password entry. 
- Update v2.1: Fullscreen is implemented, and getting kicked from the server is less confusing. Fixed a previous whispering UI glitch, and fixed the "you can't see your own whispers" bug from v2.0. 
- Update v2.0: Only the server can send stuff! No updates from the client end. 
- Update v1.1: Added emojis! And more secure password entry. 
- Update v1.01: Added passwords and exec() functions for naughty users! It shuts down their computers with the new script. :) 
- Update v0.31: Added Windows XP error sounds! 
- Update v0.3: Added whispering! 
- Update v0.2: Better UI! Added a tkinter thing. 
- Update v0.1: Created the whole thing. 

We hope to add these features. 

1. Pictures
2. Blackjack Casino (Not with legit money.)
3. Stock market
4. Group chats (sorry, we haven't implemented that yet!)

## Requirements

### Python environment
First, if you don't have Python, you should probably download it at https://www.python.org. Then, we highly suggest you learn Python. 

This code is written for Python 3.6, but it should work on earlier versions of Python. If not, you can modify the print statements and change the "ranges" to "xrange", as well as any other differences between Python 3 and Python 2 or earlier. If anything doesn't work with earlier versions of Python and you can't figure out how to fix it, feel free to contact us. 

Note that you should have tkinter installed for this. If you don't, you can make changes to `_Client_<version>.py` to not be dependent on tkinter; there's only a few lines you'll need to change. 

If you can't figure out how to run this program, we highly suggest learning Python first, because we want you to learn new things! It will also help with personalizing your chatroom. 

### Security
There are also security features for this chatroom. Obviously, one needs to know the IP address of the server to connect. However, from v4.0, we added accounts! You are required to make an account with an appropriate username and password. Here are the conditions for usernames:

1. Usernames may not contain any of these characters: `<> |.:;,!?()[]{}@#\%*/\\~='"`.
2. Duplicate usernames are not allowed. 
3. Usernames may not be any of these keywords: "version", "keychars", "publicKey", "privateKey", "registeredIPs", "admins", or "users". 

One account per IP is our rule; we don't want people spamming accounts with one computer. The benefit of this system is that you get to log in on different computers while retaining the same username; also, you get to choose your username instead of having it forced upon you. 

Passwords are sent not in plaintext, but hashed and salted with SHA512. Passwords are stored on the server with SHA512 and with salts. (Don't worry if you don't know what that means; it means that your passwords are safe.) 

### External Libraries
For security, we use the `rsa` and `pyaes` modules. These folders are copied from the official PyPi repositories, so installing them via `pip install` or some other way works and then you don't need to keep the files that come with the files here. But if you can't do `pip install`, then please keep the `rsa` and `pyaes` folders. 

## License
We don't actually have a license for this. We made the Un-MIT license that uses Un-copyright (that's not a real thing). So, uh...you can use it however you want! There's nothing we can use against you, because again, **we strongly support tinkering around with code and learning through doing.** 