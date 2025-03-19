# Import Discord API
import discord
from discord.ext import commands

# Load the environment files
import os
import requests
from dotenv import load_dotenv
load_dotenv()

# Imports a json that conveniently contains all of the League champions with their champion ids
import json
with open('LeagueChamps.json') as lc:
    LeagueChamps = json.load(lc)

with open('StoredAccounts.json') as sa:
    Accounts = json.load(sa)

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
# This leave channel should be changed to the appropriate channel in the server
LEAVE_CHANNEL = int(os.getenv("SIONARA"))

@client.event
async def on_member_remove(member):
    channel = client.get_channel(LEAVE_CHANNEL)
    guild = member.guild

    # Fetch the latest audit log entry for kicks
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
        #print(entry)
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
                                     Help command to show everyone the functions
--------------------------------------------------------------------------------------------------------------------------------'''
@client.command()
async def commands(ctx):
    '''await ctx.send(f"**Available commands**\n" +
                   f"+add summoner name / nickname" +
                   f"+list" +
                   f"+remove nickname" +

                   f"+join" +  Probably not worth mentioning these two as they do not serve any real purpose
                   f"+leave"
                   ) '''
    embed = discord.Embed(
        title = "**Available commands**",
        color = 0x6d44c7
    )
    embed.set_thumbnail()
    embed.add_field(
        name = "+add summoner name / nickname",
        value = "Binds a nickname to an account so that it can be used instead of the full name",
        inline = False
    )
    embed.add_field(
        name = "+remove nickname",
        value = "Unbinds the nickname from the account",
        inline = False
    )
    embed.add_field(
        name = "+list",
        value = "Lists out all of the currently bound nicknames",
        inline = False
    )

    await ctx.send(embed = embed)
    

'''--------------------------------------------------------------------------------------------------------------------------------
                                            Riot games stats command
