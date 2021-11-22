import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashCommandOptionType as SOT
from discord_slash.context import SlashContext

from subprocess import check_output


class PiHelper:
    @staticmethod
    def _get_cpu_temp():
        try:
            # * Check Raspberry Pi Temperature
            temp = check_output(["vcgencmd", "measure_temp"]).decode("utf-8")
            temp = temp.split("=")[1].split("'")[0]  # * By GitHub Copilot ✨✨
            return float(temp)
        except:
            return -274  # * Not on Raspberry Pi

    @staticmethod
    def _get_ram_usage():
        try:
            ram = check_output(["free", "-m"]).decode("utf-8")
            ramUsed = ram.split("\n")[1].split()[2]
            ramCap = ram.split("\n")[1].split()[1]
            return [int(ramUsed), int(ramCap)]
        except:
            return [-1, -1]  # * Not on Linux

    @staticmethod
    def get_status():
        temp = PiHelper._get_cpu_temp()
        ram = PiHelper._get_ram_usage()

        return {
            "system": "Raspberry Pi" if temp > -274 else "Linux" if ram[0] > 0 else "Windows",
            "temp": temp,
            "ram": {
                "usage": ram[0],
                "max": ram[1],
            },
            "available": {
                "temp": temp > -274,
                "ram": ram[0] > 0,
            }
        }


class RaspberryPi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="haruno", description="Asking Haruno if she is fine")
    async def _haruno(self, ctx: SlashContext):
        status = PiHelper.get_status()

        embed = (
            discord.Embed(
                title="Harunon Bot Status",
                description=f"Running on: {status['system']}",
            )
            .set_author(
                name=self.bot.user.name, icon_url=self.bot.user.avatar_url
            )
            .set_footer(
                text="Bot made by CarelessDev/oneesan-lover ❤️❤️❤️"
            )
        )

        if status["available"]["temp"]:
            embed = embed.add_field(
                name="CPU Temperature", value=f"{status['temp']}°C")
        if status["available"]["ram"]:
            embed = embed.add_field(
                name="RAM Usage", value=f"{status['ram']['usage']}MB / {status['ram']['max']}MB")

        # * GitHub Copilot Superior

        await ctx.send("Yahallo!", embed=embed)
