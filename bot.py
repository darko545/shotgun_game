import asyncio
import time
import random

import discord
from discord_token import TOKEN
from Player import Player
from Shotgun import Shotgun, beautify_slugs, cause_effect, get_random_slugs
from constants import b_nums, nums_b, cool_win_messages


intents = discord.Intents.default()
intents.message_content = True
intents.moderation = True
game_channels = []

def get_everyone_role(server_roles):
    for role in server_roles:
        if role.name == '@everyone':
            return role

def get_hp_display(player):
    return ' '.join('❤️' for _ in range(player.hp)) + ' '.join('🖤' for _ in range(player.max_hp - player.hp))

def get_player_stats(player, shotgun):
    return (
        player.name +
        '{}{}'.format(
            '🔗' if player.handcuffed else '',
            '🔫{}'.format('🪓' if shotgun.dmg == 2 else '  ') if player == shotgun.current_holder else '',
        ) +
        '\n' +
        ' '.join('❤️' for _ in range(player.hp)) +
        '\n{}'.format(''.join(
            '[{} ]'.format(b_item) for b_item in player.get_beautiful_inv()[:4])) +
        '\n{}'.format(''.join(
            '[{} ]'.format(b_item) for b_item in player.get_beautiful_inv()[4:])) +
        '\n-----------------'
    )

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
        self.player_1_userid = None
        self.player_2_userid = None
        overwrite_everybody.send_messages = False
        overwrite_everybody.add_reactions = False
        overwrite_everybody.read_messages = False
        overwrite_everybody.view_channel = False
        channel = None
        channel = self.client.get_channel(self.channel_id)
        everyone_role = get_everyone_role(channel.guild.roles)
        await channel.set_permissions(everyone_role, overwrite=overwrite_everybody)
        await channel.set_permissions(client.user, send_messages=True, add_reactions=True)
        await channel.purge()

    async def setup_game_channel(self, player1):
        def check(reaction, user):
            return reaction.message.channel.id == self.channel_id
        overwrite_everybody = discord.PermissionOverwrite()
        self.occupied = True
        overwrite_everybody.send_messages = False
        overwrite_everybody.add_reactions = False
        overwrite_everybody.read_messages = True
        overwrite_everybody.view_channel = True
        channel = None
        channel = self.client.get_channel(self.channel_id)
        everyone_role = get_everyone_role(channel.guild.roles)
        await channel.set_permissions(everyone_role, overwrite=overwrite_everybody)
        await channel.set_permissions(client.user, send_messages=True, add_reactions=True)
        stop_inner_loop = False
        stop_outer_loop = False
        while(not stop_outer_loop and channel):
            await channel.purge()
            await channel.send('Player: ' + player1.mention + ' is waiting to play...')
            message = await channel.send('Do you want to play a game of shotgun with ' + player1.name + '? ('+ player1.name +' can press ❌ to cancel lobby)', silent=True)
            await message.add_reaction('<:voted:1197236357249114233>')
            await message.add_reaction('❌')

            while (not stop_inner_loop):
                try:
                    reaction, player2 = await client.wait_for('reaction_add', check=check, timeout=600)
                except asyncio.TimeoutError:
                    await channel.purge()
                    stop_inner_loop = True
                    stop_outer_loop = True
                    await self.init_game_channel()
                    continue

                if str(reaction.emoji) == '❌' and player1 == player2:
                    await channel.purge()
                    stop_inner_loop = True
                    stop_outer_loop = True
                    await self.init_game_channel()
                    continue
                if str(reaction.emoji) == '<:voted:1197236357249114233>':
                    if player1 == player2:
                        await channel.send(
                            'Sorry ' + player1.mention + ', you can\'t play by yourself..',
                            delete_after=3,
                            silent=True,
                        )
                        await message.clear_reactions()
                        await message.add_reaction('<:voted:1197236357249114233>')
                        await message.add_reaction('❌')
                        continue
                    else:
                        self.player_1_userid = player1.id
                        self.player_2_userid = player2.id
                        stop_inner_loop = True
                        stop_outer_loop = True
                        await self.start_game(player1, player2, channel)

    async def start_game(self, player1, player2, channel):
        def check(reaction, user):
            return reaction.message.channel.id == self.channel_id
        try:
            s_player1 = Player(name=player1.mention)
            s_player2 = Player(name=player2.mention, hp=s_player1.hp)
            shotgun = Shotgun(s_player1, s_player2)
            await channel.purge()
            while(s_player1.hp > 0 and s_player2.hp > 0):
                random_slugs = get_random_slugs()
                await channel.send('Slugs: ' + beautify_slugs(random_slugs), delete_after=5)
                time.sleep(4)
                shotgun.load_slugs(random_slugs)
                for _ in range(1, 5):
                    s_player1.add_item_to_inventory()
                    s_player2.add_item_to_inventory()

                while(len(shotgun.slugs) != 0 and s_player1.hp > 0 and s_player2.hp > 0):
                    await channel.purge()
                    player1_stats = get_player_stats(s_player1, shotgun)
                    player2_stats = get_player_stats(s_player2, shotgun)
                    await channel.send(player1_stats)
                    await channel.send(player2_stats)
                    message = await channel.send(
                        'Turn: ' + shotgun.current_holder.name + '\n'
                        'Click a reaction below to take your action\n'
                        '🔼 - Shoot your opponent and pass the turn\n'
                        '🔽 - Shoot yourself (opponent\'s turn is skipped if blank shot)'
                        '{}'.format(
                            '\n🎒 - Check your inventory' if len(shotgun.current_holder.inventory) > 0 else ''
                        )
                    )
                    await message.add_reaction('🔼')
                    await message.add_reaction('🔽')
                    if len(shotgun.current_holder.inventory) > 0: await message.add_reaction('🎒')
                    break_reactions_loop = False
                    while(not break_reactions_loop):
                        reaction, player = await client.wait_for('reaction_add', check=check, timeout=600)
                        if not player.mention == shotgun.current_holder.name:
                            await channel.send('Wait your turn ' + player.mention, delete_after=10)
                        else:
                            match reaction.emoji:
                                case '🔼':
                                    asyncio.sleep(1)
                                    await channel.purge()
                                    async with channel.typing():
                                        await asyncio.sleep(5)
                                    current_damage = shotgun.dmg
                                    shot_live = shotgun.shoot_opponent()
                                    if shot_live:
                                        await channel.send('BOOM!')
                                        await channel.send(shotgun.current_opponent.name + ' -' + current_damage + 'hp')
                                    else:
                                        await channel.send('...click')
                                    time.sleep(3)
                                    break
                                case '🔽':
                                    asyncio.sleep(1)
                                    await channel.purge()
                                    async with channel.typing():
                                        await asyncio.sleep(5)
                                    current_damage = shotgun.dmg
                                    shot_live = shotgun.shoot_self()
                                    if shot_live:
                                        await channel.send('BOOM!')
                                        await channel.send(shotgun.current_holder.name + ' -' + current_damage + 'hp')
                                    else:
                                        await channel.send('...click')
                                    time.sleep(3)
                                    break
                                case '🎒':
                                    await channel.purge()
                                    await channel.send('Pick an item to use: ')
                                    b_inventory = shotgun.current_holder.get_beautiful_inv()
                                    inv_first_line = await channel.send(
                                        ''.join('[  {}  ]'.format(b_item) for b_item in b_inventory[:4]))
                                    for i in range(0, len(b_inventory[:4])):
                                        await inv_first_line.add_reaction(b_nums[i+1])
                                    inv_second_line = None
                                    if len(b_inventory) > 4:
                                        inv_second_line = await channel.send(
                                            ''.join('[  {}  ]'.format(b_item) for b_item in b_inventory[4:]))
                                        for i in range(1, len(b_inventory[4:])+1):
                                            await inv_second_line.add_reaction(b_nums[i+4])
                                    return_message = await channel.send('Return?')
                                    await return_message.add_reaction('🔙')
                                    while(True):
                                        reaction, inv_player = await client.wait_for('reaction_add', check=check, timeout=600)
                                        if player.id != inv_player.id:
                                            await channel.send('Wait your turn ' + player.mention, delete_after=10)
                                        else:
                                            if reaction.emoji == '🔙':
                                                break_reactions_loop = True
                                                break
                                            else:
                                                success, effect = cause_effect(
                                                    shotgun.current_holder.inventory[nums_b[reaction.emoji]-1],
                                                    shotgun
                                                )
                                                if success:
                                                    if effect:
                                                        await channel.send(effect)
                                                        time.sleep(5)
                                                    shotgun.current_holder.inventory.pop(nums_b[reaction.emoji]-1)
                                                    break_reactions_loop = True
                                                    break
                                                else:
                                                    await channel.send('Can\'t use that item right now...', delete_after=3)
                                    continue
                                case _:
                                    continue
        except asyncio.TimeoutError:
            await channel.purge()
            await self.init_game_channel()
        winner = None
        loser = None
        win_message = random.choice(cool_win_messages)
        for player in (s_player1, s_player2):
            if player.hp > 0:
                winner = player
            else:
                loser = player
        await channel.send(win_message.format(winner=winner.name, loser=loser.name))
        time.sleep(10)
        await channel.purge()
        await self.init_game_channel()

                        

class ShotgunGameBot(discord.Client):
    game_channels = []
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

        for server in self.guilds:
            server_channels = 0
            for channel in server.channels:
                if channel.name.startswith('shotgun_game'):
                    print(channel.guild.name + '> ' + channel.name)
                    self.game_channels.append(channel)
                    server_channels += 1
                    if server_channels >= 3:
                        break
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
                        loop.create_task(game_channel.setup_game_channel(message.author))
                        await channel.send(
                            'We have a room waiting for you '+message.author.mention+': ' + g_channel.mention, delete_after=10)
                        return
            await channel.send('No available channels, sorry ' + message.author.mention + '!', delete_after=10)
        

client = ShotgunGameBot(intents=intents)
client.run(TOKEN)
