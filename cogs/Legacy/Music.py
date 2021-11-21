import discord
from discord.ext import commands
import youtube_dl
import asyncio
import functools
import asyncio
import math
import constants.Haruno as Haruno

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
    async def create_source(cls, ctx, search: str, *, loop: asyncio.BaseEventLoop = None):
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


Song_queue = {}


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


class MusicLegacy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.loop = False

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send('An error occurred: {}'.format(str(error)))

    async def play_nexts_song(self, ctx):
        global Song_queue
        player = ctx.voice_client
        server_id = ctx.voice_client.server_id if ctx else None
        if Song_queue[server_id] != [] and server_id:
            current_song = Song_queue[server_id].pop(0)
            if self.loop[server_id]:
                source = await YTDLSource.create_source(ctx, current_song.url)
                Song_queue[server_id].append(source)
            #print([x.title for x in Song_queue[server_id]])
            player.play(current_song, after=lambda x=None: asyncio.run(
                self.play_nexts_song(ctx)))
        else:
            return

    @commands.command(name='join', aliases=['j'])
    async def _join(self, ctx: commands.context, *, channel: discord.VoiceChannel = None):
        """Join user VC"""
        if not channel and not ctx.author.voice:
            raise VoiceError(
                'You are neither connected to a voice channel nor specified a channel to join.')

        destination = channel or ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(destination)
            return
        else:
            await destination.connect()
            await ctx.send("お姉さんが入った!")

    @commands.command(name="leave", aliases=['le'])
    async def _leave(self, ctx: commands.context):
        """leave vc"""
        await ctx.voice_client.disconnect()
        await ctx.send("じゃ またねええ!")

    @commands.command(name="skip", aliases=['s'])
    async def _skip(self, ctx: commands.context):
        """skip current song"""
        if not ctx.voice_client.is_playing:
            return await ctx.send("Not playing any music right now...")
        # Song_queue[ctx.voice_client.server_id].pop(0)
        ctx.voice_client.stop()
        msg = await ctx.send("スキップ成功!")
        await msg.add_reaction("⏭")

    @commands.command(name="pause", aliases=['pa'])
    async def _pause(self, ctx: commands.context):
        """pause current song"""
        if not ctx.voice_client.is_playing:
            return await ctx.send("Not playing any music right now...")
        if ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            ctx.voice_client.pause()
            await ctx.message.add_reaction("⏯")

    @commands.command(name="resume", aliases=['r'])
    async def _resume(self, ctx: commands.context):
        """resume"""
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.message.add_reaction("⏯")

    @commands.command(name="queue", aliases=['q'])
    async def _queue(self, ctx: commands.context, page:int = 1):
        """Display list of songs"""
        global Song_queue

        server_id = ctx.message.guild.id
        if not Song_queue[server_id] and not ctx.voice_client.is_playing():
            return await ctx.send("残念ですから Queue is current empty.")
        page = page
        items_per_page = 10
        pages = math.ceil(len(Song_queue[server_id]) + 1 / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ""
        for i, song in enumerate([ctx.voice_client.source] + Song_queue[server_id][start:end], start=start):
            queue += "`{0}.` [**{1.title}**]({1.url}){2}\n".format(
                i + 1, song,
                " <<< Now Playing" if i == 0 else ""
            )

        embed = (
                discord.Embed(
                    description=f"**{len(Song_queue[server_id]) + 1} Songs in Queue:**\n\n{queue}", color=Haruno.COLOR
                )
                .set_footer(text=f"Viewing page {page}/{pages}"))

        await ctx.send(embed=embed)

    @commands.command(name="loop", aliases=['l'])
    async def _loop_queue(self, ctx: commands.context):
        """loop queue"""
        server_id = ctx.message.guild.id
        self.loop = self.loop if self.loop else {guild_id: loop for (
            guild_id, loop) in [(i.id, False) for i in self.bot.guilds]}
        if self.loop[server_id] == False:
            self.loop[server_id] = True
            msg = await ctx.send("ループしま～す!")
            await msg.add_reaction("➰")
            # await ctx.send(str(self.loop))
        else:
            self.loop[server_id] = False
            msg = await ctx.send("ループしません")
            await msg.add_reaction("❌")

    @commands.command(name="play", aliases=['p', 'lay'])
    async def _play(self, ctx: commands.context, *, song: str):
        """play song, search or url"""
        global Song_queue
        async with ctx.typing():

            await ctx.invoke(self._join)

            server_id = ctx.voice_client.server_id
            self.loop = self.loop if self.loop else {guild_id: loop for (
                guild_id, loop) in [(i.id, False) for i in self.bot.guilds]}

            source = await YTDLSource.create_source(ctx, song, loop=self.bot.loop)
            if server_id in Song_queue:
                Song_queue[server_id].append(source)
            else:
                Song_queue[server_id] = [source]
            if not ctx.voice_client.is_playing():
                ctx.voice_client.play(Song_queue[server_id].pop(0), after=lambda e: asyncio.run(
                    self.play_nexts_song(ctx)))
            song = Song(source)
        await ctx.send(embed=song.create_embed("enqueued"))

    @commands.command(name="remove", aliases=['re'])
    async def _remove(self, ctx: commands.context, index: int = 1):
        global Song_queue
        if not ctx.author.voice:
            return await ctx.send("no")
        server_id = ctx.message.guild.id
        if Song_queue[server_id] != []:
            index = min(max(index, -1), len(Song_queue[server_id]))

            if not self.loop[server_id]:
                ctx.voice_client.stop()
            msg = await ctx.send("Removed {1} [**{0.title}**](<{0.url}>) 成功!".format(Song_queue[server_id].pop(index - 1), index))
            await msg.add_reaction("✅")
        else:
            return await ctx.send("Queue is already empty!")

    @commands.command(name="now", aliases=['n'])
    async def _now(self, ctx: commands.Context):
        """show current song"""
        await ctx.send(embed=Song(ctx.voice_client.source).create_embed())

    @commands.command(name="clear", aliases=['c'])
    async def _clear(self, ctx: commands.Context):
        """clear queue"""
        global Song_queue
        server_id = ctx.voice_client.server_id
        Song_queue[server_id] = []
        msg = await ctx.send("Queue cleared! 成功!")
        await msg.add_reaction("✅")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.id == self.bot.user.id:
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
