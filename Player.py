import random

from constants import items_list

def get_random_item():
    item_index = random.randint(1, len(items_list.items()))
    return item_index

class Player:
    name = None
    dead = False
    handcuffed = False
    inventory = []

    def __init__(self, name=None, hp=None, inventory=None):
        if hp:
            self.hp = hp
        else: 
            self.hp = random.randint(2,4)

        if inventory:
            self.inventory = inventory
        else:
            self.inventory = []
        self.name = name

    def get_stats(self):
        return {
            'name': self.name,
            'hp': self.hp,
            'inventory': self.inventory
        }

    def die(self):
        self.dead = True

    def change_hp(self, diff):
        if self.dead:
            print('Already dead.')
            return
        if self.hp == 4: return
        self.hp += diff
        if self.hp <= 0:
            self.die()

    def add_item_to_inventory(self):
        if len(self.inventory) < 8:
            item_index = get_random_item()
            self.inventory.append(item_index)