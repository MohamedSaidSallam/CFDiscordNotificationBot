import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import CFDiscordNotificationBot.CFAPI
import datetime

load_dotenv()
SECRET_KEY = os.getenv("DISCORD_TOKEN")

client = commands.Bot(command_prefix=';')


@client.event
async def on_ready():
    print('Bot is ready')


@client.command()
async def hi(ctx):
    await ctx.send("Hello World")


@client.command()
async def upcoming(ctx):
    contestsData = discord.Embed(
        title="Upcoming Codeforces Rounds",
        color=discord.Colour.dark_blue()
    )
    contests = CFDiscordNotificationBot.CFAPI.getBeforeContests()
    data = ''
    for contest in contests[::-1]:
        data += (f"**{contest.name}**"
                 f"\n\u200bStart Time: "
                 f"{datetime.datetime.fromtimestamp(contest.startTimeSeconds).strftime('%Y-%m-%d %H:%M:%S')}"
                 f"\n\u200bDuration Time: {contest.durationSeconds / 60 / 60} hours\n\n")
    contestsData.add_field(name='\u200b', value=data)
    await ctx.send(embed=contestsData)


client.run(SECRET_KEY)
