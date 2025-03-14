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
                        Supposed to send a message whenever someone leaves the server
--------------------------------------------------------------------------------------------------------------------------------'''
@client.event
async def on_member_remove(member):
    channel = client.get_channel(728631905330790431)
    await channel.send("user has left the server")

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
print(os.getenv("POOKIE_BOT_TOKEN"))
client.run(TOKEN)