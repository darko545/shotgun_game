import asyncio

import discord
from discord.ext import commands

lock = asyncio.Lock()

intents = discord.Intents.default()
intents.message_content = True
intents.moderation = True
game_channels = []
token = ''

def get_everyone_role(server_roles):
    for role in server_roles:
        if role.name == '@everyone':
            return role

class GameChannel:
    client = None
    channel_id = None
    player_1_userid = None
    player_2_userid = None
    occupied = False
    def __init__(self, client, channel_id):
        self.client = client
        self.channel_id = channel_id

    async def init_game_channel(self):
        overwrite_everybody = discord.PermissionOverwrite()
        self.occupied = False
        overwrite_everybody.send_messages = False
        overwrite_everybody.add_reactions = False
        overwrite_everybody.read_messages = False
        overwrite_everybody.view_channel = False
        channel = None
        async with lock:
            channel = self.client.get_channel(self.channel_id)
            everyone_role = get_everyone_role(channel.guild.roles)
            await channel.set_permissions(everyone_role, overwrite=overwrite_everybody)
            await channel.set_permissions(client.user, send_messages=True, add_reactions=True)

    async def start_game_channel(self, player1):
        def check(reaction, user):
            return reaction.message.channel.id == self.channel_id
        overwrite_everybody = discord.PermissionOverwrite()
        self.occupied = True
        overwrite_everybody.send_messages = False
        overwrite_everybody.add_reactions = False
        overwrite_everybody.read_messages = True
        overwrite_everybody.view_channel = True
        channel = None
        async with lock:
            channel = self.client.get_channel(self.channel_id)
            everyone_role = get_everyone_role(channel.guild.roles)
            await channel.set_permissions(everyone_role, overwrite=overwrite_everybody)
            await channel.set_permissions(client.user, send_messages=True, add_reactions=True)
        stop_inner_loop = False
        stop_outer_loop = False
        while(not stop_outer_loop and channel):
            
            async with lock:
                channel = self.client.get_channel(self.channel_id)
                await channel.purge()
                message = await channel.send('Do you want to play a game?', silent=True)
                await message.add_reaction('<:voted:1197236357249114233>')

            reaction, player1 = await client.wait_for('reaction_add', check=check)
            print(reaction)
            print(player1)
            async with lock:
                channel = self.client.get_channel(self.channel_id)
                await channel.purge()
                await channel.send('Player: ' + player1.mention + ' is waiting to play...', silent=True)
                message = await channel.send('Do you want to join? ('+player1.mention+' can press ❌ to cancel lobby)', silent=True)
                await message.add_reaction('<:voted:1197236357249114233>')
                await message.add_reaction('❌')

            while (not stop_inner_loop):
                reaction, player2 = await client.wait_for('reaction_add', check=check)
                print(reaction)
                print(player2)
                if str(reaction.emoji) == '❌' and player1 == player2:
                    await channel.purge()
                    stop_inner_loop = True
                    continue
                if str(reaction.emoji) == '👍':
                    if player1 == player2:
                        await channel.send('Sorry ' + player1.mention + ', you can\'t play by yourself..', delete_after=3, silent=True)
                        await asyncio.sleep(4)
                        await message.clear_reactions()
                        await message.add_reaction('👍')
                        await message.add_reaction('❌')
                        continue
                    else:
                        self.player_1_userid = player1.id
                        self.player_2_userid = player2.id
        self.occupied = False


class ShotgunGameBot(discord.Client):
    game_channels = []
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

        for server in self.guilds:
            for channel in server.channels:
                if channel.name.startswith('shotgun_game'):
                    print(channel.guild.name + '> ' + channel.name)
                    self.game_channels.append(channel)
        print(self.game_channels)
        loop = asyncio.get_event_loop()
        for channel in self.game_channels:
            ch = GameChannel(self, channel.id)
            game_channels.append(ch)
            loop.create_task(ch.init_game_channel())

    async def on_message(self, message):
        if message.content.startswith('!shotgun'):
            channel = message.channel
            for game_channel in game_channels:
                g_channel = self.get_channel(game_channel.channel_id)
                if g_channel.guild == channel.guild:
                    if not game_channel.occupied:
                        game_channel.occupied = True
                        loop = asyncio.get_event_loop()
                        loop.create_task(game_channel.start_game_channel(message.author))
                        return
            await channel.send(f'No available channels, sorry!')

client = ShotgunGameBot(intents=intents)
client.run(token)

bot = commands.Bot(command_prefix='!')
@bot.command()
async def shotgun(ctx):
    print(ctx)
    

bot.run(token)