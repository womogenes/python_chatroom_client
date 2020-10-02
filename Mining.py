
# Mining.py aaaaaaaaaaaaaaaa
# Python Chatroom 
# 
# You can edit this file to mine coins. 
# ================================================================ 
# HOW THIS WORKS 
#   If you send a message to the server of this format: 
#       /mine <string>, 
#   The server will append the previous hash to <string> and hash 
#       it with a sha512 hash. If this hash starts with at least 
#       a given number of zeroes, you earn 5 coins. This <string> 
#       must be 86 characters long. 
# 
#   This previous hash is stored in "client.prevHash". 
#       This variable changes as people mine and earn money. 
#   The given number of zeroes is stored in "client.hashZeroes". 
#       This variable may or may not change. 
# 
#   The protocol for sending hashes is 
#       client.send("/mine " + <string>, False). 
#   You should check your hashes with the following function: 
#          hashlib.sha512(<string>).hexdigest() 
#       to check if it contains an adequate amount of leading zeroes 
#       before you send it off to the server. The server is not 
#       meant to be a checking service. DO NOT SPAM THE SERVER. 
# 
#   The following function will be executed as a thread every time 
#       you log on. Edit it for mining. You can use any libraries 
#       you like or not use any libraries, but you are not allowed 
#       to spam the server. 
#       (Some coding experience is required.) 
# 
# ================================================================ 
#   As you can see, this is a bashy process. Testing hashes will 
#       require lots of CPU power. You do not need to mine, but 
#       earning coins can let you buy things, described in other 
#       documents. 
# 
# Have fun! 

import hashlib

def mine(client):
    '''
    mine(client)
    Edit this function to mine coins.
    Instructions are included with this file.
    '''
    return
