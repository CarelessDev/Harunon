import os
import json
import discord
from discord_slash import SlashCommand
from discord.ext import commands, tasks
from dotenv import load_dotenv
from random import choice
from cogs.Haru import Haru
from cogs.Slashes import Slash
from cogs.Kashi import Kashi
from cogs.Voiceslash import Music

with open("data.json") as f:
    data = json.load(f)


if __name__ == "__main__":
    load_dotenv()

    TOKEN = os.getenv("DISCORD_TOKEN")

    bot = commands.Bot(command_prefix=commands.when_mentioned_or("haru "))
    slash = SlashCommand(bot, sync_commands=True)

    def setup(bot):
        bot.add_cog(Music(bot))
        bot.add_cog(Haru(bot))
        bot.add_cog(Kashi(bot))
        bot.add_cog(Slash(bot))

    setup(bot)

    @bot.event
    async def on_ready():
        print(f"はるのん Ready! Logged in as {bot.user.name}")
        change_status.start()

    @tasks.loop(seconds=300)
    async def change_status():
        status: str = choice(data["activities"])
        activity: discord.Activity = discord.Activity(
            type=discord.ActivityType.listening, name=status)
        await bot.change_presence(activity=activity)

    bot.run(TOKEN)
