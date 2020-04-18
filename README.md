# Discord Voice Channel Kick Bot

This bot will every so often join a random voice channel that it can see, play
an audio file, and kick a random user from said voice channel. Then leaves the
voice channel.

It can optionally send messages to the kicked user in a DM afterwards.

This is very useful I swear.

Can also be activated on command with a secret word that can only be executed
by approved users. The bot waits a random amount of time after this command has
been sent to make it difficult for others to determine what the command is.

## Setting Up

### Dependencies

You need to have [ffmpeg](https://ffmpeg.org/) installed on your system.

Then create a python environment and install the required python modules:

```
python -m virtualenv -p python3 env
source env/bin/activate
pip install -r requirements.txt
```

### Config

Copy `sample.config.yaml` to `config.yaml` and edit to your desire.

Options:

* `bot_token` **Required.** Your Discord bot token.
* `allowed_command_user_ids` **Required.** The Discord numberical IDs of the
  users who are allowed to execute bot commands.
* `audio_clip_filepath` **Required.** The path to the audio file to play before
  kicking a user.
* `trigger_phrase` If a user that's allowed to execute commands says this
  phrase, the bot will join a voice channel and kick a user. The phrase is
  case-insensitive.
* `picture_folder` Folder of pictures to send to the kicked user afterwards in
  a DM. If empty or not defined, the bot will not DM any pictures.
* `picture_amount` How many pictures to pull from `picture_folder`. Defaults to 1.
* `picture_captions` A list of captions for each sent photos.
  The bot will pick a random one to send with each picture. If the list if empty,
  picture captions will not be added.
* `before_picture_messages` A list of messages to DM the user after kicking them.
  Defaults to an empty list. Sends before photos.
* `between_picture_delay` Delay in seconds between sending each photo. Defaults
  to 0.
* `after_picture_messages` A list of messages to DM the user after kicking them.
  Defaults to an empty list. Sends after photos.
* `targeted_victims` A list of Discord User IDs and ratios of how likely they are
  to get kicked.

## Running the bot

Make sure the python environment is activated, then start the bot:

```
source env/bin/activate
python ./main.py
```

## Inviting the bot to your server

To actually get the bot into your server, you need to open the following link
in a browser:

(Make sure to replace `YOUR_BOT_CLIENT_ID` with the client ID you get from
Discord's developer portal.

```
https://discordapp.com/api/oauth2/authorize?client_id=YOUR_BOT_CLIENT_ID&scope=bot&permissions=8
```

Also note that this gives the bot admin perms in your server which is probably
overkill. It probably only needs the `Move Users` permission.
