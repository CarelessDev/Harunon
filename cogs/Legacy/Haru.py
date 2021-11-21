from discord.ext import commands
from datetime import datetime


class Haru(commands.Cog):
    """陽乃ベストお姉さん"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send("An error occurred: {}".format(str(error)))

    @commands.command(name="ping")
    async def _ping(self, ctx: commands.Context):
        """Ping Pong 遊ぼう!"""
        interval = datetime.utcnow() - ctx.message.created_at
        await ctx.send(
            f"Pong! Ping = {interval.total_seconds() * 1000} ms"
        )
