import time
import random

from constants import items_list
from Player import Player
from Shotgun import Shotgun, beautify_slugs, cause_effect, get_random_slugs

def display_players_stats(player1, player2, shotgun):
    print(
        player1.name,
        '{}{} - '.format(
            '🔗' if player1.handcuffed else '',
            '🔫' if player1 == shotgun.current_holder else '',
        ),
        ' '.join('❤️' for _ in range(player1.hp)),
        '\t\t',
        '|{} |'.format('🪓' if shotgun.dmg == 2 else '  '),
        '\t\t',
        ' '.join('❤️' for _ in range(player2.hp)),
        '\t- {}{}'.format(
            '🔗' if player2.handcuffed else '',
            '🔫' if player2 == shotgun.current_holder else '',
        ),
        player2.name,
    )
    print(
        '{}'.format(''.join('[{} ]'.format(b_item) for b_item in player1.get_beautiful_inv()[:4])),
        '     ' * (4 - len(player1.inventory[:4])),
        '     ' * (4 - len(player2.inventory[:4])),
        '    ' * 5,
        '{}'.format(''.join('[{} ]'.format(b_item) for b_item in player2.get_beautiful_inv()[:4])),
    )
    print(
        '{}'.format(''.join('[{} ]'.format(b_item) for b_item in player1.get_beautiful_inv()[4:])),
        '     ' * (4 - len(player1.inventory[4:])),
        '     ' * (4 - len(player2.inventory[4:])),
        '    ' * 5,
        '{}'.format(''.join('[{} ]'.format(b_item) for b_item in player2.get_beautiful_inv()[4:])),
    )

def display_boom(boom):
    print('\n\n')
    for _ in range(1, 3):
        time.sleep(0.5)
        print('.', end='')
        time.sleep(random.random())
    if boom: print('BOOM!!!')
    else: print('click')
    print()
    time.sleep(3)
    print('\n\n')

def display_inventory(shotgun):
    print('\t 0  --  Go back')
    for i in range(0, len(shotgun.current_holder.inventory)):
        print('\t', i + 1, ' -- ', items_list[shotgun.current_holder.inventory[i]])
    wat_item = input()
    if int(wat_item) != 0 and int(wat_item) <= len(shotgun.current_holder.inventory):
        inventory_item_index = int(wat_item) - 1
        success, effect = cause_effect(
            shotgun.current_holder,
            shotgun.current_opponent,
            shotgun.current_holder.inventory[inventory_item_index],
            shotgun,
        )
        if success:
            shotgun.current_holder.inventory.pop(inventory_item_index)
        else:
            print()
            print('You can\'t use that item right now!')
            print()
            time.sleep(2)
        if effect:
            time.sleep(1)
            print(effect)
            time.sleep(4)


player1 = Player(name='Darko')
player2 = Player(name='Obi', hp=player1.hp)
shotgun = Shotgun(player1, player2)

while(player1.hp > 0 and player2.hp > 0):
    random_slugs = get_random_slugs()
    print('\n\n\n\n')
    print('Slugs: ', beautify_slugs(random_slugs), '\n\n')
    time.sleep(5)
    print('\n'*50)
    shotgun.load_slugs(random_slugs)
    for _ in range(1, 4):
        player1.add_item_to_inventory()
        player2.add_item_to_inventory()

    while(len(shotgun.slugs) != 0):
        if(player1.hp <= 0 or player2.hp <= 0):
            print('Game Over!')
            break
        display_players_stats(player1, player2, shotgun)
        print('\n')

        print('Current turn: ', shotgun.current_holder.name)
        print('What do?\n\t 1 -- Shoot opponent\n\t 2 -- Shoot self (shooting self with blank slug skips opponent)\n\t 3 -- Open Inventory')
        wat_do = input()
        boom = None
        match wat_do:
            case '1':
                display_boom(shotgun.shoot_opponent())
            case '2':
                display_boom(shotgun.shoot_self())
            case '3':
                display_inventory(shotgun)
            case _:
                print('What the fuck are you doing?')
        print('\n'*50)

