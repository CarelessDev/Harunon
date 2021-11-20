from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option
import discord
from discord.ext import commands
import youtube_dl
import asyncio
import functools
import asyncio
import math
from utils.env import guild_ids


# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''


class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass


class YTDLSource1(discord.PCMVolumeTransformer):
    ytdl_format_options = {
        "format": "bestaudio/best",
        "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
        "restrictfilenames": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "auto",
        # bind to ipv4 since ipv6 addresses cause issues sometimes
        "source_address": "0.0.0.0"
    }

    ffmpeg_options = {
        "options": "-vn"
    }

    ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: cls.ytdl.extract_info(url, download=not stream))

        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]

        filename = data["url"] if stream else cls.ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **cls.ffmpeg_options), data=data)


class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        "format": "bestaudio/best",
        "extractaudio": True,
        "audioformat": "mp3",
        "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
        "restrictfilenames": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch",
        "source_address": "0.0.0.0",
    }

    FFMPEG_OPTIONS = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn",
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)
        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data
        self.uploader = data.get("uploader")
        self.uploader_url = data.get("uploader_url")
        date = data.get("upload_date")
        self.upload_date = date[6:8] + "." + date[4:6] + "." + date[0:4]
        self.title = data.get("title")
        self.thumbnail = data.get("thumbnail")
        self.description = data.get("description")
        self.duration = self.parse_duration(int(data.get("duration")))
        self.tags = data.get("tags")
        self.url = data.get("webpage_url")
        self.views = data.get("view_count")
        self.likes = data.get("like_count")
        self.dislikes = data.get("dislike_count")
        self.stream_url = data.get("url")

    def __str__(self):
        return "**{0.title}** by **{0.uploader}**".format(self)

    @classmethod
    async def create_source(cls, ctx: SlashContext, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        # search algorithm
        partial = functools.partial(
            cls.ytdl.extract_info, search, download=False, process=False)

        data = await loop.run_in_executor(None, partial)
        #

        if data is None:
            raise YTDLError(
                "Couldn\"t find anything that matches `{}`".format(search))

        if "entries" not in data:
            process_info = data
        else:
            process_info = None
            for entry in data["entries"]:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError(
                    "Couldn't find anything that matches `{}`".format(search))

        webpage_url = process_info["webpage_url"]
        partial = functools.partial(
            cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError("Couldn't fetch `{}`".format(webpage_url))

        if "entries" not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info["entries"].pop(0)
                except IndexError:
                    raise YTDLError(
                        "Couldn't retrieve any matches for `{}`".format(webpage_url))

        return cls(ctx, discord.FFmpegPCMAudio(info["url"], **cls.FFMPEG_OPTIONS), data=info)

    @staticmethod
    def parse_duration(duration: int):
        if duration > 0:
            minutes, seconds = divmod(duration, 60)
            value = "{}:{}{}".format(
                minutes, '0' if seconds < 10 else '', seconds)

        elif duration == 0:
            value = "LIVE"

        return value


class Song:
    __slots__ = ("source", "requester")

    def __init__(self, source):
        self.source = source
        self.requester = source.requester

    def create_embed(self, words="Now playing"):
        embed = (discord.Embed(title=words, description="```css\n{0.source.title}\n```".format(self), color=0x5a3844)
                 .add_field(name="Duration", value=self.source.duration)
                 .add_field(name="Requested by", value=self.requester.mention)
                 .add_field(name="Uploader", value="[{0.source.uploader}]({0.source.uploader_url})".format(self))
                 .add_field(name="Watched by", value="{0.source.views}".format(self))
                 .add_field(name="Liked by", value="{0.source.likes}".format(self))
                 .add_field(name="URL", value="[Click]({0.source.url})".format(self))
                 .set_thumbnail(url=self.source.thumbnail)
                 .set_author(name=self.requester.name, icon_url=self.requester.avatar_url))
        return embed


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queues = {}
        self.loop = False
        self.ctx = None
        self.server_id = None
        self.current_song = None

    async def play_nexts_song(self, ctx):
        player = ctx.voice_client
        if self.queues[self.server_id] != []:
            self.current_song = self.queues[self.server_id].pop(0)
            if self.loop:
                source = await YTDLSource.create_source(ctx, self.current_song.url)
                self.queues[self.server_id].append(source)
            #print([x.title for x in self.queues[self.server_id]])
            player.play(self.current_song, after=lambda x=None: asyncio.run(
                self.play_nexts_song(ctx)))
        else:
            self.current_song = None

    @cog_ext.cog_slash(name="join", description="Join Voice Chat", guild_ids=guild_ids)
    async def _join(self, ctx: SlashContext):
        channel = ctx.author.voice.channel
        await ctx.send("お姉さんが入った!")
        await channel.connect()

    @cog_ext.cog_slash(name="leave", description="Leave Voice Chat", guild_ids=guild_ids)
    async def _leave(self, ctx: SlashContext):
        await ctx.voice_client.disconnect()
        await ctx.send("じゃ またねええ!")

    @cog_ext.cog_slash(name="skip", description="Skip a Song", guild_ids=guild_ids)
    async def _skip(self, ctx: SlashContext):
        if not ctx.voice_client.is_playing:
            return await ctx.send("Not playing any music right now...")
        # self.queues[ctx.voice_client.server_id].pop(0)
        ctx.voice_client.stop()
        await ctx.send("⏭ スキップ成功!")

    @cog_ext.cog_slash(name="pause", description="Pause the Song", guild_ids=guild_ids)
    async def _pause(self, ctx: SlashContext):
        if not ctx.voice_client.is_playing:
            return await ctx.send("Not playing any music right now...")
        if ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            ctx.voice_client.pause()
            await ctx.send("⏯ Paused")

    @cog_ext.cog_slash(name="resume", description="Resume the Song", guild_ids=guild_ids)
    async def _resume(self, ctx: SlashContext):
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("⏯ Resumed")

    @cog_ext.cog_slash(name="queue", description="Show the Queue", guild_ids=guild_ids)
    async def _queue(self, ctx: SlashContext):
        if not self.queues[self.server_id]:
            return await ctx.send("残念ですから Queue is current empty.")
        page = 1
        items_per_page = 10
        pages = math.ceil(len(self.queues[self.server_id]) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ""
        for i, song in enumerate(self.queues[self.server_id][start:end], start=start):
            queue += "`{0}.` [**{1.title}**]({1.url}){2}\n".format(
                i + 1, song,
                " <<< Now Playing" if i == 0 else ""
            )

        embed = (
            discord.Embed(
                description="**{} song in queues:**\n\n{}".format(
                    len(self.queues[self.server_id]), queue)
            )
            .set_footer(text="Viewing page {}/{}".format(page, pages)))
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="loop", description="Loop!", guild_ids=guild_ids)
    async def _loop_queue(self, ctx: SlashContext):
        if self.loop == False:
            self.loop = True
            await ctx.send("ループしま～す!")
        else:
            self.loop = False
            await ctx.send("ループしません")

    @cog_ext.cog_slash(
        name="play", description="Play some Music", guild_ids=guild_ids,
        options=[
            create_option(
                name="song",
                description="Song Name",
                required=True,
                option_type=3
            )
        ]
    )
    async def _play(self, ctx: SlashContext, *, song: str):
        if not ctx.voice_client:
            channel = ctx.author.voice.channel
            await channel.connect()

        self.ctx = ctx
        self.server_id = ctx.voice_client.server_id
        await ctx.defer()
        source = await YTDLSource.create_source(ctx, song, loop=self.bot.loop)
        if self.server_id in self.queues:
            self.queues[self.server_id].append(source)
        else:
            self.queues[self.server_id] = [source]
        if not ctx.voice_client.is_playing():
            ctx.voice_client.play(self.queues[self.server_id][0], after=lambda e: asyncio.run(
                self.play_nexts_song(ctx)))
        song = Song(source)
        await ctx.send(embed=song.create_embed("enqueued"))

    @cog_ext.cog_slash(
        name="remove", description="Remove Song from Queue", guild_ids=guild_ids,
        options=[
            create_option(
                name="index",
                description="Song Index to remove",
                required=True,
                option_type=10
            )
        ]
    )
    async def _remove(self, ctx: SlashContext, index: int):
        if self.queues[self.server_id] != []:
            index = min(max(index, -1), len(self.queues[self.server_id]))

            if not self.loop:
                ctx.voice_client.stop()
            await ctx.send("Removed {1} [**{0.title}**](<{0.url}>) 成功! ✅".format(self.queues[self.server_id].pop(index - 1), index))
        else:
            return await ctx.send("Queue is already empty!")

    @cog_ext.cog_slash(name="now", description="Show Current Song", guild_ids=guild_ids)
    async def _now(self, ctx: commands.Context):
        await ctx.send(embed=Song(ctx.voice_client.source).create_embed())

    @cog_ext.cog_slash(name="clear", description="Clear the Queue", guild_ids=guild_ids)
    async def _now(self, ctx: commands.Context):
        self.queues[self.server_id] = []
        await ctx.send("Queue cleared! 成功! ✅")