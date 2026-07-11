import asyncio
import logging
import os
import tomllib
import discord
from discord.ext import commands

from core.utils.checks import global_interaction_check
from core.utils.db import init_db
from core.utils.helpers import post_commands_to_api, post_leaderboard_to_api
from core.utils.leaderboard import load_leaderboard, track_command

# Load config
with open("config.toml", "rb") as f:
    _config = tomllib.load(f)

TOKEN = _config["TOKEN"]

# Load altgen config so we can run its cogs on this bot's token
import json as _json
ALTGEN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cogs", "altgen")
with open(os.path.join(ALTGEN_DIR, "config.json"), "r") as f:
    _altgen_config = _json.load(f)
ALTGEN_PREFIX = _altgen_config.get("prefix", ".")

from core.utils.logger import setup_logger
logger = setup_logger()

class Vobyisafemboy(commands.AutoShardedBot):
  def __init__(self, *arg, **kwargs):
    intents = discord.Intents.all()
    intents.presences = True
    intents.members = True
    super().__init__(command_prefix=".",
                     case_insensitive=True,
                     intents=intents,
                     strip_after_prefix=True,
                     allowed_mentions=discord.AllowedMentions(
                     everyone=True, replied_user=True, roles=True),
                     sync_commands_debug=True,
                     help_command=None
    )

intents = discord.Intents.all()
bot = Vobyisafemboy

bot.tree.interaction_check = global_interaction_check

# Attach altgen bot helpers so its cogs can reuse them on this token
import sys as _sys
if ALTGEN_DIR not in _sys.path:
    _sys.path.append(ALTGEN_DIR)
import gen as _altgen_gen_module

bot.gen = _altgen_gen_module
bot.color = 0xff0000
bot.prefix = ALTGEN_PREFIX
bot.cooldown = set()
bot.altgen_config = _altgen_config


def get_global_total_commands() -> int:
    _, total_commands = load_leaderboard()
    return total_commands


async def update_bot_status():
    activity = discord.Activity(
        name=f"zne.breed.rip | {get_global_total_commands()} raids...",
        type=discord.ActivityType.streaming,
        url="https://twitch.tv/voby7"
    )
    await bot.change_presence(activity=activity)


async def leaderboard_sync_loop():
    await asyncio.sleep(5 * 60)
    while True:
        await post_leaderboard_to_api(bot)
        await update_bot_status()
        await asyncio.sleep(5 * 60)


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.application_command:
        return

    if not interaction.command:
        return

    await track_command(str(interaction.user.id), interaction.command.qualified_name)


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    import traceback
    traceback.print_exception(type(error), error, error.__traceback__)


def discover_altgen_cogs(cogs_dir: str = os.path.join("cogs", "altgen", "cogs")) -> list[str]:
    cogs = []
    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            cogs.append(filename[:-3])
    cogs.sort()
    return cogs


def load_altgen_cogs():
    for name in discover_altgen_cogs():
        module_name = f"cogs.altgen.cogs.{name}"
        try:
            module = __import__(module_name, fromlist=[""])
            module.cog_setup(bot)
            logger.info(f"altgen cog loaded: {module_name}")
        except Exception as e:
            logger.error(f"Failed to load altgen cog {module_name}: {e}", exc_info=True)


def discover_cogs(commands_dir: str = "cogs") -> list[str]:
    cogs = []
    for filename in os.listdir(commands_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            cogs.append(f"cogs.{filename[:-3]}")
    cogs.sort()
    return cogs


@bot.event
async def on_ready():
    os.system("cls" if os.name == "nt" else "clear")
    await init_db()
    logger.info(f"i am {bot.user}")

    for cog in discover_cogs():
        try:
            await bot.load_extension(cog)
            logger.info(f"new cog loaded: {cog}")
        except Exception as e:
            logger.error(f"Failed to load cog {cog}: {e}", exc_info=True)

    load_altgen_cogs()

    try:
        await bot.tree.sync()
    except Exception as e:
        logger.error(f"Error syncing tree: {e}")

    await post_commands_to_api(bot)
    await post_leaderboard_to_api(bot)
    await update_bot_status()

    if not getattr(bot, "_leaderboard_sync_task", None) or bot._leaderboard_sync_task.done():
        bot._leaderboard_sync_task = asyncio.create_task(leaderboard_sync_loop())

    invite_url = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot"
    logger.info(f"Bot invite: {invite_url}")


async def main():
    logger.info("Starting bot...")
    await bot.start(TOKEN)
    logger.info("Bot disconnected.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit
