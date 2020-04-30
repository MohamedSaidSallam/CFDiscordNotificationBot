import asyncio
import json
from datetime import datetime
from pathlib import Path

import discord
from discord.ext import commands

import CFDiscordNotificationBot.CFAPI

CF_LOGO = "https://sta.codeforces.com/s/14049/images/codeforces-telegram-square.png"

PATH_FODLER_DATA = 'Data/'
PATH_FILE_CHANNELS_TO_NOTIFY =PATH_FODLER_DATA + "channelsToNotify.json"

def getFormattedBeforeStart(relativeTimeSeconds):
    beforeStart = -1 * relativeTimeSeconds
    beforeStartPostfix = "sec(s)"
    if beforeStart > 60:
        beforeStartPostfix = "min(s)"
        beforeStart /= 60
        if beforeStart > 60:
            beforeStartPostfix = "hr(s)"
            beforeStart /= 60
            if beforeStart > 24:
                beforeStartPostfix = "day(s)"
                beforeStart /= 24
    return beforeStart, beforeStartPostfix

def loadChannelsToNotify():
    Path("Data").mkdir(parents=True, exist_ok=True)
    try:
        with open(PATH_FILE_CHANNELS_TO_NOTIFY, "r") as inputFile:
            channelsToNotify = json.load(inputFile)
        return channelsToNotify
    except FileNotFoundError as e:
        saveChannelsToNotify({})
        return {}

def saveChannelsToNotify(channelsToNotify):
    with open(PATH_FILE_CHANNELS_TO_NOTIFY, "w") as outputFile:
        json.dump(channelsToNotify, outputFile)

class CF(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channelsToNotify = loadChannelsToNotify()

    @commands.command(name="upcoming", description="", brief="", aliases=['upc'])
    async def upcoming(self, ctx):
        contestsData = discord.Embed(
            title="Upcoming Codeforces Rounds",
            url='https://codeforces.com/contests',
            color=discord.Colour.dark_blue()
        )
        contests = CFDiscordNotificationBot.CFAPI.getBeforeContests()
        for contest in contests[::-1]:
            beforeStart, beforeStartPostfix = getFormattedBeforeStart(
                contest.relativeTimeSeconds)
            contestsData.add_field(
                name=f"**{contest.name}**",
                value=f"@_{datetime.fromtimestamp(contest.startTimeSeconds).strftime('%m-%d %H:%M')}_"
                f", In _{int(beforeStart)}_ {beforeStartPostfix}\n"
                f"Duration: _{contest.durationSeconds / 60 / 60}_ hr(s)\n"
                f"Scoring System: _{contest.type}_\n",
                inline=False)
        contestsData.set_thumbnail(url=CF_LOGO)
        await ctx.send(embed=contestsData)

    @commands.command(name="registerChannelForNotifications", description="", brief="", aliases=['rfn'])
    async def registerChannelForNotifications(self, ctx, roleToTag: discord.Role):
        self.channelsToNotify.setdefault(
            ctx.guild.id, []).append((ctx.channel.id, roleToTag.mention))
        saveChannelsToNotify(self.channelsToNotify)
        await ctx.send("Registered")


def setup(bot):
    bot.add_cog(CF(bot))
