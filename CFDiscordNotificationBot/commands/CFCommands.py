import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path

import CFDiscordNotificationBot.CFAPI as CFAPI
import discord
import pytz
from discord.ext import commands
from discord.ext.commands.errors import ConversionError

CF_LOGO = "https://sta.codeforces.com/s/14049/images/codeforces-telegram-square.png"

PATH_FODLER_DATA = 'Data/'
PATH_FILE_CHANNELS_TO_NOTIFY = PATH_FODLER_DATA + "channelsToNotify.json"

CACHE_REFRESH_RATE = 24 * 60 * 60

NOTIFICATION_FREQ = [
    (timedelta(days=0, hours=0, minutes=0, seconds=0), "Contest Started!!! GOOD LUCK"),
    timedelta(days=0, hours=0, minutes=5, seconds=0),
    timedelta(days=0, hours=0, minutes=30, seconds=0),
    timedelta(days=0, hours=3, minutes=0, seconds=0),
    timedelta(days=1, hours=0, minutes=0, seconds=0)
]

LOCAL_TZ = pytz.timezone('Africa/Cairo') # todo: add command to set per server timezone

def getFormattedBeforeStart(beforeStart):
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
            rawJson = json.load(inputFile)
        channelsToNotify = {int(key): value for key, value in rawJson.items()}
        return channelsToNotify
    except FileNotFoundError as e:
        saveChannelsToNotify({})
        return {}


def saveChannelsToNotify(channelsToNotify):
    with open(PATH_FILE_CHANNELS_TO_NOTIFY, "w") as outputFile:
        json.dump(channelsToNotify, outputFile)


def addContestEmbedFields(contestsEmbed, contest):
    startTime = datetime.utcfromtimestamp(contest.startTimeSeconds).replace(tzinfo=pytz.utc).astimezone(tz=LOCAL_TZ)
    beforeStart, beforeStartPostfix = getFormattedBeforeStart(
        max(0,
            (startTime -
             datetime.now().replace(tzinfo=pytz.utc).astimezone(tz=LOCAL_TZ)).total_seconds()
            )
    )
    contestsEmbed.add_field(
        name=f"**{contest.name}**",
        value=f"@_{startTime.strftime('%m-%d %H:%M')}_"
        f", In _{round(beforeStart)}_ {beforeStartPostfix}\n"
        f"Duration: _{contest.durationSeconds / 60 / 60}_ hr(s)\n"
        f"Scoring System: _{contest.type}_\n",
        inline=False)


def getEmbedContestNotification(contest):
    contestEmbed = discord.Embed(
        title=f"Reminder: {contest.name}",
        url=f'https://codeforces.com/contestRegistration/{contest.id}',
        color=discord.Colour.dark_blue()
    )
    addContestEmbedFields(contestEmbed, contest)
    contestEmbed.set_thumbnail(url=CF_LOGO)
    # ! only works if the notification was sent 2 days or less before the contest
    contestEmbed.set_footer(text="Click on the link to register")
    return contestEmbed


def UpcomingContestRawToEmbed(contests):
    contestsEmbed = discord.Embed(
        title="Upcoming Codeforces Rounds",
        url='https://codeforces.com/contests',
        color=discord.Colour.dark_blue()
    )
    for contest in contests[::-1]:
        addContestEmbedFields(contestsEmbed, contest)
    contestsEmbed.set_thumbnail(url=CF_LOGO)
    return contestsEmbed


class CF(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channelsToNotify = loadChannelsToNotify()

        self.updateCache()
        asyncio.ensure_future(self.scheduleCacheRefresh())

        # asyncio.ensure_future(self.notifyChannels(10, self.contestCacheRaw[0], "testing smth"))

        for contest in self.contestCacheRaw:
            self.scheduleContestNotification(contest)

    def updateCache(self):
        self.contestCacheRaw = CFAPI.getBeforeContests()
        self.contestCacheEmbed = UpcomingContestRawToEmbed(
            self.contestCacheRaw)

    async def scheduleCacheRefresh(self):
        while True:
            await asyncio.sleep(CACHE_REFRESH_RATE)
            oldContestNames = [
                contest.name for contest in self.contestCacheRaw]
            self.updateCache()
            for contest in self.contestCacheRaw:
                if contest.name not in oldContestNames:
                    self.scheduleContestNotification(
                        contest)  # ! duplicate notifications ?

    def scheduleContestNotification(self, contest):
        datetimeNow = datetime.now()
        for notifyObj in NOTIFICATION_FREQ:
            notificationTimedelta, msg = notifyObj if type(
                notifyObj) is tuple else (notifyObj, None)
            notificationTime = datetime.fromtimestamp(
                contest.startTimeSeconds) - notificationTimedelta
            delay = (notificationTime - datetimeNow).total_seconds()
            print(contest.name, delay)
            if delay > 0:
                asyncio.ensure_future(self.notifyChannels(
                    delay, contest, msg))

        contestDuration = timedelta(days=contest.durationSeconds // 86399, seconds=contest.durationSeconds % 86399) \
            if contest.durationSeconds > 86399 else timedelta(seconds=contest.durationSeconds)

        delay = ((datetime.fromtimestamp(contest.startTimeSeconds) +
                  contestDuration) - datetimeNow).total_seconds()
        asyncio.ensure_future(self.notifyChannels(delay, contest,
                                                  "Contest Ended!! Hope you enjoyed it :D"))

    async def notifyChannels(self, delay, contest, msg=None):
        await asyncio.sleep(delay)
        embed = getEmbedContestNotification(contest)
        for channels in self.channelsToNotify.values():
            for channel, role in channels:
                await self.bot.get_channel(channel).send(f"{role}{(' ' + msg) if msg is not None else ''}", embed=embed)

    @commands.command(name="upcoming", description="", brief="", aliases=['upc'])
    async def upcoming(self, ctx):
        await ctx.send(embed=self.contestCacheEmbed)

    @commands.command(name="registerChannelForNotifications", description="", brief="", aliases=['rfn'])
    async def registerChannelForNotifications(self, ctx, roleToTag: discord.Role):
        if ctx.guild.id in self.channelsToNotify \
                and ctx.channel.id in [channel[0] for channel in self.channelsToNotify[ctx.guild.id]]:
            await ctx.send("Already registered")
        else:
            self.channelsToNotify.setdefault(
                ctx.guild.id, []).append((ctx.channel.id, roleToTag.mention))
            saveChannelsToNotify(self.channelsToNotify)
            await ctx.send("Registered")

    @commands.command(name="unRegisterChannelForNotifications", description="", brief="", aliases=['urfn'])
    async def unRegisterChannelForNotifications(self, ctx):
        if ctx.guild.id in self.channelsToNotify \
                and ctx.channel.id in [channel[0] for channel in self.channelsToNotify[ctx.guild.id]]:
            self.channelsToNotify[ctx.guild.id] = [
                item for item in self.channelsToNotify[ctx.guild.id] if item[0] != ctx.channel.id]
            saveChannelsToNotify(self.channelsToNotify)
            await ctx.send("Unregistered")
        else:
            await ctx.send("Channel wasn't Registered")


def setup(bot):
    bot.add_cog(CF(bot))
