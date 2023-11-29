import discord
from datetime import datetime
from discord.ext import commands


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

submitted_photos = []
reaction_tracking = {}
specific_emoji = '👍'

last_reset_time = None

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.event
async def on_message(message):
    global submitted_photos, reaction_tracking
    if message.author == bot.user:
        return

    if message.content.startswith('$officer'):
        await message.channel.send('I am the law')

    if message.content.startswith('$reset'):
        submitted_photos = []
        await message.channel.send("Judgement starts now")
        await message.channel.send("Submissions Cleared")
        reaction_tracking.clear()
        await message.channel.send('Reaction tracking reset.')

    # this is where the vote command is going to be in the code
    if message.content.startswith("$vote"):
        response = "Reaction Counts:\n"
        most = 0
        print(reaction_tracking.items())
        for message_id, votes in reaction_tracking.items():
            response += f"Photo URL {message_id}: {votes} {specific_emoji} reactions \n"
            if votes > most:
                most = votes
        for message_id, votes in reaction_tracking.items():
            if votes == most:
                await message.channel.send(message_id)

    if not message.author.bot:
        if message.attachments:
            first_image = message.attachments[0]
            await message.add_reaction('👍')
            submitted_photos.append(first_image.url)
            reaction_tracking[first_image.url] = 0
            await message.channel.send("Image Detected")
    await bot.process_commands(message)


@bot.event
async def on_reaction_add(reaction, user):
    if not user.bot:  # add counting here later which is going to be something that I need to figure out right now
        message = reaction.message.attachments[0]
        message_id = message.url

        if message_id in reaction_tracking and str(reaction.emoji) == specific_emoji:
            reaction_tracking[message_id] += 1
            print("Poggers")

# Run the bot
bot.run("MTE2NDMyMTQzOTU2NzA3MzQ0MQ.GbejaB.wm_T_QZFPzDdX3rf0AU7pKf3ZqHSvo-2or9q94")
