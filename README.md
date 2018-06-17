# BDO Discord Bot
A simple Discord Bot to replace some of the lost functionality when the original [BDO Bot](https://github.com/jojothegoat/bdobot) is shutdown.
This bot was built with the intention of running in on AWS Lambda. 

You can invite the bot to your server using this [link](https://discordapp.com/api/oauth2/authorize?client_id=457383567048310800&permissions=134144&scope=bot).

## Features:
* Notify when game service is online/offline
* Notify when a new patch is available
* Notify when new forum threads for patch notes, events and news & announcements are created

## Caveats:
* The bot will only post notifications to a channel named #announcements
* There are no commands available
* Because the bot runs on AWS lambda, it will only appear online when it checks for updates
* Updates occur every 5 minutes
