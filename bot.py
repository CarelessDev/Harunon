import os
import discord
import asyncio
from discord_slash import SlashCommand
from discord.ext import commands, tasks
from dotenv import load_dotenv
from random import choice
from cogs.Legacy.Haru import Haru
from cogs.Legacy.Music import MusicLegacy
from cogs.Slash.Haru import Slash
from cogs.Slash.Kashi import Kashi
from cogs.Slash.Music import MusicSlash
from utils.data import data

if __name__ == "__main__":
    load_dotenv()

    TOKEN = os.getenv("DISCORD_TOKEN")

    bot = commands.Bot(command_prefix="simp")
    slash = SlashCommand(bot, sync_commands=True)

    # * Add Cogs
    bot.add_cog(MusicSlash(bot))
    bot.add_cog(Haru(bot))
    bot.add_cog(Kashi(bot))
    bot.add_cog(Slash(bot))
    bot.add_cog(MusicLegacy(bot))

    @bot.event
    async def on_ready():
        print(f"はるのん Ready! Logged in as {bot.user.name}")
        change_status.start()

    @bot.event
    async def on_voice_state_update(member, before, after):
        if not member.id == bot.user.id:
            return
        elif before.channel is None:
            voice = after.channel.guild.voice_client
            time = 0
            while True:
                await asyncio.sleep(1)
                time = time + 1
                if voice.is_playing() and not voice.is_paused():
                    time = 0
                if time == 5:
                    await voice.disconnect()
                if not voice.is_connected():
                    break

    @tasks.loop(seconds=300)
    async def change_status():
        status: str = choice(data["activities"])
        activity = discord.Activity(
            type=discord.ActivityType.listening, name=status
        )
        await bot.change_presence(activity=activity)

    bot.run(TOKEN)

    # while True:
    #     console = input()
    #     if console == "logout":
    #         bot.logout()
    #     else:
    #         print("Invalid command")
