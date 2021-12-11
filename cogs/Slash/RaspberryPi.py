import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashCommandOptionType as SOT
from discord_slash.context import SlashContext
from typing import List

import constants.Haruno as Haruno
from utils.slash import SlashUtils
from utils.env import guild_ids
from datetime import datetime

from subprocess import check_output


def get_version() -> str:
    try:
        # * GitHub Copilot amazed me again ✨✨
        chash = check_output(
            ["git", "rev-parse", "HEAD"]).decode("utf-8")[:7]
        ccount = int(check_output(
            ["git", "rev-list", "--count", "HEAD"]).decode("utf-8").strip())
        cbranch = check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode("utf-8").strip()

        # * Get Last Commit Time
        ctime = check_output(
            ["git", "log", "-1", "--format=%cd"]).decode("utf-8").strip()

        return f"Version: {ccount} ({cbranch} @ {chash})\n{ctime}"
    except:
        return "Version: UNKNOWN"


VERSION: str = get_version()


class PiHelper:
    has_done_pull_action = False

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
    def _check_for_updates() -> bool:
        # * git: Check if there is something to pull
        try:
            if len(check_output(["git", "pull"]).decode("utf-8")) > 25:
                PiHelper.has_done_pull_action = True
        except:
            pass

        return PiHelper.has_done_pull_action

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
            "version": VERSION,
            "available": {
                "temp": temp > -274,
                "ram": ram[0] > 0,
                "linuxup": linuxup is not None,
                "processup": True,
            },
            "need_update": PiHelper._check_for_updates(),
        }


class RaspberryPi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    NEED_UPDATE = "✨✨ New Version of Bot is Available! ✨✨"

    @cog_ext.cog_slash(
        name="status",
        description="Asking Haruno if she is fine",
        guild_ids=guild_ids,
        options=[SlashUtils.ephemeral()]
    )
    async def _haruno(self, ctx: SlashContext, ephemeral: bool = False):
        interval = (datetime.utcnow() - ctx.created_at).total_seconds() * 1000

        status = PiHelper.get_status()

        need_update = (
            "\n" + RaspberryPi.NEED_UPDATE) if status["need_update"] else ""

        embed = (
            discord.Embed(
                title="Harunon Bot Status",
                description=f"```Running on: {status['system']}\n{status['version']}{need_update}```",
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
                name="CPU Temperature", value=f"{status['temp']} °C")
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

        await ctx.send("Yahallo!", embed=embed, hidden=ephemeral)
