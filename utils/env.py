import os
from dotenv import load_dotenv
load_dotenv()


guild_ids = [int(id) for id in os.getenv("guild_ids").split(",")]
