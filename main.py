import asyncio
import random
import discord
import yaml

# Conversion from sec to min
MIN = 60

bot = discord.Client()


async def start_a_tour():
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
            member_to_kick: discord.Member = random.choice(voice_channel.members)

            # Don't try to kick ourselves
            if member_to_kick.id != bot.user.id:
                break

        print("Trying to kick member '%s'" % (member_to_kick,))
        await member_to_kick.edit(voice_channel=None)
        print("Kicked member")

        # Leave the channel
        await voice_client.disconnect()

    def after_play(e):
        # We have to hook into asyncio here as voice_client.play
        # runs the Callable it's given without await'ing it
        # Basically this just calls `kick_member_and_disconnect`
        asyncio.run_coroutine_threadsafe(kick_member_and_disconnect(), bot.loop)

    # Play the audio
    # Runs `after_play` when audio has finished playing
    voice_client.play(discord.FFmpegPCMAudio(audio_clip_filepath), after=after_play)


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
    if trigger_phrase and message.content.lower() == trigger_phrase.lower():
        if message.author.id not in allowed_command_user_ids:
            print("Rejecting non-authorized author id %d" % message.author.id)
            return

        # Wait a random amount of time
        # (for sam to get online)
        sleep_amount = random.randint(20, 60)
        print("Trigger phrase ACTIVATED! Waiting %d seconds..." % (sleep_amount,))
        await asyncio.sleep(sleep_amount)

        # Try to kick a user from a channel
        print("Triggered!")
        await start_a_tour()


@bot.event
async def on_ready():
    while True:
        # Start the scheduler for a random time
        await asyncio.sleep(random.randint(5 * MIN, 60 * MIN))

        # Try to kick a user from a channel
        await start_a_tour()

print("Connected and logged in. Here I come!")

with open("config.yaml") as f:
    config = yaml.safe_load(f.read())

trigger_phrase = config.get("trigger_phrase", "")
allowed_command_user_ids = config["allowed_command_user_ids"]
audio_clip_filepath = config["audio_clip_filepath"]
bot.run(config["bot_token"])