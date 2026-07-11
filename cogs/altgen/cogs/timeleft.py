import time
import discord
import json
import os

config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

def get_color(color_str):
    if isinstance(color_str, str) and color_str.upper() == 'RANDOM':
        return discord.Color.random()
    return discord.Color(color_str)

def cog_setup(bot):
    @bot.command(name='timeleft', aliases=['cooldown', 'cooldowns', 'timeover'])
    async def _timeleft(ctx):
        user = ctx.author
        timeout = int(config['GenCooldown'])
        import database as db_module
        author = db_module.db.get(f'ae_{ctx.author.id}_{user.id}')

        if author is not None and timeout - (time.time() * 1000 - int(author)) > 0:
            remaining = timeout - (time.time() * 1000 - int(author))
            minutes = int(remaining // 60000)
            seconds = int((remaining % 60000) // 1000)
            return await ctx.reply(embed=discord.Embed(
                title='Time Left',
                description=f"You have to wait **{minutes}m and {seconds}s** until you can get a new account (again)!",
                color=get_color(config['Color'])
            ).set_footer(text=f"Requested by {ctx.author} ").set_image(url=config.get('Banner', '')))

        cooldowns = discord.Embed(
            title='No Time-Left',
            description="Feel free to generate another account! You don't have cooldown.",
            color=get_color(config['Color'])
        ).set_footer(text=f"Requested by {ctx.author} ").set_image(url=config.get('Banner', ''))
        await ctx.send(embed=cooldowns)
