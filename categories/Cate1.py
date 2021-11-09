from discord.ext import commands
import discord




class Social_credit(commands.Cog):
    """Social Credibility"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send('An error occurred: {}'.format(str(error)))
    

    @commands.command(name='credit', aliases=['c'])
    async def social_credit(self, ctx):
        """commie"""
        file_name = "./Lyr.txt"
        with open(file_name, 'rb') as f:
            for x in f:
                await ctx.send(x)


    