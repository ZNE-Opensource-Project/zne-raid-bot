import discord

def cog_setup(bot):
    @bot.command(name='nuke', aliases=[])
    async def _nuke(ctx):
        if not ctx.guild:
            return
        if not ctx.author.guild_permissions.administrator:
            return

        cloned = await ctx.channel.clone(reason=f"Nuked by {str(ctx.author)} ({ctx.author.id})")
        await cloned.edit(position=ctx.channel.position)
        await cloned.send(f":boom: The purge requested by {ctx.author} has been performed. https://cdn.discordapp.com/attachments/842303468160286761/884475305501294683/standard.gif")
        await ctx.channel.delete()
