import discord
import os

ALTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'alts')

def cog_setup(bot):
    @bot.command(name='addnewfile', aliases=[])
    async def _addnewfile(ctx, type_name: str = None):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send(embed=discord.Embed(title="You don't have permission to use gen!", color=bot.color))
        if not type_name:
            return await ctx.send(embed=discord.Embed(title=f"Usage: {bot.prefix}addnewfile <type>", color=bot.color))
        os.makedirs(ALTS_DIR, exist_ok=True)
        with open(os.path.join(ALTS_DIR, f'{type_name}.txt'), 'w', encoding='utf-8') as f:
            pass
        await ctx.send(embed=discord.Embed(title=f"Added new file!", color=bot.color))
