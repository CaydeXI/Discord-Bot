#Import Discord API
import discord
from discord.ext import commands

# Load the environment files
import os
import requests
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
                                                  Embeds stuff
--------------------------------------------------------------------------------------------------------------------------------'''
@client.command()
async def embed(ctx):
    embed = discord.Embed(
        title = "Dog", 
        url = "https://google.com", 
        description = "We love dogs!", 
        color = 0x4dff4d)
    embed.set_author(name = "James S", url = "https://google.com")
    await ctx.send(embed = embed)

'''--------------------------------------------------------------------------------------------------------------------------------
                                                  Riot games stuff
--------------------------------------------------------------------------------------------------------------------------------'''
# Initialize both of these beforehand because I know I'm going to need them later
RIOT_ACCOUNT_URL = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id"
RIOT_API_KEY = os.getenv("RIOT_API_KEY")

def get_riot_puuid(summoner_name, message: str):
    riot_id = message.split('#')[0]
    tagline = message.split('#')[1]
    url = f"{RIOT_ACCOUNT_URL}/{riot_id}/{tagline}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    response = requests.get(url, headers = headers)

    # Status code 200 means all is good, anything not 200 is bad
    if response.status_code == 200:
        return response.json()    # returns puuid
    else:
        return None

RIOT_SUMMONER_URL = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid"
@client.command()
async def get_summoner_data(puuid):
    url = f"{RIOT_SUMMONER_URL}/{puuid}"
    print(url)
    headers = {"X-Riot-Token": RIOT_API_KEY}
    response = requests.get(url, headers = headers)

    print(response.json())

'''--------------------------------------------------------------------------------------------------------------------------------
                                                    Runs the pookie bot
--------------------------------------------------------------------------------------------------------------------------------'''
TOKEN = os.getenv('POOKIE_BOT_TOKEN')
client.run(TOKEN)