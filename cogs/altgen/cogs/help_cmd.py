import discord

class HelpView(discord.ui.LayoutView):    
    container1 = discord.ui.Container(
        discord.ui.TextDisplay(content="# ZNEGEN Help\nAll of the commands for ZNEGEN.\n"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content="## Gen\nGenerate an alt.\n## Stock\nView account stock.\n## Timeleft\nView how much time you have left before generating.\n## Addnewfile\nAdd a new empty account stock\n## Restock\n[ OWNER ] Restock accounts."),
        discord.ui.TextDisplay(content="-# made by voby7"),
        discord.ui.MediaGallery(
            discord.MediaGalleryItem(
                media="https://zne.breed.rip/assets/banner.gif",
            ),
        ),
    )

def cog_setup(bot):
    @bot.command(name='help', aliases=[])
    async def _help(ctx):
        view = HelpView()
        await ctx.send(view=view)
