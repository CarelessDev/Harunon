import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.context import SlashContext
from typing import List
import constants.Haruno as Haruno
from utils.env import guild_ids
from datetime import datetime

from subprocess import check_output


class PiHelper:
    @staticmethod
    def _get_cpu_temp() -> float:
        try:
            # * Check Raspberry Pi Temperature
            temp = check_output(["vcgencmd", "measure_temp"]).decode("utf-8")
            temp = temp.split("=")[1].split("'")[0]  # * By GitHub Copilot ✨✨
            return float(temp)
        except:
            return -274  # * Not on Raspberry Pi

    @staticmethod
    def _get_ram_usage() -> List[int]:
        try:
            ram = check_output(["free", "-m"]).decode("utf-8")
            ramUsed = ram.split("\n")[1].split()[2]
            ramCap = ram.split("\n")[1].split()[1]
            return [int(ramUsed), int(ramCap)]
        except:
            return [-1, -1]  # * Not on Linux

    @staticmethod
    def _get_linux_uptime() -> str:
        # * Partially By GitHub Copilot
        try:
            uptime = check_output(["uptime"]).decode("utf-8")
            splitcomma = uptime.split(",")
            uptime = splitcomma[0].split("up")[1].strip()
            if "days" in uptime:
                uptime += " " + splitcomma[1].strip()
            return uptime
        except:
            return None

    @staticmethod
    def _get_process_uptime() -> str:
        interval = datetime.utcnow() - Haruno.START_TIME

        # * Format time
        days = interval.days
        hours = interval.seconds // 3600
        minutes = (interval.seconds // 60) % 60
        seconds = interval.seconds % 60

        # * Return Formatted Time
        return f"{days}d {hours}h {minutes}m {seconds}s"

        # * By GitHub Copilot again ✨✨

    @staticmethod
    def get_status():
        temp = PiHelper._get_cpu_temp()
        ram = PiHelper._get_ram_usage()
        linuxup = PiHelper._get_linux_uptime()
        processup = PiHelper._get_process_uptime()

        return {
            "system": "Raspberry Pi" if temp > -274 else "Linux" if ram[0] > 0 else "Windows",
            "temp": temp,
            "ram": {
                "usage": ram[0],
                "max": ram[1],
            },
            "linuxup": linuxup,
            "procup": processup,
            "available": {
                "temp": temp > -274,
                "ram": ram[0] > 0,
                "linuxup": linuxup is not None,
                "processup": True,
            },
        }


class RaspberryPi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="status",
        description="Asking Haruno if she is fine",
        guild_ids=guild_ids
    )
    async def _haruno(self, ctx: SlashContext):
        interval = (datetime.utcnow() - ctx.created_at).total_seconds() * 1000

        status = PiHelper.get_status()

        embed = (
            discord.Embed(
                title="Harunon Bot Status",
                description=f"```Running on: {status['system']}```",
                color=Haruno.COLOR,
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
                name="RAM Usage", value=f"{status['ram']['usage']}MB / {status['ram']['max']}MB"
            )

        embed = embed.add_field(name="Ping", value=f"{interval} ms")

        if status["available"]["linuxup"]:
            embed = embed.add_field(
                name="Linux Uptime", value=f"{status['linuxup']}"
            )

        embed = embed.add_field(
            name="Harunon Uptime", value=f"{status['procup']}"
        )

        # * GitHub Copilot Superior

        await ctx.send("Yahallo!", embed=embed)
