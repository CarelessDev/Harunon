from discord_slash import  SlashContext, cog_ext, ComponentContext
from discord_slash.utils.manage_commands import create_choice, create_option
import discord
from discord.ext import commands
from dotenv import load_dotenv
import json, os
import youtube_dl
import asyncio, functools
import asyncio
import math
from random import choice

load_dotenv()


guild_ids = [int(id) for id in os.getenv('guild_ids').split(',')]

with open("./words.json", "r") as f:
    data = json.load(f)

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''


class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass

class YTDLSource1(discord.PCMVolumeTransformer):
    ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
    }

    ffmpeg_options = {
        'options': '-vn'
    }

    ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: cls.ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else cls.ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **cls.ffmpeg_options), data=data)
        

class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)
        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data
        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return '**{0.title}** by **{0.uploader}**'.format(self)

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
                'Couldn\'t find anything that matches `{}`'.format(search))


        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError(
                    'Couldn\'t find anything that matches `{}`'.format(search))

        webpage_url = process_info['webpage_url']
        partial = functools.partial(
            cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError('Couldn\'t fetch `{}`'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError(
                        'Couldn\'t retrieve any matches for `{}`'.format(webpage_url))

        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

   

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
    __slots__ = ('source', 'requester')

    def __init__(self, source):
        self.source = source
        self.requester = source.requester

    def create_embed(self, words="Now playing"):
        embed = (discord.Embed(title=words, description='```css\n{0.source.title}\n```'.format(self), color=0x66ff99)  # discord.Color.blurple())
                 .add_field(name='Duration', value=self.source.duration)
                 .add_field(name='Requested by', value=self.requester.mention)
                 .add_field(name='Uploader', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
                 .add_field(name='URL', value='[Click]({0.source.url})'.format(self))
                 .set_thumbnail(url=self.source.thumbnail)
                 .set_author(name=self.requester.name, icon_url=self.requester.avatar_url))
        return embed


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queues= {}
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
            player.play(self.current_song, after=lambda x=None:asyncio.run(self.play_nexts_song(ctx)))
        else:
            self.current_song = None

    @cog_ext.cog_slash(name="lulu",description="play lulu", guild_ids=guild_ids, 
                        options=[create_option(name='url',
                                    description='lulu gonna eat u',
                                    required=True,
                                    option_type=3,
                                    choices=[create_choice(name=key, value=data["lulu"][key]) for key in list(data["lulu"].keys())[:25]]
                                    )])
    async def _lulu(self, ctx:SlashContext , url:str):
        if not ctx.voice_client:
            channel = ctx.author.voice.channel
            await channel.connect()
        await ctx.defer()
        player = await YTDLSource1.from_url(url=url, loop=self.bot.loop)
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        embed = discord.Embed(title=f"lulu has said {player.title}", color=discord.Color.blurple())
        embed.set_thumbnail(url="https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/ff8bf031-fb82-4095-a6e7-1abc85e4042c/debniea-d8b3f927-ada7-43b0-8001-725744eb6fd9.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcL2ZmOGJmMDMxLWZiODItNDA5NS1hNmU3LTFhYmM4NWU0MDQyY1wvZGVibmllYS1kOGIzZjkyNy1hZGE3LTQzYjAtODAwMS03MjU3NDRlYjZmZDkucG5nIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.K8SKYiO-lTUDWvnLxrcrL8ezNL7Y-Af-rsF-Nu51r0U")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
        #await ctx.voice_client.disconnect()
    @cog_ext.cog_slash(name="lulu2",description="play lulu", guild_ids=guild_ids, 
                        options=[create_option(name='url',
                                    description='lulu gonna eat u',
                                    required=True,
                                    option_type=3,
                                    choices=[create_choice(name=key, value=data["lulu"][key]) for key in list(data["lulu"].keys())[25:50]]
                                    )])
    async def _lulu2(self, ctx:SlashContext , url:str):
        if not ctx.voice_client:
            channel = ctx.author.voice.channel
            await channel.connect()
        await ctx.defer()
        player = await YTDLSource1.from_url(url=url, loop=self.bot.loop)
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        embed = discord.Embed(title=f"lulu has said {player.title}", color=discord.Color.blurple())
        embed.set_thumbnail(url="https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/ff8bf031-fb82-4095-a6e7-1abc85e4042c/debniea-d8b3f927-ada7-43b0-8001-725744eb6fd9.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcL2ZmOGJmMDMxLWZiODItNDA5NS1hNmU3LTFhYmM4NWU0MDQyY1wvZGVibmllYS1kOGIzZjkyNy1hZGE3LTQzYjAtODAwMS03MjU3NDRlYjZmZDkucG5nIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.K8SKYiO-lTUDWvnLxrcrL8ezNL7Y-Af-rsF-Nu51r0U")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
    @cog_ext.cog_slash(name="lulu3",description="play lulu", guild_ids=guild_ids, 
                        options=[create_option(name='url',
                                    description='lulu gonna eat u',
                                    required=True,
                                    option_type=3,
                                    choices=[create_choice(name=key, value=data["lulu"][key]) for key in list(data["lulu"].keys())[50:75]]
                                    )])
    async def _lulu3(self, ctx:SlashContext , url:str):
        if not ctx.voice_client:
            channel = ctx.author.voice.channel
            await channel.connect()
        await ctx.defer()
        player = await YTDLSource1.from_url(url=url, loop=self.bot.loop)
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        embed = discord.Embed(title=f"lulu has said {player.title}", color=discord.Color.blurple())
        embed.set_thumbnail(url="https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/ff8bf031-fb82-4095-a6e7-1abc85e4042c/debniea-d8b3f927-ada7-43b0-8001-725744eb6fd9.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcL2ZmOGJmMDMxLWZiODItNDA5NS1hNmU3LTFhYmM4NWU0MDQyY1wvZGVibmllYS1kOGIzZjkyNy1hZGE3LTQzYjAtODAwMS03MjU3NDRlYjZmZDkucG5nIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.K8SKYiO-lTUDWvnLxrcrL8ezNL7Y-Af-rsF-Nu51r0U")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
        #await ctx.voice_client.disconnect()
    @cog_ext.cog_slash(name="lulu4",description="play lulu", guild_ids=guild_ids, 
                        options=[create_option(name='url',
                                    description='lulu gonna eat u',
                                    required=True,
                                    option_type=3,
                                    choices=[create_choice(name=key, value=data["lulu"][key]) for key in list(data["lulu"].keys())[75:100]]
                                    )])
    async def _lulu4(self, ctx:SlashContext , url:str):
        if not ctx.voice_client:
            channel = ctx.author.voice.channel
            await channel.connect()
        await ctx.defer()
        player = await YTDLSource1.from_url(url=url, loop=self.bot.loop)
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        embed = discord.Embed(title=f"lulu has said {player.title}", color=discord.Color.blurple())
        embed.set_thumbnail(url="https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/ff8bf031-fb82-4095-a6e7-1abc85e4042c/debniea-d8b3f927-ada7-43b0-8001-725744eb6fd9.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcL2ZmOGJmMDMxLWZiODItNDA5NS1hNmU3LTFhYmM4NWU0MDQyY1wvZGVibmllYS1kOGIzZjkyNy1hZGE3LTQzYjAtODAwMS03MjU3NDRlYjZmZDkucG5nIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.K8SKYiO-lTUDWvnLxrcrL8ezNL7Y-Af-rsF-Nu51r0U")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
    @cog_ext.cog_slash(name="lulu5",description="play lulu", guild_ids=guild_ids, 
                        options=[create_option(name='url',
                                    description='lulu gonna eat u',
                                    required=True,
                                    option_type=3,
                                    choices=[create_choice(name=key, value=data["lulu"][key]) for key in list(data["lulu"].keys())[100:]]
                                    )])
    async def _lulu5(self, ctx:SlashContext , url:str):
        if not ctx.voice_client:
            channel = ctx.author.voice.channel
            await channel.connect()
        await ctx.defer()
        player = await YTDLSource1.from_url(url=url, loop=self.bot.loop)
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        embed = discord.Embed(title=f"lulu has said {player.title}", color=discord.Color.blurple())
        embed.set_thumbnail(url="https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/ff8bf031-fb82-4095-a6e7-1abc85e4042c/debniea-d8b3f927-ada7-43b0-8001-725744eb6fd9.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcL2ZmOGJmMDMxLWZiODItNDA5NS1hNmU3LTFhYmM4NWU0MDQyY1wvZGVibmllYS1kOGIzZjkyNy1hZGE3LTQzYjAtODAwMS03MjU3NDRlYjZmZDkucG5nIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.K8SKYiO-lTUDWvnLxrcrL8ezNL7Y-Af-rsF-Nu51r0U")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="thorns",description="gay", guild_ids=guild_ids)
    async def _thorns(self, ctx:SlashContext):
        if not ctx.voice_client:
            channel = ctx.author.voice.channel
            await channel.connect()
        url = choice(["https://aceship.github.io/AN-EN-Tags/etc/voice/char_293_thorns/CN_028.mp3", "https://aceship.github.io/AN-EN-Tags/etc/voice/char_293_thorns/CN_026.mp3"])
        await ctx.defer()
        player = await YTDLSource1.from_url(url=url, loop=self.bot.loop)
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        embed = discord.Embed(title=f"chi", color=discord.Color.blurple())
        embed.set_image(url="https://media.discordapp.net/attachments/515423288114151425/878336201675923507/image0.gif")
        await ctx.send(embed=embed)

    
    @cog_ext.cog_slash(name="tesr",description="join a vc", guild_ids=guild_ids)
    async def _tesr(self, ctx:SlashContext):
        await ctx.send(str(self.bot.loop))

 
    @cog_ext.cog_slash(name="join",description="join a vc", guild_ids=guild_ids)
    async def _join(self, ctx:SlashContext):
        channel = ctx.author.voice.channel
        await ctx.send("joined vc")
        await channel.connect()

    @cog_ext.cog_slash(name="leave",description="leave vc", guild_ids=guild_ids)
    async def _leave(self, ctx:SlashContext):
        await ctx.voice_client.disconnect()
        await ctx.send("leave")
        

    @cog_ext.cog_slash(name="skip",description="skip song", guild_ids=guild_ids)
    async def _skip(self, ctx:SlashContext):
        if not ctx.voice_client.is_playing:
            return await ctx.send('Not playing any music right now...')
        #self.queues[ctx.voice_client.server_id].pop(0)
        ctx.voice_client.stop() 
        await ctx.send('skip!⏭')
        
    @cog_ext.cog_slash(name="pause",description="pause song", guild_ids=guild_ids)
    async def _pause(self, ctx:SlashContext):
        if not ctx.voice_client.is_playing:
            return await ctx.send('Not playing any music right now...')
        if ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            ctx.voice_client.pause()
            await ctx.send('pause⏯')

    @cog_ext.cog_slash(name="resume",description="resume song", guild_ids=guild_ids)
    async def _resume(self, ctx:SlashContext):
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("resume")

    @cog_ext.cog_slash(name="queue",description="show song queue", guild_ids=guild_ids)
    async def _queue(self, ctx:SlashContext):
        #await ctx.send(f"queue: {[song.title for song in self.queues[ctx.voice_client.server_id]]}")
        
        if not self.queues[self.server_id]:
            return await ctx.send('Empty queue.')
        page = 1
        items_per_page = 10
        pages = math.ceil(len(self.queues[self.server_id]) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(self.queues[self.server_id][start:end], start=start):
            queue += '`{0}.` [**{1.title}**]({1.url})\n'.format(
                i + 1, song)

        embed = (discord.Embed(description='**{} tracks:**\n\n{}'.format(len(self.queues[self.server_id]), queue))
                .set_footer(text='Viewing page {}/{}'.format(page, pages)))
        await ctx.send(embed=embed)



    @cog_ext.cog_slash(name="loop",description="loop queue", guild_ids=guild_ids)
    async def _loop_queue(self, ctx:SlashContext):
        if self.loop == False:
            self.loop = True
            await ctx.send("Queue loop == True")
        else:
            self.loop = False
            await ctx.send("loop now False")


    @cog_ext.cog_slash(name="play",description="play music", guild_ids=guild_ids, 
                        options=[create_option(name='song',
                                    description='song name',
                                    required=True,
                                    option_type=3)])
    async def _play(self, ctx:SlashContext , *, song:str):
        if not ctx.voice_client:
            channel = ctx.author.voice.channel
            await channel.connect()
        
        self.ctx = ctx
        self.server_id = ctx.voice_client.server_id
        await ctx.defer()  
        source = await YTDLSource.create_source(ctx, song,loop=self.bot.loop)
        if self.server_id in self.queues:
            self.queues[self.server_id].append(source)
        else:
            self.queues[self.server_id] = [source]
        if not ctx.voice_client.is_playing():
            ctx.voice_client.play(self.queues[self.server_id][0], after=lambda e: asyncio.run(self.play_nexts_song(ctx)))
        song = Song(source)  
        await ctx.send(embed=song.create_embed("enqueued"))


    @cog_ext.cog_slash(name="remove",description="remove song from queue", guild_ids=guild_ids, 
                        options=[create_option(name='index',
                                    description='song index',
                                    required=True,
                                    option_type=10)])
    async def _remove(self, ctx:SlashContext , index:int):    
        if self.queues[self.server_id] != []:
            index = min(max(index, -1), len(self.queues[self.server_id]))
            
            if not self.loop:
                   ctx.voice_client.stop()
            await ctx.send('remove {1} [**{0.title}**](<{0.url}>) ✅'.format(self.queues[self.server_id].pop(index - 1), index))
            
            #await ctx.send(f"{index} ")
        else:
            return await ctx.send('Empty queue.')

    
    @cog_ext.cog_slash(name="now",description="show current song", guild_ids=guild_ids)
    async def _now(self, ctx: commands.Context):
        await ctx.send(embed=Song(ctx.voice_client.source).create_embed())

    @cog_ext.cog_slash(name="clear",description="clear queue", guild_ids=guild_ids)
    async def _now(self, ctx: commands.Context):
        self.queues[self.server_id] = []
        await ctx.send('Queue cleared!')

    
    

        