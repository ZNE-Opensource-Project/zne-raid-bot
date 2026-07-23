import asyncio
import logging
import os
import tomllib
import discord
import sys as _sys
from discord.ext import commands

from core.utils.checks import global_interaction_check
from core.context import Context
from core.utils.db import init_db
from core.utils.helpers import post_commands_to_api, post_leaderboard_to_api
from core.utils.leaderboard import load_leaderboard, track_command
from core.utils.logger import setup_logger



with open("config.toml", "rb") as f:
    _config = tomllib.load(f)

TOKEN = _config["TOKEN"]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="z", intents=intents)
bot.context_cls = Context
logger = setup_logger()
bot.tree.interaction_check = global_interaction_check

bot.color = 0xff0000
bot.prefix = "z"


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

    await track_command(
        str(interaction.user.id),
        interaction.command.qualified_name,
        display_name=interaction.user.display_name,
        avatar_url=interaction.user.display_avatar.url,
    )


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)
    
@bot.event
async def on_command_error(ctx, error):
    import traceback
    traceback.print_exception(type(error), error, error.__traceback__)


def discover_cogs(commands_dir: str = "cogs") -> list[str]:
    cogs = []
    for filename in os.listdir(commands_dir):
        full_path = os.path.join(commands_dir, filename)
        if filename.endswith(".py") and not filename.startswith("__"):
            cogs.append(f"cogs.{filename[:-3]}")
        elif os.path.isdir(full_path) and filename != "__pycache__":
            if os.path.exists(os.path.join(full_path, "__init__.py")):
                cogs.append(f"cogs.{filename}")
    cogs.sort()
    return cogs


async def load_cog(cog: str):
    try:
        module = __import__(cog, fromlist=[""])
    except Exception as e:
        logger.error(f"Failed to import cog {cog}: {e}", exc_info=True)
        return

    if hasattr(module, "cog_setup"):
        try:
            module.cog_setup(bot)
            logger.info(f"new cog loaded: {cog}")
        except Exception as e:
            logger.error(f"Failed to load cog {cog}: {e}", exc_info=True)
        return

    try:
        await bot.load_extension(cog)
        logger.info(f"new cog loaded: {cog}")
    except Exception as e:
        logger.error(f"Failed to load cog {cog}: {e}", exc_info=True)


@bot.event
async def on_ready():
    await init_db()
    logger.info(f"i am {bot.user}")

    for cog in discover_cogs():
        await load_cog(cog)

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
