from discord.ext import commands
import discord


class Haru(commands.Cog):
    """陽乃ベストお姉さん"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send("An error occurred: {}".format(str(error)))
