import discord
from discord.ext import commands, tasks

from random import choice

import json
import os

if os.path.exists(os.getcwd() + "/config.json"):
    with open("./config.json") as f:
        configData = json.load(f)
else:
    configTemplate = {"Token":"", "Prefix": "-"}
    with open(os.getcwd() + "/config.json", "w+") as f:
        json.dump(configTemplate, f)


token = configData["Token"]
prefix = configData["Prefix"]

client = commands.Bot(command_prefix="-")
client.remove_command("help")


@client.event
async def on_ready():
    change_status.start()
    print("Bot is online!")
    await client.change_presence(activity=discord.Game(name="smth better than u"))

status = ["Jamming out to music!", "Eating!", "Sleeping!", "smth better than u"]


@tasks.loop(seconds=20)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))


@client.command(description="Gets the bot's latency")
async def ping(ctx):
    latency = round(client.latency*1000, 1)
    await ctx.send(f"**Pong!** {latency}ms")

@client.command(description="Says hello to the user")
async def hi(ctx):
    user = ctx.author
    if user.nick != None:
        user = user.nick
    else:
        user = user.name

    responses = [f"***grumble*** Why did you wake me up {user}???", f"Hello {user}!", f"Top of the morning lad :coffee:", f"What up dawgg, whats poppin"]
    await ctx.send(choice(responses))

@client.command(description="Bans the user from the server")
@commands.has_permissions(ban_members = True)
async def ban(ctx, member: discord.Member, *, reason=None):
    if reason==None:
        reason = "No reason specified"
    await member.ban(reason = reason)
    await ctx.send(f"{member} **was banned**")
    await ctx.send(f"**Reason:** {reason}")

@client.command(description="Kicks the user from the server")
@commands.has_permissions(kick_members = True)
async def kick(ctx, member: discord.Member, *, reason=None):
    if reason==None:
        reason = "No reason specified"
    await member.kick(reason = reason)
    await ctx.send(f"{member} **was kicked**")
    await ctx.send(f"**Reason:** {reason}")

@client.command(description="Unbans the user from the server")
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    bannedUsers = await ctx.guild.bans()
    name, discriminator = member.split("#")

    for ban in bannedUsers:
        user = ban.user

        if (user.name, user.discriminator) == (name, discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f"{user.mention} **was unbanned**")
            return

@client.command(description="Sets the activity of the bot")
@commands.has_permissions(administrator=True)
async def activity(ctx, *, activity):
    await client.change_presence(activity=discord.Game(name=activity))
    await ctx.send(f"Bot's activity has been changed to **{activity}**")

@client.command(description="Displays the user info of the specified user")
async def userinfo(ctx, member:discord.Member=None):
    if member==None:
        user = ctx.author
    else:
        user = member
    embed=discord.Embed(title="USER INFO", description=f"Here is the info we retrieved about {user}", color=user.color)
    embed.set_thumbnail(url=user.avatar_url)
    embed.add_field(name="NAME", value=user.name, inline=True)
    embed.add_field(name="NICKNAME", value=user.nick, inline=True)
    embed.add_field(name="ID", value=user.id, inline=True)
    embed.add_field(name="STATUS", value=user.status, inline=True)
    embed.add_field(name="TOP ROLE", value=user.top_role.name, inline=True)
    await ctx.send(embed=embed)

@client.command(description="The help command")
async def help(ctx, commandSent=None ):
    if commandSent != None:

        for command in client.commands:
            if commandSent.lower() == command.name.lower():
                
                paramString = ""
                
                if len(command.clean_params) == 0:
                    paramString = "None"

                for param in command.clean_params:
                    paramString += param + ", "

                paramString = paramString[:-2]
                embed=discord.Embed(title=f"HELP - {command.name}", description=command.description)
                embed.add_field(name="Parameters:", value=paramString)
                await ctx.message.delete()
                await ctx.author.send(embed=embed)
    else:
        embed=discord.Embed(title="HELP")
        embed.add_field(name="**ping**", value="get the bot's latency")
        embed.add_field(name="**hi**", value="says hello to a specified user, Parameters: Member")
        embed.add_field(name="**userinfo**", value="gets info about specified user, Optional Parameter: Member")

        await ctx.message.delete()
        await ctx.author.send(embed=embed)

@client.command(description="Mutes the specified user")
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member:discord.Member, *, reason=None):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")
        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=True)
    await member.add_roles(mutedRole, reason=reason)
    await ctx.send(f"Muted {member.mention}")
    await ctx.send(f"Reason: {reason}")
    await member.send(f"You were muted in the server **{guild.name}**")
    await member.send(f"Reason: {reason}")

@client.command(description="Unmutes the specified user")
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member):
    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.remove_roles(mutedRole)
    await ctx.send(f"Unmuted {member.mention}")
    await member.send(f"You were unmuted from the server **{ctx.guild.name}**")


client.run(token)