import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("DISCORD_TOKEN")

client = commands.Bot(command_prefix=';')


@client.event
async def on_ready():
    print('Bot is ready')


@client.command()
async def hi(ctx):
    await ctx.send("Hello World")


def runBot():
    client.load_extension('CFDiscordNotificationBot.commands.CFCommands')
    client.run(SECRET_KEY)
