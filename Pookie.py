#Import Discord API
import discord
from discord.ext import commands

# Load the environment files
import os
from dotenv import load_dotenv
load_dotenv()

# Perhaps not needed for actual function of bot, just for videos
#import requests
#import json

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

client = commands.Bot(command_prefix = '+', intents = intents)

'''--------------------------------------------------------------------------------------------------------------------------------
                                Sends a message to let us know the bot is online
--------------------------------------------------------------------------------------------------------------------------------'''
@client.event
async def on_ready():
    print("Pookie bot is online")
    print("--------------------")

# Just a test message
@client.command()
async def test(ctx):
    user_id = str(ctx.author)
    print(user_id)
    await ctx.send("**# " + user_id + "** testing testing")

'''--------------------------------------------------------------------------------------------------------------------------------
                                    Act like and angel and dress like crazy
--------------------------------------------------------------------------------------------------------------------------------'''
@client.event
async def on_message(message):
    await client.process_commands(message)
    
    if "crazy" in message.content:
        await message.channel.send("no no")

'''--------------------------------------------------------------------------------------------------------------------------------
                        Supposed to send a message whenever someone leaves the server
--------------------------------------------------------------------------------------------------------------------------------'''
LEAVE_CHANNEL = int(os.getenv("SIONARA"))

@client.event
async def on_member_remove(member):
    channel = client.get_channel(LEAVE_CHANNEL)
    guild = member.guild
    #audit_logs = guild.audit_logs(limit = 1, action = discord.AuditLogAction.kick)

    # Fetch the latest audit log entry for kicks
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
        print(entry)
        if entry.target == member:  # Ensure the log entry matches the member that left
            message = f"**{member.nick}** just left the server."
            
    await channel.send(message)

'''--------------------------------------------------------------------------------------------------------------------------------
                                                  Join/Leave voice calls
--------------------------------------------------------------------------------------------------------------------------------'''
@client.command(pass_context = True)
async def join(ctx):
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("You must be in a voice channel to run this command")

@client.command(pass_context = True)
async def leave(ctx):
    if (ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send("Left voice channel")
    else:
        await ctx.send("Not currently in a voice channel")

'''--------------------------------------------------------------------------------------------------------------------------------
                                                    Runs the pookie bot
--------------------------------------------------------------------------------------------------------------------------------'''
TOKEN = os.getenv('POOKIE_BOT_TOKEN')
client.run(TOKEN)