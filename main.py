import asyncio
import random
import discord
import yaml
import os

from typing import Optional, List, Tuple

# Conversion from sec to min
MIN = 60

bot = discord.Client()


async def start_a_tour(audio_filepath):
    """Starts a tour!

    Joins an active voice channel, plays the clip, kicks a random user
    and then leaves. Good job!
    """
    # Retrieve a random active voice channel
    voice_channel = await retrieve_active_voice_channel()

    # Join the voice channel
    voice_client: discord.VoiceClient = await voice_channel.connect()

    async def kick_member_and_disconnect():
        # Kick a random member
        while True:
            member_to_kick: Optional[discord.Member] = None

            # Iterate through each of the victims and get their ID and
            # kick percentage. Then, generate a number between 0-100.
            # If that number is less than or equal to their kick
            # percentage * 100, they get kicked.
            #
            # So if kick percentage is 0.2, multiply that by 100 to get 20.
            # Then check if the random number is less than or equal to 20.
            # If so, the user is kicked!
            random.shuffle(targeted_victims)
            for victim_user_id, percentage in targeted_victims:
                # Check that this user is currently in the voice channel
                if voice_channel.guild.get_member(victim_user_id) not in voice_channel.members:
                    continue

                random_int = random.randint(0, 101)

                if random_int <= percentage * 100:
                    member_to_kick = voice_channel.guild.get_member(victim_user_id)
                    print("Found member to kick from victim's list")

            if not member_to_kick:
                # Choose a random member in the voice channel
                print("Choosing a random member to kick...")
                member_to_kick: discord.Member = random.choice(voice_channel.members)

            # Don't try to kick ourselves
            if member_to_kick.id != bot.user.id:
                # We got a member that's not ourselves, continue!
                print("Whoops, nearly kicked ourselves!")
                break

        print("Kicking member '%s'..." % (member_to_kick,))
        await member_to_kick.edit(voice_channel=None)

        # Leave the channel
        print("Leaving voice channel")
        await voice_client.disconnect()

        # Announce that the tour is beginning

        # Send them some cool photos if we have any
        if picture_folder:
            await send_pictures_and_captions(member_to_kick)

            for message in after_picture_messages:
                print("Sending message to", member_to_kick.nick, message)
                await member_to_kick.dm_channel.send(message)

    def after_play(e):
        # We have to hook into asyncio here as voice_client.play
        # runs the Callable it's given without await'ing it
        # Basically this just calls `kick_member_and_disconnect`
        asyncio.run_coroutine_threadsafe(kick_member_and_disconnect(), bot.loop)

    # Play the audio
    # Runs `after_play` when audio has finished playing
    voice_client.play(discord.FFmpegPCMAudio(audio_filepath), after=after_play)


async def dm_file_to_user(filepath: str, user: discord.Member):
    """DMs a file at a given filepath to a user"""
    # Get a discord.File of the given file
    file = discord.File(filepath)

    # Check that we have a DM with this user
    if user.dm_channel is None:
        await user.create_dm()

    # Send the file
    await user.dm_channel.send(file=file)


async def send_pictures_and_captions(to_user: discord.Member):
    """Send some photos from the configured picture folder with captions to the specified user

    This method makes use of the `picture_folder`, `picture_amount` and
    `picture_captions` config options
    """
    print("Sending photos to", to_user.nick)

    # Pick some random photos to send
    picture_filenames = random.sample(os.listdir(picture_folder), picture_amount)
    picture_filepaths = [os.path.join(picture_folder, filename) for filename in picture_filenames]

    picture_caption_choices = []
    if picture_captions:
        picture_caption_choices = random.sample(picture_captions, len(picture_filepaths))

    for message in before_picture_messages:
        print("Sending messages:", before_picture_messages)
        # Check if this is supposed to be a file
        if message.startswith("file:"):
            # Remove the "file:" bit from the filepath
            filepath = message[5:]

            # Send the file
            await dm_file_to_user(filepath, to_user)
        else:
            await to_user.dm_channel.send(message)

    for index, filepath in enumerate(picture_filepaths):
        # Send the image
        print("Sending photo", filepath)
        await dm_file_to_user(filepath, to_user)

        # Optionally, send a random caption
        if picture_captions:
            caption = picture_caption_choices[index]
            print("Sending caption:", caption)
            await to_user.dm_channel.send(caption)

        # Optionally delay between sending each image
        # Don't delay after sending the last image
        if index != len(picture_filepaths) - 1:
            await asyncio.sleep(between_picture_delay)


async def retrieve_active_voice_channel():
    """Scans all active voice channels the bot can see and returns a random one"""
    # Get all channels the bot can see
    channels = [c for c in bot.get_all_channels()]

    # Randomize them so we don't pick the same channel every time
    random.shuffle(channels)

    # Check if each channel is a VoiceChannel with active members
    for channel in channels:
        if isinstance(channel, discord.VoiceChannel):
            if len(channel.members) > 0:
                # We found an active voice channel!
                return channel


# Text command to have bot join channel
@bot.event
async def on_message(message):
    msg = message.content.lower()
    if msg in triggers.keys():
        if message.author.id not in allowed_command_user_ids:
            print("Rejecting non-authorized author id %d" % message.author.id)
            return

        # Wait a random amount of time
        # (for sam to get online)
        sleep_amount = random.randint(trigger_sleep_min, trigger_sleep_max)
        print("Trigger phrase ACTIVATED! Waiting %d seconds..." % (sleep_amount,))
        await asyncio.sleep(sleep_amount)

        # Try to kick a user from a channel
        print("Triggered!")
        await start_a_tour(triggers[msg])


@bot.event
async def on_ready():
    while True:
        # Start the scheduler for a random time
        await asyncio.sleep(random.randint(20 * MIN, 60 * MIN))

        # Try to kick a user from a channel
        await start_a_tour(default_audio_clip)

print("Connected and logged in. Here I come!")

# Read the config file and store it in a python dictionary
with open("config.yaml") as f:
    config = yaml.safe_load(f.read())

# Config options
picture_folder = config.get("picture_folder", "")
picture_amount = config.get("picture_amount", 1)
picture_captions = config.get("picture_captions", [])
before_picture_messages = config.get("before_picture_messages", [])
after_picture_messages = config.get("after_picture_messages", [])
between_picture_delay = config.get("between_picture_delay", 0)

targeted_victims: List[Tuple[int, float]] = config.get("targeted_victims", [])

trigger_phrase = config.get("trigger_phrase", "")
trigger_sleep_min = config.get("trigger_sleep_min", 0)
trigger_sleep_max = config.get("trigger_sleep_max", 0)
allowed_command_user_ids = config["allowed_command_user_ids"]

triggers = config["triggers"]
default_audio_clip = config["default_audio_clip"]

bot.run(config["bot_token"])