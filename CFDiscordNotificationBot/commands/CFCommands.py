import datetime

import discord
from discord.ext import commands

import CFDiscordNotificationBot.CFAPI


class CF(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="upcoming", description="", brief="", aliases=['upc'])
    async def upcoming(self, ctx):
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

def setup(bot):
    bot.add_cog(CF(bot))
