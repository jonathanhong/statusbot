#Jonathan Hong
#this irc bot will connect to a certain channel/s and "listen" for certain input
#which is in the form of a color and a message. It will then login to the status page
#and post the message in the specified color. The page itself will automatically
#post to twitter and the rss feed.

import sys
import socket
import ssl
import string
import urllib
import urllib2
import cookielib
import credentials

readbuffer = ""

#this function will check the color from the list of valid colors
def checkColor(input):
    colors = ["green", "orange", "yellow", "red"]
    for color in colors:
        if (color == input):
            return True
    return False

#logs on via the login page
#sends the message via the home page after a successful login
#grabs the page after a request to check that the correct
#message is displayed.
def login(color, message, respondTo):
    #store cookie
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    login_data = urllib.urlencode(LOGINVALUES)
    #login
    opener.open(LOGINURL, login_data)
    resp = opener.open(LOGINURL)
    resphtml = resp.read()
    #if successfully logged in
    if (resphtml.find("You are already logged in!")):
        update_data = urllib.urlencode({'status' : message, 'color' : color})
        opener.open(UPDATEURL, update_data)
        resp = opener.open(UPDATEURL)
        resphtml = resp.read()
        #notify if the message was sent successfully
        if (resphtml.find(message)):
            irc.send("PRIVMSG %s :Update message sent.\r\n" % respondTo)
        else:
            irc.send("PRIVMSG %s :Update message not sent.\r\n" % respondTo)
    else:
        irc.send("PRIVMSG %s :Login failed.\r\n" % respondTo)
	
	
#gets the username of the person that sent the message
def getUser(str):
    index = str.find("!")
    return str[1:index]

#returns the help string to be messaged to a user via pm	
def getTutorial(user):
    irc.send("PRIVMSG %s :%s\r\n" % (user, "Syntax: !status [color] [message]\r\n:"))
    irc.send("PRIVMSG %s :%s\r\n" % (user, "Valid colors: [green, yellow, orange, red]\r\n"))

#connects to IRC, sets nick/user, joins channel
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
irc = ssl.wrap_socket(s)
irc.send("NICK %s\r\n" % NICK)
irc.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))
irc.send("JOIN %s %s\r\n" % (CHANNEL, PASSWORD))

#user = username, 
while 1:
    readbuffer = readbuffer+irc.recv(1024)
    temp = string.split(readbuffer, "\n")
    readbuffer = temp.pop( )
    #print(temp) #uncomment for reading the buffer

    #checks each line, splitting the line into words seperated by spaces
    for origline in temp:
        origline=string.rstrip(origline)
        line=string.split(origline)
        #checks for PING from server or normal message
        if (line[0] == "PING"):
            irc.send("PONG %s\r\n" % line[1])
        else:
            user = getUser(line[0])
        #checks for messages
        if(line[1] == "PRIVMSG"):
            #if they send a private message with "help"
            if (line[2].lower() == NICK and line[3].lower() == ":help"):
                getTutorial(user)
            #checks for channel message or a pm
            elif (line[2] == CHANNEL or line[2].lower() == NICK):
                #sets the correct user or channel to respond in
                if (line[2].lower() == NICK):
                    respondTo = user
                elif (line[2] == CHANNEL):
                    respondTo = CHANNEL
                #general prompt to respond to
                if (line[3].lower() == ":!status"):
                    #make sure proper number of arguments are there
                    #ex. irchandle:~user@box PRIVMSG #channel :!status [color] [message]
                    if (len(line) > 4):
                        color = line[4]
                        if (checkColor(color.lower())):
                            text = origline.split(color, 1)
                            #if they entered a message or not. login and send update
                            if (text[1] == ""):
                                irc.send("PRIVMSG %s :Please type \"!status help\" or \"/msg StatusBot help\" for correct usage.\r\n" % (respondTo))
                            else:
                                login(color, text[1].lower(), respondTo)
                        elif (color.lower() == "help"):
                            getTutorial(user)
                        else:
                            irc.send("PRIVMSG %s :Invalid color choice, please choose [green, yellow, orange, red].\r\n" % (respondTo))
                    else:
                        irc.send("PRIVMSG %s :Please type \"!status help\" or \"/msg StatusBot help\" for correct usage.\r\n" % (respondTo))
                #if someone just WANTS to type "statusbot:" lol
                elif (line[3].lower() == ":statusbot:"):
                    irc.send("PRIVMSG %s :Please type \"!status help\" or \"/msg StatusBot help\" for correct usage.\r\n" % (respondTo))
