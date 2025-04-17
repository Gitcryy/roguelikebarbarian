import random as r

class dices:
    def __init__(self, sides:int):
        self.sides = sides

    def roll(self, sides:int):
        return r.randint(1, sides)
