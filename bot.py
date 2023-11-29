
import discord
from discord.ext import commands, tasks
import os

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Replace these with your channel IDs
submission_channel_id = int(os.getenv('SUBMISSION_CHANNEL_ID'))
voting_channel_id = int(os.getenv('VOTING_CHANNEL_ID'))

# Global variable to track whether voting has ended
voting_ended = False

# Function to count votes
async def count_votes():
    global voting_ended
    if voting_ended:
        return

    voting_channel = bot.get_channel(voting_channel_id)
    winner = None
    max_votes = 0

    # Assuming the last message is the starting point for counting votes
    async for message in voting_channel.history(limit=100):
        if message.author == bot.user and message.attachments:
            votes = sum(reaction.count for reaction in message.reactions if reaction.emoji in ['👍', '👎'])

            if votes > max_votes:
                max_votes = votes
                winner = message

    if winner:
        await voting_channel.send(f"The winning submission is {winner.attachments[0].url} with {max_votes} votes!")
    else:
        await voting_channel.send("No submissions or votes this time.")

    voting_ended = True

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    automatic_vote_counting.start()  # Start the vote counting task

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id == submission_channel_id and message.attachments:
        voting_channel = bot.get_channel(voting_channel_id)

        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif']):
                sent_message = await voting_channel.send(attachment.url)
                await sent_message.add_reaction('👍')
                await sent_message.add_reaction('👎')

        # Delete the original message from the submission channel
        await message.delete()

@bot.command()
@commands.has_permissions(administrator=True)  # Ensure only admins can use this command
async def end_voting(ctx):
    await count_votes()
    await ctx.send("Voting has ended and the winner has been announced.")

@tasks.loop(hours=24)  # Set this to the desired interval
async def automatic_vote_counting():
    await count_votes()

# Run the bot with the token from an environment variable
bot_token = os.getenv('DISCORD_BOT_TOKEN')
bot.run(bot_token)
