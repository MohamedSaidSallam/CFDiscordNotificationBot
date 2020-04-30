from datetime import datetime

import discord
from discord.ext import commands

import CFDiscordNotificationBot.CFAPI

CF_LOGO = "https://sta.codeforces.com/s/14049/images/codeforces-telegram-square.png"


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

class CF(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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


def setup(bot):
    bot.add_cog(CF(bot))
