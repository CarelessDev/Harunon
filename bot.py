import os, json
import discord
from discord_slash import SlashCommand
from discord.ext import commands, tasks
from dotenv import load_dotenv
from random import choice
from categories.Cate1 import Social_credit
from categories.Slashes import Slash
from categories.Cate2 import on_hold


with open("words.json") as f:
    data = json.load(f)


if __name__ == "__main__":
    load_dotenv()

    TOKEN = os.getenv('DISCORD_TOKEN')

    bot = commands.Bot(command_prefix=commands.when_mentioned_or('Jek '))
    slash = SlashCommand(bot, sync_commands = True)


    def setup(bot):
        bot.add_cog(Social_credit(bot))
        bot.add_cog(on_hold(bot))
        bot.add_cog(Slash(bot))


    
    setup(bot)


    @bot.event
    async def on_ready():
        print('join us')
        change_status.start()


    @tasks.loop(seconds=300)
    async def change_status():
        status: str = choice(data["activities"])
        activity: discord.Activity = discord.Activity(
            type=discord.ActivityType.listening, name=status)
        await bot.change_presence(activity=activity)


    bot.run(TOKEN)
