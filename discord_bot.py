import discord
from discord.ext import commands

# Define your bot prefix (e.g., !)
bot = commands.Bot(command_prefix="!")

# Event when the bot has successfully connected
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Command to send a message to a specific user
@bot.command()
async def send(ctx, user: discord.User, *, message: str):
    """Send a message to a specific user"""
    try:
        await user.send(message)
        await ctx.send(f"Message sent to {user.name}")
    except discord.DiscordException as e:
        await ctx.send(f"Failed to send message: {e}")

# Start the bot using your bot's token
bot.run('discord_bot_token')
