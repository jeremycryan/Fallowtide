import pygame
from field import Field
from hand import Deck, Hand
import math


class Frame:
    def __init__(self, game):
        self.game = game
        self.done = False

    def load(self):
        pass

    def update(self, dt, events):
        pass

    def draw(self, surface, offset=(0, 0)):
        surface.fill((0, 0, 0))

    def next_frame(self):
        return Frame(self.game)


class GameFrame(Frame):
    def __init__(self, game):
        super().__init__(game)

    def load(self):
        self.field = Field(self)
        self.deck = Deck()
        self.hand = Hand(self.deck, self)

        self.shake_amp = 0
        self.since_shake = 999

    def shake(self, amp=15):
        self.since_shake = 0
        self.shake_amp = amp

    def update(self, dt, events):
        self.since_shake += dt
        self.shake_amp *= 0.002**dt
        if self.shake_amp > 0:
            self.shake_amp -= 10*dt
            if self.shake_amp < 0:
                self.shake_amp = 0

        self.field.update(dt, events)
        self.hand.update(dt, events)

    def add_shake(self, offset):
        y = offset[1] + self.shake_amp * math.cos(self.since_shake * 36)
        x = y * 0.1
        return x, y

    def draw(self, surface, offset=(0, 0)):
        surface.fill((50, 50, 50))

        offset = self.add_shake(offset)

        self.field.draw(surface, offset)
        self.hand.draw(surface, offset)

    def next_frame(self):
        return Frame(self.game)