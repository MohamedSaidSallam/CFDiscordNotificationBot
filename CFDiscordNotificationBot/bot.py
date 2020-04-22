import discord
from discord.ext import commands

client = commands.Bot(command_prefix=';')


@client.event
async def on_ready():
    print('Bot is ready')


@client.commands()
async def hi(ctx):
    await ctx.send("Hello World")

client.run('NzAyNTg5NDI2NDg3OTE4NzMz.XqCPlg.OdmiF1dLjmRoY2cWlNWylQ3SseE')