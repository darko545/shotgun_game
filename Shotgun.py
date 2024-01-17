import random
import time

def cause_effect(user, target, itemNumber, shotgun):
    if itemNumber == 1:
        user.change_hp(1)
    if itemNumber == 2:
        shotgun.increase_dmg()
    if itemNumber == 3:
        print()
        time.sleep(1)
        print('You empty the chamber, the slug was: ', 'Fake' if not shotgun.unload_slug() else 'Live')
        time.sleep(1)
        print()
    if itemNumber == 4:
        
        print()
        time.sleep(1)
        print('You check the chamber, the next slug is: ', 'Fake' if not shotgun.slugs[0] else 'Live')
        time.sleep(1)
        print()
    if itemNumber == 5:
        target.handcuffed = True

def get_random_slugs(maxSlugs=8):
    live_slugs = random.randint(1, int(maxSlugs/2))
    fake_slugs = live_slugs + 1 if random.random() > 0.5 else live_slugs
    if fake_slugs >= 3 and random.random() > 0.5:
        fake_slugs -= 1
    slugs = [1,] * live_slugs + [0,] * fake_slugs
    random.shuffle(slugs)
    return slugs

class Shotgun:
    current_holder = None
    current_opponent = None
    dmg = 1
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
            self.current_holder.change_hp(-self.dmg)
            self.dmg = 1
            self.switch_holder()
        self.unload_slug()
        return used_slug

    def shoot_opponent(self):
        used_slug = self.slugs[0]
        if used_slug:
            self.current_opponent.change_hp(-self.dmg)
            self.dmg = 1
        self.unload_slug()
        self.switch_holder()
        return used_slug