--------------------------------------------------------------------------------------------------------------------------------'''
# Initialize both of these beforehand because I know I'm going to need them later
RIOT_ACCOUNT_URL = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id"
RIOT_API_KEY = os.getenv("RIOT_API_KEY")

# This function takes in the summoner name and tagline and gets their PUUID from the Riot API

def get_riot_puuid(message):
    split = message.split("#", maxsplit = 1)
    riot_id = split[0]
    tagline = split[1]
    url = f"{RIOT_ACCOUNT_URL}/{riot_id.replace(" ", "%20")}/{tagline}"
    opgg = f"https://www.op.gg/summoners/na/{riot_id.replace(" ", "%20")}-{tagline}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    response = requests.get(url, headers = headers)

    # Status code 200 means all is good, anything not 200 is bad
    if response.status_code == 200:
        return response.json()["puuid"], opgg    # returns puuid and the op.gg link
    else:
        print(f"Failed to get Riot puuid. Error code: {response.status_code}")
        return None

RIOT_SUMMONER_URL = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid"

# This function takes the PUUID obtained from the first function and returns summoner data
def get_summoner_data(puuid):
    url = f"{RIOT_SUMMONER_URL}/{puuid}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    response = requests.get(url, headers = headers)

    '''{ This is the response from my account with sensitive information removed
        "id": "",
        "accountId": "",
        "puuid": "",
        "profileIconId": 6555,
        "revisionDate": 1741828142000,
        "summonerLevel": 547
    }'''

    if response.status_code == 200:
        profile_icon = response.json()["profileIconId"]
        summoner_level = response.json()["summonerLevel"]
        return profile_icon, summoner_level
    else:
        print(f"Failed to get summoner data. Error code: {response.status_code}")
        return None
    
RIOT_LEAGUE_URL = "https://na1.api.riotgames.com/lol/league/v4/entries/by-puuid"

# This functions returns info about player's ranked statistics
def get_ranked_stats(puuid):
    url = f"{RIOT_LEAGUE_URL}/{puuid}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    response = requests.get(url, headers = headers)

    '''{ This is the response from my account with the sensitive information removed
        "leagueId": "",
        "queueType": "RANKED_SOLO_5x5",
        "tier": "PLATINUM",
        "rank": "I",
        "summonerId": "",
        "puuid": "",
        "leaguePoints": 56,
        "wins": 10,
        "losses": 3,
        "veteran": false,
        "inactive": false,
        "freshBlood": false,
        "hotStreak": false
    }'''

    if response.status_code == 200:
        # Handles the case where a player is unranked
        if len(response.json()) == 0:
            tier = "Unranked"
            rank = ""
            lp = 0
            win_rate = 0
        else:
            for x in range (len(response.json())):
                if response.json()[x].get("queueType") == "RANKED_SOLO_5x5":
                    tier = response.json()[x]["tier"]
                    rank = response.json()[x]["rank"]
                    lp = response.json()[x]["leaguePoints"]
                    wins = response.json()[x]["wins"]
                    losses = response.json()[x]["losses"]
                    win_rate = int( 100 * ( wins / ( wins + losses )))
                    

        return  tier, rank, lp, win_rate
    else:
        print(f"Failed to get ranked statistics. Error code: {response.status_code}")
        return None

RIOT_CHAMP_MASTERY_URL = "https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid"

# This function returns the player's most played champions in descending order
def get_most_played_champions(puuid):
    url = f"{RIOT_CHAMP_MASTERY_URL}/{puuid}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    response = requests.get(url, headers = headers)

    '''{ This is the response from my account with the sensitive information removed
    "puuid": "",
    "championId": 50,
    "championLevel": 16,
    "championPoints": 144476,
    "lastPlayTime": 1737675256000,
    "championPointsSinceLastLevel": 2876,
    "championPointsUntilNextLevel": 8124,
    "markRequiredForNextLevel": 2,
    "tokensEarned": 4,
    "championSeasonMilestone": 0,
    "nextSeasonMilestone": {
        "requireGradeCounts": {
            "A-": 1
        },
        "rewardMarks": 1,
        "bonus": false,
        "totalGamesRequires": 1
    }'''

    if response.status_code == 200:
        champ = []
        champlevel = []
        champpoints = []
        for x in range (5):
            champ.append(LeagueChamps.get(f"{response.json()[x].get("championId")}").get("name"))
            champlevel.append(response.json()[x].get("championLevel"))
            champpoints.append(response.json()[x].get("championPoints"))
        
        champ_url = get_champ_splash(response.json()[0].get("championId"))

        return champ, champlevel, champpoints, champ_url
    else:
        print(f"Failed to get champion mastery. Error code: {response.status_code}")
        return None

# This function get the current game version, this method is required for the icon repo
def get_patch_version():
    url = "https://ddragon.leagueoflegends.com/api/versions.json"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()[0]
    else:
        print(f"Failed to get patch version: Error code: {response.status_code}")
        return None

# This function accesses the official League icon repository to get a specific icon
def get_icon_data(icon_id):
    patch_version = get_patch_version()
    url = f"https://ddragon.leagueoflegends.com/cdn/{patch_version}/data/en_US/profileicon.json"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json().get("data").get(f"{icon_id}").get("image").get("sprite")
    else:
        print(f"Failed to get icon data: Error code: {response.status_code}")
        return None

def get_champ_splash(champ_id):
    champ_splash = LeagueChamps.get(f"{champ_id}").get("key")
    url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ_splash}_0.jpg"
    response = requests.get(url)

    if response.status_code == 200:
        return url
    else:
        print(f"Failed to get champion splash: Error code: {response.status_code}")
        return None

@client.command()
async def stats(ctx, *, summoner_name: str):
    if Accounts.get(summoner_name):
        puuid, opgg = get_riot_puuid(Accounts.get(summoner_name))    #Works properly
        summoner_name = Accounts.get(summoner_name)
    else:
        puuid, opgg = get_riot_puuid(summoner_name) 

    profile_icon_id, summoner_level = get_summoner_data(puuid)
    #print(f"{profile_icon_id}/{summoner_level}")

    tier, rank, lp, win_rate = get_ranked_stats(puuid)
    #print(f"{tier}/{rank}/{lp}/{win_rate}")

    icon_data = get_icon_data(profile_icon_id)
    icon_url = f"https://ddragon.leagueoflegends.com/cdn/15.5.1/img/profileicon/{profile_icon_id}.png"

    champs, champlevels, champpoints, champ_url = get_most_played_champions(puuid)
    #print(f"{champs}\n{champlevels}\n{champpoints}")

    #get_match_history(puuid)

    embed = discord.Embed(
        title = summoner_name.split("#")[0],
        url = opgg,
        description = f"{champs[0]} lover\n Level {summoner_level}",
        color = 0x4dff4d)
    embed.set_thumbnail(url = icon_url)
    embed.add_field(
            name = "Ranked stats",
            value = f"{tier} {rank}\n {lp} LP\n {win_rate}% Win Rate",
            inline = True )
    embed.add_field(name = "Most Played Champions",
        value = f"1. {champs[0]}, Level {champlevels[0]},\n {champpoints[0]} Mastery\n" +
                f"2. {champs[1]}, Level {champlevels[1]},\n {champpoints[1]} Mastery\n" +
                f"3. {champs[2]}, Level {champlevels[2]},\n {champpoints[2]} Mastery\n" +
                f"4. {champs[3]}, Level {champlevels[3]},\n {champpoints[3]} Mastery\n" +
                f"5. {champs[4]}, Level {champlevels[4]},\n {champpoints[4]} Mastery\n",

        inline = True)
    embed.set_image(url = champ_url)
    
    await ctx.send(embed = embed)

'''--------------------------------------------------------------------------------------------------------------------------------
                                            Riot games match history commands
--------------------------------------------------------------------------------------------------------------------------------'''
def get_match_history(puuid):
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=5"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    response = requests.get(url, headers = headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get match history. Error code: {response.status_code}")
        return None

'''--------------------------------------------------------------------------------------------------------------------------------
                                            List function to store names
--------------------------------------------------------------------------------------------------------------------------------'''
# Accounts is the name of the json file
# format would be like +add Spellqueefs Edge#shart/darji
@client.command()
async def add(ctx, *, stored_name):
    summoner_name = stored_name.split("/", maxsplit = 1)[0]
    moniker = stored_name.split("/", maxsplit = 1)[1].strip()
    #print(f"{summoner_name} + {moniker}")

    # Creates a data entry with the key:value pair
    data = {moniker : summoner_name}

    # Checks if the account is already stored in the json file with that nickname
    if Accounts.get(moniker):
        await ctx.send("Account is already in the list that nickname")
    else:
        Accounts.update(data)
        await ctx.send("Account added successfully")

    # Saves the dict to the json file
    with open("StoredAccounts.json", 'w') as sa:
        json.dump(Accounts, sa, indent = 4)

@client.command()
async def remove(ctx, *, name):
    if Accounts.get(name):
        Accounts.pop(name)

        # Saves the dict to the json file
        with open("StoredAccounts.json", 'w') as sa:
            json.dump(Accounts, sa, indent = 4)
        await ctx.send("Successfully removed the nickname")
    else:
        await ctx.send("That nickname was not found in the database")

@client.command()
async def list(ctx):
    embed = discord.Embed(
        title = "List of saved nicknames",
        color = 0x4dff4d)
    # This link actually just links to a message that I sent in my DMs, so you'll probably have to replace this
    embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/868495107274448926/1351310309981421668/league_logo.jpg?ex=67d9e94c&is=67d897cc&hm=9f135b05c908e440e54c63154094eca2ca270749b9f9df41bb267c7fbf510fdf&")
    for nickname in Accounts:
        embed.add_field(
            name = f"{nickname} : {Accounts[nickname]}",
            value = "",
            inline = False
        )
    
    await ctx.send(embed = embed)

'''--------------------------------------------------------------------------------------------------------------------------------
                                                    Runs the pookie bot
--------------------------------------------------------------------------------------------------------------------------------'''
TOKEN = os.getenv('POOKIE_BOT_TOKEN')
client.run(TOKEN)