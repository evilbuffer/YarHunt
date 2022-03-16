from library.yaralib import *
from library.dispatch import *
from config import *
import discord
from discord.ext import commands
import threading


malbot = commands.Bot(command_prefix="!")
cogs = []
cogs.append("cogs.cmd_handler")


if __name__ == "__main__":
    for ext in cogs:
        malbot.load_extension(ext)

@malbot.event
async def on_ready():

    await malbot.change_presence(activity=discord.Game(name="Hunting malware"))
    compile_directory()
    sch_dispatcher_thread = threading.Thread(target=sch_dispatcher)
    sch_dispatcher_thread.start()

    print("BOT IS READY")
malbot.run(bot_token)