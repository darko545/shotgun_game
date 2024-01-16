import random

items_list = {
    1: 'cigarrette',
    2: 'saw',
    3: 'beer',
    4: 'lens',
    5: 'cuffs',
}

def get_random_item():
    item_index = random.randint(1, len(items_list.items()))
    return item_index

def get_random_slugs(maxLive=4, maxFake=4):
    liveSlugs = random.randint(1, maxLive)
    fakeSlugs = random.randint(liveSlugs, maxFake)
    slugs = [1,] * liveSlugs + [0,] * fakeSlugs
    random.shuffle(slugs)
    return slugs
    

class ItemEffects:
    def cause_effect(user, target, itemNumber, shotgun):
        if itemNumber == 1:
            user.change_hp(1)
        if itemNumber == 2:
            shotgun.increase_dmg()
        if itemNumber == 3:
            print("Fake" if not shotgun.unload_slug() else "Live")
        if itemNumber == 4:
            print("Fake" if not shotgun.slugs[0] else "Live")
        if itemNumber == 5:
            target.handcuffed = True

class Shotgun:
    current_holder = None
    current_opponent = None
    dmg = 2
    slugs = []

    def __init__(self, player1, player2, holder=None, opponent=None):
        players = [player1, player2]
        random.shuffle(players)
        if not holder:
            self.current_holder = players[0]
        else:
            self.current_holder = holder

        if not opponent:
            self.current_opponent = players[1]
        else:
            self.current_opponent = opponent

    def increase_dmg(self):
        self.dmg = 2

    def load_slugs(self, slugs=get_random_slugs()):
        random.shuffle(slugs)
        self.slugs = slugs
    
    def unload_slug(self):
        slug = self.slugs[0]
        if len(self.slugs) == 1:
            self.slugs = []
        else:
            self.slugs = self.slugs[1:]
        return slug
    
    def switch_holder(self):
        if self.current_opponent.handcuffed:
            self.current_opponent.handcuffed = False
            return
        temp_opponent = self.current_holder
        self.current_holder = self.current_opponent
        self.current_opponent = temp_opponent


    def shoot_self(self):
        used_slug = self.slugs[0]
        if used_slug:  # Slug was live
            print(self.current_holder.get_stats())
            self.current_holder.change_hp(-self.dmg)
            self.dmg = 1
            self.switch_holder()
        print("...click!" if not used_slug else "BOOM!")
        self.unload_slug()

    def shoot_opponent(self):
        used_slug = self.slugs[0]
        if used_slug:
            self.current_opponent.change_hp(-self.dmg)
            self.dmg = 1
        print("...click!" if not used_slug else "BOOM!")
        self.unload_slug()
        self.switch_holder()


class Player:
    name = None
    dead = False
    handcuffed = False
    inventory = []

    def __init__(self, name=None, hp=0, inventory=None):
        self.hp = hp or random.randint(2,4)
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
        print('YOU DIED!')
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
            print(self.name, ' received: ', items_list[item_index])


player1 = Player(name='Darko')
player2 = Player(name='Obi', hp=player1.get_stats().get('hp'))
shotgun = Shotgun(player1, player2)

while(player1.hp > 0 and player2.hp > 0):
    random_slugs = get_random_slugs()
    print('Slugs: ', random_slugs)
    shotgun.load_slugs(random_slugs)
    for _ in range(1, 4):
        player1.add_item_to_inventory()
        player2.add_item_to_inventory()

    while(len(shotgun.slugs) != 0):
        print(player1.name, '\nHP: ', player1.hp, '\n')
        print(player2.name, '\nHP: ', player2.hp)

        print('Current holder: ', shotgun.current_holder.name)
        wat_do = input("""What do?
               1 -- Shoot opponent
               2 -- Shoot self (shooting self with blank slug skips opponent)
               3 -- Open Inventory
                   """)
        if wat_do == '1':
            shotgun.shoot_opponent()
        elif wat_do == '2':
            shotgun.shoot_self()
        elif wat_do == '3':
            print('0 -- Go back')
            for i in range(0, len(shotgun.current_holder.inventory)):
                print(i + 1, ' -- ', items_list[shotgun.current_holder.inventory[i]])
            wat_item = input()
            if wat_item == 0:
                continue
            inventory_item_index = int(wat_item) - 1
            ItemEffects.cause_effect(shotgun.current_holder, shotgun.current_opponent, shotgun.current_holder.inventory[inventory_item_index], shotgun)
            shotgun.current_holder.inventory.pop(inventory_item_index)
        else:
            print('What the fuck are you doing?')

