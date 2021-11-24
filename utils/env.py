import os
from dotenv import load_dotenv
import asyncpraw
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

guild_ids = [int(id) for id in os.getenv("guild_ids").split(",")]

reddit = asyncpraw.Reddit(
    client_id=os.getenv("client_id"),
    client_secret=os.getenv("client_secret"),
    username=os.getenv("username"),
    password=os.getenv("password"),
    user_agent=os.getenv("user_agent")
)

TENOR_APIKEY = os.getenv("TENOR_APIKEY")
