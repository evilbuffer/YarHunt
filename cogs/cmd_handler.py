import discord
from discord.ext import commands
from library.webfuncs import download_yara_rule, delete_yara_rule
import os 
from library.yaralib import get_yara_rules
from library.dispatch import get_running_jobs

class CmdHandlerCog(commands.Cog):
    def __init(self, bot):
        self.bot = bot

    @commands.command(name="upload")
    async def upload_rule(self, ctx):
        # Maybe implement a whitelist for who can upload here
        res = download_yara_rule(str(ctx.message.attachments[0]))
        if res:
            embed = discord.Embed(title="Rule sucessfully uploaded",color=0x00ff00)
            embed.add_field(name="URL", value=str(ctx.message.attachments[0]), inline=False)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Rule upload failed due to file type",color=0x00ff00)
            embed.add_field(name="URL", value=str(ctx.message.attachments[0]), inline=False)
            await ctx.send(embed=embed)

    @commands.command(name="rules")
    async def list_rules(self, ctx):
        rules = get_yara_rules()
        await ctx.send(rules)

    @commands.command(name="jobs")
    async def get_sch_jobs(self, ctx):
        jobs = get_running_jobs()
        embed = discord.Embed(title="Running jobs", color=0x00ff00)
        embed.add_field(name="Jobs", value=jobs)
        await ctx.send(embed=embed)

    @commands.command(name="delete")
    async def delete_rule(self, ctx):
        target_rule = delete_yara_rule(str(ctx.message.attachments[0]))
        embed = discord.Embed(title="Status", color=0x00ff00)
        embed.add_field(name="Status", value="Yara rule deleted")
        await ctx.send(embed=embed)




def setup(bot):
    bot.add_cog(CmdHandlerCog(bot))