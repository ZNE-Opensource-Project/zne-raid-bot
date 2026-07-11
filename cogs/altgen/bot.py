import discord
from discord.ext import commands
import json
import os
import asyncio
import sys
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

class Astroz(commands.AutoShardedBot):
  def __init__(self, *arg, **kwargs):
    intents = discord.Intents.all()
    intents.presences = True
    intents.members = True
    super().__init__(command_prefix=config['prefix'],
                     case_insensitive=True,
                     intents=intents,
                     status=discord.Status.online,
                     strip_after_prefix=True,
                     allowed_mentions=discord.AllowedMentions(
                       everyone=False, replied_user=False, roles=False),
                     sync_commands_debug=True,
                     help_command=None
    )
    
bot = Astroz()

bot.prefix = config['prefix']
bot.color = 0xff0000
bot.cooldown = set()

async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = f'cogs.{filename[:-3]}'
            try:
                module = __import__(module_name, fromlist=[''])
                module.cog_setup(bot)
                print(f'Loaded cog: {module_name}')
            except Exception as e:
                print(f'Failed to load cog {module_name}: {e}')

import gen as gen_module
bot.gen = gen_module

@bot.event
async def on_ready():
    print(f'{str(bot.user)} is online in {len(bot.guilds)} servers!')

@bot.event
async def on_command_error(ctx, error):
    traceback.print_exception(type(error), error, error.__traceback__)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.channel.type != discord.ChannelType.text:
        return
    await bot.process_commands(message)

async def main():
    async with bot:
        await load_cogs()
        await bot.start(config['token'])

if __name__ == '__main__':
    asyncio.run(main())
