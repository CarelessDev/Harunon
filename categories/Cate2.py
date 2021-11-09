from discord.ext import commands

class on_hold(commands.Cog):
    """cumming soon"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send('An error occurred: {}'.format(str(error)))
    

    @commands.command(name='none')
    async def on_hold(self, ctx):
        """ introduction"""
        file_name = "./Lyr.txt"
        with open(file_name, 'rb') as f:
            for x in f:
                await ctx.send(x)