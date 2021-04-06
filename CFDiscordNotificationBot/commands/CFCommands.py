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

CACHE_REFRESH_RATE = 24 * 60 * 60  # seconds

NOTIFICATION_FREQ = [
    (timedelta(days=0, hours=0, minutes=0, seconds=0), "Contest Started!!! GOOD LUCK"),
    timedelta(days=0, hours=0, minutes=5, seconds=0),
    timedelta(days=0, hours=0, minutes=30, seconds=0),
    timedelta(days=1, hours=0, minutes=0, seconds=0)
]

# todo: add command to set per server timezone
LOCAL_TZ = pytz.timezone('Africa/Cairo')


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
    except FileNotFoundError:
        saveChannelsToNotify({})
        return {}


def saveChannelsToNotify(channelsToNotify):
    with open(PATH_FILE_CHANNELS_TO_NOTIFY, "w") as outputFile:
        json.dump(channelsToNotify, outputFile)


def addContestEmbedFields(contestsEmbed, contest):
    startTime = datetime.utcfromtimestamp(contest.startTimeSeconds).replace(
        tzinfo=pytz.utc).astimezone(tz=LOCAL_TZ)
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


def getContestsEmbed(title, contests):
    contestsEmbed = discord.Embed(
        title=title,
        url='https://codeforces.com/contests',
        color=discord.Colour.dark_blue()
    )
    for contest in contests[::-1]:
        addContestEmbedFields(contestsEmbed, contest)
    contestsEmbed.set_thumbnail(url=CF_LOGO)
    return contestsEmbed


def getContestEndNotifcation(contest):
    return (((datetime.fromtimestamp(contest.startTimeSeconds +
                                     contest.durationSeconds)) - datetime.now()).total_seconds(), contest,
            "Contest Ended!! Hope you enjoyed it :D")


class CF(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channelsToNotify = loadChannelsToNotify()

        self.updateCache()
        asyncio.ensure_future(self.scheduleCacheRefresh())

        self.scheduleNotifications()

    def updateCache(self):
        self.contestCacheRaw = CFAPI.getBeforeContests()
        self.contestCacheEmbed = getContestsEmbed("Upcoming Codeforces Rounds",
                                                  self.contestCacheRaw)

    def scheduleNotifications(self):
        notificaitons = {}
        for contest in self.contestCacheRaw:
            contestNotifcations = self.scheduleContestNotification(contest)
            for delay, contest, msg in contestNotifcations:
                if delay in notificaitons:
                    notificaitons[delay].append((contest, msg))
                else:
                    notificaitons[delay] = [(contest, msg)]

        for delay, contests in notificaitons.items():
            asyncio.ensure_future(self.notifyChannels(delay, contests))

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
        output = []
        datetimeNow = datetime.now()
        for notifyObj in NOTIFICATION_FREQ:
            notificationTimedelta, msg = notifyObj if type(
                notifyObj) is tuple else (notifyObj, None)
            notificationTime = datetime.fromtimestamp(
                contest.startTimeSeconds) - notificationTimedelta
            delay = (notificationTime - datetimeNow).total_seconds()
            if delay > 0:
                output.append((delay, contest, msg))

        output.append(getContestEndNotifcation(contest))
        return output

    async def notifyChannels(self, delay, contests):
        await asyncio.sleep(delay)
        embed = getContestsEmbed("Reminder", list(
            map(lambda contest: contest[0], contests)))

        msg = None
        for contest in contests:
            if contest[1]:
                msg = contest[1]
                break

        for channels in self.channelsToNotify.values():
            for channel, role in channels:
                channel = self.bot.get_channel(channel)
                if channel:
                    await channel.send(f"{role}{(' ' + msg) if msg is not None else ''}", embed=embed)

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
