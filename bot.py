import os
import discord
import asyncio
from discord_slash import SlashCommand, SlashContext
from discord.ext import commands, tasks
from dotenv import load_dotenv
from random import choice
from cogs.Legacy.Haru import Haru
from cogs.Legacy.Music import MusicLegacy
from cogs.Slash.Haru import HaruSlash
from cogs.Slash.Kashi import Kashi
from cogs.Slash.Music import MusicSlash
from cogs.Slash.RaspberryPi import RaspberryPi
from utils.data import data

if __name__ == "__main__":
    load_dotenv()

    TOKEN = os.getenv("DISCORD_TOKEN")

    bot = commands.Bot(command_prefix="simp")
    slash = SlashCommand(bot, sync_commands=True)

    # * Add Cogs (Legacy)
    bot.add_cog(Haru(bot))
    bot.add_cog(MusicLegacy(bot))

    # * Slash Cogs
    bot.add_cog(HaruSlash(bot))
    bot.add_cog(Kashi(bot))
    bot.add_cog(MusicSlash(bot))
    bot.add_cog(RaspberryPi(bot))

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

    @bot.event
    async def on_slash_command_error(ctx:SlashContext, ex):
        print('An error occurred: {}'.format(str(ex)))

        

    @tasks.loop(seconds=300)
    async def change_status():
        status: str = choice(data["activities"])
        activity = discord.Activity(
            type=discord.ActivityType.listening, name=status
        )
        await bot.change_presence(activity=activity)

    bot.run(TOKEN)
