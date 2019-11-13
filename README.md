
# Python ChatRoom Client

Welcome to the Python ChatRoom! Most help information is in this file, but some stuff is in the `api.txt` file. 
- You can find the API documentation inside the `api.txt` file. You don't really need to worry about this file unless you're planning on modifying the code or making your own chatroom.  
- You can find descriptions of updates in the `revisions.txt` file. 
- You **MUST** read the Terms and Conditions, contained in the `Terms and Conditions.txt` file, before using the chatroom. Alternatively, you can start the program and it will show them to you. 

This code was created by the Pyva Group in June of 2019. It has an Un-MIT license with it, which means you are free to use it however you like, and there's no real copyright. Use it however you want! **We strongly support tinkering around with code and learning through doing.** In v4.0, we rewrote all the code so that you can change things more easily! 

If you would like to contact us about any issues listed below, simply have a comment about the program such as improvements we can make or just praise, or have anything else to say, please use the email pyvagroup@gmail.com to get in touch. We'll try to reply as soon as possible, but please be patient. We usually respond in six to eight weeks. 

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
With your earned coins, you can buy things! There's not a lot of things you can buy right now. Right now, you can buy admin power (described above) with 1000 coins. (We might schange the price.) 

If you have suggestions for improving this system, please email us! We'd love to hear your ideas. In the future, we're thinking of adding a casino and a stock market. #### Security
There are also security features for this chatroom. Obviously, one needs to know the IP address of the server to connect. However, from v4.0, we added accounts! You are required to make an account with an appropriate username and password. Here are the conditions for usernames:

1. Usernames may not contain any of these characters: `<> |.:;,!?()[]{}@#\%*/\\~='"`.
2. Duplicate usernames are not allowed. 
3. Usernames may not be any of these keywords: "version", "keychars", "publicKey", "privateKey", "registeredIPs", "admins", or "users". 

One account per IP is our rule; we don't want people spamming accounts with one computer. The benefit of this system is that you get to log in on different computers while retaining the same username; also, you get to choose your username instead of having it forced upon you. 

Passwords are sent not in plaintext, but hashed and salted with SHA512. Passwords are stored on the server with SHA512 and with salts. (Don't worry if you don't know what that means; it means that your passwords are safe.) 

## Requirements

### Python environment
First, if you don't have Python, you should probably download it at https://www.python.org. Then, we highly suggest you learn Python. 

This code is written for Python 3, but it should work on earlier versions of Python so long as you modify the syntax differences. If anything doesn't work with earlier versions of Python and you can't figure out how to fix it, feel free to contact us. 

Note that you should have tkinter installed for this. If you don't, you can make changes to `_Client_<version>.py` to not be dependent on tkinter; there's only a few lines you'll need to change. 

If you can't figure out how to run this program, we highly suggest learning Python first, because we want you to learn new things! It will also help with personalizing your chatroom. 

### External Libraries
For security, we use the `rsa` and `pyaes` modules. These folders are copied from the official PyPi repositories, so installing them via `pip install` or some other way works and then you don't need to keep the files that come with the files here. But if you can't do `pip install`, then please keep the `rsa` and `pyaes` folders. 

## License
We don't actually have a license for this. We made the Un-MIT license that uses Un-copyright (that's not a real thing). So, you can use it however you want! There's nothing we can use against you, because again, **we strongly support tinkering around with code and learning through doing.** 