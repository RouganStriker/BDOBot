# Black Desert Online Discord Bot
A simple Discord Bot to replace some of the lost functionality when the original [BDO Bot](https://www.reddit.com/r/blackdesertonline/comments/8p30ii/bdobot_discord_bot_is_shutting_down/) is shutdown.
This bot was built assuming it will run on AWS Lambda with DynamoDB.

You can invite the bot to your server using this [link](https://discordapp.com/api/oauth2/authorize?client_id=457383567048310800&permissions=134144&scope=bot).

## Features
* Notify when game service is online/offline
* Notify when a new patch is available
* Notify when new forum threads for patch notes, events and news & announcements are created

## Configuration
The bot requires the following environment variables to run
#### All Plugins
* DISCORD_TOKEN - The bot's Discord token
#### Login Check Plugin
* BDO_USERNAME - Black Desert Online account username
* BDO_PASSWORD - Corresponding password for the Black Desert Online account
* ENVIRONMENT - Specify **AWS** if the bot is running on AWS with encrypted environment variables for the username and password

## Caveats
* The bot will only post notifications to a channel named #announcements
* There are no commands available
* Because the bot runs on AWS lambda, it will only appear online when it checks for updates
* Updates occur every 5 minutes
