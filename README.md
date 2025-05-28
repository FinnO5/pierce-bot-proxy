# pierce-bot-proxy
A Discord bot system that lets users send and receive messages in servers through the bot’s identity using a custom web UI — perfect for when you can’t use your own account directly.
chat-gpt
__________________
I did in fact use chat gpt in the making of this, and right before I uploaded I asked it to just go through make clean up my comments, but not chnage any fucntinality. The proccess I go through is me driven, the ai is like a unpaid intern working for me(😿). Its definetly better at me at some things, but ultimatly I need to be leading and doing to bulk of th work. At least that is the way that it is sattfiitying for me 🤷.

Purpose
____________________
This system is designed primarily for teens who want to use Discord, but whose parents have restrictions on their phone, computer, or internet access. It allows you to use Discord without having the official app installed and without being logged in directly.

The project is meant to appear harmless and secure from a parent's perspective—especially if they're not particularly tech-savvy. When you open the index page, you'll see a simple set of buttons. Entering the correct password unlocks the actual Discord-like interface.

You can run this server on something like a Raspberry Pi and hide the device somewhere out of sight (like in a closet). When you're ready, just connect to it from your phone. If you need to hide the interface quickly, clicking one of the password buttons will hide the UI and return to the basic button page.

Even in your browser history, it will just show localhost or a local network address, and if a parent visits it, they'll only see the basic button screen—not the actual chat UI.

But ultimatly i can see many uses for it.


IT DOESN’T WORK! (set up)
_________________________

okay here’s what you need to do:

0. **Clone the repo**

1. install dependecnys and maybe python 3.12, thats what i used 🤷

2. **Make a Discord developer account**, add a new application, and make sure it has a bot.  

3. Go to the **Installation** tab in the application page and change the default install settings:  
   - **Scopes**: `application.commands`, `bot`  
   - **Permissions**: `Read Message History`, `Send Messages`  

4. Copy the generated install link and use it to add your bot to whichever server you want.  

5. Go to the **Bot** tab and copy the bot token.  

6. put your new bot token in the .env file in the program directory

Tenor search widget isnt working!!!!
1. you need a tenor search api key, so you will first need to make a developer aocunt and then get one from their site
2. and then put your key into the html
3. or you could jsut opne tenor in another tab and copy in links


Feature List!
--------------------
weve got 
-sending messages

-loading messages

-able to be pulled from channel to channel with !bind

-sending gifs

-displaying gifs

-auto update on other user sent message

-user chosen amount of queried messages

-a dynamic and awsome ui

-no encryption at all

-no security whatsoever

-BURN IT ALL feature built into when you click one of those password buttons, it clears the iframe






