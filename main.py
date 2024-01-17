import time
import random

from constants import items_list
from Player import Player
from Shotgun import Shotgun, cause_effect, get_random_slugs

player1 = Player(name='Darko')
player2 = Player(name='Obi', hp=player1.hp)
shotgun = Shotgun(player1, player2)

while(player1.hp > 0 and player2.hp > 0):
    random_slugs = get_random_slugs()
    print('Slugs: ', random_slugs)
    shotgun.load_slugs(random_slugs)
    for _ in range(1, 4):
        player1.add_item_to_inventory()
        player2.add_item_to_inventory()

    while(len(shotgun.slugs) != 0):
        if(player1.hp <= 0 or player2.hp <= 0):
            print('Game Over!')
            break
        print(player1.name, '\nHP: ', player1.hp, '\n')
        print(player2.name, '\nHP: ', player2.hp)

        print('Current holder: ', shotgun.current_holder.name)
        print('What do?\n\t 1 -- Shoot opponent\n\t 2 -- Shoot self (shooting self with blank slug skips opponent)\n\t 3 -- Open Inventory')
        wat_do = input()
        boom = None
        if wat_do == '1':
            boom = shotgun.shoot_opponent()
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
        elif wat_do == '2':
            boom = shotgun.shoot_self()
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
        elif wat_do == '3':
            print('\t 0  --  Go back')
            for i in range(0, len(shotgun.current_holder.inventory)):
                print('\t', i + 1, ' -- ', items_list[shotgun.current_holder.inventory[i]])
            wat_item = input()
            if int(wat_item) != 0:
                inventory_item_index = int(wat_item) - 1
                success = cause_effect(shotgun.current_holder, shotgun.current_opponent, shotgun.current_holder.inventory[inventory_item_index], shotgun)
                if success:
                    shotgun.current_holder.inventory.pop(inventory_item_index)
                else:
                    print()
                    print('You can\'t use that item right now!')
                    print()
                    time.sleep(2)
        else:
            print('What the fuck are you doing?')
    

