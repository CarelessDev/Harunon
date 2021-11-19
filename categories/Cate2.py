from discord.ext import commands


class on_hold(commands.Cog):
    """cumming soon"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send("An error occurred: {}".format(str(error)))

    @commands.command(name="harumodoki")
    async def on_hold(self, ctx):
        """探しに行くんだ そこへ"""
        file_name = "./歌詞/春擬き.txt"
        with open(file_name, "r") as f:
            for x in f:
                await ctx.send(x)
