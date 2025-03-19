## League Statistics Discord Bot
Discord bot the displays a user's Ranked statistics and champion mastery

## Process
This is honestly the first thing that I have really worked on with my free time. 
I know that all this information is pretty easily available in either the League client, or op.gg / u.gg,
but I just wanted to create an easy way for my friends and I to access our basics stats (even if they don't
really use the bot). In addition to the ranked statistics and champion mastery, the bot also displays the 
user's profile icon and splashart of their most played champion.

As it the first time I've worked in Python in a long while, I had to refamiliarize myself with the syntax of
the language. It was also my first time working with the Discord package, requests, Riot API, and os, so I had to learn 
some of the commands for those as well, but thankfully it wasn't that difficult.

For os, it was actually just opening the .env file using the os.getenv method to retrieve my tokens.

For requests, the whole difficulty was just finding the correct url to request and formatting the url correctly
so that it would work for any champion or player that would appear.

For Discord, as this was the entirety of the program, I spent a bit of time learning some important syntax.
At the beginning, I would run into many issues that the bot wouldn't have the correct permissions, or I thought
that I lost my key, or I had forgotten to enable some setting. However, once the initial hassle was settled, 
using discord's commands to operate the bot wasn't too difficult.

For the Riot API, is was difficult to navigate at first. I had trouble determining what exactly I needed from the API
as well as which APIs to use to obtain that information (they have like 20 APIs across their games). Their user
statistics are stored in the developer portal, so I had to comb through their APIs there, while their game assets
were stored on data dragon. Most of the difficulty of using these were the way the data was stored, on the developer 
portal APIs, the champions were stored by their champ ID, but when going through the data dragon assets, they were stored
by their name. To make things a bit more confusing, some of their champions didn't follow the same naming conventions as 
others (eg. the key for Rek'Sai would be RekSai, but the key for Kai'Sa would be Kaisa). Since these keys were inconsistent,
I couldn't just generalize a method to take a champions name and return its key. I created a json with all of the champion 
names and keys stored by champ ID to make obtaining this information easier.

## Quality of Life
While it is nice to be able to view basic stats without having to leave Discord, it is made more inconvenient
by having to remember the full summoner name. Ever since summoner names changed to Riot IDs, they no longer became
unique and required having a tagline to identify people with the same name. Most people don't really remember what 
their taglines are, so I added in a system for the bot to use that will allow users to bind their account name to 
a nickname of their choosing. This way, people can just type in a simple moniker to get their accounts. There is 
no limit to how many nicknames one account can have, as long as the nicknames themselves are unique.

## Final
The bot was fun to make. I originally created it on a complete whim with no idea what I wanted to do with it.
I was just adding random functions like the bot can join or leave voice channels and send a message whenver 
someone leaves my server. Eventually I settled on this, and even though the bot might sit like this, it was pretty
good experience navigating my way through complicated APIs
